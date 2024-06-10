import os
import configparser
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# Configuration resources
def create_pycavi_config(raw_data_dir=None, project_dir=None):
    """Function to create configuration file.
    The configuration file is read by all notebooks,
    and have the information on where the different files
    are located."""
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    #    'debug_mode': debug_mode,
    #    'log_level': log_level,
    #    'raw_data_dir': raw_dir,
    #    'project_dir': project_dir,
    #    'reduced_calib_dir': reduced_calib_dir,
    #    'reduced_science_dir': reduced_science_dir,
    #    'project_logs_dir': project_logs_dir,
    #    'sex_dir_name': sex_dir_name,
    #    'scamp_dir_name': scamp_dir_name,
    #    'swarp_dir_name': swarp_dir_name,
    #    'cal_dir_name': cal_dir_name}
    config['General'] = {'debug': True, 'log_level': 'info'}
    config['Provenance'] = {'Observatory': 'Paranal', 
                            'Telescope': 'VST', 
                            'Instrument': 'OmegaCam',
                            'FilePrefix': 'OMEGA'}
    if project_dir is not None:
            reduced_calib_dir = project_dir+'/calib/' # Directory tree with reduced calibration files + soft links to raw calibrations
            reduced_science_dir = project_dir+'/science/' # Directory tree with reduced science frames + soft links to reduced calibrations.
            project_logs_dir = project_dir+'/logs/' # Directory containing logs created by running the reduction
    else:
        reduced_calib_dir = None
        reduced_science_dir = None
        project_logs_dir = None
    sex_dir_name = 'Sextractor_dir'     # will be created by notebook X below the target directory
    scamp_dir_name = 'Scamp_dir'         # will be created by notebook X below the target directory
    swarp_dir_name = 'Swarp_dir'        # will be created by notebook X below the target directory
    cal_dir_name = 'Calibration_dir'    # will be created by notebook X below the target directory

    config['Directories'] = {'raw_data_dir': raw_data_dir,
                             'project_dir': project_dir, 
                             'reduced_calib_dir': reduced_calib_dir,
                             'reduced_science_dir': reduced_science_dir,
                             'project_logs_dir': project_logs_dir,
                             'sex_dir_name': sex_dir_name,
                             'scamp_dir_name': scamp_dir_name,
                             'swarp_dir_name': swarp_dir_name,
                             'cal_dir_name': cal_dir_name}

    # Write the configuration to a file
    Path('./config').mkdir(parents=True, exist_ok=True)
    with open('./config/pycavi.cfg', 'w') as configfile:
        config.write(configfile)

def read_pycavi_config(project_dir=None):
    """Function to read configuration file."""
    if project_dir is None:
        print('No root directory for project specified.')
        return None

    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('./config/pycavi.cfg')

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    observatory = config.get('Provenance', 'Observatory')
    telescope = config.get('Provenance', 'Telescope')
    instrument = config.get('Provenance', 'Instrument')
    file_prefix = config.get('Provenance', 'FilePrefix')
    raw_data_dir = config.get('Directories', 'raw_data_dir')
    project_dir = config.get('Directories', 'project_dir')
    reduced_calib_dir = config.get('Directories', 'reduced_calib_dir')
    reduced_science_dir = config.get('Directories', 'reduced_science_dir')
    project_logs_dir = config.get('Directories', 'project_logs_dir')
    sex_dir_name = config.get('Directories', 'sex_dir_name')
    scamp_dir_name = config.get('Directories', 'scamp_dir_name')
    swarp_dir_name = config.get('Directories', 'swarp_dir_name')
    cal_dir_name = config.get('Directories', 'cal_dir_name')

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'observatory': observatory,
        'telescope': telescope,
        'instrument': instrument,
        'file_prefix': file_prefix,
        'raw_data_dir': raw_data_dir,
        'project_dir': project_dir,
        'reduced_calib_dir': reduced_calib_dir,
        'reduced_science_dir': reduced_science_dir,
        'project_logs_dir': project_logs_dir,
        'sex_dir_name': sex_dir_name,
        'scamp_dir_name': scamp_dir_name,
        'swarp_dir_name': swarp_dir_name,
        'cal_dir_name': cal_dir_name}

    return config_values

# tkinter widget tools 

class ProjectInfo:
    """Class for entry window to aid in the configuration file creation."""
    def __init__(self):
        self.popup = tk.Tk()
        self.popup.transient()

        super(ProjectInfo, self).__init__()
        self.widgets={}

        # First row, column 0, the root directory for project
        self.raw_dir_label = tk.Label(self.popup, text="No directory containing raw data selected")
        self.raw_dir_label.grid(column=1, row=0)

        # First row, column 1, the button to navigate to directory
        select_button = tk.Button(self.popup, text="Select raw data directory", command=self.select_raw_directory)
        select_button.grid(column=0, row=0)


        # Second row, column 0, the root directory for project
        self.project_root_dir_label = tk.Label(self.popup, text="No root directory for project selected")
        self.project_root_dir_label.grid(column=1, row=1)

        # Second row, column 1, the button to navigate to directory
        select_button = tk.Button(self.popup, text="Select root directory", command=self.select_project_root_directory)
        select_button.grid(column=0, row=1)

        # Third row, column 0, the name of the project subdirectory
        project_subdir_label = ttk.Label(self.popup, text="Project subdirectory name:")
        project_subdir_label.grid(column=0, row=2)

        # Third row column 1
        self.project_subdir = tk.StringVar()
        project_subdir_entry = ttk.Entry(self.popup, textvariable=self.project_subdir)
        project_subdir_entry.grid(column=1, row=2)

        # Fourth row the Enter command
        enter_button = ttk.Button (self.popup, text = "Enter", command=self.close_window)
        enter_button.grid(columnspan=2)

        self.popup.mainloop()

    def select_raw_directory(self):
        self.raw_data_directory = filedialog.askdirectory()
        if self.raw_data_directory:
            self.raw_dir_label.config(text=self.raw_data_directory)

    def select_project_root_directory(self):
        self.project_root_directory = filedialog.askdirectory()
        if self.project_root_directory:
            self.project_root_dir_label.config(text=self.project_root_directory)

    def close_window (self):
        self.popup.destroy()



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
