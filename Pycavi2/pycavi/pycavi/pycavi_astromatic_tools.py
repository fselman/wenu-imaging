import os
import glob
from textwrap import wrap
import logging

from astropy.io import fits
from pycavi.pycavi.pycavi_metadata import coadd_observation_metadata

from pycavi.papi.papi_sextractor import SExtractor
from pycavi.papi.papi_scamp import SCAMP
from pycavi.papi.papi_swarp import SWarp

# --------------------------------- SExtractor -----------------------------
#
# Interface tools to PAPI Sextractor astromatic wrapper
#

def prepare_to_sextract(target, redo_sextractor):
    """
    Prepare directory where source-extraction will take place. 
    Returns flag indicating whether we should run sextractor.
    """
    sextractor_cat_file = os.path.splitext(target)[0]+".cat"
    sextractor_base_dir = "/".join(target.split("/")[:-1])
    print("sextractor_base_dir: {}".format(sextractor_base_dir))
    ready_to_sextract = False
    if not os.path.isfile(sextractor_cat_file):
        logging.info("Running Sextractor on image {}".format(target.split("/")[-1]))
        ready_to_sextract = True
    elif redo_sextractor:
        logging.info("Removing {} before proceeding".format(sextractor_cat_file))
        os.remove(sextractor_cat_file)
        os.sync()
        ready_to_sextract = True
    else:
        logging.info("Catalogue {} already exists and redo is False. Skipping Sextractor".format(sextractor_cat_file))
        ready_to_sextract = False
    return ready_to_sextract
    
def run_sextractor_on_target(filename_abspath, sextractor_dir_path, special_pars):
    """
    Run sextractor over the wcs.fits image created by solve_field.
    The final output is a catalogue of stars in the mosaic in format FITS_LDAC, ready to be read by Scamp.
    """

    log_file_sextractor = sextractor_dir_path + "/pymeffpp_sextractor.log"
    
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                                  logging.FileHandler(log_file_sextractor),
                                  logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)

    # Due to limitations in path length of astromatic we need to work 
    # in the directory where the files to be sextracted are located.
    wcs_image_path =  '/'.join(filename_abspath.split("/")[:-1])
    image_name = filename_abspath.split("/")[-1]
    logging.info("Moving to target's directory: {}".format(wcs_image_path))
    current_dir = os.getcwd()
    os.chdir(wcs_image_path)
    
    # we call the Sextractor class which will created all the files necessaries to run sextractor
    # then just run it
    # that will create the output necessary for Scamp

    image_name = filename_abspath.split("/")[-1]
    sextractor_cat_file = image_name[:-5]+'.cat'
    sextractor = SExtractor()

    # we tune some parameters
    for key, val in special_pars.items():
        if key in special_pars.keys():
            logging.info("sextractor.config[{}] = {}".format(key, val))
            if key == "NTHREADS":
                # Not in PAPI's legacy config schema; pass as a native option.
                sextractor.ext_config[key] = val
            else:
                sextractor.config[key] = val
        else:
            logging.info("**** Wrong key passed to sextractor: {}".format(key))
    p = sextractor.run(image_name)
    print('py-sextractor.cat --> {}'.format(sextractor_cat_file))
    os.rename('py-sextractor.cat', sextractor_cat_file)
    #if p == 1:
    #    logging.info("Sextraction failed")
    #elif p == 0:
    #    logging.info("Sextraction finished without problems")
     #   print('py-sextractor.cat --> {}'.format(sextractor_cat_file))
     #   os.rename('py-sextractor.cat', sextractor_cat_file)
        
    os.chdir(current_dir)
    return sextractor


# --------------------------------- SCAMP -----------------------------
#
# Interface tools to PAPI Scamp astromatic wrapper
#

def write_ahead_file(filename_abspath):

    file_dir = "/".join(filename_abspath.split("/")[:-1])  # the directory where the fits is located
    file_fits = filename_abspath.split("/")[-1]  # fits image over which Scamp will run

    # here we write the extension headers to the .ahead file for scamp use
    logging.info('write_scamp_ahead_file: {}\n dir_name: {}'.format(file_fits, file_dir))
    hdu_list = fits.open(filename_abspath)


    # this should be selectable whether to update the FITS file
    # or to create a separate wcs.ahead file
    #
    with open(file_dir + "/" + file_fits[:-5] + ".ahead", "w") as f:
        for an_hdu in hdu_list[1:]:
            header = an_hdu.header
            for aline in wrap(repr(header), 80):
                print(aline, file=f)
            print('END', file=f)
    hdu_list.close()


