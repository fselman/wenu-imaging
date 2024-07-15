import glob
from mefpp_solve import *


def run_py4_solve(observation_dir: str, cpu_count: int = 32, redo_astrometry: bool = False):
    """
    Run astrometry over a given observation directory.
    For each _pre_wcs fits image within the folder, it will create an independent fits image for each extension,
    for which later will be run astrometry net to create a wcs solution.
    Tested with the 4100 and 5200 astromatric indexes series.
    Be careful with the hard disk space, because many new fits images will be created.

    cpu_count: number of processors when calling the multiprocessing
    redo_astrometry: it will look if the final _wcs.fits mosaic exists. If redo_astrometry is False will not create
                     a new one. If True it creates it again and overwrite the previous one.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                            logging.FileHandler(observation_dir + "/pymeffpp_solve.log"),
                            logging.StreamHandler()])

    os.chdir(observation_dir)
    logging.info('current directory: {0}'.format(os.getcwd()))
    list_to_solve = glob.glob('OMEGA.*_pre.fits')

    if len(list_to_solve) == 0:
        logging.info("No images to solve, skipping directory")
        return

    i = 0
    for file_name in list_to_solve:
        i += 1
        logging.info("solving image {0:02d}/{1:02d}: {2}".format(i, len(list_to_solve), file_name[:-5] + '.fits', ))
        # if wcs image exist, continue to the next
        # this must be more flexible, allowing the option to redo the astrometry if the user wants to.
        mosaic_wcs = observation_dir + "/" + file_name[:-5] + "/" + file_name[:-5] + "_wcs.fits"
        if os.path.isfile(mosaic_wcs) and not redo_astrometry:
            logging.info("wcs image already exist, skipping to the next image")
            continue
        run_solve_field(file_name[:-5], cpu_count=cpu_count)
        create_wcs_frame(os.path.abspath(file_name), mode="continue")


if __name__ == "__main__":
    # Set the reduced science dir where it will look for the reduced science images
    # For each target within the folder will check the filters before start to work on each observation.
    root_dir = ""
    reduced_science_dir = root_dir + "science/science/"

    # a list with the tags of image filters. During the tests I worked only with r_SDSS and NB_659
    filters_to_sol = ["r_SDSS", "NB_659"]

    # target list will include all the observed targets within the reduced_science directory
    target_list = []
    for object_ in glob.glob(reduced_science_dir + "*"):
        target_list.append(object_)
    target_list.sort()

    # for each observed target will all the images which filters correspond to the ones given in filters_to_sol
    for target_ in target_list:
        for filter_ in filters_to_sol:
            for observation_ in glob.glob(target_ + "/" + filter_ + "/*"):
                run_py4_solve(observation_, cpu_count=4, redo_astrometry=False)

    # job done
    print("Py2 Astrometry solve-field Done!")
