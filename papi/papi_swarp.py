import builtins

import copy
import logging

import subprocess
import re
try:
    import exceptions
except ImportError:
    import builtins as exceptions

# ################
# SWarp class start here
# ################

# adapted to python3 from the PAPI pipeline
# Uses run_command instead of runCmd. This permits logging to a file.

# ======================================================================

# __version__ = "0.1 (2019-08-13)"


class SWARPException(Exception):
    pass


# ======================================================================

class SWarp(object):
    """
    A wrapper class to transparently use SWARP.

    """

    _SW_config = {

        # ------------------------------Output-------------------------------------------
        # # Default configuration file for SWarp 2.38.0
        # # EB 2014-03-10
        # #

        "IMAGEOUT_NAME":
            {"comment": "Output filename",
             "value": "coadd.fits"},

        "WEIGHTOUT_NAME":
            {"comment": "Output weight-map filename",
             "value": "coadd.weight.fits"},

        "HEADER_ONLY":
            {"comment": "Only a header as an output file (Y/N)?",
             "value": "N"},

        "HEADER_SUFFIX":
            {"comment": 'Filename extension for additional headers',
             "value": ".head"},

        # ------------------------------- Input Weights --------------------------------
        "RESCALE_WEIGHTS":
            {
                "comment": "Rescale input weights/variances (Y/N)?",
                "value": "Y"
                },

        "WEIGHT_TYPE":
            {"comment": "BACKGROUND,MAP_RMS,MAP_VARIANCE or MAP_WEIGHT",
             "value": "NONE"},

        "WEIGHT_SUFFIX":
            {"comment": "Suffix to use for weight-maps",
             "value": ".weight.fits"},

        "WEIGHT_IMAGE":
            {"comment": "Weightmap filename if suffix not used (all or for each weight-map)",
             "value": ""},

        "WEIGHT_THRESH":
            {"comment": "Bad pixel weight-threshold",
             "value": ""},

        # ------------------------------- Co-addition ----------------------------------

        "COMBINE":
            {"comment": 'Combine resampled images (Y/N)?',
             "value": 'Y'},

        "COMBINE_TYPE":
            {"comment": "MEDIAN,AVERAGE,MIN,MAX,WEIGHTED,CHI2 or SUM",
             "value": "MEDIAN"},

        "CLIP_AMPFRAC":
            {"comment": "Fraction of flux variation allowed with clipping",
             "value": 0.3},

        "CLIP_SIGMA":
            {"comment": "RMS error multiple variation allowed with clipping",
             "value": 4.0},

        "CLIP_WRITELOG":
            {"comment": "Write output file with coordinates of clipped pixels (Y/N)",
             "value": "N"},

        "CLIP_LOGNAME":
            {"comment": "Name of output file with coordinates of clipped pixels",
             "value": "clipped.log"},

        "BLANK_BADPIXELS":
            {"comment": "Set to 0 pixels having a weight of 0",
             "value": "N"},

        # -------------------------------- Astrometry ----------------------------------

        "CELESTIAL_TYPE":
            {"comment": "NATIVE, PIXEL, EQUATORIAL,GALACTIC,ECLIPTIC, or SUPERGALACTIC",
             "value": "NATIVE"},

        "PROJECTION_TYPE":
            {"comment": "Any WCS projection code or NONE",
             "value": "TAN"},

        "PROJECTION_ERR":
            {"comment": "Maximum projection error (in output pixels), or 0 for no approximation",
             "value": 0.001},

        "CENTER_TYPE":
            {"comment": "MANUAL, ALL or MOST",
             "value": "ALL"},

        "CENTER":
            {"comment": "Coordinates of the image center",
             "value": "00:00:00.0, +00:00:00.0"},

        "PIXELSCALE_TYPE":
            {"comment": "MANUAL,FIT,MIN,MAX or MEDIAN",
             "value": "MEDIAN"},

        "PIXEL_SCALE":
            {"comment": "Pixel scale",
             "value": 0.0},

        "IMAGE_SIZE":
            {"comment": "Image size (0 = AUTOMATIC)",
             "value": 0},

        # -------------------------------- Resampling ----------------------------------

        "RESAMPLE":
            {"comment": "Resample input images (Y/N)?",
             "value": "Y"},

        "RESAMPLE_DIR":
            {"comment": "Directory path for resampled images",
             "value": "."},

        "RESAMPLE_SUFFIX":
            {"comment": "filename extension for resampled images",
             "value": ".resamp.fits"},

        "RESAMPLING_TYPE":
            {"comment": "NEAREST,BILINEAR,LANCZOS2,LANCZOS3or LANCZOS4 (1 per axis)",
             "value": "LANCZOS3"},

        "OVERSAMPLING":
            {"comment": "Oversampling in each dimension 0 = automatic)",
             "value": 0},

        "INTERPOLATE":
            {"comment": "Interpolate bad input pixels (Y/N)? (all or for each image)",
             "value": "N"},

        "FSCALASTRO_TYPE":
            {"comment": "NONE,FIXED, or VARIABLE",
             "value": "FIXED"},

        "FSCALE_KEYWORD":
            {"comment": "FITS keyword for the multiplicative factor applied to each input image",
             "value": "FLXSCALE"},

        "FSCALE_DEFAULT":
            {"comment": "Default FSCALE value if not in header",
             "value": 1.0},

        "GAIN_KEYWORD":
            {"comment": "FITS keyword for effect. gain (e-/ADU)",
             "value": "GAIN"},

        "GAIN_DEFAULT":
            {"comment": "Default gain if no FITS keyword found 0 = infinity (all or for each image)",
             "value": 1.0},

        "SATLEV_KEYWORD":
            {"comment": "FITS keyword for saturation level (ADU)",
             "value": "SATURATE"},

        "SATLEV_DEFAULT":
            {"comment": "Default saturation if no FITS keyword",
             "value": 50000.0},

        # --------------------------- Background subtraction ---------------------------

        "SUBTRACT_BACK":
            {"comment": "Subtraction sky background (Y/N)? (all or for each image)",
             "value": "Y"},

        "BACK_TYPE":
            {"comment": "AUTO or MANUAL (all or for each image)",
             "value": "AUTO"},

        "BACK_DEFAULT":
            {"comment": "Default background value in MANUAL (all or for each image)",
             "value": 0.0},

        "BACK_SIZE":
            {"comment": "Background mesh size (pixels) all or for each image)",
             "value": 128},

        "BACK_FILTERSIZE":
            {"comment": "Background map filter range (meshes) (all or for each image)",
             "value": 3},

        "BACK_FILTTHRESH":
            {"comment": "Threshold above which the background-map filter operates",
             "value": 0.0},

        # ------------------------------ Memory management -----------------------------

        "VMEM_DIR":
            {"comment": "Directory path for swap files",
             "value": "."},

        "VMEM_MAX":
            {"comment": "Maximum amount of virtual memory (MB)",
             "value": 2047},

        "MEM_MAX":
            {"comment": "Maximum amount of usable RAM (MB)",
             "value": 256},

        "COMBINE_BUFSIZE":
            {"comment": "RAM dedicated to co-addition(MB)",
             "value": 256},

        # ------------------------------ Miscellaneous ---------------------------------

        "DELETE_TMPFILES":
            {"comment": "Delete temporary resampled FITS files (Y/N)?",
             "value": "Y"},

        "COPY_KEYWORDS":
            {"comment": 'List of FITS keywords to propagate from the input to the output headers',
             "value": "OBJECT"},

        "WRITE_FILEINFO":
            {"comment": "Write information about each input file in the output image header?",
             "value": "N"},

        "WRITE_XML":
            {"comment": 'Write XML file (Y/N)?',
             "value": "Y"},

        "XML_NAME":
            {"comment": "Filename for XML output",
             "value": "swarp.xml"},

        "XSL_URL":
            {"comment": "Filename for XSL style-sheet",
             "value": "file:///usr/share/swarp/swarp.xsl"},

        "VERBOSE_TYPE":
            {"comment": "QUIET,NORMAL or FULL",
             "value": "NORMAL"},

        "NNODES":
            {"comment": "Number of nodes (for clusters)",
             "value": 1},

        "NODE_INDEX":
            {"comment": "Node index (for clusters)",
             "value": 0},

        "NTHREADS":
            {"comment": "Number of simultaneous threads for the SMP version of SWarp, 0 = automatic",
             "value": 0},

        "NOPENFILES_MAX":
            {"comment": "Maximum number of files opened by SWarp",
             "value": 512},

        # -- Extra-keys (will not be saved in the main configuration file

        "CONFIG_FILE":
            {"comment": '[Extra key] name of the main configuration file',
             "value": "SWARP.conf"}
    }

    # -- Special config. keys that should not go into the config. file.

    _SW_config_special_keys = ["CONFIG_FILE"]

    def __init__(self, swarp_dir):
        """
        SWARP class constructor.
        If a specific config_file is provided, it is used.

        parameters:
        swarp_logdir:str
            The path to the Swarp directory where the logfile will be created.
        """

        self.swarp_dir = swarp_dir
        self.logfile = self.swarp_dir + "/SWarp_logfile.log"

        self.config = (
            dict([(k, copy.deepcopy(SWarp._SW_config[k]["value"]))
                  for k in SWarp._SW_config.keys()]))

        # Extra config parameters that will be added/updated to the current
        # values of the config file
        self.ext_config = {}

        self.program = None
        self.version = None

    def setup(self, path=None):
        """
        Look for SWARP program ('swarp').
        If a full path is provided, only this path is checked.
        Raise a SWARPException if it failed.
        Return program and version if it succeed.
        """

        # -- Finding SWARP program and its version
        # first look for 'swarp'

        candidates = ['/opt/local/bin/swarp', 'swarp', "SWarp"]

        if path:
            candidates = [path]

        selected = None
        for candidate in candidates:
            try:
                p = subprocess.Popen(candidate, shell=True, bufsize=0,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, close_fds=True)

                versionline = p.communicate()[0]

                if versionline.decode('ascii').find("SWarp") != -1:
                    selected = candidate
                    break
            except IOError:
                continue

        if not selected:
            raise Exception("""
                  Cannot find SWARP program. Check your PATH,
                  or provide the SWARP program path in the constructor.
                  """)

        _program = selected

        # print versionline
        _version_match = re.search("[Vv]ersion ([0-9\.])+", versionline.decode('ascii'))
        if not _version_match:
            raise Exception("Cannot determine SWARP version.")

        _version = _version_match.group()[8:]
        if not _version:
            raise Exception("Cannot determine SWARP version.")

        # print "Use " + self.program + " [" + self.version + "]"

        return _program, _version

    def update_config(self):
        """
        Update the configuration files according to the current in-memory SWARP
        configuration.
        """

        # -- Write main configuration file

        main_f = builtins.open(self.config['CONFIG_FILE'], 'w')

        for key in self.config.keys():
            if key in SWarp._SW_config_special_keys:
                continue

            value = str(self.config[key])

            print(("%-16s       %-16s # %s" %
                   (key, value, SWarp._SW_config[key]['comment'])), file=main_f)

        main_f.close()

    def run(self, file_list, updateconfig=True, clean=False, path=None):
        """
        Description
        -----------

        Run SWARP for a given list of files (fits files), and it can be one
        single file.

        Parameters
        ----------
        file_list: list or str
            the images to be swarped. If a list is given each entry must correspond to a single image. If str is given
            must correspond to a single image.

        updateconfig: bool
            If True (default), the configuration files will be updated before
            running SWARP.

        clean: bool
            If clean is True (default: False), configuration files (if any) will
            be deleted after SWARP terminates.

        path: str
            Path to the 'swarp' application (binary file) in the system.
        """

        if updateconfig:
            self.update_config()

        # Try to find SWARP program
        # This will raise an exception if it failed

        self.program, self.version = self.setup(path)

        # check how many files in the input
        if type(file_list) == list:
            my_files = ""
            for file in file_list:
                my_files = my_files + " " + file
        else:
            my_files = file_list  # a single file

        # Compound extra config command line args
        ext_args = ""
        for key in self.ext_config.keys():
            ext_args = ext_args + " -" + key + " " + str(self.ext_config[key])

        commandline = (
                self.program + " -c " + self.config['CONFIG_FILE'] + " " + ext_args + " " + my_files)

        rcode = run_commands(commandline, logfile=self.logfile)

        if rcode != 0:
            raise Exception("SWARP command [%s] failed." % str(commandline))

        if clean:
            self.clean()

    def clean(self, config=True):
        """
        Remove the generated SWARP files (if any).
        If config is True, remove generated configuration files.
        """

        try:
            if config:
                os.unlink(self.config['CONFIG_FILE'])

        except OSError:
            pass