def prepare_to_scamp(target, redo_scamp):
    """
    Prepare directory where scamp will take place. 
    Returns flag indicating whether we should run scamp.
    """
    sextractor_cat_file = target[:-5]+".cat"
    scamp_ahead_file = target[:-5]+".ahead"  # this file is produced by the write_ahead_file procedure
    scamp_head_file = target[:-5]+".head"    # this file was produced by a previous scamp run
    ready_to_scamp = False and redo_scamp

    if os.path.isfile(sextractor_cat_file):
        if not os.path.isfile(scamp_head_file):
            logging.info("Running Scamp on image {}".format(target.split("/")[-1]))
            if os.path.isfile(scamp_ahead_file):
                os.remove(scamp_ahead_file)
                os.sync()
            write_ahead_file(target)  # creates the .ahead file with the headers of the image
            ready_to_scamp = True
        elif os.path.isfile(scamp_head_file) and redo_scamp:
            logging.info("Removing {} before proceeding".format(scamp_head_file))
            os.remove(scamp_head_file)
            os.sync()
            if os.path.isfile(scamp_ahead_file):
                os.remove(scamp_ahead_file)
                os.sync()
            write_ahead_file(target)
            ready_to_scamp = True
        else:
            logging.info("Header file {} already exists. Skipping Scamp".format(scamp_head_file))
    else:
            logging.info("Cannot find source-extractor catalogue: {}".format(sextractor_cat_file))
            ready_to_scamp = False
    return ready_to_scamp
        
def run_scamp_on_target(target, scamp_dir_path, special_pars, scamp_path=None):
    """
    Run Scamp over the wcs.fits image.
    It creates a .ahead file from the image header, and uses the catalogue output by Sextractor.
    As final output a .head file with the corrected WCS headers is created, which will be later read by Swarp.
    """

        # Due to limitations in path length of astromatic we need to work 
    # in the directory where the files to be sextracted are located.
    wcs_image_path =  '/'.join(target.split("/")[:-1])
    file_cat = target.split("/")[-1][:-5]+'.cat'
    logging.info("Moving to target's directory: {}".format(wcs_image_path))
    current_dir = os.getcwd()
    os.chdir(wcs_image_path)
    
    scamp = SCAMP()    # Initialize the Scamp class with default configuration
    
    # change some parameters from default
        # we tune some parameters
    for key, val in special_pars.items():
        if key in special_pars.keys():
            logging.info("scamp.config[{}] = {}".format(key, val))
            scamp.config[key] = val
        else:
            logging.info("**** Wrong key passed to scamp: {}".format(key))
    
    scamp.run(file_cat, updateconfig=True, clean=False, path=scamp_path)  # run scamp on the single image
    
    logging.info("Scamp finished without problems. Check the diagnosis plots for more information.")

    os.chdir(current_dir)

    return scamp


# ------------------------------- SWARP TOOLS --------------------------------
#
# Interface tools to papi Swarp astromatic wrappers 
#

def select_observations(image, observation, filt):
    """Determine if image name contains the observation
    and the filter string in the name. Return boolean."""

    if observation in image and filt in image:
        return True
    else:
        return False

def get_scamp_lists_dict(reduced_dir, reject_observations, filters_to_scamp):
    """
    Returns a dictionary, indexed by <target>/<filter> with the list of all
    solve-field wcs output files of the form *_wcs.fits for that combination
    of targets and filters.
    """
    observations = []
    filters = []
    targets_to_scamp = []
    list_of_solve_wcs_files = glob.glob(reduced_dir+"/**/*_pre/*_wcs.fits", recursive=True)
    for target in list_of_solve_wcs_files:
        zfilter = target.split("/")[-4]
        if (zfilter in filters_to_scamp) or not filters_to_scamp:     # if the list of input filters is empty we do all of them
            targets_to_scamp.append(target)
            observations.append(target.split("/")[-5])
            filters.append(zfilter)

    observations = set(observations)


    good_targets_to_scamp = []
    for atarget in targets_to_scamp:
        rejected = False
        for a_reject in reject_observations:
            #print(a_reject, atarget)
            if a_reject in atarget:
                logging.info('Bad observation, rejecting: {}'.format(atarget))
                rejected = True
        if not rejected:
            good_targets_to_scamp.append(atarget)

    scamp_lists_dict = {}
    for observation in observations:
        for filter_ in filters:
            list_to_scamp = []
            filtered_images = filter(lambda x: select_observations(x, observation, filter_), good_targets_to_scamp)
            #logging.info(observation + "/" + filter_)

            list_of_filtered_images = list(filtered_images)
            if list_of_filtered_images:
                scamp_lists_dict[observation + "/" + filter_] = list_of_filtered_images

    return scamp_lists_dict

