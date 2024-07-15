import os
import configparser
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import astropy.constants as constants

# Configuration resources

def init_pycavi_config(raw_data_dir=None, project_dir=None):
    """Function to create configuration file.
    The configuration file is read by all notebooks,
    and have the information on where the different files
    are located."""
    config_str = """
[General]
  debug = True
  log_level = info
[Provenance]
  Institution = ESO
  Observatory = Paranal
  Telescope = VST
  Instrument = OmegaCam
[Directories] 
    raw_data_dir =
    project_dir =
    static_calib_dir =
    reduced_calib_dir =
    reduced_std_dir =
    reduced_science_dir =
    project_logs_dir =
    sex_dir_name =
    scamp_dir_name =
    swarp_dir_name =
    cal_dir_name =
"""
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_string(config_str)

    if project_dir is not None:
            static_calib_dir = project_dir+'/static_calib/' # static calibrations go here, e.g. bpm, fringe frames, linearity curves, etc.
            reduced_calib_dir = project_dir+'/calib/' # Directory tree with reduced calibration files + soft links to raw calibrations
            reduced_std_dir = project_dir+'/std/'       # Directory tree with reduced standard star observations
            reduced_science_dir = project_dir+'/science/' # Directory tree with reduced science frames + soft links to reduced calibrations.
            project_logs_dir = project_dir+'/logs/' # Directory containing logs created by running the reduction
    else:
        static_calib_dir = None
        reduced_calib_dir = None
        reduced_std_dir = None
        reduced_science_dir = None
        project_logs_dir = None
    sex_dir_name = 'Sextractor_dir'     # will be created by notebook X below the target directory
    scamp_dir_name = 'Scamp_dir'         # will be created by notebook X below the target directory
    swarp_dir_name = 'Swarp_dir'        # will be created by notebook X below the target directory
    cal_dir_name = 'Calibration_dir'    # will be created by notebook X below the target directory

    config['Directories'] = {'raw_data_dir': raw_data_dir,
                             'project_dir': project_dir, 
                             'static_calib_dir': static_calib_dir,
                             'reduced_calib_dir': reduced_calib_dir,
                             'reduced_std_dir': reduced_std_dir,
                             'reduced_science_dir': reduced_science_dir,
                             'project_logs_dir': project_logs_dir,
                             'sex_dir_name': sex_dir_name,
                             'scamp_dir_name': scamp_dir_name,
                             'swarp_dir_name': swarp_dir_name,
                             'cal_dir_name': cal_dir_name}

    return config

def write_pycavi_config(config, config_dir=None):
    """Write the config values to the project configuration file"""
    if config_dir is None:
        print('No root directory for project specified.')
        return None
    # Write the configuration to a file
    if config is not None:
        Path(config_dir).mkdir(parents=True, exist_ok=True)
        with open(config_dir+'/pycavi.cfg', 'w') as configfile:
            config.write(configfile)

def read_pycavi_config(config_dir=None):
    """Function to read configuration file."""
    if config_dir is None:
        print('No root directory for project specified.')
        return None

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(config_dir+'/pycavi.cfg')

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    institution = config.get('Provenance', 'Institution')
    observatory = config.get('Provenance', 'Observatory')
    telescope = config.get('Provenance', 'Telescope')
    instrument = config.get('Provenance', 'Instrument')
    raw_data_dir = config.get('Directories', 'raw_data_dir')
    project_dir = config.get('Directories', 'project_dir')
    static_calib_dir = config.get('Directories', 'static_calib_dir')
    reduced_calib_dir = config.get('Directories', 'reduced_calib_dir')
    reduced_std_dir = config.get('Directories', 'reduced_std_dir')
    reduced_science_dir = config.get('Directories', 'reduced_science_dir')
    project_logs_dir = config.get('Directories', 'project_logs_dir')
    sex_dir_name = config.get('Directories', 'sex_dir_name')
    scamp_dir_name = config.get('Directories', 'scamp_dir_name')
    swarp_dir_name = config.get('Directories', 'swarp_dir_name')
    cal_dir_name = config.get('Directories', 'cal_dir_name')

    return config

# tkinter widget tools 

