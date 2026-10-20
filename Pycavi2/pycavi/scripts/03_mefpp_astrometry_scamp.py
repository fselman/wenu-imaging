import os
import glob
import logging
from mefpp_astromatic import SExtractor, Scamp


def prepare_sextractor_plus_scamp(filename_abspath: str, log_dir: str, redo_sextractor: bool = False,
                                  redo_scamp: bool = False):
    """
    Prepare the directories necessaries to run Sextractor and Scamp prior their execution.
    It checks if the output files are present. If it is the case, then skipped the respective execution.

    Parameters
    ----------
    filename_abspath: str
        The absolute path to the wcs mosaic.

    log_dir: str
        the path to log folder.

    redo_sextractor: bool
        If True will rerun SExtractor even if the .cat fits file exists.

    redo_scamp: bool
        If True will rerun Scamp even if the .head file exists.
    """

    # define the paths to the sextractor and scamp folders and created it
    dir_name = "/".join(filename_abspath.split("/")[:-1])
    sextractor_dir_path = "/".join(filename_abspath.split("/")[:-4]) + "/Sextractor_dir"
    scamp_dir_path = "/".join(filename_abspath.split("/")[:-4]) + "/Scamp_dir"
    log_file_sextractor_scamp = log_dir + "/pymeffpp_sextractor_scamp.log"

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                            logging.FileHandler(log_file_sextractor_scamp),
                            logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)

    # creates the Sextractor and Scamp folders where the log files will be located
    try:
        logging.info("Atempting to create the Sextractor folder")
        os.mkdir(sextractor_dir_path)
        logging.info("Folder created")
    except:
        logging.info("Folder already exists")

    try:
        logging.info("Atempting to create the Scamp folder")
        os.mkdir(scamp_dir_path)
        logging.info("Folder created")
    except:
        logging.info("Folder already exists")

    # now the folder are created, it is moment to run sextractor first
    # first move the folder where the data are
    logging.info("Moving to target's directory: {}".format(dir_name))
    current_dir = os.getcwd()
    os.chdir(dir_name)
    # check if the sextractor catalogue exists, if it does then continue, unless the flag "redo_sextractor"
    # is True
    # run sextractor if it is the case
    if not os.path.isfile(filename_abspath[:-5] + ".cat") or redo_sextractor:
        logging.info("Running Sextractor on image {}".format(filename_abspath.split("/")[-1]))
        run_sextractor_on_target(filename_abspath, sextractor_dir_path)
    else:
        logging.info(
            "Catalogue {} already exists. Skipping Sextractor".format(filename_abspath.split("/")[-1][:-5] + ".cat"))
    # At this point Sextractor is finished and we can start to run Scamp
    # check if the Scamp .head file exists, same procedure as for Sextractor
    if not os.path.isfile(filename_abspath[:-5] + ".head") or redo_scamp:
        logging.info("Running Scamp on image {}".format(filename_abspath.split("/")[-1]))
        run_scamp_on_target(filename_abspath, scamp_dir_path)
    else:
        logging.info(
            "Header file {} already exists. Skipping Scamp".format(filename_abspath.split("/")[-1][:-5] + ".head"))

    # the process is done, we can return to the original folder
    logging.info("SExtractor + Scamp finished on image {}".format(filename_abspath.split("/")[-1]))
    logging.info("Returning to original directory: {}".format(current_dir))
    os.chdir(current_dir)


def run_sextractor_on_target(filename_abspath, sextractor_dir_path):
    """
    Run sextractor over the wcs.fits image created by solve_field.
    The final output is a catalogue of stars in the mosaic in format FITS_LDAC, ready to be read by Scamp.
    """
    # we call the Sextractor class which will created all the files necessaries to run sextractor
    # then just run it
    # that will create the output necessary for Scamp

    sextractor = SExtractor(filename_abspath, sextractor_dir_path)
    p = sextractor.run_sextractor()
    if p == 1:
        logging.info("Sextraction failed")
    elif p == 0:
        logging.info("Sextraction finished without problems")


def run_scamp_on_target(filename_abspath, scamp_dir_path):
    """
    Run Scamp over the wcs.fits image.
    It creates a .ahead file from the image header, and uses the catalogue output by Sextractor.
    As final output a .head file with the corrected WCS headers is created, which will be later read by Swarp.
    """
    scamp = Scamp(filename_abspath, scamp_dir_path)  # Initialize the Scamp class with default configuration

    # change some parameters from default
    scamp.config["ASTREF_BAND"] = "REDDEST"
    scamp.config["ASTREFMAG_LIMITS"] = [10, 18]
    scamp.config["POSITION_MAXERR"] = 2
    scamp.config["MOSAIC_TYPE"] = "FIX_FOCALPLANE"
    scamp.config["CROSSID_RADIUS"] = 5.0
    scamp.config["SN_THRESHOLDS"] = [10.0, 40.0]
    scamp.config["FWHM_THRESHOLDS"] = [1.0, 10.0]
    scamp.config["POSANGLE_MAXERR"] = 2.5

    scamp.write_ahead_file()  # creates the .ahead file with the headers of the image
    scamp.run(scamp.cat, updateconfig=True, clean=False)  # run scamp on the single image

    logging.info("Scamp finished without problems. Check the diagnosis plots for more information.")


if __name__ == "__main__":

    root_dir = ""
    reduced_science_dir = root_dir + "science/"
    logdir = root_dir + "logs/"

    # here we select all the folders with the _pre_wcs.fits mosaic
    targets_to_scamp = []
    for target in glob.glob(reduced_science_dir + "science/*/*/*/*_pre/*_wcs.fits"):
        targets_to_scamp.append(target)
    targets_to_scamp.sort()

    c = 0
    for target in targets_to_scamp:
        print("Preparing to Sextract and Scamp fits image : {:d}/{:d}".format(c, len(targets_to_scamp)))
        print("Fits image : {}".format(target.split("/")[-1]))
        prepare_sextractor_plus_scamp(target, logdir, redo_sextractor=False, redo_scamp=False)
        c += 1

    logging.info('-------------- DONE ---------------')
