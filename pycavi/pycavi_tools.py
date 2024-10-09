import os
import configparser
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import logging

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import astropy.constants as constants

import subprocess

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
    logging.info("Flambda_zp: speed of light in Angstroms per second: {}".format(c))
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

def band_pass_std_name(band):
    """
    Given a band returns the standard bandpass name. Needed due to
    the multitude of names of filters used by OCAM, WFI, and other
    instruments.

    This table should be used to determine the standard bandpass
    associated to a filter. Should not be used to get the properties
    of the filter, such as pivot wavelength, which depends on the
    actual realization of the passband.
    """
    aliases = {
            "U": "U",
            "U/38": "U",                # WFI narrower U
            "U/50": "U",                # WFI Broadhurst filter U350/6
            "U/360": "U",               # WFI Broadhurst filter U350/6
            "B": "B",
            "B/99": "B",                # WFI original B
            "BB#B/123_ESO878": "B",     # WFI new B
            "B_JOHN": "B",              # OCAM Johnson B
            "V": "V",
            "V/89": "V",                # WFI Johnson V
            "V_JOHN": "V",              # OCAM Johnson V
            "R": "R",
            "Rc/162": "R",              # WFI Johnson R (large round filter)
            "I": "I",
            "Ic/lwp": "I",              # WFI Cousins I but with upper cutoff open
            "BB#I/203_ESO879": "I",     # WFI EIS I filter
            "Z": "Z",                   # WFI Z filter
            "Z+/61": "Z",               # WFI Z filter
            "Z+/60": "Z",               # WFI Z filter
            "u": "u",                   # Sloan u
            "u_sdss": "u",
            "u_SDSS": "u",
            "g": "g",                   # Sloan g
            "g_sdss": "g",
            "g_SDSS": "g",
            "r": "r",                   # Sloan r
            "r_sdss": "r",
            "r_SDSS": "r",
            "i": "i",                   # Sloan i
            "i_sdss": "i",
            "i_SDSS": "i",
            "z": "z",                   # Sloan z
            "z_SDSS": "z",
            "z_sdss": "z",
            "H_alpha": "H_alpha",
            "NB_659": "H_alpha",         # OCAM VPHA project H-alpha filter
            }

    return aliases.get(band, None)

def get_mab_minus_vega(band):
    """
    This procedures returns the parameters for passbands determined
    by Blanton (2007), 
    https://ui.adsabs.harvard.edu/abs/2007AJ....133..734B/abstract

    Used mostly for AB - Vega magnitude differences.
    """
    band_properties = {"U": {"leff": 3571, "mab_mveg": 0.79, "MsunAB": 6.35, "MsunVega": 5.55},
    "B": {"leff": 4344, "mab_mveg": -0.09, "MsunAB": 5.36, "MsunVega": 5.45},
    "V": {"leff": 5456, "mab_mveg": 0.02, "MsunAB": 4.80, "MsunVega": 4.78},
    "R": {"leff": 6442, "mab_mveg": 0.21, "MsunAB": 4.61, "MsunVega": 4.41},
    "I": {"leff": 7994, "mab_mveg": 0.45, "MsunAB": 4.52, "MsunVega": 4.07},
    "u": {"leff": 3546, "mab_mveg": 0.91, "MsunAB": 6.38, "MsunVega": 5.47},
    "g": {"leff": 4670, "mab_mveg": -0.08, "MsunAB": 5.12, "MsunVega": 5.20},
    "r": {"leff": 6156, "mab_mveg": 0.16, "MsunAB": 4.64, "MsunVega": 4.49},
    "i": {"leff": 7472, "mab_mveg": 0.37, "MsunAB": 4.53, "MsunVega": 4.16},
    "z": {"leff": 8917, "mab_mveg": 0.54, "MsunAB": 4.51, "MsunVega": 3.97},
    "H_alpha": {"leff": 6590.63, "mab_mveg": 0.338, "MsunAB": -1, "MsunVega": -1}}

    std_band = band_pass_std_name(band)
    if std_band is not None:
        return band_properties[std_band]["mab_mveg"]
    else:
        return None