class ProjectInfo:
    """Class for entry window to aid in the configuration file creation."""
    def __init__(self, config_dir):
        self.popup = tk.Tk()
        self.popup.transient()

        super(ProjectInfo, self).__init__()
        self.widgets={}

        # we read current values as defaults
        self.config_dir = config_dir
        self.config_file = config_dir+'/'+'pycavi.cfg'

        if os.path.isfile(self.config_file):
            self.config = read_pycavi_config(config_dir)
            self.instrument = self.config['Provenance']['Instrument']
            self.telescope = self.config['Provenance']['Telescope']
            self.observatory = self.config['Provenance']['Observatory']
            self.institution = self.config['Provenance']['Institution']
            self.raw_data_dir = self.config['Directories']['raw_data_dir']
            self.project_dir = self.config['Directories']['project_dir']
        else:
            print("No config file found.")
            self.config = init_pycavi_config()
            
            self.instrument = self.config['Provenance']['instrument']

            self.telescope = self.config['Provenance']['telescope']

            self.observatory = self.config['Provenance']['observatory']

            self.institution = self.config['Provenance']['institution']

            self.raw_data_dir = self.config['Directories']['raw_data_dir']

            self.project_dir = self.config['Directories']['project_dir']


        # row 0, column 0, the name of the project subdirectory
        OPTIONS = ["OmegaCam,VST,Paranal,ESO",
                   "WFI,2.2-m,La Silla,ESO",
                    ] #etc
        self.origin = tk.StringVar()
        self.origin.set(OPTIONS[0]) # default value
        project_origin = tk.OptionMenu(self.popup, self.origin, *OPTIONS)
        project_origin.grid(columnspan=2)

        # row 1, column 0, the root directory for project
        self.raw_dir_label = tk.Label(self.popup, text=self.raw_data_dir)
        self.raw_dir_label.grid(column=1, row=1)

        # row 1, column 1, the button to navigate to directory
        select_button_raw = tk.Button(self.popup, text="Select raw data directory", command=self.select_raw_dir)
        select_button_raw.grid(column=0, row=1)


        # row 2, column 0, the root directory for project
        self.project_dir_label = tk.Label(self.popup, text=self.project_dir)
        self.project_dir_label.grid(column=1, row=2)

        # row 2, column 1, the button to navigate to directory
        select_button_root = tk.Button(self.popup, text="Select directory for project", command=self.select_project_dir)
        select_button_root.grid(column=0, row=2)

        # row 3, column 0, the name of the project subdirectory
        #project_subdir_label = ttk.Label(self.popup, text="Project subdirectory name:")
        #project_subdir_label.grid(column=0, row=3)

        # row 3, column 1
        #self.project_subdir = tk.StringVar()
        #project_subdir_entry = ttk.Entry(self.popup, textvariable=self.project_subdir)
        #project_subdir_entry.grid(column=1, row=3)

        # row 4, the Enter command
        enter_button = ttk.Button (self.popup, text = "Enter", command=self.close_window)
        enter_button.grid(columnspan=2)

        self.popup.mainloop()

    def select_raw_dir(self):
        self.raw_data_dir = filedialog.askdirectory()
        if self.raw_data_dir:
            self.config['Directories']['raw_data_dir'] = self.raw_data_dir+'/'
            self.raw_dir_label.config(text=self.raw_data_dir)

    def select_project_dir(self):
        self.project_dir = filedialog.askdirectory()
        self.project_dir = self.project_dir+'/'
        if self.project_dir:
            self.config['Directories']['project_dir'] = self.project_dir+'/'
            self.config['Directories']['static_calib_dir'] = self.project_dir +'/'+'static_calib'+'/'
            self.config['Directories']['reduced_calib_dir'] = self.project_dir +'/'+'calib'+'/'
            self.config['Directories']['reduced_std_dir'] = self.project_dir +'/'+'std'+'/'
            self.config['Directories']['reduced_science_dir'] = self.project_dir +'/'+'science'+'/'
            self.config['Directories']['project_logs_dir'] = self.project_dir +'/'+'logs'+'/'
            self.project_dir_label.config(text=self.project_dir)

    def close_window (self):

        # before leaving we need to parse the origin string
        # "OmegaCam,VST,Paranal,ESO"
        origin_list = self.origin.get().split(',')
        if len(origin_list) == 4:
            self.config['Provenance']['Instrument'] = origin_list[0]
            self.config['Provenance']['Telescope'] = origin_list[1]
            self.config['Provenance']['Observatory'] = origin_list[2]
            self.config['Provenance']['Institution'] = origin_list[3]
        else:
            print("Problem parsing origin string from pulldown widget: {}".formatI(self.origin))
        write_pycavi_config(self.config, self.config_dir)
        self.popup.destroy()

