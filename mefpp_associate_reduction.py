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

        self.partList = {}
        self.OBstartDict = {}
        self.filterDict = {}
        self.biasDict = {}
        self.domeDict = {}
        self.skyDict = {}

        # we fill the dictionaries of observation types
        i_exposure = 0
        for file_name in listing:

            i_exposure+= 1
            exposure = Exposure(file_name, instrument)
            self.insertExposure(exposure)
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

        # finally we create the frame list, which will contain the
        # files to be processed for each type of partition

        # here we create a bias.list file in each bias partition
        self.createFrameList(reduced_cal_dir, 'bias.list', self.biasDict)

        # here we create a dome.list file in dome flat field partition
        self.createFrameList(reduced_cal_dir, 'dome.list', self.domeDict)

        # here we create a sky.list file in each sky flat field partition
        self.createFrameList(reduced_cal_dir, 'sky.list', self.skyDict)

        # here we create a sky.list file in each sky flat field partition
        self.createFrameList(reduced_science_dir, 'std.list', self.stdDict)

        # here we create a science.list file in each science partition
        self.createFrameList(reduced_science_dir, 'science.list', self.sciDict)

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
            key_str = 'std/' + exposure.target + '_' + \
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

    def createFrameList(self, base_dir, list_name, frameDict):
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
            self.filter = self.getKeyVal(primary_header, instrument.config.get('Primary Keywords', 'filt_key').replace('"',''))
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

    def __init__(self, filename, frametype):

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

        # we construct the names according to file type
        self.framelist = None
        self.frame = None
        if frametype == 'BPM':
            self.framelist = None
            self.frame = self.base_path + '/OMEGACAM_BPM_01.fits'
        elif frametype == 'BIAS':
            self.framelist = self.base_path + '/bias.list'
            self.frame = self.base_path + '/OMEGACAM_MB_1x1.fits'
        elif frametype == 'FLAT,DOME':
            self.framelist = self.base_path + '/dome.list'
            self.frame = self.base_path + '/OMEGACAM_DOMEFF_' + self.filter + '_1x1.fits'
        elif frametype == 'FLAT,SKY':
            self.framelist = self.base_path + '/sky.list'
            self.frame = self.base_path + '/OMEGACAM_SKYFF_' + self.filter + '_1x1.fits'
        elif frametype == 'MFF':
            self.framelist = self.base_path + '/mff.list'
            self.frame = self.base_path + '/OMEGACAM_MFF_' + self.filter + '_1x1.fits'
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

    #def insertExposure(self, exposure):
#
        # we select the partition according to exposure dpr.type
        #if 'BIAS' in exposure.dpr_type:
            #key_str = 'bias/' + '%d' % exposure.obsid + '/' + exposure.OBstart
        #elif 'FLAT,DOME' in exposure.dpr_type:
            #key_str = 'dome/' + '%d' % exposure.obsid + '/' + exposure.filter + '/' + exposure.OBstart
        #elif 'FLAT,SKY' in exposure.dpr_type:
            #key_str = 'sky/' + '%d' % exposure.obsid + '/' + exposure.filter + '/' + exposure.OBstart
        #elif ('CALIB' in exposure.dpr_catg) and ('STD,ZEROPOINT' in exposure.dpr_type):
            #key_str = 'std/' + exposure.target + '_' + \
                      #exposure.filter + '/' + \
                      #exposure.OBstart
        #elif ('SCIENCE' in exposure.dpr_catg) and ('OBJECT' in exposure.dpr_type):
            #key_str = 'science/' + exposure.target + '_' + \
                      #("%010.3f" % exposure.tel_alpha).replace('.', 'p') + '_' + \
                      #("%09.1f" % exposure.tel_delta).replace('.', 'p').replace('-', 'm') + '/' + \
                      #exposure.filter + '/' + \
                      #exposure.OBstart
        #else:
            #print('dpr type: %s' % exposure.dpr_type, ' not classifiable.', end='\r')
            #key_str = 'unknown/' + '%s' % exposure.dpr_type

        #self.base_path = key_str
        #self.exposureList.append(exposure)
        #self.OBstart = exposure.OBstart
        #self.filter = exposure.filter
        #if key_str in self.partList:
            #self.partList[key_str].append(exposure)
        #else:
            #self.partList[key_str] = [exposure]
            #self.OBstartDict[key_str] = exposure.OBstart
            #self.filterDict[key_str] = exposure.filter

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


def associate_bpm(partition, bpm_partitions):
    for part in partition:
        part.bpmPartition = bpm_partitions[0]
        for i in range(1, 33):
            bpm_file = part.bpmPartition.base_path + "/OMEGACAM_BPM_{:02d}.fits".format(i)
            if not Path(bpm_file).is_file():
                try:
                    os.symlink(bpm_file, part.base_path + "/OMEGACAM_BPM_{:02d}.fits".format(i))
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