def drew_vst_synthetic_colours(r_sdss, i_sdss, mag_min, mag_max):
    """
    Calculate "standard" H-alpha AB magnitudes given the
    catalogue standard r_sdss, and i_sdss magnitudes.
    Implements the Drew et al 2014 synthetic VST relations.

    Input
    =====
        A set of SDSS r, i magnitudes.

    Output
    ======
        The Halpha AB magnitudes, assumimg main sequence stars.

    This is a minimal implementation for testing. This can be easily
    improved if we get the star type. Now we use the main sequence 
    conversion.
    """
    #Spectral type	Main sequence (V)		Giants (III)
						    #(model)	                                (P98 library spectra)
	    #u − g	g − r	r − i	r − Hα		u − g	g − r	r − i	r − Hα	r − i	r − Hα
    #O6	−1.494	−0.313	−0.145	0.071							
    #O8	−1.463	−0.299	−0.152	0.055						−0.158	0.074
    #O9	−1.426	−0.271	−0.142	0.064		−1.426	−0.271	−0.142	0.064		
    #B0	−1.404	−0.267	−0.143	0.058		−1.404	−0.267	−0.143	0.058		
    #B1	−1.296	−0.236	−0.130	0.052		−1.316	−0.234	−0.130	0.057	−0.095	0.071
    #B2	−1.181	−0.214	−0.117	0.049		−1.209	−0.211	−0.116	0.056		
    #B3	−1.025	−0.182	−0.098	0.048		−1.046	−0.182	−0.098	0.054	−0.035	0.083
    #B5	−0.799	−0.133	−0.071	0.043		−0.814	−0.134	−0.072	0.050	−0.016	0.083
    #B6	−0.699	−0.116	−0.062	0.040		−0.714	−0.116	−0.062	0.046		
    #B7	−0.550	−0.094	−0.051	0.033		−0.568	−0.095	−0.051	0.041		
    #B8	−0.361	−0.071	−0.039	0.022		−0.383	−0.072	−0.039	0.032		
    #B9	−0.168	−0.040	−0.023	0.009		−0.186	−0.044	−0.024	0.021	−0.018	0.035
    #A0	−0.024	0.000	−0.003	−0.002		−0.030	−0.009	−0.006	0.011	0.012	0.034
    #A1	0.007	0.015	0.004	−0.004		0.007	0.004	0.000	0.008		
    #A2	0.039	0.038	0.014	−0.005		0.051	0.022	0.009	0.008		
    #A3	0.064	0.062	0.025	−0.005		0.085	0.045	0.019	0.007	0.037	0.063
    #A5	0.096	0.130	0.056	0.008		0.143	0.107	0.048	0.015	0.096	0.087
    #A7	0.073	0.206	0.089	0.030		0.145	0.179	0.078	0.032	0.115	0.094
    #F0	0.003	0.336	0.153	0.086		0.091	0.317	0.144	0.084	0.156	0.102
    #F2	−0.021	0.396	0.182	0.111		0.064	0.380	0.174	0.109	0.204	0.172
    #F5	−0.039	0.505	0.230	0.150		0.046	0.491	0.224	0.148	0.238	0.164
    #F8	−0.013	0.587	0.263	0.174							
    #G0	0.012	0.628	0.278	0.185						0.333	0.213
    #G2	0.011	0.628	0.279	0.185		0.253	0.759	0.329	0.215		
    #G5	0.162	0.756	0.327	0.217		0.405	0.870	0.368	0.235	0.396	0.250
    #G8	0.355	0.845	0.358	0.233		0.531	0.944	0.395	0.247	0.419	0.247
    #K0	0.523	0.938	0.396	0.248		0.640	1.002	0.417	0.256	0.446	0.254
    #K1	0.551	0.954	0.403	0.251		0.803	1.085	0.451	0.269	0.468	0.269
    #K2	0.629	0.993	0.419	0.258		0.963	1.159	0.483	0.281	0.508	0.293
    #K3	0.779	1.062	0.447	0.269		1.227	1.276	0.536	0.299	0.514	0.286
    #K4	0.871	1.108	0.468	0.278		1.374	1.342	0.585	0.320	0.592	0.313
    #K5	1.083	1.210	0.522	0.300		1.578	1.420	0.630	0.338	0.714	0.337
    #K7	1.387	1.402	0.724	0.387							
    #M0	1.372	1.411	0.789	0.411		1.697	1.454	0.686	0.360	0.827	0.411
    #M1	1.335	1.439	0.934	0.467		1.838	1.506	0.769	0.395	0.872	0.401
    #M2	1.262	1.442	1.112	0.522		1.938	1.546	0.825	0.420	0.920	0.443
    #M3	1.236	1.447	1.179	0.545		1.980	1.556	0.933	0.444	1.165	0.471
    #M4	1.248	1.457	1.168	0.543		1.959	1.551	1.136	0.500	1.472	0.512
    #M5						                2.009	1.569	1.296	0.556	1.739	0.560
    #M6						                2.199	1.612	1.267	0.554		

    # Tables to be used for interpolation.
    # The tables are in the Vega system
    drew_r_minus_i = [-0.145, -0.152, -0.142, -0.143, -0.130, -0.117, -0.098, -0.071, -0.062, -0.051, 
                -0.039, -0.023, -0.003,  0.004,  0.014,  0.025,  0.056,  0.089,  0.153,  0.182, 
                0.230,  0.263,  0.278,  0.279,  0.327,  0.358,  0.396,  0.403,  0.419,  0.447, 
                0.468,  0.522,  0.724,  0.789,  0.934,  1.112,  1.179,  1.168]
    drew_r_minus_Ha = [0.071,  0.055,  0.064,  0.058,  0.052,  0.049,  0.048,  0.043,  0.040,  0.033, 
                0.022,  0.009, -0.002, -0.004, -0.005, -0.005,  0.008,  0.030,  0.086,  0.111,
                0.150,  0.174,  0.185,  0.185,  0.217,  0.233,  0.248,  0.251,  0.258,  0.269,
                0.278,  0.300,  0.387,  0.411,  0.467,  0.522,  0.545,  0.543]
    color_to_ab_rmi = get_mab_minus_vega("r_sdss") - get_mab_minus_vega("i_sdss")
    color_to_ab_rmha = get_mab_minus_vega("r_sdss") - get_mab_minus_vega("NB_659")
    drew_r_i_ab = [x + color_to_ab_rmi for x in drew_r_minus_i]
    drew_r_ha_ab = [x + color_to_ab_rmha for x in  drew_r_minus_Ha]


    clean_nans = ~np.isnan(r_sdss) & ~np.isnan(i_sdss)
    clean_mags = (r_sdss >= mag_min) & (r_sdss <= mag_max)
    condition = clean_nans & clean_mags

    r_minus_i = np.full_like(r_sdss, np.nan, dtype=np.float64)
    r_minus_i[condition] = r_sdss[condition] -  i_sdss[condition]

    clean_color = (r_minus_i >= drew_r_i_ab[0]) & (r_minus_i <= drew_r_i_ab[-1])
    #clean_color = (r_minus_i >= drew_r_i_ab[0]) & (r_minus_i <= 0.70)
    r_minus_i[~clean_color] = np.nan

    interp_data = np.interp(r_minus_i, drew_r_i_ab, drew_r_ha_ab)
    calculated_ha_ab = r_sdss - interp_data

    return calculated_ha_ab
    

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


