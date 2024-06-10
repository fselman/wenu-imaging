import os
import configparser
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Configuration resources
def create_pycavi_config():
    """Function to create configuration file.
    The configuration file is read by all notebooks,
    and have the information on where the different files
    are located."""
    config = configparser.ConfigParser()

    # Add sections and key-value pairs
    config['General'] = {'debug': True, 'log_level': 'info'}
    raw_dir = '/data/raw_files_dir/'
    root_dir = os.getcwd()
    project_dir = root_dir+'/NewProject/'   # below project_dir notebook X will create calib and science subdirectories
                                            # under each science subdirectory a <target> subdirectory will be created.
                                            # Under the <target> subdirectory notebook X will create filter subdirectories
                                            # Under <target> subdirectory notebook X will create the sex, scamp, swarp, and cal subdirectories.
    sex_dir_name = 'Sextractor_dir'     # will be created by notebook X below the target directory
    scamp_dir_name = 'Scamp_dir'         # will be created by notebook X below the target directory
    swarp_dir_name = 'Swarp_dir'        # will be created by notebook X below the target directory
    cal_dir_name = 'Calibration_dir'    # will be created by notebook X below the target directory

    config['Directories'] = {'raw_dir': raw_dir,
                             'root_dir': root_dir, 
                             'project_dir': project_dir, 
                             'sex_dir_name': sex_dir_name,
                             'scamp_dir_name': scamp_dir_name,
                             'swarp_dir_name': swarp_dir_name,
                             'cal_dir_name': cal_dir_name}

    # Write the configuration to a file
    Path('./config').mkdir(parents=True, exist_ok=True)
    with open('./config/pycavi.cfg', 'w') as configfile:
        config.write(configfile)

def read_pycavi_config():
    """Function to read configuration file."""
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('./config/pycavi.cfg')

    # Access values from the configuration file
    debug_mode = config.getboolean('General', 'debug')
    log_level = config.get('General', 'log_level')
    raw_dir = config.get('Directories', 'raw_dir')
    root_dir = config.get('Directories', 'root_dir')
    project_dir = config.get('Directories', 'project_dir')
    sex_dir_name = config.get('Directories', 'sex_dir_name')
    scamp_dir_name = config.get('Directories', 'scamp_dir_name')
    swarp_dir_name = config.get('Directories', 'swarp_dir_name')
    cal_dir_name = config.get('Directories', 'cal_dir_name')

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'raw_dir': raw_dir,
        'root_dir': root_dir,
        'project_dir': project_dir,
        'sex_dir_name': sex_dir_name,
        'scamp_dir_name': scamp_dir_name,
        'swarp_dir_name': swarp_dir_name,
        'cal_dir_name': cal_dir_name}

    return config_values

class ProjectInfo:
    """Class for entry window to aid in the configuration file creation."""
    def __init__(self, root):
        self.root = root
        super(ProjectInfo, self).__init__()
        self.widgets={}

        # First row, column 0, the root directory for project
        self.selected_dir_label = tk.Label(root, text="No directory selected")
        self.selected_dir_label.grid(column=0, row=0)

        # First row, column 1, the button to navigate to directory
        select_button = tk.Button(root, text="Select root directory", command=self.select_directory)
        select_button.grid(column=1, row=0)

        # Second row, column 0, the name of the project subdirectory
        project_subdir_label = ttk.Label(root, text="Project subdirectory name:")
        project_subdir_label.grid(column=0, row=1)

        # Second row column 1
        self.project_subdir = tk.StringVar()
        project_subdir_entry = ttk.Entry(root, textvariable=self.project_subdir)
        project_subdir_entry.grid(column=1, row=1)

        #def read_info():
        #    """ callback when the read info button clicked
        #    """
        #    self.project_subdir.get()
        #    msg = f'You entered root directory: {self.select_directory} and project dir: {self.project_subdir.get()}'
        #    tk.messagebox.showinfo(
        #        title='Information',
        #        message=msg
        #    )

        # entry info button
        #read_info_button = ttk.Button(root, text="Enter info and close window", command=read_info)
        #read_info_button.grid(row=2,columnspan=2, pady=10)

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.selected_dir_label.config(text=self.directory)



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