def scamp_lists(reduced_dir, reject_observations, filters_to_scamp):
    """
    Returns a dictionary indexed with a string made from the observation
    name and filter, the observation_tag or data partition, with the list
    of files for each observation tag.

    The purpose of partitioning the data this way is to allow the selection
    of which data partition to scamp. We only allow scamping per data partition.
    """
    scamp_lists = get_scamp_lists_dict(reduced_dir, reject_observations, filters_to_scamp)
    #print(scamp_lists.keys())
    observation_tags = list(set(scamp_lists.keys()))
    observation_tags.sort()
    for i in range(len(observation_tags)):
        logging.info("scamp_lists: index: {} -- observation_tag: {}".format(i, observation_tags[i]))

    files_to_scamp = {}
    for i in range(len(observation_tags)):
        targets_to_scamp = glob.glob(reduced_dir+"/**/"+observation_tags[i]+"/*/*_pre/*_wcs.fits", recursive=True)
        #print(i, observation_tags[i])
        files_to_scamp[observation_tags[i]] = []
        for j in range(len(targets_to_scamp)):
            files_to_scamp[observation_tags[i]].append(targets_to_scamp[j])

    print_files = False
    for i in range(len(observation_tags)):
        if print_files:
            print("index: {} -- partition tag: {} -- nfiles: {} ".format(i, observation_tags[i], len(files_to_scamp[sci_observation_tags[i]])))
        for afile in files_to_scamp[observation_tags[i]]:
            if print_files:
                print("   ---------------> ", os.path.basename(targets_to_scamp[j]))
            else:
                pass

    return files_to_scamp


def get_swarp_lists_dict(reduced_dir, reject_observations, filters_to_swarp):
    """
    Returns a dictionary, indexed by <target>/<filter> with the list of all
    Scamp output files of the form *_wcs.head for that combination
    of targets and filters.
    """
    observations = []
    filters = []
    targets_to_swarp = []
    list_of_scamp_head_files = glob.glob(reduced_dir+"/**/*_pre/*_wcs.head", recursive=True)
    for target in list_of_scamp_head_files:
        zfilter = target.split("/")[-4]
        if (zfilter in filters_to_swarp) or not filters_to_swarp:     # if the list of input filters is empty we do all of them
            targets_to_swarp.append(target)
            observations.append(target.split("/")[-5])
            filters.append(zfilter)

    observations = set(observations)


    good_targets_to_swarp = []
    for atarget in targets_to_swarp:
        rejected = False
        for a_reject in reject_observations:
            #print(a_reject, atarget)
            if a_reject in atarget:
                logging.info('Bad observation, rejecting: {}'.format(atarget))
                rejected = True
        if not rejected:
            good_targets_to_swarp.append(atarget)

    swarp_lists_dict = {}
    for observation in observations:
        for filter_ in filters:
            list_to_swarp = []
            filtered_images = filter(lambda x: select_observations(x, observation, filter_), good_targets_to_swarp)
            #logging.info(observation + "/" + filter_)

            list_of_filtered_images = list(filtered_images)
            if list_of_filtered_images:
                swarp_lists_dict[observation + "/" + filter_] = list_of_filtered_images

    return swarp_lists_dict

