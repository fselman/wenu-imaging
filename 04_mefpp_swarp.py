import os
import glob
import logging
from astropy.io import fits
from mefpp_astromatic import SWarp


def select_observations(image, observation_select, filt_select):
    if observation_select in image and filt_select in image:
        return True
    else:
        return False


def run_swarp(swarp_dir, frame_list):
    swarp = SWarp(swarp_dir)

    # creates the swap and resamp folders
    if not os.path.isdir("./resamp"):
        os.mkdir("./resamp")
    if not os.path.isdir("./swap"):
        os.mkdir("./swap")

    # updates some SWarp parameters
    swarp.config["IMAGEOUT_NAME"] = frame_list[:-5] + ".fits"
    swarp.config["RESAMPLE_DIR"] = "./resamp"
    swarp.config["VMEM_DIR"] = "./swap"
    swarp.config["COPY_KEYWORDS"] = "OBJECT,RA,DEC,INSTRUME,FILTER,TELESCOP"
    swarp.config["WRITE_FILEINFO"] = "Y"

    if "NB_659" in frame_list:
        swarp.config["SUBTRACT_BACK"] = "N"

    logging.info("Running Swarp on framelist")
    swarp.run('@' + frame_list, updateconfig=True, clean=False)


def update_headers(swarped_image, reference_image):
    """
    Read the headers of the reference image in look for OBJECT, RA and DEC headers which were not copied during SWarp
    """
    reference_header = fits.getheader(reference_image)

    with fits.open(swarped_image, mode="update", output_verify="ignore") as hdul:
        hdr = hdul[0].header
        hdr["BUNIT"] = ("e-/s", "units of image pixels")
        hdr["ORIGIN"] = reference_header["ORIGIN"]
        hdr["OBJECT"] = reference_header["OBJECT"]
        hdr["RA"] = reference_header["RA"]
        hdr["DEC"] = reference_header["DEC"]


def prepare_swarp(science_dir, images_list):
    """
    Creates the Swarp directories where the swarped image and the logfiles will be stored (unique to observation).
    """
    swarp_observation = images_list[0].split("/")[-5]
    swarp_filter = images_list[0].split("/")[-4]
    swarp_dir = science_dir + swarp_observation + "/Swarp_dir"

    logging.info("Attempting to create the SWarp folder..")
    if not os.path.isdir(swarp_dir):
        os.mkdir(swarp_dir)
        logging.info("Folder created")
    else:
        logging.info("Folder already exists")

    current_dir = os.getcwd()
    os.chdir(swarp_dir)

    # we create the list with images to swarp
    with open(swarp_observation + "_" + swarp_filter + ".list", "w") as f:
        for image in images_list:
            f.write(image[:-5] + ".fits\n")

    # now we can run swarp
    run_swarp(swarp_dir, swarp_observation + "_" + swarp_filter + ".list")

    # update the headers of the swarped image
    update_headers(swarp_observation + "_" + swarp_filter + ".fits", images_list[0][:-5] + ".fits")

    # back to the original folder
    os.chdir(current_dir)


if __name__ == "__main__":

    # the root directory where the calibrated and science images will go
    root_dir = ""
    reduced_science_dir = root_dir + "science/science/"
    log_dir = root_dir + "logs/"

    log_file_swarp = log_dir + "/pymeffpp_swarp.log"
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                            logging.FileHandler(log_file_swarp),
                            logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)

    observations = []
    filters = []
    targets_to_swarp = []
    swarp_list = {}

    # all this part is to select all the .head files and grouping accordling to observation and filter
    # the grouped images are stored in the swarp_list dictionary, where the key correspond to the combination
    # of observation plus filter, and the element to corresponding list of images
    for target in glob.glob(reduced_science_dir + "/*/*/*/*_pre/*_wcs.head"):
        targets_to_swarp.append(target)
        observations.append(target.split("/")[-5])
        filters.append(target.split("/")[-4])

    observations = set(observations)
    filters = set(filters)

    for observation in observations:
        for filter_ in filters:
            list_to_swarp = []
            filtered_images = filter(lambda x: select_observations(x, observation, filter_), targets_to_swarp)
            swarp_list[observation + "/" + filter_] = list(filtered_images)

    for observation_tag in swarp_list.keys():
        logging.info("SWarping observation {}, filter {}".format(observation_tag.split("/")[0],
                                                                 observation_tag.split("/")[1]))
        prepare_swarp(reduced_science_dir, swarp_list[observation_tag])

    logging.info('-------------- DONE ---------------')
