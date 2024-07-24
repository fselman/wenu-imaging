import os
import configparser


class Instrument:
    """ Instrument class used to adapt the reduction process to a given instrument.
        This class give the keyword names containing important information
        for the reduction process.

        It also gives the keyword that identify the different files used
        for calibration. It identifies bias, dome flats, sky flats, standard
        stars, and science frames. 

        The aim of this class is to simplify the making the software adaptable
        to any instrument.

        Input:

            config_dir: full path to directory where the instrument configuration
                        file can be found.

            instrument: instrument used to obtain the data. Currently only OmegaCam
                        from VST/Paranal and WFI from 2.2-m/La Silla.

    """
    def __init__(self, config_dir, instrument='omegacam'):
        config = self.read_instrument_config(config_dir, instrument)
        self.config = config

        # 
        #[Project]                                                                              Values for OmegaCam
        #
        self.instrument_str = config.get('Project', 'instrument_str').replace('"','')
        self.config_dir = config_dir #+'/'+config.get('Project', 'config_dir').replace('"','')

        #[Data]                                                                 ---  Values for OmegaCam ----
        #
        self.mefpp_paf  = config.get('Data', 'mefpp_paf').replace('"','')                        # Parameter file for mefpp reduction
        self.file_format = config.get('Data', 'file_format').replace('"','')                     # Format used for files
        self.raw_file_prefix = config.get('Data', 'raw_file_prefix').replace('"','')             # "OMEGA."
        self.raw_file_suffix = config.get('Data', 'raw_file_suffix').replace('"','')             # ".fits"
        self.reduced_file_prefix = config.get('Data', 'reduced_file_prefix').replace('"','')     # ""OMEGACAM_"
        self.reduced_file_suffix = config.get('Data', 'reduced_file_suffix').replace('"','')     # ".fits"
        self.correct_light_concentration = config.getboolean('Data', 'correct_light_concentration')   # Whether to apply concentration correction

        # we extract from the mefpp_paf file the product root names
        # MEF.BIAS.NAME.O                         "OCAM_MB";
        # MEF.BPM.NAME.O                          "OCAM_BPM";
        # MEF.DOMEFF.NAME.O                       "OCAM_DOMEFF";
        # MEF.SKYFF.NAME.O                        "OCAM_SKYFF";
        # MEF.MFF.NAME.O                      	"OCAM_MFF";
        self.bias_prefix = self.read_key_from_paf('MEF.BIAS.NAME.O')
        self.bpm_prefix = self.read_key_from_paf('MEF.BPM.NAME.O')
        self.domeff_prefix = self.read_key_from_paf('MEF.DOMEFF.NAME.O')
        self.skyff_prefix = self.read_key_from_paf('MEF.SKYFF.NAME.O')
        self.mff_prefix = self.read_key_from_paf('MEF.MFF.NAME.O')

        # image section to check final swarp mosaic data in pixels
        self.img_sec_x1 = int(config.get('Data', 'img_sec_x1'))
        self.img_sec_x2 = int(config.get('Data', 'img_sec_x2'))
        self.img_sec_y1 = int(config.get('Data', 'img_sec_y1'))
        self.img_sec_y2 = int(config.get('Data', 'img_sec_y2'))

        # Important keywords for data reduction from primary headers
        #
        # [Primary Keywords]
        self.inst_name_key = config.get('Primary Keywords', 'inst_name_key').replace('"','')      # "INSTRUME" for OCAM
        self.inst_name_val = config.get('Primary Keywords', 'inst_name_val').replace('"','')      # Instrument for which data will be reduced

        self.obid_key = config.get('Primary Keywords', 'obid_key')                # Observing sequence id.
        self.obstart_key = config.get('Primary Keywords', 'obstart_key').replace('"','')          # Time that the observing sequence started.
                                                                                  #  ob.id + ob.start uniquely identify observation execution.
        self.dateobs_key = config.get('Primary Keywords', 'dateobs_key').replace('"','')          # Used to group according to distance in time
                                                                                  # and to get Moon info. Uses format:
                                                                                  #    yyyy = int(self.dateobs[0:4])
                                                                                  #      mm = int(self.dateobs[5:7])
                                                                                  #      dd = int(self.dateobs[8:10])
                                                                                  #
        self.ra_key = config.get('Primary Keywords', 'ra_key').replace('"','')                    # Keyword giving RA of pointing, unique for frame in sequence.
        self.dec_key = config.get('Primary Keywords', 'dec_key').replace('"','')                  # Keyword giving Dec of pointing, unique for framer in sequence.
        self.targ_alpha_key = config.get('Primary Keywords', 'targ_alpha_key').replace('"','')    # Keyword giving RA of target. Shared by all frames in a sequence.
        self.targ_delta_key = config.get('Primary Keywords', 'targ_delta_key').replace('"','')    # Keyword giving Dec of target. Shared by all frames in a sequence.
        self.targ_name_key = config.get('Primary Keywords', 'targ_name_key').replace('"','')      # Name of target. Will be used to name subdirectory.
        self.tplnexp_key = config.get('Primary Keywords', 'tplnexp_key')          # Number of exposures in observing sequence
        self.tplexpno_key = config.get('Primary Keywords', 'tplexpno_key')        # Sequential number of exposure in sequence
        self.inst_exp_key = config.get('Primary Keywords', 'inst_exp_key')        # EXPTIME FITS keyword. Mandatory.
        self.object_key = config.get('Primary Keywords', 'object_key').replace('"','')            # FITS keyword identifying object observed
        self.filt_key = config.get('Primary Keywords', 'filt_key').replace('"','')                # Filter FITS keyword. Mandatory.
        self.airm_start_key = config.get('Primary Keywords', 'airm_start_key').replace('"','')    # Airmass at start of observation. Mandatory.
        self.airm_end_key = config.get('Primary Keywords', 'airm_end_key').replace('"','')        # Airmass at end of observation. Mandatory.

        # keywords to identify the needed raw data types for calibration and science -----   OmegaCam values
        #
        #[Primary Keywords]
        self.dpr_catg_key = config.get('Primary Keywords', 'dpr_catg_key').replace('"','')        # "HIERARCH ESO DPR CATG"
        self.dpr_type_key = config.get('Primary Keywords', 'dpr_type_key').replace('"','')        # "HIERARCH ESO DPR TYPE"

        self.bias_dpr_catg_val = config.get('Primary Keywords', 'bias_dpr_catg_val').replace('"','')        # "CALIB"
        self.bias_dpr_type_val = config.get('Primary Keywords', 'bias_dpr_type_val').replace('"','')        # "BIAS"

        self.domeff_dpr_catg_val = config.get('Primary Keywords', 'domeff_dpr_catg_val').replace('"','')    # "CALIB"
        self.domeff_dpr_type_val = config.get('Primary Keywords', 'domeff_dpr_type_val').replace('"','')    # "FLAT,DOME"

        self.skyff_dpr_catg_val = config.get('Primary Keywords', 'skyff_dpr_catg_val').replace('"','')      # "CALIB"
        self.skyff_dpr_type_val = config.get('Primary Keywords', 'skyff_dpr_type_val').replace('"','')      # "FLAT,SKY"

        self.std_dpr_catg_val = config.get('Primary Keywords', 'std_dpr_catg_val').replace('"','')          # "CALIB"
        self.std_dpr_type_val = config.get('Primary Keywords', 'std_dpr_type_val').replace('"','')          # "STD,ZEROPOINT"
    
        self.sci_dpr_catg_val = config.get('Primary Keywords', 'sci_dpr_catg_val').replace('"','')          # "SCIENCE"
        self.sci_dpr_type_val = config.get('Primary Keywords', 'sci_dpr_type_val').replace('"','')          # "OBJECT","SKY"

        # Detector mode keywords. Onlyframes with same detector mode can be mixed in notebooks 00 to 03
        #
        self.det_mode_name = config.get('Primary Keywords', 'det_mode_name').replace('"','')      # FITS keyword. If present in config file it will be used as suffix.
        self.det_readmode_key = config.get('Primary Keywords', 'det_readmode_key').replace('"','')    # readout mode FITS key. Part of suffix y previous key not present.
        self.det_binx_key = config.get('Primary Keywords', 'det_binx_key')        # FITS keyword giving binning in x. For suffix.
        self.det_biny_key = config.get('Primary Keywords', 'det_biny_key')        # FITS keyword giving binning in y. For suffix.


        # MEF extension keywords. OmegaCam has 32 extensions, and WFI has 8 extensions
        #
        #[Extension Keywords]
        #
        self.nextensions = int(config.get('Extension Keywords', 'nextensions'))
        ext_name_key_list = ["ext_{:02d}_name".format(i) for i in range(1, self.nextensions+1)]
        ext_use_list = ["ext_{:02d}_use".format(i) for i in range(1, self.nextensions+1)]
        ext_gain_key_list = ["ext_{:02d}_gain_key".format(i) for i in range(1, self.nextensions+1)]
        self.valid_ext_names = []
        self.valid_ext_gain_dict = {}    # dictionary indexed by the extension name giving keyword containing gain
        for i in range(self.nextensions):
            use_val = config.getboolean('Extension Keywords', ext_use_list[i])
            name_val = config.get('Extension Keywords', ext_name_key_list[i]).replace('"','')
            gain_key_val = config.get('Extension Keywords', ext_gain_key_list[i]).replace('"','')
            if use_val:
                self.valid_ext_names.append(name_val)
                self.valid_ext_gain_dict[name_val] = gain_key_val
            else:
                print("Bad extension {}".format(name_val))

        self.next_valid = len(self.valid_ext_names)


    def read_instrument_config(self, config_dir=None, instrument='omegacam'):
        """Function to read configuration file."""
        if config_dir is None:
            print('No root directory for project specified.')
            return None

        # Create a ConfigParser object
        config = configparser.ConfigParser(inline_comment_prefixes=('#'))

        # Read the configuration file
        config.read(config_dir+'/'+instrument+'.cfg')

        return config


    def read_key_from_paf(self,key_str):
        """
        Reads the mefpp paf file to read key value.
        Used to determine product file prefix.
        """
        mefpp_paf = self.config_dir+'/'+self.mefpp_paf
        found_key = False
        with open(mefpp_paf, 'r') as f:
            lines = f.readlines()
            for aline in lines:
                aline = aline[:-1]
                if len(aline) == 0:
                    continue
                elif aline[0] == '#':
                    continue
                fields = aline.split()
                if key_str in fields[0]:
                    found_key = True
                    product_name = fields[1].strip(';').strip('"')
                    break
        if found_key:
            print("{}: {}".format(key_str, product_name))
            return product_name
        else:
            raise Exception("key: {} not found in {}".format(key, mefpp_paf))


if __name__ == "__main__":
    print(" ------------------------ TESTING PYCAVI INSTRUMENT MODULE ----------------------")

    instrument = Instrument(config_dir='./config/', instrument='omegacam')

    # Print the retrieved values
    print("Number of valid extensions: {}".format(len(instrument.valid_ext_names)))
    for i in range(len(instrument.valid_ext_names)):
        print(instrument.valid_ext_names[i], instrument.valid_ext_gain_dict[instrument.valid_ext_names[i]])





    config = instrument.config
    for akey1 in config.keys():
        print("{}: {}".format(akey1, config[akey1]))
        for akey2 in config[akey1].keys():
            print("{}: {} {}".format(akey1, akey2, config[akey1][akey2]))

    print(list(config.get('Primary Keywords', 'sci_dpr_type_val').replace('"','').split(',')))

    print("bias_prefix: {}".format(instrument.bias_prefix))
    print("bpm_prefix: {}".format(instrument.bpm_prefix))
    print("domeff_prefix: {}".format(instrument.domeff_prefix))
    print("skyff_prefix: {}".format(instrument.skyff_prefix))
    print("mff_prefix: {}".format(instrument.mff_prefix))
