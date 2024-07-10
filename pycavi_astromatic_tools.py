import os
from textwrap import wrap
import logging

from astropy.io import fits

from papi_sextractor import SExtractor
from papi_scamp import SCAMP

def prepare_to_sextract(target, redo_sextractor):
    """
    Prepare directory where source-extraction will take place. 
    Returns flag indicating whether we should run sextractor.
    """
    sextractor_cat_file = target[:-4]+".cat"
    sextractor_base_dir = "/".join(target.split("/")[:-1])
    print("sextractor_base_dir: {}".format(sextractor_base_dir))
    ready_to_sextract = False and redo_sextractor
    if not os.path.isfile(sextractor_base_dir+'/'+sextractor_cat_file):
        logging.info("Running Sextractor on image {}".format(target.split("/")[-1]))
        ready_to_sextract = True
    elif os.path.isfile(sextractor_base_dir+'/'+sextractor_cat_file) and redo_sextractor:
        logging.info("Removing {} before proceeding".format(sextractor_cat_file))
        os.remove(sextractor_base_dir+'/'+sextractor_cat_file)
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
        
def run_scamp_on_target(target, scamp_dir_path, special_pars):
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
    
    scamp.run(file_cat, updateconfig=True, clean=False)  # run scamp on the single image
    
    logging.info("Scamp finished without problems. Check the diagnosis plots for more information.")

    os.chdir(current_dir)

    return scamp