def associateBPM(part, scipart):
    have_bpm_link = True
    have_bpm = True
    for i in range(1, 33):
        bpm_name = part.base_path + '/OMEGACAM_BPM_%02d.fits' % (i,)
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
        part.bpmPartition = ExposuresPartition(bpm_frame, 'BPM')


def associateBias(part, scipart):
    have_bias_link = True
    have_bias = True

    bias_name = part.base_path + '/OMEGACAM_MB_1x1.fits'
    if not Path(bias_name).is_symlink():
        have_bias_link = False

    if not Path(bias_name).exists():
        have_bias = False

    part.bias_have = have_bias
    part.bias_have_link = have_bias_link

    if have_bias_link:
        bias_frame = Path(bias_name).resolve().as_posix()
        part.biasFrame = bias_frame
        part.biasPartition = ExposuresPartition(bias_frame, 'BIAS')


def associateDome(part, scipart):
    have_dome_link = True
    have_dome = True

    dome_name = part.base_path + '/OMEGACAM_DOMEFF_' + scipart.filter + '_1x1.fits'
    if not Path(dome_name).is_symlink():
        have_dome_link = False

    if not Path(dome_name).exists():
        have_dome = False

    part.dome_have = have_dome
    part.dome_have_link = have_dome_link

    if have_dome_link:
        dome_frame = Path(dome_name).resolve().as_posix()
        part.domeFrame = dome_frame
        part.domePartition = ExposuresPartition(dome_frame, 'FLAT,DOME')


def associateSky(part, scipart):
    have_sky_link = True
    have_sky = True

    # sky_name = part.base_path+'/OMEGACAM_SKYFF_'+scipart.filter+'_1x1.fits'
    sky_name = part.base_path + '/sky.list'
    if not Path(sky_name).is_symlink():
        have_sky_link = False

    if not Path(sky_name).exists():
        have_sky = False

    part.sky_have = have_sky
    part.sky_have_link = have_sky_link

    if have_sky_link or have_sky:
        sky_frame = Path(sky_name).resolve().as_posix()
        part.skyPartition = ExposuresPartition(sky_frame, 'FLAT,SKY')


def associateMFF(part, scipart):
    have_mff_link = True
    have_mff = True

    mff_name = part.base_path + '/OMEGACAM_MFF_' + scipart.filter + '_1x1.fits'
    if not Path(mff_name).is_symlink():
        have_mff_link = False

    if not Path(mff_name).exists():
        have_mff = False

    part.mff_have = have_mff
    part.mff_have_link = have_mff_link

    if have_mff_link:
        mff_frame = Path(mff_name).resolve().as_posix()
        part.mffFrame = mff_frame
        part.mffPartition = ExposuresPartition(mff_frame, 'MFF')


def mefpp_reduce_bpm(mefpp_dir, calib_dir):
    # here we reduce the bpm frames which for now is only a cp operation
    bpm_files_list = [mefpp_dir + '/static_cal/' + 'OMEGACAM_BPM_%02d.fits' % i for i in range(1, 33)]
    for file in bpm_files_list:
        # print(file)
        shutil.copy(file, calib_dir + '/bpm/')
    print('mefpp_reduce_bpm: done copying BPMs')