# Pycavi tool to create region file
def create_ds9_reg_file(ra_array, dec_array, filename, radius=20.0, coords='image'):
    """
    Create a DS9 region file from arrays of right ascension and declination,
    including a header with coordinate system and equinox information.

    Parameters:
    ra_array (numpy.ndarray): Array of right ascension values (degrees, decimal format, 2000 equinox).
    dec_array (numpy.ndarray): Array of declination values (degrees, decimal format, 2000 equinox).
    filename (str): Name of the output region file.
    radius (float): Radius of the circles (default is 10.0).
    """

    # Ensure RA and Dec arrays have the same length
    if len(ra_array) != len(dec_array):
        raise ValueError("create_ds9_reg_file: RA and Dec arrays must have the same length.")

    if 'pixel' in coords or 'image' in coords:
        region_file_content = (
            "# Region file format: DS9 version 4.1\n" +
            "global color=green dashlist=8 3 width=1 font='helvetica 10 normal' select=1 highlite=1 dash=0 " +
            "fixed=0 edit=1 move=1 delete=1 include=1 source=1\n" +
            "image\n"  # Specifies coordinate system (FK5) and equinox (2000)
        )
        # Add circles for each star
        for ra, dec in zip(ra_array, dec_array):
            region_file_content += f"circle({ra},{dec},{radius})\n"
    elif "fk5" in coords:
        region_file_content = (
            "# Region file format: DS9 version 4.1\n" +
            "global color=green dashlist=8 3 width=1 font='helvetica 10 normal' select=1 highlite=1 dash=0 " +
            "fixed=0 edit=1 move=1 delete=1 include=1 source=1\n" +
            "fk5\n"  # Specifies coordinate system (FK5) and equinox (2000)
        )
        # Add circles for each star
        for ra, dec in zip(ra_array, dec_array):
            region_file_content += f"circle({ra}d,{dec}d,{radius}\")\n"
    else:
        raise ValueError("create_ds9_reg_file: unknow coordinate type")

    # Write the content to the specified file
    with open(filename, 'w') as file:
        file.write(region_file_content)

    logging.info(f"create_ds9_reg_file: DS9 region file '{filename}' created successfully.")