# FITS handling tools

def keys_from_header(hdu, keys):
    """
    returns the value stored in the frame hdu headers

    Parameters
    ----------
    keys: str or list
        the key, a single value if a str is passed, or a list of keys to select from the headers.
    """
    if type(keys) == str:
        return hdu[keys]
    elif type(keys) == list:
        returned_values = []
        for key in keys:
            returned_values.append(hdu[key])
        return returned_values

# Photometric tools


def Flambda_zp(flt):
    """
    Returns the zero point to add to -2.5log(flux [erg/s/cm^2/A)
    to get the AB magnitudes in band self.band from calibrated frame.

    Reference: Oke, J.B. 1974, ApJS, 27, 21
    Formula in paper: m(AB) = -2.5 log(f) - 48.60

                        where f is in erg sec^-1 cm^-2 Hz^-1

    The value from Bohlin and Gilliland 2004 as reported by 
    Tokunaga and Vacca 2005 is 48.574 assuming lambda iso
    for V filter is 5546 A, and isophotal flux density
    of 3.63x10^(-20) erg/s/cm^2/Hz.

    NB: pivot wavelength should be given in same length units as f_lambda.
        The constant 3.34x10^(-19) includes 1/c and the conversion from
        Angstroms to cm.
    """
    c = constants.c.cgs.value*10**(-2)*10**(10)  # speed of light in Angstroms/s
    print(c)
    plbd = plambda(flt)
    if plbd is not None:
        return -48.574 - 2.5*np.log10(plbd**2/c)
    else:
        return None

def filter_width(flt):
    """
    Filter widths for OmegaCam band passes.
    From the SVO filter services.
    http://svo2.cab.inta-csic.es/theory/fps/index.php?mode=browse&gname=Paranal&gname2=OmegaCAM&asttype=
    """
    effective_width = {"u_SDSS": 482.5,
                       "g_SDSS": 1203.3,
                       "r_SDSS": 1354.3,
                       "NB_659": 103.8,  # This is the VPHAS+ filter
                       "i_SDSS": 1463.7,
                       "z_SDSS": 864.5,
                       "B_JOHN": 866.6,  # This is the Bessell B isophotal mag
                       "V_JOHN": 908.1}  # This is the Bessel V isophotal mag

    if flt in effective_width.keys():
        return effective_width[flt]
    else:
        print("get_filter_width: unrecognized filter pass band {}".format(flt))
        return None

def plambda(flt):
    """
    Returns the pivot wavelength, needed for conversion between
    Fnu and Flambda.

    From the SVO filter services.
    http://svo2.cab.inta-csic.es/theory/fps/index.php?mode=browse&gname=Paranal&gname2=OmegaCAM&asttype=
    """
    pivot_wave = {"u_SDSS": 3569.6,
                  "g_SDSS": 4712.0,
                  "r_SDSS": 6286.0,
                  "NB_659": 6588.6,
                  "i_SDSS": 7555.1,
                  "z_SDSS": 8888.6,
                  "B_JOHN": 4404.3,
                  "V_JOHN": 5505.2}

    if flt in pivot_wave.keys():
        return pivot_wave[flt]
    else:
        print("getPivotWavelength: unrecognized filter pass band {}".format(flt))
        return None

def extinction_coeff(plambda, observatory):
    """
    Atmospheric extinction coefficients.
    """
    if 'paranal' in observatory.lower():
        return paranal_extinction_curve(plambda)
    else:
        return None