def mefpp_reduce_bias(mefpp_dir, bias_part_list):
    print('mefpp_reduce_bias: length of bias partition list: %d' % len(set(bias_part_list)))
    for bias_part in set(bias_part_list):

        basepath = bias_part.base_path
        bias_list = basepath + '/bias.list'
        print('mefpp_reduce_bias: ', bias_list)

        bias_list_exists = False
        if Path(bias_list).exists():
            bias_list_exists = True

        mefpp_paf_exists = False
        if Path(basepath + '/mefpp.paf').exists():
            mefpp_paf_exists = True

        if not mefpp_paf_exists:
            if Path(mefpp_dir + '/config/mefpp.paf').exists():
                shutil.copy(mefpp_dir + '/config/omegacam.paf', basepath + '/mefpp.paf')
                if Path(basepath + '/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('mefpp_reduce_bias: could not create mefpp file.')
            else:
                pass

        bpm_files_list = glob.glob(basepath + '/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        bias_already_reduced = False
        if Path(basepath + '/OMEGACAM_MB_1x1.fits').exists():
            bias_already_reduced = True

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


def mefpp_reduce_dome(mefpp_dir, dome_part_list):
    print('mefpp_reduce_dome: length of dome partition list: %d' % len(set(dome_part_list)))
    for dome_part in dome_part_list:

        basepath = dome_part.base_path
        dome_list = basepath + '/dome.list'

        dome_list_exists = False
        if Path(dome_list).exists():
            dome_list_exists = True

        mefpp_paf_exists = False
        if Path(basepath + '/mefpp.paf').exists():
            mefpp_paf_exists = True

        if not mefpp_paf_exists:
            if Path(mefpp_dir + '/config/mefpp.paf').exists():
                shutil.copy(mefpp_dir + '/config/omegacam.paf', basepath + '/mefpp.paf')
                if Path(basepath + '/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass

        bpm_files_list = glob.glob(basepath + '/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/OMEGACAM_MB_1x1.fits').exists():
            mb_exists = True
        else:
            pass

        dome_already_reduced = False
        if Path(basepath + '/OMEGACAM_DOMEFF_' + dome_part.filter + '_1x1.fits').exists():
            dome_already_reduced = True

        print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)

        if (not dome_already_reduced) and (dome_list_exists and mefpp_paf_exists and bpm_exists and mb_exists):
            print(basepath.split()[-1], dome_list_exists, mefpp_paf_exists, bpm_exists, mb_exists, dome_already_reduced)
            # os.chdir(basepath)
            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           ' --bias ' + basepath + '/OMEGACAM_MB_1x1.fits ' + \
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


def mefpp_reduce_sky(mefpp_dir, sky_part_list):
    print('mefpp_reduce_sky: length of sky partition list: %d' % len(set(sky_part_list)))
    for sky_part in set(sky_part_list):

        basepath = sky_part.base_path
        sky_list = basepath + '/sky.list'

        sky_list_exists = False
        if Path(sky_list).exists():
            sky_list_exists = True

        mefpp_paf_exists = False
        if Path(basepath + '/mefpp.paf').exists():
            mefpp_paf_exists = True

        if not mefpp_paf_exists:
            if Path(mefpp_dir + '/config/mefpp.paf').exists():
                shutil.copy(mefpp_dir + '/config/omegacam.paf', basepath + '/mefpp.paf')
                if Path(basepath + '/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass

        bpm_files_list = glob.glob(basepath + '/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/OMEGACAM_MB_1x1.fits').exists():
            mb_exists = True
        else:
            pass

        # here we check for the required dome ff
        domeff_exists = False
        domeff_name = basepath + '/OMEGACAM_DOMEFF_' + sky_part.filter + '_1x1.fits'
        if Path(domeff_name).exists():
            print(domeff_name + ' exists')
            domeff_exists = True
        else:
            print(domeff_name + ' does not exist')
            pass

        sky_already_reduced = False
        skyff_name = basepath + '/OMEGACAM_SKYFF_' + sky_part.filter + '_1x1.fits'
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
                           ' --bias ' + basepath + '/OMEGACAM_MB_1x1.fits ' + \
                           ' --dome ' + basepath + '/OMEGACAM_DOMEFF_' + sky_part.filter + '_1x1.fits ' + \
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


def mefpp_reduce_science(mefpp_dir, sci_part_list):
    for sci_part in set(sci_part_list):

        basepath = sci_part.base_path
        sci_list = basepath + '/science.list'

        sci_list_exists = False
        if Path(sci_list).exists():
            sci_list_exists = True

        mefpp_paf_exists = False
        if Path(basepath + '/mefpp.paf').exists():
            mefpp_paf_exists = True

        if not mefpp_paf_exists:
            if Path(mefpp_dir + '/config/mefpp.paf').exists():
                shutil.copy(mefpp_dir + '/config/omegacam.paf', basepath + '/mefpp.paf')
                if Path(basepath + '/mefpp.paf').exists():
                    mefpp_paf_exists = True
                else:
                    raise Exception('Could not create mefpp file.')
            else:
                pass

        bpm_files_list = glob.glob(basepath + '/OMEGACAM_BPM_??.fits', recursive=False)
        bpm_exists = True
        for bpm_file in bpm_files_list:
            if not Path(bpm_file).exists():
                bpm_exists = bpm_exists and False

        # here we check the presence of the required master bias frame
        mb_exists = False
        if Path(basepath + '/OMEGACAM_MB_1x1.fits').exists():
            mb_exists = True
        else:
            pass

        # here we check for the required master ff
        mff_exists = False
        mff_name = basepath + '/OMEGACAM_MFF_' + sci_part.filter + '_1x1.fits'
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
            if len(content) == 1:
                sci_list = content[0]

            command_line = 'nohup ' + mefpp_dir + '/bin/mefpp ' + \
                           ' --bias ' + basepath + '/OMEGACAM_MB_1x1.fits ' + \
                           ' --mff ' + basepath + '/OMEGACAM_MFF_' + sci_part.filter + '_1x1.fits ' + \
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
    if instrument.inst_name_val is not "OMEGACAM":
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