def run_swarp(swarp_dir_path, frame_list_name, special_pars=None, path=None):
    """Run swarp on the output of scamp for a given observation and filter."""
    os.chdir(swarp_dir_path)
    swarp = SWarp(swarp_dir_path)

    # creates the swap and resamp folders
    if not os.path.isdir("./resamp"):
        os.mkdir("./resamp")
    if not os.path.isdir("./swap"):
        os.mkdir("./swap")

    # change some parameters from default
    # we tune some parameters
    if special_pars is not None:
        for key, val in special_pars.items():
            if key in special_pars.keys():
                logging.info("swarp.config[{}] = {}".format(key, val))
                swarp.config[key] = val
            else:
                logging.info("**** Wrong key passed to swarp: {}".format(key))

    # Validate all science inputs before launching the native coadd. The list
    # produced by prepare_to_swarp contains FITS paths, not .head paths.
    with open(frame_list_name) as stream:
        images = [line.strip() for line in stream if line.strip()]
    coadd_observation_metadata(images)
    logging.info("Running Swarp on framelist")
    swarp.run('@'+ frame_list_name, updateconfig=True, clean=False, path=path)
    update_headers(swarp.config["IMAGEOUT_NAME"], images[0], images)
    weight = swarp.config["WEIGHTOUT_NAME"]
    if os.path.isfile(weight):
        update_headers(weight, images[0], images, weight_map=True)


def update_headers(swarped_image, reference_image, contributing_images=None, weight_map=False):
    """Apply all-input observation metadata, preserving native EXPTIME/GAIN.

    The two-argument interface remains valid for one contributing exposure.
    Weight maps receive timing/provenance but never science pixel units.
    """
    metadata = coadd_observation_metadata(
        contributing_images if contributing_images is not None else [reference_image])
    with fits.open(swarped_image, mode="update") as hdul:
        hdr = hdul[0].header
        for key in metadata:
            if key != "BUNIT" or not weight_map:
                hdr[key] = (metadata[key], metadata.comments[key])
        hdr["RA"] = hdr["CRVAL1"]
        hdr["DEC"] = hdr["CRVAL2"]
        # Existing native checksums would otherwise describe the old header.
        for hdu in hdul:
            if "CHECKSUM" in hdu.header or "DATASUM" in hdu.header:
                hdu.add_checksum()


def prepare_to_swarp(images_list, swarp_dir_path, frames_list_name, special_pars):
    """
    Creates the Swarp directories where the swarped image and the logfiles
    will be stored (unique to observation).
    Creates in the swarp directory the file listing all the scamp .head files
    that will be swarped.

    Returns the name of the file listing the .head files if succesful. Otherwise
    it returns None.
    """
    #print(images_list[0])
    first_image_path = images_list[0]
    print("first_image_path: {}".format(first_image_path))
    observation = first_image_path.split("/")[-5]
    filter_ = first_image_path.split("/")[-4]
    logging.info("filter_: {}".format(filter_))
    logging_string = "\n          - observation: {0}".format(observation) + \
                    "\n          - filter_: {0}".format(filter_) + \
                    "\n          - swarp_dir: {0}".format(swarp_dir_path) + \
                    "\n          - first_image_path: {0}".format(first_image_path)
    logging.info(logging_string)

    logging.info("Attempting to create the SWarp folder..")
    if not os.path.isdir(swarp_dir_path):
        os.mkdir(swarp_dir_path)
        logging.info("Folder created")
    else:
        logging.info("Folder already exists")

    current_dir = os.getcwd()
    os.chdir(swarp_dir_path)

    # we create the list with images to swarp
    #frame_list_name = first_image_path.split("/")[-1][:-5]+'.list'  # we extract the framelist name from the first image in the list
    current_dir = os.getcwd()
    os.chdir(swarp_dir_path)
    logging.info("Creating frame list to swarp in directory: {}".format(os.getcwd()))
    # Version1: we give only the basenames in the framelist but create symlinks in the swarp dir.
    #           tested but if is no different that the simpler version below.
    #with open(frames_list_name, "w") as f:
    #    for image in images_list:
    #        f.write(os.path.basename(image[:-5]+".fits")+"\n")
    #        os.symlink(image[:-5]+".fits", os.path.basename(image[:-5]+".fits"))
    #        os.symlink(image[:-5]+".head", os.path.basename(image[:-5]+".head"))
    #    return frames_list_name

    # Version2: we give the full path in the framelist
    if frames_list_name is not None:
        with open(frames_list_name, "w") as f:
            for image in images_list:
                f.write(image[:-5]+".fits"+"\n")
            return frames_list_name

    # back to the original folder
    os.chdir(current_dir)

    return None

# --------------------------------------- _oOo_ ------------------------------------------