def paranal_extinction_curve(lambd):
    """Patat et al. 2011 A&A 527, A91 Table B.1
    https://ui.adsabs.harvard.edu/abs/2011A%26A...527A..91P/abstract
    """
    extinction_table = np.array([[3325, 0.686, 0.021], [3375, 0.606, 0.009], [3425, 0.581, 0.007],
        [3475, 0.552, 0.007], [3525, 0.526, 0.006], [3575, 0.504, 0.006], [3625, 0.478, 0.006],
        [3675, 0.456, 0.006], [3725, 0.430, 0.006], [3775, 0.409, 0.005], [3825, 0.386, 0.006],
        [3875, 0.378, 0.006], [3925, 0.363, 0.005], [3975, 0.345, 0.004], [4025, 0.330, 0.004],
        [4075, 0.316, 0.004], [4125, 0.298, 0.004], [4175, 0.285, 0.004], [4225, 0.274, 0.004],
        [4275, 0.265, 0.004], [4325, 0.253, 0.004], [4375, 0.241, 0.003], [4425, 0.229, 0.003],
        [4475, 0.221, 0.003], [4525, 0.212, 0.003], [4575, 0.204, 0.003], [4625, 0.198, 0.003],
        [4675, 0.190, 0.003], [4725, 0.185, 0.003], [4775, 0.182, 0.003], [4825, 0.176, 0.003],
        [4875, 0.169, 0.003], [4825, 0.176, 0.003], [4925, 0.162, 0.003], [4975, 0.157, 0.003],
        [5025, 0.156, 0.003], [5075, 0.153, 0.003], [5125, 0.146, 0.003], [5175, 0.143, 0.003],
        [5225, 0.141, 0.003], [5275, 0.139, 0.003], [5325, 0.139, 0.002], [5375, 0.134, 0.002],
        [5425, 0.133, 0.002], [5475, 0.131, 0.002], [5525, 0.129, 0.002], [5575, 0.127, 0.002],
        [5625, 0.128, 0.002], [5675, 0.130, 0.002], [5725, 0.134, 0.002], [5775, 0.132, 0.002],
        [5825, 0.124, 0.002], [5875, 0.122, 0.003], [5925, 0.125, 0.003], [5975, 0.122, 0.003],
        [6025, 0.117, 0.002], [6075, 0.115, 0.002], [6125, 0.108, 0.002], [6175, 0.104, 0.002],
        [6225, 0.102, 0.002], [6275, 0.099, 0.002], [6325, 0.095, 0.002], [6375, 0.092, 0.002],
        [6425, 0.085, 0.002], [6475, 0.086, 0.003], [6525, 0.083, 0.003], [6575, 0.081, 0.002],
        [6625, 0.076, 0.002], [6675, 0.072, 0.002], [6725, 0.068, 0.002], [6775, 0.064, 0.002],
        [7060, 0.064, 0.003], [7450, 0.048, 0.002], [7940, 0.042, 0.003], [8500, 0.032, 0.001],
        [8675, 0.030, 0.001], [8850, 0.029, 0.001], [10000, 0.022, 0.001]])

    #interp_data = np.interp(r_minus_i[clean_color], drew_r_i_ab, drew_r_ha_ab)
    wavelength = extinction_table[:,0]
    extinct = extinction_table[:,1]
    extinct_err = extinction_table[:,2]
    return np.interp(lambd, wavelength, extinct)


# Plotting tools
def pycavi_qc_plot_hist(array, label='x-val', nbins=30, x_range="8-deciles", figname=None):
    """Simple histogram of values in array."""
    if "8-deciles" in x_range:
        deciles = np.nanpercentile(array, np.arange(0, 100, 10))
        min_val = deciles[0]
        max_val = deciles[-1]
    elif "full" in x_range:
        min_val = np.nanmin(array)
        max_val = np.nanmax(array)
    else:
        logging.info('pycavi_qc_plot_hist: unknown x_range type. Allowed values: 8-deciles or full')
    if not np.isnan(min_val) and not np.isnan(max_val) and min_val != max_val:
        total_range = max_val - min_val
        onetenth = total_range/10.0
        plt.hist(array, density=False, bins=30, range=(min_val-onetenth, max_val+onetenth))  # density=False would make counts
        plt.xlim(min_val, max_val)
        plt.ylabel('Number')
        plt.xlabel(label)
        plt.show()
    else:
        print(label+' array is nan')

    if figname is not None:
        plt.savefig(figname)


if __name__ == "__main__":
    print("pycavi_tools test - Flambda_zp({0}): {1}".format("V_JOHN", Flambda_zp("V_JOHN")))
