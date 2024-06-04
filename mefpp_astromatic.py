# Includes several classes to manage the run of SExtractor, Scamp and Swarp
import os
import re
import copy
import logging
import builtins
import subprocess
from textwrap import wrap
from astropy.io import fits


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

    logging.info("runCmd: Running command: {0}".format(str_cmd))
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


class SExtractor:

    def __init__(self, filename_abspath, sex_dir_path, input_param=None, input_config=None):
        """
        Simple class to run sextractor over a OMEGA.*_pre_wcs.fits image, the output from solve_field.
        filename : the path to the wcs mosaic image
        """
        self.fits_name = filename_abspath.split("/")[-1]  # name of the fits image input to sextractor
        self.cat_name = self.fits_name[:-5] + ".cat"  # name of the catalogue which will be created by sextractor
        self.dir_name = "/".join(filename_abspath.split("/")[:-1])  # the path to the directory where the mosaic is
        self.sex_dir = sex_dir_path  # the path where the sextractor folder is located
        self.logfile = self.sex_dir + "/" + self.fits_name[:-5]+"_sex.log"  # path to the log file

        # write the sextractor necessary files in the same folder
        if input_param is None:
            self.write_default_param()
        else:
            self.write_input_file(input_param, self.sex_dir + "/sex_default.param")
            #self.write_input_file(input_param, self.dir_name + "/sex_default.param")
        self.write_default_nnw()
        self.write_default_conv()
        if input_config is None:
            self.write_default_config()
        else:
            self.write_input_file(input_config, self.dir_name + "/default.sex")

    def write_input_file(self, input_dict, savename):
        """Given an input file as dictionary, write insted of the default value"""
        #os.chmod(savename, 0o755)
        logging.info("self.dirname: {0}".format(self.dir_name))
        logging.info("savename: {0}".format(savename))
        with open(savename, "w") as f:
            for key in input_dict:
                print("{} {}".format(key, input_dict[key]), file=f)

    def write_default_param(self):
        """Minimal procedure to write a sextractor output
        pars file needed to subsequently run scamp."""
        lines = """NUMBER                   Running object number                                    
EXT_NUMBER               FITS extension number                                    
FLUX_ISO                 Isophotal flux                                            [count]
FLUXERR_ISO              RMS error for isophotal flux                              [count]
MAG_ISO                  Isophotal magnitude                                       [mag]
MAGERR_ISO               RMS error for isophotal magnitude                         [mag]
FLUX_AUTO                Flux within a Kron-like elliptical aperture               [count]
FLUXERR_AUTO             RMS error for AUTO flux                                   [count]
MAG_AUTO                 Kron-like elliptical aperture magnitude                   [mag]
MAGERR_AUTO              RMS error for AUTO magnitude                              [mag]
A_IMAGE                  Profile RMS along major axis                              [pixel]
B_IMAGE                  Profile RMS along minor axis                              [pixel]
THETA_IMAGE              Position angle (CCW/x)                                    [deg]
XWIN_IMAGE               Windowed position estimate along x                        [pixel]
YWIN_IMAGE               Windowed position estimate along y                        [pixel]
ERRX2WIN_IMAGE           Variance of windowed pos along x                          [pixel**2]
ERRY2WIN_IMAGE           Variance of windowed pos along y                          [pixel**2]
ERRXYWIN_IMAGE           Covariance of windowed pos between x and y                [pixel**2]
ERRX2WIN_WORLD           Variance of windowed pos along X-WORLD (alpha)            [deg**2]
ERRY2WIN_WORLD           Variance of windowed pos along Y-WORLD (delta)            [deg**2]
ERRXYWIN_WORLD           Covariance of windowed pos X-WORLD/Y-WORLD                [deg**2]
ERRAWIN_IMAGE            RMS windowed pos error along major axis                   [pixel]
ERRBWIN_IMAGE            RMS windowed pos error along minor axis                   [pixel]
ERRTHETAWIN_IMAGE        Windowed error ellipse pos angle (CCW/x)                  [deg]
FLAGS                    Extraction flags                                         
FLAGS_WEIGHT             Weighted extraction flags                                
FLAGS_WIN                Flags for WINdowed parameters                            
FWHM_IMAGE               FWHM assuming a gaussian core                             [pixel]
ELONGATION               A_IMAGE/B_IMAGE                                          
ELLIPTICITY              1 - B_IMAGE/A_IMAGE                                      
CLASS_STAR               S/G classifier output                                    """
        with open(self.dir_name + "/sex_default.param", "w") as f:
            for aline in lines.split('\n'):
                print(aline, file=f)

    def write_default_nnw(self):
        """Procedure to write basic sextractor .nnw file"""
        lines = """NNW
# Neural Network Weights for the SExtractor star/galaxy classifier (V1.3)
# inputs:	9 for profile parameters + 1 for seeing.
# outputs:	``Stellarity index'' (0.0 to 1.0)
# Seeing FWHM range: from 0.025 to 5.5'' (images must have 1.5 < FWHM < 5 pixels)
# Optimized for Moffat profiles with 2<= beta <= 4.

 3 10 10  1

-1.56604e+00 -2.48265e+00 -1.44564e+00 -1.24675e+00 -9.44913e-01 -5.22453e-01  4.61342e-02  8.31957e-01  2.15505e+00  2.64769e-01
 3.03477e+00  2.69561e+00  3.16188e+00  3.34497e+00  3.51885e+00  3.65570e+00  3.74856e+00  3.84541e+00  4.22811e+00  3.27734e+00
-3.22480e-01 -2.12804e+00  6.50750e-01 -1.11242e+00 -1.40683e+00 -1.55944e+00 -1.84558e+00 -1.18946e-01  5.52395e-01 -4.36564e-01 -5.30052e+00
 4.62594e-01 -3.29127e+00  1.10950e+00 -6.01857e-01  1.29492e-01  1.42290e+00  2.90741e+00  2.44058e+00 -9.19118e-01  8.42851e-01 -4.69824e+00
-2.57424e+00  8.96469e-01  8.34775e-01  2.18845e+00  2.46526e+00  8.60878e-02 -6.88080e-01 -1.33623e-02  9.30403e-02  1.64942e+00 -1.01231e+00
 4.81041e+00  1.53747e+00 -1.12216e+00 -3.16008e+00 -1.67404e+00 -1.75767e+00 -1.29310e+00  5.59549e-01  8.08468e-01 -1.01592e-02 -7.54052e+00
 1.01933e+01 -2.09484e+01 -1.07426e+00  9.87912e-01  6.05210e-01 -6.04535e-02 -5.87826e-01 -7.94117e-01 -4.89190e-01 -8.12710e-02 -2.07067e+01
-5.31793e+00  7.94240e+00 -4.64165e+00 -4.37436e+00 -1.55417e+00  7.54368e-01  1.09608e+00  1.45967e+00  1.62946e+00 -1.01301e+00  1.13514e-01
 2.20336e-01  1.70056e+00 -5.20105e-01 -4.28330e-01  1.57258e-03 -3.36502e-01 -8.18568e-02 -7.16163e+00  8.23195e+00 -1.71561e-02 -1.13749e+01
 3.75075e+00  7.25399e+00 -1.75325e+00 -2.68814e+00 -3.71128e+00 -4.62933e+00 -2.13747e+00 -1.89186e-01  1.29122e+00 -7.49380e-01  6.71712e-01
-8.41923e-01  4.64997e+00  5.65808e-01 -3.08277e-01 -1.01687e+00  1.73127e-01 -8.92130e-01  1.89044e+00 -2.75543e-01 -7.72828e-01  5.36745e-01
-3.65598e+00  7.56997e+00 -3.76373e+00 -1.74542e+00 -1.37540e-01 -5.55400e-01 -1.59195e-01  1.27910e-01  1.91906e+00  1.42119e+00 -4.35502e+00
-1.70059e+00 -3.65695e+00  1.22367e+00 -5.74367e-01 -3.29571e+00  2.46316e+00  5.22353e+00  2.42038e+00  1.22919e+00 -9.22250e-01 -2.32028e+00

 0.00000e+00 
 1.00000e+00"""
        with open(self.dir_name + "/default.nnw", "w") as f:
            for aline in lines.split('\n'):
                print(aline, file=f)

    def write_default_conv(self):
        """Procedure to write basic sextractor .conv file."""
        lines = """CONV NORM
# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.
1 2 1
2 4 2
1 2 1"""
        with open(self.dir_name + "/default.conv", "w") as f:
            for aline in lines.split('\n'):
                print(aline, file=f)

    def write_default_config(self):
        """Procedure to write default.sex file, minimally."""
        lines = """# Default configuration file for SExtractor 2.25.0
# EB 2018-02-08
#

#-------------------------------- Catalog ------------------------------------
""" + "CATALOG_NAME    " + self.cat_name + " # name of the output catalog" + """
CATALOG_TYPE     FITS_LDAC     # NONE,ASCII,ASCII_HEAD, ASCII_SKYCAT,
                                # ASCII_VOTABLE, FITS_1.0 or FITS_LDAC
PARAMETERS_NAME  sex_default.param  # name of the file containing catalog contents

#------------------------------- Extraction ----------------------------------

DETECT_TYPE      CCD            # CCD (linear) or PHOTO (with gamma correction)
DETECT_MINAREA   5              # min. # of pixels above threshold
DETECT_THRESH    3            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2
ANALYSIS_THRESH  3            # <sigmas> or <threshold>,<ZP> in mag.arcsec-2

FILTER           Y              # apply filter for detection (Y or N)?
FILTER_NAME      default.conv   # name of the file containing the filter

DEBLEND_NTHRESH  32             # Number of deblending sub-thresholds
DEBLEND_MINCONT  0.005          # Minimum contrast parameter for deblending

CLEAN            Y              # Clean spurious detections? (Y or N)?
CLEAN_PARAM      1.0            # Cleaning efficiency

MASK_TYPE        CORRECT        # type of detection MASKing: can be one of
                                # NONE, BLANK or CORRECT

#------------------------------ Photometry -----------------------------------

PHOT_APERTURES   5              # MAG_APER aperture diameter(s) in pixels
PHOT_AUTOPARAMS  2.5, 3.5       # MAG_AUTO parameters: <Kron_fact>,<min_radius>
PHOT_PETROPARAMS 2.0, 3.5       # MAG_PETRO parameters: <Petrosian_fact>,
                                # <min_radius>

SATUR_LEVEL      50000.0        # level (in ADUs) at which arises saturation
SATUR_KEY        SATURATE       # keyword for saturation level (in ADUs)

MAG_ZEROPOINT    25.0            # magnitude zero-point
MAG_GAMMA        4.0            # gamma of emulsion (for photographic scans)
GAIN             2.6            # detector gain in e-/ADU
GAIN_KEY         GAIN           # keyword for detector gain in e-/ADU
PIXEL_SCALE      0            # size of pixel in arcsec (0=use FITS WCS info)

#------------------------- Star/Galaxy Separation ----------------------------

SEEING_FWHM      1.2            # stellar FWHM in arcsec
STARNNW_NAME     default.nnw    # Neural-Network_Weight table filename

#------------------------------ Background -----------------------------------

BACK_SIZE        128             # Background mesh: <size> or <width>,<height>
BACK_FILTERSIZE  3              # Background filter: <size> or <width>,<height>

BACKPHOTO_TYPE   GLOBAL         # can be GLOBAL or LOCAL

#------------------------------ Check Image ----------------------------------

CHECKIMAGE_TYPE  NONE      # can be NONE, BACKGROUND, BACKGROUND_RMS,
                                # MINIBACKGROUND, MINIBACK_RMS, -BACKGROUND,
                                # FILTERED, OBJECTS, -OBJECTS, SEGMENTATION,
                                # or APERTURES
CHECKIMAGE_NAME  check.fits     # Filename for the check-image

#--------------------- Memory (change with caution!) -------------------------

MEMORY_OBJSTACK  3000           # number of objects in stack
MEMORY_PIXSTACK  300000         # number of pixels in stack
MEMORY_BUFSIZE   1024           # number of lines in buffer

#----------------------------- Miscellaneous ---------------------------------

VERBOSE_TYPE     NORMAL         # can be QUIET, NORMAL or FULL
HEADER_SUFFIX    .head          # Filename extension for additional headers
WRITE_XML        N              # Write XML file (Y/N)?
XML_NAME         sex.xml        # Filename for XML output
    """
        with open(self.dir_name + "/default.sex", "w") as f:
            for aline in lines.split('\n'):
                print(aline, file=f)

    def run_sextractor(self):

        # here we run sextractor...
        # it assumes we are in the same folder with the fits image and the configuration files
        logoutput = open(self.logfile, "w+")
        logging.debug("run_sextractor: sex logs " + self.logfile)

        # this part will run sextractor
        # depending on the version the call must be done with /usr/bin/sex for 2.18 or lower version
        # and /usr/bin/source-extractor for the newest ones
        # in my case I used 2.25, so it must be called with the source-extractor command
        # TO DO : the code should be able to detect which version of sextractor and changed the code accordingly
        try:
            logging.debug("run_sextractor: on file {0}".format(self.fits_name))
            p = subprocess.Popen(["/opt/local/bin/source-extractor", self.fits_name, '-c', 'default.sex'],
                                 stdout=logoutput, stderr=logoutput, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            logging.info(e.output)
            return 1  # 1 means the process failed

        while True:
            if p.poll() is not None:
                break
        logoutput.close()
        return 0  # a zero indicates a successfully sextraction.


# adapted to python3 from the PAPI pipeline

# ======================================================================

__version__ = "0.1 (2019-08-13)"


# ======================================================================


class SCAMP_Exception(Exception):
    pass


class SCAMP_AccuracyException(Exception):
    pass


# ======================================================================

class Scamp:
    """
    A wrapper class to transparently use SCAMP.

    """

    _SC_config = {

        # ----------------------------- Field grouping ---------------------------------

        "FGROUP_RADIUS":
            {"comment": "Max dist (deg) between field groups",
             "value": 1.0},

        # ---------------------------- Reference catalogs ------------------------------

        "REF_SERVER":
            {"comment": "Internet addresses of catalog servers",
             "value": "cocat1.u-strasbg.fr"},

        "ASTREF_CATALOG":
            {
                "comment": "NONE, FILE, USNO-A1, USNO-A2, USNO-B1, GSC-1.3, GSC-2.2, UCAC-1, UCAC-2,NOMAD-1, 2MASS, DENIS-3, SDSS-R3, SDSS-R5 or SDSS-R6 ",
                "value": "USNO-B1"},

        "ASTREF_BAND":
            {"comment": "Photom. band for astr.ref.magnitudes or DEFAULT, BLUEST, or REDDEST",
             "value": "DEFAULT"},

        "ASTREFMAG_LIMITS":
            {"comment": "Select magnitude range in ASTREF_BAND",
             "value": [-99.0, 99.0]},

        "ASTREFCAT_NAME":
            {"comment": "Local astrometric reference catalogs",
             "value": "NONE"},

        "SAVE_REFCATALOG":
            {"comment": "Save ref catalogs in FITS-LDAC format?",
             "value": "Y"},

        "REFOUT_CATPATH":
            {"comment": "Save path for reference catalogs",
             "value": "."},

        # --------------------------- Merged output catalogs ---------------------------

        "MERGEDOUTCAT_NAME":
            {"comment": "Merged output catalog filename",
             "value": "merged.cat"},

        "MERGEDOUTCAT_TYPE":
            {"comment": "NONE, ASCII_HEAD, ASCII, FITS_LDAC",
             "value": 'NONE'},

        # --------------------------- Fulloutput catalogs ---------------------------

        "FULLOUTCAT_NAME":
            {"comment": "Full output catalog filename",
             "value": "full.cat"},

        "FULLOUTCAT_TYPE":
            {"comment": "NONE, ASCII_HEAD, ASCII, FITS_LDAC",
             "value": 'NONE'},

        # ----------------------------- Pattern matching -------------------------------

        "MATCH":
            {"comment": "Do pattern-matching (Y/N) ?",
             "value": "Y"},

        "MATCH_NMAX":
            {"comment": 'Max.number of detections for MATCHing(0=auto)',
             "value": 0},

        "PIXSCALE_MAXERR":
            {"comment": "Max scale-factor uncertainty",
             "value": 1.2},

        "POSANGLE_MAXERR":
            {"comment": 'Max position-angle uncertainty (deg)',
             "value": 5.0},

        "POSITION_MAXERR":
            {"comment": "Max positional uncertainty (arcmin)",
             "value": 1.0},

        "MATCH_RESOL":
            {"comment": "Matching resolution (arcsec); 0=auto",
             "value": 0},

        "MOSAIC_TYPE":
            {"comment": "UNCHANGED, SAME_CRVAL, SHARE_PROJAXIS, FIX_FOCALPLANE or LOOSE",
             "value": "SHARE_PROJAXIS"},

        "MATCH_FLIPPED":
            {"comment": "Allow matching with flipped axes?",
             "value": "N"},

        # ---------------------------- Cross-identification ----------------------------
        "CROSSID_RADIUS":
            {"comment": "Cross-id initial radius (arcsec)",
             "value": 2.0},

        # ---------------------------- Astrometric solution ----------------------------

        "SOLVE_ASTROM":
            {"comment": "Compute astrometric solution (Y/N) ?",
             "value": "Y"},

        "PROJECTION_TYPE":
            {"comment": "SAME, TPV or TAN",
             "value": "SAME"},

        "ASTRINSTRU_KEY":
            {"comment": "FITS keyword(s) defining the astrom",
             "value": "FILTER"},

        "STABILITY_TYPE":
            {"comment": "EXPOSURE, GROUP, INSTRUMENT or FILE",
             "value": "INSTRUMENT"},

        "CENTROID_KEYS":
            {"comment": "Cat. parameters for centroiding",
             "value": "XWIN_IMAGE,YWIN_IMAGE"},

        "CENTROIDERR_KEYS":
            {"comment": 'Cat. params for centroid err ellipse',
             "value": "ERRAWIN_IMAGE,ERRBWIN_IMAGE,ERRTHETAWIN_IMAGE"},

        "DISTORT_KEYS":
            {"comment": 'Cat. parameters or FITS keywords',
             "value": "XWIN_IMAGE,YWIN_IMAGE"},

        "DISTORT_GROUPS":
            {"comment": "Filename for the check-image",
             "value": [1, 1]},

        "DISTORT_DEGREES":
            {"comment": "Polynom degree for each group",
             "value": 3},

        # ---------------------------- Photometric solution ----------------------------
        "SOLVE_PHOTOM":
            {"comment": 'Compute photometric solution (Y/N) ?',
             "value": "N"},

        "MAGZERO_OUT":
            {"comment": 'Magnitude zero-point(s) in output',
             "value": 0.0},

        "MAGZERO_INTERR":
            {"comment": 'Internal mag.zero-point accuracy',
             "value": 0.01},

        "MAGZERO_REFERR":
            {"comment": 'Photom.field mag.zero-point accuracy',
             "value": 0.03},

        "PHOTINSTRU_KEY":
            {"comment": 'FITS keyword(s) defining the photom.',
             "value": "FILTER"},

        "MAGZERO_KEY":
            {"comment": 'FITS keyword for the mag zero-point',
             "value": "PHOT_C"},

        "EXPOTIME_KEY":
            {"comment": 'FITS keyword for the exposure time (s)',
             "value": "EXPTIME"},

        "AIRMASS_KEY":
            {"comment": 'FITS keyword for the airmass',
             "value": "AIRMASS"},

        "EXTINCT_KEY":
            {"comment": 'FITS keyword for the extinction coeff',
             "value": "PHOT_K"},

        "PHOTOMFLAG_KEY":
            {"comment": 'FITS keyword for the photometry flag',
             "value": "PHOTFLAG"},

        "PHOTFLUX_KEY":
            {"comment": 'Catalog param. for the flux measurement',
             "value": "FLUX_AUTO"},

        "PHOTFLUXERR_KEY":
            {"comment": 'Catalog parameter for the flux error',
             "value": "FLUXERR_AUTO"},

        "PHOTCLIP_NSIGMA":
            {"comment": 'Photom.clipping threshold in sigmas',
             "value": 3.0},

        # ------------------------------- Check-plots ----------------------------------

        #         "CHECKPLOT_CKEY":
        #        {"comment": 'FITS keyword for PLPLOT field colour',
        #         "value": "SCAMPCOL"},

        "CHECKPLOT_DEV":
            {"comment": 'NULL, XWIN, TK, PS, PSC, XFIG, PNG, JPEG, AQT, PDF or SVG',
             "value": "PNG"},

        "CHECKPLOT_TYPE":
            {"comment": 'Check-plots to perform',
             "value": "FGROUPS,DISTORTION,ASTR_INTERROR2D,ASTR_INTERROR1D,ASTR_REFERROR2D,ASTR_REFERROR1D,ASTR_CHI2,PHOT_ERROR"},

        "CHECKPLOT_NAME":
            {"comment": 'Check-plot filename(s)',
             "value": "fgroups,distort,astr_interror2d,astr_interror1d,astr_referror2d,astr_referror1d,astr_chi2,psphot_error"},

        # ------------------------------ Miscellaneous ---------------------------------

        "SN_THRESHOLDS":
            {"comment": 'S/N thresholds (in sigmas) for all and high-SN sample',
             "value": [10.0, 100.0]},

        "FWHM_THRESHOLDS":
            {"comment": 'FWHM thresholds (in pixels) for sources',
             "value": [0.0, 100.0]},

        "AHEADER_SUFFIX":
            {"comment": 'Filename extension for additional INPUT headers',
             "value": ".ahead"},

        "HEADER_SUFFIX":
            {"comment": 'Filename extension for OUTPUT headers',
             "value": ".head"},

        "HEADER_TYPE":
            {"comment": 'NORMAL or FOCAL_PLANE',
             "value": "NORMAL"},

        "VERBOSE_TYPE":
            {"comment": 'QUIET, NORMAL, LOG or FULL',
             "value": "NORMAL"},

        "WRITE_XML":
            {"comment": 'Write XML file (Y/N)?',
             "value": "Y"},

        "XML_NAME":
            {"comment": 'Filename for XML output',
             "value": "scamp.xml"},

        "NTHREADS":
            {"comment": 'umber of simultaneous threads for the SMP version of SCAMP (0=automatic)',
             "value": 0},

        # -- Extra-keys (will not be saved in the main configuration file

        "CONFIG_FILE":
            {"comment": '[Extra key] name of the main configuration file',
             "value": "scamp.conf"}
    }

    # -- Special config. keys that should not go into the config. file.

    _SC_config_special_keys = ["CONFIG_FILE"]

    def __init__(self, filename_abspath, scamp_dir_path):
        """
        SCAMP class constructor.
        If a specific config_file is provided, it is used
        """

        self.dir = "/".join(filename_abspath.split("/")[:-1])  # the directory where the fits is located
        self.fits = filename_abspath.split("/")[-1]  # fits image over which Scamp will run
        self.cat = self.fits[:-5] + ".cat"  # the sextractor catalogue
        self.log_file = scamp_dir_path + "/" + self.fits[:-5] + ".log"

        self.config = (
            dict([(k, copy.deepcopy(Scamp._SC_config[k]["value"])) for k in Scamp._SC_config.keys()]))

        # Extra config parameters that will be added/updated to the current values of the config file
        self.ext_config = {}

        self.program = None
        self.version = None

    def setup(self, path=None):
        """
        Look for SCAMP program ('scamp').
        If a full path is provided, only this path is checked.
        Raise a SCAMP_Exception if it failed.
        Return program and version if it succeed.
        """

        # -- Finding scamp program and its version
        # first look for 'scamp'

        candidates = ['/opt/local/scamp/bin/scamp', 'scamp']

        if path:
            candidates = [path]

        selected = None
        for candidate in candidates:
            try:
                p = subprocess.Popen(candidate, shell=True, bufsize=0,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, close_fds=True)

                versionline = p.communicate()[0]

                if versionline.decode('unicode_escape').find("SCAMP") != -1:
                    selected = candidate
                    break
            except (IOError, OSError):
                continue

        if not selected:
            raise Exception("""
                  Cannot find SCAMP program. Check your PATH,
                  or provide the SCAMP program path in the constructor.
                  """)

        _program = selected

        _version_match = re.search("[Vv]ersion ([0-9\.])+", versionline.decode('unicode_escape'))
        if not _version_match:
            raise Exception("Cannot determine SCAMP version.")

        _version = _version_match.group()[8:]
        if not _version:
            raise Exception("Cannot determine SCAMP version.")

        return _program, _version

    def update_config(self):
        """
        Update the configuration files according to the current
        in-memory SCAMP configuration.
        """

        # -- Write main configuration file

        main_f = builtins.open(self.config["CONFIG_FILE"], "w")

        for key in self.config.keys():
            if key in Scamp._SC_config_special_keys:
                continue

            if (key == "DISTORT_GROUPS" or key == "SN_THRESHOLDS" or key == "FWHM_THRESHOLDS" or
                    key == "ASTREFMAG_LIMITS"):  # tuple instead of a single value
                value = ",".join(map(str, self.config[key]))
            else:
                value = str(self.config[key])

            print("%-16s       %-16s # %s" %
                  (key, value, Scamp._SC_config[key]['comment']), file=main_f)

        main_f.close()

    def run(self, catalog_list, updateconfig=True, clean=False, path=None):
        """
        Run SCAMP for a given list of catalog (.ldac files), and it can be one
        single catalog list.

        Parameters
        ----------
        catalog_list: str
            A list with the images over which Scamp will run. Can be a list with multiple images or a string for a
            single image.

        updateconfig: bool
            Is True (default), the configuration files will be updated before
            running SCAMP.

        clean: bool
            If True (default: False), configuration files (if any) will be
            deleted after SCAMP terminates.
        path: str
            Path name to look for scamp binary file in the system.

        Raises
        ------
        SCAMP_Exception
            Cannot run SCAMP
        SCAMP_AccuracyException
            SCAMP Warning/error: Significant inaccuracy likely to occur in
            projection.

        """

        if updateconfig:
            self.update_config()

        # Try to find SCAMP program
        # This will raise an exception if it failed

        self.program, self.version = self.setup(path)

        # check how many files in the input
        my_catalogs = ""
        if type(catalog_list) == list:
            for file in catalog_list:
                my_catalogs = my_catalogs + " " + file
        else:
            my_catalogs = catalog_list  # a single file

        # Compound extra config command line args
        ext_args = ""
        for key in self.ext_config.keys():
            ext_args = ext_args + " -" + key + " " + str(self.ext_config[key])

        commandline = (
                self.program + " -c " + self.config['CONFIG_FILE'] + " " + ext_args + " " + my_catalogs)

        logging.debug(self.__class__.__name__ + '->run: '.format(commandline))

        # original commands does not include log_file, if you want to keep the original run
        # set logfile parameter to None.
        rcode = run_commands(commandline, logfile=self.log_file)

        if rcode == 1:
            # print("ERROR!!!")
            raise Exception("SCAMP command [%s] failed." % str(commandline))
        elif rcode == 2:
            logging.info("SCAMP Warning: Significant inaccuracy likely to occur in projection: {0}".format(commandline))

        if clean:
            self.clean()

    def clean(self, config=True, catalog=False, check=False):
        """
        Remove the generated SCAMP files (if any).
        If config is True, remove generated configuration files.
        If catalog is True, remove the output catalog.
        If check is True, remove output check image.
        """

        try:
            if config:
                os.unlink(self.config['CONFIG_FILE'])
            if check:
                os.unlink(self.config['CHECKIMAGE_NAME'])

        except OSError:
            pass

    def write_ahead_file(self):
        # here we write the extension headers to the .ahead file for scamp use
        logging.info('write_scamp_ahead_file: dir_name: {0}'.format(self.fits))
        hdu_list = fits.open(self.dir + "/" + self.fits)

        # before writing the headers we add a few keywords in 8-char format
        header0 = hdu_list[0].header

        # translate filter keyword
        try:
            zfilter = header0['HIERARCH ESO INS FILT1 NAME']
            logging.debug('write_scamp_ahead_file: FILTER: ' + zfilter)
        except:
            zfilter = 'NOT_FOUND'
            logging.debug('write_scamp_ahead_file: failed to determine FILTER. Setting it to NOT_FOUND')

        try:
            header0.insert('LST', ('FILTER', zfilter, 'pymefpp: Filter used for observation'), after=True)
            logging.info('write_scamp_ahead_file: Setting FILTER to ' + zfilter)
        except:
            logging.debug('write_scamp_ahead_file: failed to insert keyword FILTER after keyword LST')

        # translate airmass keyword
        try:
            airmass_start = header0['HIERARCH ESO TEL AIRM START']
            airmass_end = header0['HIERARCH ESO TEL AIRM END']
            airmass_obs = (airmass_start + airmass_end) / 2.0
        except:
            airmass_obs = 1.0
            logging.debug('write_scamp_ahead_file: failed to determine airmass. Setting it to 1.0')

        try:
            header0.insert('FILTER', ('AIRMASS', airmass_obs, 'mefpp_scamp: Average airmass of frame'), after=True)
            logging.info('write_scamp_ahead_file: Setting AIRMASS to {0:5.3f}'.format(airmass_obs))
        except:
            logging.debug('write_scamp_ahead_file: failed to insert keyword AIRMASS after FILTER')

        # this should be selectable whether to update the FITS file
        # or to create a separate wcs.ahead file
        #
        with open(self.dir + "/" + self.fits[:-5] + ".ahead", "w") as f:
            for an_hdu in hdu_list[1:]:
                header = an_hdu.header
                for aline in wrap(repr(header), 80):
                    print(aline, file=f)
                print('END', file=f)
        hdu_list.close()

# ################
# SWarp class start here
# ################

# adapted to python3 from the PAPI pipeline

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