# ======================================================================
# A utility function
# ======================================================================
def run_commands(str_cmd, p_shell=True, logfile=None):
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

    logging.info("run_commands: Running command: {0}".format(str_cmd))

    # for convenience we save the command in the directory where it runs
    with open("swarp_command.txt", "w") as text_file:
        text_file.write("{}".format(str_cmd))

    log_path = subprocess.PIPE if logfile is None else open(logfile, "w+")
    univ_lines = None if logfile is None else True

    try:
        p = subprocess.Popen(str_cmd, bufsize=0, shell=p_shell, stdin=subprocess.PIPE, stdout=log_path,
                             stderr=log_path, close_fds=True, universal_newlines=univ_lines)
    except Exception as e:
        logging.info("Some error while running command...")
        print(e)
        raise

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
            logging.info("Can not get accuracy astrometric calibration")
            return 2
        elif (err.count('ERROR ') or err.count('error ') or err.count("Error ")
              or err.count('*Error*')
              or err.count('Segmentation fault') or err.count("command not found")
              or err.count('No source found')
              or err.count("No such file or directory")
              or err.count('WARNING: Not enough matched detections')  # SCAMP
              or err.count('WARNING: Significant inaccuracy likely to occur in projection')):  # SCAMP
            logging.info("An error happened while running command --> {0}".format(err))
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


