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
    def __init__(self, config_dir, instrument='OCAM'):
        config = self.read_instrument_config(config_dir, instrument)
        self.config = config

        # 
        #[Project]                                                                  Values for OmegaCam
        #
        self.instrument_str = config.get('Project', 'instrument_str')               # "OCAM"

        #[Data]                                                                 ---  Values for OmegaCam ----
        #
        self.file_format = config.get('Data', 'file_format')                     # Format used for files
        self.raw_file_prefix = config.get('Data', 'raw_file_prefix')             # "OMEGA."
        self.raw_file_suffix = config.get('Data', 'raw_file_suffix')             # ".fits"
        self.reduced_file_prefix = config.get('Data', 'reduced_file_prefix')     # ""OMEGACAM_"
        self.reduced_file_suffix = config.get('Data', 'reduced_file_suffix')     # ".fits"

        # Important keywords for data reduction from primary headers
        #
        # [Primary Keywords]
        self.inst_name_key = config.get('Primary Keywords', 'inst_name_key')      # "INSTRUME" for OCAM
        self.inst_exp_key = config.get('Primary Keywords', 'inst_exp_key')        # EXPTIME FITS keyword. Mandatory.
        self.object_key = config.get('Primary Keywords', 'object_key')            # FITS keyword identifying object observed
        self.filt_key = config.get('Primary Keywords', 'filt_key')                # Filter FITS keyword. Mandatory.
        self.airm_start_key = config.get('Primary Keywords', 'airm_start_key')    # Airmass at start of observation. Mandatory.
        self.airm_end_key = config.get('Primary Keywords', 'airm_end_key')        # Airmass at end of observation. Mandatory.

        # keywords to identify the needed raw data types for calibration and science -----   OmegaCam values
        #
        #[Primary Keywords]
        self.bias_dpr_catg_key = config.get('Primary Keywords', 'bias_dpr_catg_key')        # "HIERARCH ESO DPR CATG"
        self.bias_dpr_catg_val = config.get('Primary Keywords', 'bias_dpr_catg_val')        # "CALIB"
        self.bias_dpr_type_key = config.get('Primary Keywords', 'bias_dpr_type_key')        # "HIERARCH ESO DPR TYPE"
        self.bias_dpr_type_val = config.get('Primary Keywords', 'bias_dpr_type_val')        # "BIAS"

        self.domeff_dpr_catg_key = config.get('Primary Keywords', 'domeff_dpr_catg_key')    # "HIERARCH ESO DPR CATG"
        self.domeff_dpr_catg_val = config.get('Primary Keywords', 'domeff_dpr_catg_val')    # "CALIB"
        self.domeff_dpr_type_key = config.get('Primary Keywords', 'domeff_dpr_type_key')    # "HIERARCH ESO DPR TYPE"
        self.domeff_dpr_type_val = config.get('Primary Keywords', 'domeff_dpr_type_val')    # "FLAT,DOME"

        self.skyff_dpr_catg_key = config.get('Primary Keywords', 'skyff_dpr_catg_key')      # "HIERARCH ESO DPR CATG"
        self.skyff_dpr_catg_val = config.get('Primary Keywords', 'skyff_dpr_catg_val')      # "CALIB"
        self.skyff_dpr_type_key = config.get('Primary Keywords', 'skyff_dpr_type_key')      # "HIERARCH ESO DPR TYPE"
        self.skyff_dpr_type_val = config.get('Primary Keywords', 'skyff_dpr_type_val')      # "FLAT,SKY"

        self.std_dpr_catg_key = config.get('Primary Keywords', 'std_dpr_catg_key')          # "HIERARCH ESO DPR CATG"
        self.std_dpr_catg_val = config.get('Primary Keywords', 'std_dpr_catg_val')          # "CALIB"
        self.std_dpr_type_key = config.get('Primary Keywords', 'std_dpr_type_key')          # "HIERARCH ESO DPR TYPE"
        self.std_dpr_type_val = config.get('Primary Keywords', 'std_dpr_type_val')          # "STD,ZEROPOINT"
    
        self.sci_dpr_catg_key = config.get('Primary Keywords', 'sci_dpr_catg_key')          # "HIERARCH ESO DPR CATG"
        self.sci_dpr_catg_val = config.get('Primary Keywords', 'sci_dpr_catg_val')          # "SCIENCE"
        self.sci_dpr_type_key = config.get('Primary Keywords', 'sci_dpr_type_key')          # "HIERARCH ESO DPR TYPE"
        self.sci_dpr_type_val = config.get('Primary Keywords', 'sci_dpr_type_val')          # "OBJECT","SKY"

        # Detector mode keywords. Onlyframes with same detector mode can be mixed in notebooks 00 to 03
        #
        self.det_mode_name = config.get('Primary Keywords', 'det_mode_name')      # FITS keyword. If present in config file it will be used as suffix.
        self.det_readmode_key = config.get('Primary Keywords', 'det_readmode_key')    # readout mode FITS key. Part of suffix y previous key not present.
        self.det_binx_key = config.get('Primary Keywords', 'det_binx_key')        # FITS keyword giving binning in x. For suffix.
        self.det_biny_key = config.get('Primary Keywords', 'det_biny_key')        # FITS keyword giving binning in y. For suffix.


        # MEF extension keywords. OmegaCam has 32 extensions, and WFI has 8 extensions
        #
        #[Extension Keywords]
        #
        nextensions = int(config.get('Extension Keywords', 'nextensions'))
        ext_name_key_list = ["ext_{:02d}_name".format(i) for i in range(1, nextensions+1)]
        ext_use_list = ["ext_{:02d}_use".format(i) for i in range(1, nextensions+1)]
        ext_gain_key_list = ["ext_{:02d}_gain_key".format(i) for i in range(1, nextensions+1)]
        self.valid_ext_names = []
        self.valid_ext_gain_keys = []
        for i in range(nextensions):
            use_val = config.getboolean('Extension Keywords', ext_use_list[i])
            name_val = config.get('Extension Keywords', ext_name_key_list[i])
            gain_key_val = config.get('Extension Keywords', ext_gain_key_list[i])
            if use_val:
                self.valid_ext_names.append(name_val)
                self.valid_ext_gain_keys.append(gain_key_val)
            else:
                print("Bad extension {}".format(name_val))

        self.next_valid = len(self.valid_ext_names)


    def read_instrument_config(self, config_dir=None, instrument='OCAM'):
        """Function to read configuration file."""
        if config_dir is None:
            print('No root directory for project specified.')
            return None

        # Create a ConfigParser object
        config = configparser.ConfigParser(inline_comment_prefixes=('#'))

        # Read the configuration file
        config.read(config_dir+'/ocam.cfg')

        return config


if __name__ == "__main__":
    print(" ------------------------ TESTING PYCAVI INSTRUMENT MODULE ----------------------")

    instrument = Instrument(config_dir='./config/', instrument='OCAM')

    # Print the retrieved values
    print("Number of valid extensions: {}".format(len(instrument.valid_ext_names)))
    for i in range(len(instrument.valid_ext_names)):
        print(instrument.valid_ext_names[i], instrument.valid_ext_gain_keys[i])





    config = instrument.config
    for akey1 in config.keys():
        print("{}: {}".format(akey1, config[akey1]))
        for akey2 in config[akey1].keys():
            print("{}: {} {}".format(akey1, akey2, config[akey1][akey2]))
