import os
import datetime as dt
import ephem
import math
import logging
import glob
import subprocess
import traceback
import shutil
import numpy as np
from pathlib import Path
from astropy.io import fits


class PartitionsTree:
    distanceCriteria = 3.0  # distance in degrees below which exposures are grouped

    def __init__(self, raw_data_dir, static_cal_dir, reduced_cal_dir, reduced_science_dir, log_dir, instrument):

        # we get some info from the instrument configuration file
        self.instrument = instrument
        file_prefix = instrument.config.get('Data', 'raw_file_prefix')
        file_suffix = instrument.config.get('Data', 'raw_file_suffix')

        # we search for all raw files
        print("argument for glob.glob: {}".format(raw_data_dir + "/**/"+file_prefix+"*"+file_suffix))
        listing = glob.glob(raw_data_dir + "/**/"+file_prefix+"*"+file_suffix, recursive=True)
        print("number of raw files found: {}".format(len(listing)))

        # we create folders
        #
        # the bad pixel map, being static, is handled a bit differently
        check_and_create_folder(static_cal_dir+'/bpm')
        Path(static_cal_dir+'bpm'+'/bpm.list').touch()
        Path(static_cal_dir+'bpm'+'/toreduce_bpm').touch()

        check_and_create_folder(reduced_cal_dir)
        check_and_create_folder(reduced_science_dir)
        check_and_create_folder(log_dir)

        # dictionaries indexed by partition path containing list of partitions
        self.partList = {}
        self.biasDict = {}
        self.domeDict = {}
        self.skyDict = {}
        self.stdDict = {}
        self.sciDict = {}

        # auxiliary dictionary that help in the partitioning
        self.OBstartDict = {}
        self.filterDict = {}

        # we fill the dictionaries of observation types
        i_exposure = 0
        for file_name in listing:

            i_exposure+= 1
            exposure = Exposure(file_name, instrument)
            self.insertExposure(exposure)

            # We update the dictionaries depending on the exposure type. Note that
            # the call to insertExposure will create the new partition if it does not
            # exists, otherwise it will append the exposure to an existing partition
            # corresponding to that type of exposure.
            #
            self.biasDict = {k:v for (k,v) in self.partList.items() if 'bias/' in k}
            self.domeDict = {k:v for (k,v) in self.partList.items() if 'dome/' in k}
            self.skyDict = {k:v for (k,v) in self.partList.items() if 'sky/' in k}
            self.stdDict = {k:v for (k,v) in self.partList.items() if 'std/' in k}
            self.sciDict = {k:v for (k,v) in self.partList.items() if 'science/' in k}
            if i_exposure%10:
                Total = len(self.biasDict) + len(self.domeDict) + \
                        len(self.skyDict) + len(self.stdDict) +\
                        len(self.sciDict)
                print("BIAS:     %d" % len(self.biasDict), \
                                "DOME:     %d" % len(self.domeDict), \
                                "SKY:      %d" % len(self.skyDict), \
                                "STD:      %d" % len(self.stdDict), \
                                "SCIENCE:  %d" % len(self.sciDict), \
                                "Total     %d" % Total, end='\r')

        # ------------------- CREATION OF PARTITIONS ------------------
        #
        # Up to this point the whole partitioning is in memory. 
        # Now each partition will be created in disk: 
        #   o each partition, encoded in the dictionary key, is
        #     a relative path to the location of the corresponding
        #     virtual master product. The listing of raw files needed
        #     to create the master product will be written there.
        #
        #   o the value associated to the key, is the list of raw
        #     frames in that partition.
        #
        # After these associations all partitions will have been
        # instanced to disk as a directory path to the listing
        # of raw frames. No association between them yet.

        # here we create a bias.list file in each bias partition
        self.instantiatePartitionToDisk(reduced_cal_dir, 'bias.list', self.biasDict)

        # here we create a dome.list file in dome flat field partition
        self.instantiatePartitionToDisk(reduced_cal_dir, 'dome.list', self.domeDict)

        # here we create a sky.list file in each sky flat field partition
        self.instantiatePartitionToDisk(reduced_cal_dir, 'sky.list', self.skyDict)

        # here we create a sky.list file in each sky flat field partition
        self.instantiatePartitionToDisk(reduced_science_dir, 'std.list', self.stdDict)

        # here we create a science.list file in each science partition
        self.instantiatePartitionToDisk(reduced_science_dir, 'science.list', self.sciDict)

        # --------------- We create the lists of partitions --------------
        #
        # Note that here we read the partitions actually created in disk.
        # In the future we could compare these lists with what was in memory.
        #

        # - bpm - 
        bpm_list = glob.glob(static_cal_dir+'**/bpm.list', recursive=True)
        logging.info('number of bpm partitions: {0}'.format(len(bpm_list)))
        self.bpm_partitions = []
        for bpm_file in bpm_list:
            self.bpm_partitions.append(BiasPartition(bpm_file))

        for part in self.bpm_partitions:
            logging.info(part.OBstart)

        # - bias
        bias_list = glob.glob(reduced_cal_dir+'**/bias.list', recursive=True)
        print('number of bias partitions: ', len(bias_list))
        self.bias_partitions = []
        for bias_file in bias_list:
            self.bias_partitions.append(BiasPartition(bias_file))
    
        for part in self.bias_partitions:
            print(part.OBstart)

        # - dome
        dome_list = glob.glob(reduced_cal_dir+'**/dome.list', recursive=True)
        print('number of dome partitions: ', len(dome_list))
        self.dome_partitions = []
        for dome_file in dome_list:
            self.dome_partitions.append(SciencePartition(dome_file))
    
        for part in self.dome_partitions:
            print(part.OBstart, part.filter)

        # - sky
        sky_list = glob.glob(reduced_cal_dir+'**/sky.list', recursive=True)
        print('number of sky partitions: ', len(sky_list))
        self.sky_partitions = []
        for sky_file in sky_list:
            self.sky_partitions.append(SciencePartition(sky_file))

        for part in self.sky_partitions:
            print(part.OBstart, part.filter)

        # - std
        std_list = glob.glob(reduced_science_dir+'**/std.list', recursive=True)
        print('number of standard stars partitions: ', len(std_list))
        self.std_partitions = []
        for std_file in std_list:
            self.std_partitions.append(SciencePartition(std_file))

        for part in self.std_partitions:
            print(part.OBstart, part.filter)

        # - science
        science_list = glob.glob(reduced_science_dir+'**/science.list', recursive=True)
        print('number of science partitions: ', len(science_list))
        self.sci_partitions = []
        for science_file in science_list:
            self.sci_partitions.append(SciencePartition(science_file))

        for part in self.sci_partitions:
            print(part.OBstart, part.filter)

        # ------------------- DEPENDENCY TREE CREATION --------------------
        #
        # Here we create the virtual calibration products. These products are the names
        # of the master calibration products symbolically linked to the partition
        # containing the list of raw data needed to create that master calibration product.
        # The actual master products will be created by the notebook that runs
        # the mefpp engine in each of those partition, in order: first the bpms, which
        # just create symbolic links to the static calibrtion bpm partition. Then the
        # biases needed for dome, sky, and science. Then the master flat field which requires
        # the master bias, master dome, and master sky products. Finally the std and science
        # treated the same way.
        #
        # exposurePartition = mar.PartitionsTree(raw_data_dir, static_cal_dir, reduced_cal_dir, reduced_science_dir, log_dir, instrument)
        # bpm_partitions = exposurePartition.bpm_partitions
        # bias_partitions = exposurePartition.bias_partitions
        # dome_partitions = exposurePartition.dome_partitions
        # sky_partitions = exposurePartition.sky_partitions
        # std_partitions = exposurePartition.std_partitions
        # sci_partitions = exposurePartition.sci_partitions
        #
        # We associate a bpm partition to each science frame and create symbolic link in
        # corresponding directory
        self.link_bpm(self.sci_partitions,  instrument, part_type='sci')
        self.link_bpm(self.dome_partitions, instrument, part_type='dome')
        self.link_bpm(self.sky_partitions,  instrument, part_type='sky')
        self.link_bpm(self.std_partitions,  instrument, part_type='std')
        self.link_bpm(self.bias_partitions, instrument, part_type='bias')

        # We select the closests in time calibration products. 
        # The following operations are done only on memory.

        # select and attach bias partition to science partitions
        self.select_nearest_calib(self.sci_partitions, self.bias_partitions, calpart_type='bias', ndays_max=10)
        self.select_nearest_calib(self.std_partitions, self.bias_partitions, calpart_type='bias', ndays_max=10)

        # select and attach sky partition to science partitions
        # Note that this also links the master flat
        self.select_nearest_calib(self.sci_partitions, self.sky_partitions, calpart_type='sky', ndays_max=30)
        self.select_nearest_calib(self.std_partitions, self.sky_partitions, calpart_type='sky', ndays_max=30)

        # select and attach bias and dome partitions to sky partitions
        self.select_nearest_calib(self.sky_partitions, self.bias_partitions, calpart_type='bias', ndays_max=30)
        self.select_nearest_calib(self.sky_partitions, self.dome_partitions, calpart_type='dome', ndays_max=30)

        # select and attach bias partitions to dome partitions
        self.select_nearest_calib(self.dome_partitions, self.bias_partitions, calpart_type='bias', ndays_max=30)

        # at this point we have the biases and mff for each science frame.
        # Now we create virtual calibration products as a symbolic link.
        #
        self.link_virtual_products(self.sci_partitions, partition_type='sci', calpart_type='bias')
        self.link_virtual_products(self.std_partitions, partition_type='std', calpart_type='bias')

        self.link_virtual_products(self.sci_partitions, partition_type='sci', calpart_type='mff')
        self.link_virtual_products(self.std_partitions, partition_type='std', calpart_type='mff')

        self.link_virtual_products(self.sky_partitions, partition_type='sky', calpart_type='bias')
        self.link_virtual_products(self.sky_partitions, partition_type='sky', calpart_type='dome')
        self.link_virtual_products(self.dome_partitions, partition_type='dome', calpart_type='bias')


    def link_bpm(self, partitions, instrument, part_type='sci'):
        """
        Creates symbolic links in all partitions in list partitions, to the
        corresponding master BPM file in the static calibration directory.

        Note that the BPM files needs to exists before creating the symbolic links.
        """
        for part in partitions:
            part.bpmPartition = self.bpm_partitions[0]
            #print((part.bpmPartition).base_path)
            #print(instrument.bpm_prefix+'*'+instrument.reduced_file_suffix)
            for i in range(1, instrument.nextensions+1):
                bpm_file = (part.bpmPartition).base_path+'/'+instrument.bpm_prefix+'_%02d.fits'%(i,)
                local_bpm_filename = part.base_path+'/'+instrument.bpm_prefix+'_%02d.fits'%(i,)
                if not Path(bpm_file).is_file():
                    try:
                        os.symlink(bpm_file, local_bpm_filename)
                        print("create symbolic link from : {}".format(local_bpm_filename))
                        print("                       to : {}".format(bpm_file))
                        Path((part.bpmPartition).base_path+'/toreduce_'+part_type).touch()
                        pass
                    except FileExistsError:
                        pass
                    except Exception as e:
                        print(e)
                        pass
                
                else:
                    print("symbolic link exists from : {}".format(local_bpm_filename))
                    print("                       to : {}".format(bpm_file))


    def select_nearest_calib(self, partitions, cal_partitions, calpart_type='bias', ndays_max=10):
        """
        Select the calibration nearest in time. For dome, sky flats, std, and sci we
        match the filter.

        This function does the linking only in memory. The command link needs to be
        invoqued afterward.
        """
        for part in partitions:
            # here we look for the closest in time bias partition
            zdate = part.OBstart

            # we find the bias closest in time
            calBestDeltaT = 3600.*24.*ndays_max
            for cal_part in cal_partitions:
                if 'bias' not in calpart_type:
                    if part.filter != cal_part.filter:
                        continue
                cal_date = cal_part.OBstart
                deltaT = timeDistance(zdate, cal_date)
                #print(sci_date, bias_date, deltaT)
                if deltaT < calBestDeltaT:
                    calBestDeltaT = deltaT
                    if 'bias' in calpart_type:
                        part.biasPartition = cal_part
                    elif 'dome' in calpart_type:
                        part.domePartition = cal_part
                    elif 'sky' in calpart_type:
                        part.skyPartition = cal_part
                        part.mffPartition = cal_part
                if hasattr(cal_part, 'filter'):
                    print(f'partition: {part.filter} {part.OBstart}\n    {calpart_type}: {cal_part.OBstart} {cal_part.filter} {round(calBestDeltaT/3600.0/24., 3)}')
                else:
                    print(f'partition: {part.filter} {part.OBstart}\n    {calpart_type}: {cal_part.OBstart} {round(calBestDeltaT/3600.0/24., 3)}')


    def link_virtual_products(self, partitions, partition_type='sci', calpart_type='bias'):
        """
        Link in each partition of type partition_type, a master calibration product, of type calpart_type.
        Each partition in the partitions list must have an associated calibratipn partition of the type.
        After running this procedure all the master calibration products needed for the reduction
        of the partition will be virtual products, that is, broken links to the calibration partition.
        The link will not be broken once the reduction processes is run the calibration partitition.
        """
        for part in partitions:
            if 'bias' in calpart_type:
                prefix = self.instrument.bias_prefix
                base_path = (part.biasPartition).base_path
                mcal = (part.biasPartition).base_path+'/'+prefix+'.fits'
                mcal_link = part.base_path+'/'+prefix+'.fits'
            if 'mff' in calpart_type:
                prefix = self.instrument.mff_prefix
                base_path = (part.mffPartition).base_path
                mcal = (part.mffPartition).base_path+'/'+prefix+'_'+part.filter+'.fits'
                mcal_link = part.base_path+'/'+prefix+'_'+part.filter+'.fits'
            if 'dome' in calpart_type:
                prefix = self.instrument.domeff_prefix
                base_path = (part.domePartition).base_path
                mcal = (part.domePartition).base_path+'/'+prefix+'_'+part.filter+'.fits'
                mcal_link = part.base_path+'/'+prefix+'_'+part.filter+'.fits'

            if not Path(mcal_link).is_symlink():
                try:
                    os.symlink(mcal, mcal_link)
                except FileExistsError:
                    pass
                except Exception as e:
                    print(e)
                    pass
                Path(base_path+'/toreduce_'+partition_type).touch()
                print(mcal)


    def insertExposure(self, exposure):
        """
            Inserts exposure instance to the partition list dictionary,
            which is indexed by a string representing the subdirectories
            to where the frame will be saved. The subdirectory path is
            of the form

                bias/<ob.id>/<ob.start>                     for biases
                <expo type>/<ob.id>/<filter>/<ob.start>     for type dome or sky flats
                std/<target>/<filter>/<ob.start>            for standard star exposures
                science/<target>_<ra>_<dec>/<filter>/<ob.start> for science and associated sky
                unknown/<dpr.type>                          for any other exposure

        """

        # we select the partition according to exposure dpr.type
        if exposure.is_bias:
            key_str = 'bias/' + '%d' % exposure.obsid + '/' + exposure.OBstart
        elif exposure.is_domeff:
            key_str = 'dome/' + '%d' % exposure.obsid + '/' + exposure.filter + '/' + exposure.OBstart
        elif exposure.is_skyff:
            key_str = 'sky/' + '%d' % exposure.obsid + '/' + exposure.filter + '/' + exposure.OBstart
        elif exposure.is_std:
            key_str = 'std/' + exposure.target + '/' + \
                      exposure.filter + '/' + \
                      exposure.OBstart
        elif exposure.is_science:
            key_str = 'science/' + exposure.target + '_' + \
                      ("%010.3f" % exposure.tel_alpha).replace('.', 'p') + '_' + \
                      ("%09.1f" % exposure.tel_delta).replace('.', 'p').replace('-', 'm') + '/' + \
                      exposure.filter + '/' + \
                      exposure.OBstart
        elif exposure.is_unknown:
            logging.info("dpr type: {exposure.dpr_type} not classifiable.")
            key_str = 'unknown/' + '%s' % exposure.dpr_type
        else:
            raise Exception("insertExposure: dpr type: {exposure.dpr_type} not classified. SHOULD NEVER REACH THIS POINT.")

        if key_str in self.partList:
            self.partList[key_str].append(exposure)
        else:
            self.partList[key_str] = [exposure]
            self.OBstartDict[key_str] = exposure.OBstart
            self.filterDict[key_str] = exposure.filter

    def instantiatePartitionToDisk(self, base_dir, list_name, frameDict):
        """Creates file *.list and write the full link to
        the raw files that will be reduced in that partition.

        Input:

            base_dir: name of directory to contain reduced calibration data
            list_name: either bias.list, dome.list, sky.list. or science.list
            frameDict: dictionary indexed with full subdirectory path
                        to where the list will be writen; and with values
                        equal to the full path to the raw files.
    
        Output:
            The creation of the list files
        """
        for aFramePartitionKey, aFramePartitionList in frameDict.items():
            subdir_str = aFramePartitionKey

            check_and_create_folder(base_dir + aFramePartitionKey)

            # we erase the list if it exists. This ensure that
            # we can run script any time.
            with open(base_dir + aFramePartitionKey + '/' + list_name, 'w') as f:
                pass

            for aFrame in aFramePartitionList:
                logging.info("{0} -- {1}".format(subdir_str, aFrame.filename))
                check_and_create_folder(base_dir + '/' + subdir_str)

                try:
                    with open(base_dir + '/' + subdir_str + '/' + list_name, 'a') as f:
                        print(aFrame.filename, file=f)
                except:
                    raise Exception('could not change directory to: ' + base_dir + '/' + subdir_str)

    def getDistance(self, partition, observation):
        ra = 0.0
        dec = 0.0
        n = 0
        for obs in partition:
            n += 1
            ra += obs.ra
            dec += obs.dec
        ra = ra / float(n)
        dec = dec / float(n)
        return math.sqrt((ra - observation.ra) ** 2 + (dec - observation.dec) ** 2)

    def getKeyVal(self, filename, key):
        with fits.open(filename) as hdu_list:
            primary_header = hdu_list[0].header
            val = primary_header[key]
            return val

    def get_phase_on_day(self, year, month, day):
        """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
        # Ephem stores its date numbers as floating points, which the following uses
        # to conveniently extract the percent time between one new moon and the next
        # This corresponds (somewhat roughly) to the phase of the moon.

        # Use Year, Month, Day as arguments
        date = ephem.Date(dt.date(year, month, day))

        nnm = ephem.next_new_moon(date)
        pnm = ephem.previous_new_moon(date)

        lunation = (date - pnm) / (nnm - pnm)

        # Note that there is a ephem.Moon().phase() command, but this returns the
        # percentage of the moon which is illuminated. This is not really what we want.

        return lunation


class Exposure:
    """
        Class to create an exposure instance using the instrument configuration for calssification.
    """
    def __init__(self, filename, instrument):

        self.filename = filename
        with fits.open(filename) as hdu_list:
            primary_header = hdu_list[0].header
            self.dpr_catg = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'dpr_catg_key').replace('"',''))
            self.dpr_type = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'dpr_type_key').replace('"',''))
            self.obsid = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'obid_key').replace('"',''))
            self.OBstart = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'obstart_key').replace('"',''))
            self.dateobs = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'dateobs_key').replace('"',''))
            self.tplnexp = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'tplnexp_key').replace('"',''))
            self.tplexpno = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'tplexpno_key').replace('"',''))
            self.filter = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'filt_key').replace('"','')).replace('#','n').replace('/','s')
            self.exptime = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'inst_exp_key').replace('"',''))

            # here we classify the exposure
            self.is_bias = False
            if instrument.config.get('Primary Keywords', 'bias_dpr_catg_val').replace('"','') in self.dpr_catg and \
                    instrument.config.get('Primary Keywords', 'bias_dpr_type_val').replace('"','') in self.dpr_type:
                self.is_bias = True

            self.is_domeff = False
            if instrument.config.get('Primary Keywords', 'domeff_dpr_catg_val').replace('"','') in self.dpr_catg and \
                    instrument.config.get('Primary Keywords', 'domeff_dpr_type_val').replace('"','') in self.dpr_type:
                self.is_domeff = True

            self.is_skyff = False
            if instrument.config.get('Primary Keywords', 'skyff_dpr_catg_val').replace('"','') in self.dpr_catg and \
                    instrument.config.get('Primary Keywords', 'skyff_dpr_type_val').replace('"','') in self.dpr_type:
                self.is_skyff = True

            self.is_std = False
            if instrument.config.get('Primary Keywords', 'std_dpr_catg_val').replace('"','') in self.dpr_catg and \
                    instrument.config.get('Primary Keywords', 'std_dpr_type_val').replace('"','') in self.dpr_type:
                self.is_std = True

            self.is_science = False
            if instrument.config.get('Primary Keywords', 'sci_dpr_catg_val').replace('"','') in self.dpr_catg:
                sci_dpr_type_val_list = list(instrument.config.get('Primary Keywords', 'sci_dpr_type_val').replace('"',''))
                for atype in sci_dpr_type_val_list:
                    if atype in self.dpr_catg:
                        self.is_science = True

            # here we add sky position info if science or std
            if (self.is_std or self.is_science):
                self.ra = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'ra_key').replace('"',''))
                self.dec = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'dec_key').replace('"',''))
                self.tel_alpha = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'targ_alpha_key').replace('"',''))
                self.tel_delta = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'targ_delta_key').replace('"',''))
                print()
                self.target = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'targ_name_key').replace('"','')).replace(' ', '_')

                # we add the FLI
                yyyy = int(self.dateobs[0:4])
                mm = int(self.dateobs[5:7])
                dd = int(self.dateobs[8:10])
                fli = self.get_phase_on_day(yyyy, mm, dd)
                if fli <= 0.5:
                    fli = fli * 2.0
                else:
                    fli = 2.0 * (1 - fli)
                self.fli = fli

            # if we cannot classify we explicitly set to unknown
            self.is_unknown = False
            if not (self.is_bias or self.is_domeff or self.is_skyff or self.is_std or self.is_science):
                self.is_unknown = True

    def get_phase_on_day(self, year, month, day):
        """Returns a floating-point number from 0-1. where 0=new, 0.5=full, 1=new"""
        # Ephem stores its date numbers as floating points, which the following uses
        # to conveniently extract the percent time between one new moon and the next
        # This corresponds (somewhat roughly) to the phase of the moon.

        # Use Year, Month, Day as arguments
        date = ephem.Date(dt.date(year, month, day))

        nnm = ephem.next_new_moon(date)
        pnm = ephem.previous_new_moon(date)
        lunation = (date - pnm) / (nnm - pnm)

        # Note that there is a ephem.Moon().phase() command, but this returns the
        # percentage of the moon which is illuminated. This is not really what we want.

        return lunation

    def getKeyVal(self, primary_header, key):
        val = primary_header[key]
        return val


class ExposuresPartition:

    def __init__(self, filename, frametype, instrument):

        self.base_path = os.path.dirname(filename)
        self.frametype = frametype

        self.filter = None
        if frametype != 'BIAS' or frametype != 'BPM':
            self.filter = self.getFilter(filename)
        self.framelist = filename
        self.frame = None

        # for the moment the BPM have no time stamp
        self.OBstart = None
        if frametype != 'BPM':
            self.OBstart = self.getOBstart(filename)

        # we construct the names of master calibration products according to file type
        self.framelist = None
        self.frame = None
        if frametype == 'BPM':
            self.framelist = None
            self.frame = self.base_path + '/'+instrument.bpm_prefix+'_01.fits'
        elif frametype == 'BIAS':
            self.framelist = self.base_path + '/bias.list'
            self.frame = self.base_path + '/'+instrument.bias_prefix+'.fits'
        elif frametype == 'FLAT,DOME':
            self.framelist = self.base_path + '/dome.list'
            self.frame = self.base_path + '/'+instrument.domeff_prefix+'_' + self.filter + '.fits'
        elif frametype == 'FLAT,SKY':
            self.framelist = self.base_path + '/sky.list'
            self.frame = self.base_path + '/'+instrument.skyff_prefix+'_' + self.filter + '.fits'
        elif frametype == 'MFF':
            self.framelist = self.base_path + '/mff.list'
            self.frame = self.base_path + '/'+instrument.mff_prefix+'_' + self.filter + '.fits'
        elif frametype == 'STD':
            self.framelist = self.base_path + '/std.list'
            self.frame = None
        elif frametype == 'SCIENCE' or frametype == 'SKY':
            self.framelist = self.base_path + '/science.list'
            self.frame = None

        self.bpmPartition = None
        self.bpmFrame = None
        self.bpm_have = False
        self.bpm_have_link = False

        self.biasPartition = None
        self.biasFrame = None
        self.bias_have = False
        self.bias_have_link = False

        self.domePartition = None
        self.domeFrame = None

        self.skyPartition = None
        self.SkyFrame = None

        self.mffPartition = None
        self.mffFrame = None

    def getFilter(self, filename):
        fields = filename.split('/')
        return fields[-3]

    def getOBstart(self, filename):
        fields = filename.split('/')
        return fields[-2]


class SciencePartition:

    def __init__(self, filename):
        self.base_path = os.path.dirname(filename)
        self.filter = self.getFilter(filename)
        self.OBstart = self.getOBstart(filename)
        self.bpmPartition = None
        self.biasPartition = None
        self.biasFrame = None
        self.domePartition = None
        self.domeFrame = None
        self.skyPartition = None
        self.SkyFrame = None
        self.mffPartition = None
        self.mffFrame = None

    def getFilter(self, filename):
        fields = filename.split('/')
        return fields[-3]

    def getOBstart(self, filename):
        fields = filename.split('/')
        return fields[-2]


class BiasPartition:

    def __init__(self, filename):
        self.base_path = os.path.dirname(filename)
        self.OBstart = filename.split('/')[-2]
        self.bpmPartition = None
        self.mffPartition = None

    def getOBstart(self, filename):
        return filename.split('/')[-2]


def check_and_create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(e)
        pass


def timeDistance(time_str1, time_str2):
    fmt = '%Y-%m-%dT%H:%M:%S'
    return abs((dt.datetime.strptime(time_str1, fmt) - dt.datetime.strptime(time_str2, fmt)).total_seconds())


def getKeyVal(filename, key):
    with fits.open(filename) as hdu_list:
        primary_header = hdu_list[0].header
        val = primary_header[key]
        return val

def get_partition(path_list):
    list_type = path_list.split("/")[-1]
    list_type = list_type[:-5]
    bias = True if "bias" in list_type else False

    images_list = glob.glob(path_list, recursive=True)
    print('number of {} partitions: {}'.format(list_type, len(images_list)))
    partitions = []
    for file in images_list:
        if bias:
            partitions.append(BiasPartition(file))
        else:
            partitions.append(SciencePartition(file))

    for part in partitions:
        print(part.OBstart)

    return partitions


def associate_bpm(partition, bpm_partitions,instrument):
    """
    We link the BPM files from the static calib directory to the data
    reduction directory.

    This is dangerous as extensions are being identified by an index
    and not by a name.
    """
    for part in partition:
        part.bpmPartition = bpm_partitions[0]
        for i in range(1, instrument.next_valid+1):
            bpm_file = part.bpmPartition.base_path + "/"+instrument.bpm_prefix+"_{:02d}.fits".format(i)
            if not Path(bpm_file).is_file():
                try:
                    os.symlink(bpm_file, part.base_path + "/"+instrument.bpm_prefix+"_{:02d}.fits".format(i))
                    pass
                except:
                    pass
                Path(part.bpmPartition.base_path + '/toreduce_bias').touch()


def runCmd(str_cmd, basepath, p_shell=True):
    """
    A wrapper to run system commands.

    Parameters
    ----------
    str_cmd: str
      Command string to be executed in the shell

    p_shell: bool
      If True (default), command will be executed through the shell, and all
      cout/cerr messages will be available.
      If False, exception is the only way to find out problems during the call.

    Returns
    -------
      0 if some error, or 1 if all was OK

    Notes
    -----
    TODO:
      - allow to launch commands in background
      - best checking of error when shell=True
    """

    print("log.info: Running command: %s \n" % (str_cmd,))

    try:
        cwd = os.getcwd()
        os.chdir(basepath)
        print('\n---- runCmd: ', str_cmd)
        p = subprocess.Popen(str_cmd, bufsize=0, shell=p_shell, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=True)
        # Warning
        # We use communicate() rather than .stdin.write, .stdout.read or .stderr.read
        # to avoid deadlocks due to any of the other OS pipe buffers filling up and
        # blocking the child process.(Python Ref.doc)

        (stdoutdata, stderrdata) = p.communicate()
        err = stdoutdata.decode('utf-8') + " " + stderrdata.decode('utf-8')
        print('debuggin: ' + err)
        # IMPORTANT: Next checking (only available when shell=True) not always detect all kind of errors !!
        if err.count('WARNING: Significant inaccuracy'):
            print("Canno't get accuracy astrometric calibration")
            return 2
        elif (err.count('ERROR ') or err.count('error ') or err.count("Error ")
              or err.count('*Error*')
              or err.count('Segmentation fault') or err.count("command not found")
              or err.count("No such file or directory")):
            print("An error happened while running command --> %s \n" % (err,))
            print(stderrdata.decode('utf8'))
            return 1  # ERROR
        else:
            print(stdoutdata.decode('utf8'))
            return 0  # NO ERROR
    except Exception:
        traceback.print_exc()


def associateBPM(part, scipart, instrument):
    """
    Associate a BPM set to a science data reduction partition.
    """
    have_bpm_link = True
    have_bpm = True
    for i in range(1, instrument.next_valid+1):
        bpm_name = part.base_path + '/'+instrument.bpm_prefix+'_%02d.fits' % (i,)
        if not Path(bpm_name).is_symlink():
            have_bpm_link = False
        else:
            have_bpm_link = have_bpm_link and True

        if not Path(bpm_name).exists():
            have_bpm = False
        else:
            have_bpm = have_bpm and True

    scipart.bpm_have = have_bpm
    scipart.bpm_have_link = have_bpm_link

    if have_bpm_link:
        bpm_frame = Path(bpm_name).resolve().as_posix()
        part.bpmFrame = bpm_frame
        part.bpmPartition = ExposuresPartition(bpm_frame, 'BPM', instrument)


def associateBias(part, scipart, instrument):
    have_bias_link = True
    have_bias = True

    bias_name = part.base_path + '/'+instrument.bias_prefix+'.fits'
    if not Path(bias_name).is_symlink():
        have_bias_link = False

    if not Path(bias_name).exists():
        have_bias = False

    part.bias_have = have_bias
    part.bias_have_link = have_bias_link

    if have_bias_link:
        bias_frame = Path(bias_name).resolve().as_posix()
        part.biasFrame = bias_frame
        part.biasPartition = ExposuresPartition(bias_frame, 'BIAS', instrument)


def associateDome(part, scipart, instrument):
    have_dome_link = True
    have_dome = True

    dome_name = part.base_path + '/'+instrument.domeff_prefix+'_' + scipart.filter + '.fits'
    if not Path(dome_name).is_symlink():
        have_dome_link = False

    if not Path(dome_name).exists():
        have_dome = False

    part.dome_have = have_dome
    part.dome_have_link = have_dome_link

    if have_dome_link:
        dome_frame = Path(dome_name).resolve().as_posix()
        part.domeFrame = dome_frame
        part.domePartition = ExposuresPartition(dome_frame, 'FLAT,DOME', instrument)


def associateSky(part, scipart, instrument):
    have_sky_link = True
    have_sky = True

    # sky_name = part.base_path+'/OMEGACAM_SKYFF_'+scipart.filter+'.fits'
    sky_name = part.base_path + '/sky.list'
    if not Path(sky_name).is_symlink():
        have_sky_link = False

    if not Path(sky_name).exists():
        have_sky = False

    part.sky_have = have_sky
    part.sky_have_link = have_sky_link

    if have_sky_link or have_sky:
        sky_frame = Path(sky_name).resolve().as_posix()
        part.skyPartition = ExposuresPartition(sky_frame, 'FLAT,SKY', instrument)


def associateMFF(part, scipart, instrument):
    have_mff_link = True
    have_mff = True

    mff_name = part.base_path + '/'+instrument.mff_prefix+'_' + scipart.filter + '.fits'
    if not Path(mff_name).is_symlink():
        have_mff_link = False

    if not Path(mff_name).exists():
        have_mff = False

    part.mff_have = have_mff
    part.mff_have_link = have_mff_link

    if have_mff_link:
        mff_frame = Path(mff_name).resolve().as_posix()
        part.mffFrame = mff_frame
        part.mffPartition = ExposuresPartition(mff_frame, 'MFF', instrument)


# ---------------------------------- Data reduction section ------------------------------

def copy_paf(mefpp_dir, basepath, instrument):
    """
    This routine copy the reduction configuration parameters needed by
    the mefpp reduction engine to the directory where the reduction
    will take place. It centralice the copying for all calibration
    and science reductions.
    """
    # we prefer the locally provided parameter file, if it exists

    mefpp_paf_exists = False
    if Path(basepath + '/mefpp.paf').exists():
        mefpp_paf_exists = True

    if not mefpp_paf_exists:
        if Path(instrument.config_dir + '/'+instrument.mefpp_paf).exists():            # locally provided mefpp paf file
            shutil.copy(instrument.config_dir + '/'+instrument.mefpp_paf, basepath + '/mefpp.paf')
            print("Using paf: {}".format(instrument.config_dir + '/'+instrument.mefpp_paf))
        elif Path(mefpp_dir + '/config/'+instrument.mefpp_paf).exists():          # pycavi distribution paf file
            print("No paf file in {}. Using user config  paf.".format(instrument.config_dir))
            print("Using mefpp  paf.")
            shutil.copy(mefpp_dir + '/config/'+instrument.mefpp_paf, basepath + '/mefpp.paf')
        else:
            print("copy_paf: could not find paf file for mefpp")

    if Path(basepath + '/mefpp.paf').exists():
        mefpp_paf_exists = True
    
    return mefpp_paf_exists

def mefpp_reduce_bpm(mefpp_dir, calib_dir, instrument):
    # here we reduce the bpm frames which for now is only a cp operation
    bpm_files_list = [mefpp_dir + '/static_cal/' +instrument.bpm_prefix +'_%02d.fits' % i for i in range(1, instrument.next_valid+1)]
    for file in bpm_files_list:
        # print(file)
        shutil.copy(file, calib_dir + '/bpm/')
    print('mefpp_reduce_bpm: done copying BPMs')


def mefpp_reduce_bias(mefpp_dir, bias_part_list, instrument):
    print('mefpp_reduce_bias: length of bias partition list: %d' % len(set(bias_part_list)))
    for bias_part in set(bias_part_list):

        basepath = bias_part.base_path
        bias_list = basepath + '/bias.list'
        print('mefpp_reduce_bias: ', bias_list)

        bias_list_exists = False
        if Path(bias_list).exists():
            bias_list_exists = True

        # copying appropriate parameter file, paf file, to basepath directory
        mefpp_paf_exists = copy_paf(mefpp_dir, basepath, instrument)
        if not mefpp_paf_exists:
            raise Exception("mefpp_reduce_bias: could not find or copy mefpp.paf to bias basepath.")

        # checking for the presence of bpm files
        bpm_files_list = glob.glob(basepath + '/'+instrument.bpm_prefix+'_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # checking to see if bias was already reduced
        #
        bias_already_reduced = False
        if Path(basepath + '/'+instrument.bias_prefix+'.fits').exists():
            bias_already_reduced = True

        # we produce the master bias here if not already done
        #
        if (not bias_already_reduced) and (bias_list_exists and mefpp_paf_exists and bpm_exists):
            print('\n\n', basepath.split()[-1], bias_list_exists, mefpp_paf_exists, bpm_exists, bias_already_reduced)
            # os.chdir(basepath)
            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           '--bias ' + bias_list + \
                           ' --biassave > ' + basepath + '/mefpp.log'
            print('basepath: ', basepath)
            print('bias_already_reduced: ', bias_already_reduced)
            print('bias_list_exists: ', bias_list_exists)
            print('mefpp_paf_exists: ', mefpp_paf_exists)
            print('bpm_exists: ', bpm_exists)
            print('\n', command_line)
            print('\nbias_list: ', bias_list)
            rcode = runCmd(command_line, basepath)
            if rcode == 1:
                raise Exception('Error running ' + command_line)
            else:
                print('success running ' + command_line)
            # os.chdir(cwd)
        else:
            print('basepath: ', basepath)
            print('bias_already_reduced: ', bias_already_reduced)
            print('bias_list_exists: ', bias_list_exists)
            print('mefpp_paf_exists: ', mefpp_paf_exists)
            print('bpm_exists: ', bpm_exists)


def mefpp_reduce_dome(mefpp_dir, dome_part_list, instrument):
    print('mefpp_reduce_dome: length of dome partition list: %d' % len(set(dome_part_list)))
    for dome_part in dome_part_list:

        basepath = dome_part.base_path
        dome_list = basepath + '/dome.list'

        dome_list_exists = False
        if Path(dome_list).exists():
            dome_list_exists = True

        # copying appropriate parameter file, paf file, to basepath directory
        mefpp_paf_exists = copy_paf(mefpp_dir, basepath, instrument)
        if not mefpp_paf_exists:
            raise Exception("mefpp_reduce_dome: could not find or copy mefpp.paf to dome basepath.")

        bpm_files_list = glob.glob(basepath + '/'+instrument.bpm_prefix+'_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/'+instrument.bias_prefix+'.fits').exists():
            mb_exists = True
        else:
            pass

        dome_already_reduced = False
        if Path(basepath + '/'+instrument.domeff_prefix+'_' + dome_part.filter + '.fits').exists():
            dome_already_reduced = True

        print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)

        if (not dome_already_reduced) and (dome_list_exists and mefpp_paf_exists and bpm_exists and mb_exists):
            print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)
            # os.chdir(basepath)
            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           ' --bias ' + basepath + '/'+instrument.bias_prefix+'.fits ' + \
                           ' --dome ' + dome_list + \
                           ' --domesave > ' + basepath + '/mefpp.log'
            print(command_line)
            rcode = runCmd(command_line, basepath)
            if rcode == 1:
                raise Exception('Error running ' + command_line)
            else:
                print('success running ' + command_line)
            # os.chdir(cwd)
        else:
            print('skipping dome reduction')


def mefpp_reduce_sky(mefpp_dir, sky_part_list, instrument):
    print('mefpp_reduce_sky: length of sky partition list: %d' % len(set(sky_part_list)))
    for sky_part in set(sky_part_list):

        basepath = sky_part.base_path
        sky_list = basepath + '/sky.list'

        sky_list_exists = False
        if Path(sky_list).exists():
            sky_list_exists = True

        # copying appropriate parameter file, paf file, to basepath directory
        mefpp_paf_exists = copy_paf(mefpp_dir, basepath, instrument)
        if not mefpp_paf_exists:
            raise Exception("mefpp_reduce_sky: could not find or copy mefpp.paf to skyff basepath.")

        bpm_files_list = glob.glob(basepath + '/'+instrument.bpm_prefix+'_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/'+instrument.bias_prefix+'.fits').exists():
            mb_exists = True
        else:
            pass

        # here we check for the required dome ff
        domeff_exists = False
        domeff_name = basepath + '/'+instrument.domeff_prefix+'_' + sky_part.filter + '.fits'
        if Path(domeff_name).exists():
            print(domeff_name + ' exists')
            domeff_exists = True
        else:
            print(domeff_name + ' does not exist')
            pass

        sky_already_reduced = False
        skyff_name = basepath + '/'+instrument.skyff_prefix+'_' + sky_part.filter + '.fits'
        if Path(skyff_name).exists():
            print(skyff_name + ' exists')
            sky_already_reduced = True
        else:
            print(skyff_name + ' does not exist')

        print(basepath.split()[-1], sky_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, domeff_exists,
              sky_already_reduced)

        if (not sky_already_reduced) and (
                sky_list_exists and mefpp_paf_exists and bpm_exists and mb_exists and domeff_exists):
            print(basepath.split()[-1], sky_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, domeff_exists,
                  sky_already_reduced)
            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           ' --bias ' + basepath + '/'+instrument.bias_prefix+'.fits ' + \
                           ' --dome ' + basepath + '/'+instrument.domeff_prefix+'_' + sky_part.filter + '.fits ' + \
                           ' --sky ' + sky_list + ' --skysave ' + \
                           '  > ' + basepath + '/mefpp.log'
            print('\n', command_line)
            rcode = runCmd(command_line, basepath)
            if rcode == 1:
                raise Exception('Error running ' + command_line)
            else:
                print('success running ' + command_line)
        else:
            print('skipping sky reduction')


def mefpp_reduce_science(mefpp_dir, sci_part_list, instrument):
    for sci_part in set(sci_part_list):

        basepath = sci_part.base_path
        sci_list = basepath + '/science.list'

        sci_list_exists = False
        if Path(sci_list).exists():
            sci_list_exists = True

        else:                                   # we treat the standard stars exactly as the science
            sci_list = basepath + '/std.list'
            if Path(sci_list).exists():
                sci_list_exists = True

        # copying appropriate parameter file, paf file, to basepath directory
        mefpp_paf_exists = copy_paf(mefpp_dir, basepath, instrument)
        if not mefpp_paf_exists:
            raise Exception("mefpp_reduce_science: could not find or copy mefpp.paf to science basepath.")

        bpm_files_list = glob.glob(basepath + '/'+instrument.bpm_prefix+'_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/'+instrument.bias_prefix+'.fits').exists():
            mb_exists = True
        else:
            pass

        # here we check for the required master ff
        mff_exists = False
        mff_name = basepath + '/'+instrument.mff_prefix+'_' + sci_part.filter + '.fits'
        if Path(mff_name).exists():
            print(mff_name + ' exists')
            mff_exists = True
        else:
            print(mff_name + ' does not exist')
            pass

        print(basepath.split()[-1], sci_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, mff_exists)

        if True and (sci_list_exists and mefpp_paf_exists and bpm_exists and mb_exists and mff_exists):
            print(basepath.split()[-1], sci_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, mff_exists)

            # check if sci_list has one line. If it does replace sci_list with the name of the science image
            f = open(sci_list, 'r')
            content = f.readlines()
            f.close()
            #if len(content) == 1:
            #    sci_list = content[0]

            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           ' --bias ' + basepath + '/'+instrument.bias_prefix+'.fits ' + \
                           ' --mff ' + basepath + '/'+instrument.mff_prefix+'_' + sci_part.filter + '.fits ' + \
                           ' --science ' + sci_list + \
                           '  > ' + basepath + '/mefpp.log'
            print('\n', command_line)
            rcode = runCmd(command_line, basepath)
            if rcode == 1:
                raise Exception('Error running ' + command_line)
            else:
                print('success running ' + command_line)
        else:
            print('skipping reduction')


def get_lightcorrection_coeffs(image_band: str, instrument):
    """
    Return the coefficients for light correction of the images.
    Values from the OmegaCam manual v109.1
    Valid for sloan u, g, r and i
    """
    # We check if we have the appropriate coefficients
    if "OMEGACAM" not in instrument.inst_name_val:
        return None

    # coefficients corresponding to xx, xy and yy
    lightcorrection_coeffs = {
        "u_SDSS": [1.6153389e-9, 1.9320844e-10, 1.4650246e-9],
        "g_SDSS": [1.7019895e-9, 3.3104022e-11, 1.6704393e-9],
        "r_SDSS": [1.5453463e-9, 2.5500341e-11, 1.3853747e-9],
        "i_SDSS": [1.5270148e-9, 1.0777857e-10, 1.1392408e-9]
    }

    return lightcorrection_coeffs[image_band]


def apply_light_correction(light_correction_coeffs, ccd_data, ccd_header, instrument):
    """
    Apply the light correction to a given ccd within the mosaic, given the light correction coefficients
    """
    if "OMEGACAM" not in  instrument.inst_name_val:
        return None
    else:
        # pixels corresponding to the center of the image
        # values corresponding to OmegaCam HIERARCH ESO DET WIN1 NX and HIERARCH ESO DET WIN1 NY headers
        # for x and y number of pixels respectively
        x_center = 17152 // 2 + 0.5
        y_center = 16800 // 2 + 0.5

        # the position of the first pixel in the ccd with respect the whole mosaic is given by
        # the header "HIERARCH ESO DET OUT1 X" and "HIERARCH ESO DET OUT1 Y".

        x_1_ccd = ccd_header["HIERARCH ESO DET OUT1 X"]
        y_1_ccd = ccd_header["HIERARCH ESO DET OUT1 Y"]

        n, m = np.shape(ccd_data)
        ccd_x = np.arange(m) + x_1_ccd - x_center
        ccd_y = np.arange(n) + y_1_ccd - y_center

        # now combine the ccd_x and ccd_y array using meshgrid, then for each entry in this array compute
        # the respective value of light correction
        ccd_x_, ccd_y_ = np.meshgrid(ccd_x, ccd_y)
        ccd_xy = np.vstack((ccd_x_.flatten(), ccd_y_.flatten())).T

        delta_mag = light_correction_coeffs[0] * ccd_xy[:, 0] * ccd_xy[:, 0] + \
                    light_correction_coeffs[1] * ccd_xy[:, 0] * ccd_xy[:, 1] + \
                    light_correction_coeffs[2] * ccd_xy[:, 1] * ccd_xy[:, 1]

        # delta_mag = -2.5 log10(F/F_0), from which one obtain F = F_0 * 10^(-delta_mag/2.5)
        # but we want to increase the flux where delta_mag is gt zero to compensate light correction effect
        # so it becomes F = F_0 * 10^(delta_mag/2.5)
    
        ccd_data *= np.power(10, delta_mag.reshape(n, m) / 2.5)
        return 0


def mefpp_normalize_science(sci_part_list, instrument):
    """
    Convert images from raw adu to e-/s units by multiplying by the avg gain and dividing by the exptime.
    In case of u,g,r and i_SDSS filters, It also applies the light correction.
    """
    for sci_part in set(sci_part_list):
        # average gain for the image, then divide all image by this avg
        # define the image parameters
        basepath = sci_part.base_path
        data_path = glob.glob(basepath + '/*_pre.fits')

        ext_name_list = instrument.valid_ext_names
        gain_name_dict = instrument.valid_ext_gain_dict
        #ext_name_list = ["ESO_CCD_#%2d" % i for i in range(65, 97)]

        for image_name in data_path:

            # read all the ccd headers to store the avg gain value
            avg_gain = 0

            jj = 0
            for ext_name in ext_name_list:
                ext_head = fits.getheader(image_name, extname=ext_name)
                gain = ext_head[gain_name_dict[ext_name]]
                avg_gain += gain
                jj+=1
            avg_gain /= instrument.next_valid
            if jj != instrument.next_valid:
                raise Exception("number of valid extensions from instrument config not equal with number of use=True values in same file")

            image_head = fits.getheader(image_name, 0)
            apply_light_corr = False
            if image_head[instrument.filt_key] in ["u_SDSS", "g_SDSS", "r_SDSS", "i_SDSS"]:
                light_coeffs = get_lightcorrection_coeffs(image_head[instrument.filt_key], instrument)
                if light_coeffs is not None and instrument.correct_light_concentration:
                    apply_light_corr = True
                else:
                    apply_light_corr = False

            with fits.open(image_name, mode="update", output_verify="ignore") as hdul:

                # we add some keywords in the primary headers to make
                # astromatic notebooks independent of the instrument
                #
                header0 = hdul[0].header

                # translate filter keyword
                try:
                    zfilter = header0[instrument.filt_key]
                    logging.debug('mefpp_normalize_science: FILTER: ' + zfilter)
                except:
                    zfilter = 'NOT_FOUND'
                    logging.debug('mefpp_normalize_science: failed to determine FILTER. Setting it to NOT_FOUND')

                try:
                    header0.insert('LST', ('FILTER', zfilter, 'pycavi: Filter used for observation'), after=True)
                    logging.info('mefpp_normalize_science: Setting FILTER to ' + zfilter)
                except:
                    logging.debug('mefpp_normalize_science: failed to insert keyword FILTER after keyword LST')

                # translate airmass keyword
                try:
                    airmass_start = header0[instrument.airm_start_key]
                    airmass_end = header0[instrument.airm_end_key]
                    airmass_obs = 1.0/((1.0/airmass_start + 1.0/airmass_end) / 2.0)
                except:
                    airmass_obs = 1.0
                    logging.debug('mefpp_normalize_science: failed to determine airmass. Setting it to 1.0')

                try:
                    header0.insert('FILTER', ('AIRMASS', round(airmass_obs, 3), 'pycavi: Average airmass of frame'), after=True)
                    logging.info('mefpp_normalize_science: Setting AIRMASS to {0:5.3f}'.format(airmass_obs))
                except:
                    logging.debug('mefpp_normalize_science: failed to insert keyword AIRMASS after FILTER')


                header0["BUNIT"] = ("e-/s", "units of image pixels")
                exptime = header0["EXPTIME"]

                for ext_name in ext_name_list:

                    ext_data = hdul[ext_name].data
                    # apply light correction if the filter support it
                    if apply_light_corr:
                        header0["LIGHTCOR"] = "True"
                        ext_head = hdul[ext_name].header
                        apply_light_correction(light_coeffs, ext_data, ext_head, instrument)
                    else:
                        header0["LIGHTCOR"] = "False"
                    ext_data *= avg_gain / exptime  # converting raw adus into e-/s