# Pycavi centralized run_command
# ======================================================================
# A utility function
# ======================================================================
def run_command(str_cmd, p_shell=True, my_env=None, logfile=None, cmdfile=None):
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

    logfile: str
        If given will define the path of the file where the stdout and stderr will be printed.

    Returns
    -------
      0 if some error, or 1 if all was OK

    """

    # Writing the command to a text file can be used for re-runnning it
    # when solving problems.
    print("run_command: cmdfile: {}".format(cmdfile))
    print("run_command: logfile: {}".format(logfile))
    print("run_command: str_cmd: {}".format(str_cmd))
    print("run_command: cwd: {}\n\n".format(os.getcwd()))

    if cmdfile is not None:
        print("run_command: cmdfile: {}".format(cmdfile))
        with open(cmdfile, "w") as text_file:
            print("run_command: str_cmd writting to command file {}".format(cmdfile))
            text_file.write("{}".format(str_cmd))
            print("run_command: str_cmd written to command file {}".format(cmdfile))
    else:
        print("run_command: cmdfile is None")

    print("run_command: Running command: {0}".format(str_cmd))

    log_path = subprocess.PIPE if logfile is None else open(logfile, "w+")
    print("run_command: log_path set")
    univ_lines = None if logfile is None else True
    print("run_command: univ_lines set")

    #try:
    print("run_command: running...")
    if my_env is None:
        p = subprocess.Popen(str_cmd, bufsize=0, shell=p_shell, stdin=subprocess.PIPE, stdout=log_path,
                             stderr=log_path, close_fds=True, universal_newlines=univ_lines)
    else:
        p = subprocess.Popen(str_cmd, bufsize=0, shell=p_shell, stdin=subprocess.PIPE, stdout=log_path,
                                 stderr=log_path, close_fds=True, universal_newlines=univ_lines, env=my_env)
    print("run_command: done.")
    #except Exception as e:
        #logging.info("run_command: some error while running command...")
        #print(e)
        #raise

    # wait for the process to finish
    while True:
        if p.poll() is not None:
            break

    if logfile is not None:
        log_path.close()

    # Warning
    # We use communicate() rather than .stdin.write, .stdout.read or .stderr.read
    # to avoid deadlocks due to any of the other OS pipe buffers filling up and
    # blocking the child process.(Python Ref.doc)

    # modified by me (Lientur) to allow the creation of a txt logfile somewhere
    # reads this logfile and look for the errors

    if logfile is None:
        (stdoutdata, stderrdata) = p.communicate()
        err = stdoutdata.decode('ascii') + " " + stderrdata.decode('ascii')

        # IMPORTANT: Next checking (only available when shell=True) not always detect all kind of errors !!
        if err.count('WARNING: Significant inaccuracy'):
            logging.info("run_command: can not get accurate astrometric calibration")
            return 2
        elif (err.count('ERROR ') or err.count('error ') or err.count("Error ")
              or err.count('*Error*')
              or err.count('Segmentation fault') or err.count("command not found")
              or err.count('No source found')
              or err.count("No such file or directory")
              or err.count('WARNING: Not enough matched detections')  # SCAMP
              or err.count('WARNING: Significant inaccuracy likely to occur in projection')):  # SCAMP
            logging.info("run_command: an error happened while running command --> {0}".format(err))
            logging.info(stderrdata.decode("ascii"))
            return 1  # ERROR
        else:
            logging.info(stdoutdata.decode('ascii'))
            return 0  # NO ERROR

    else:
        with open(logfile, "r") as f:
            err = f.readlines()

        for line in err:
            if "Error" in line:
                logging.info("An error happened while running command --> {0}".format(line))
                return 1

        return 0


if __name__ == "__main__":
    print("pycavi_tools test - Flambda_zp({0}): {1}".format("V_JOHN", Flambda_zp("V_JOHN")))
    print("pycavi_tools test - V_JOHN AB - Vega: {} ".format(get_mab_minus_vega("V_JOHN")["mab_mveg"]))
    print("pycavi_tools test - B_JOHN AB - Vega: {} ".format(get_mab_minus_vega("B_JOHN")["mab_mveg"]))
    print("pycavi_tools test - r_sdss AB - Vega: {} ".format(get_mab_minus_vega("r_SDSS")["mab_mveg"]))
    print("pycavi_tools test - r_SDSS AB - Vega: {} ".format(get_mab_minus_vega("r_SDSS")["mab_mveg"]))

    # Example usage with the ra_array and dec_array defined earlier
    # filename = '/mnt/data/stars_region_with_header.reg'
    # create_ds9_region_file_with_header(ra_array, dec_array, filename, coords="pixel")
