import os
import glob
import logging
import numpy as np
import multiprocessing
from textwrap import wrap
from astropy.io import fits

def run_py4_solve(observation_dir: str, instrument, cpu_count: int = 32, redo_astrometry: bool = False):
    """
    Run astrometry over a given observation directory.
    For each _pre_wcs fits image within the folder, it will create an independent fits image for each extension,
    for which later will be run astrometry net to create a wcs solution.
    Tested with the 4100 and 5200 astromatric indexes series.
    Be careful with the space, because many new fits images will be created.

    cpu_count: number of processors when calling the multiprocessing
    redo_astrometry: it will look if the final _wcs.fits mosaic exists. If redo_astrometry is False will not create
                     a new one. If True will created again an overwrite the previous one.

    create_wcs_frame accepts two different modes when dealing with failed CCDs: the continue mode in which it will
    copy the original, unsolved CCD into the new mosaic together with the rest of solved CCDs. The other available
    option is remove, in which the unsolved CCDs will not be included in the final mosaic, composed only by solved
    CCDs.
    """

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                            logging.FileHandler(observation_dir + "/pymeffpp_solve.log"),
                            logging.StreamHandler()])

    os.chdir(observation_dir)
    logging.info('current directory: {0}'.format(os.getcwd()))
    list_to_solve = glob.glob(instrument.raw_file_prefix+'*_pre.fits')
    print(instrument.raw_file_prefix+'*_pre.fits')

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
        if (os.path.isfile(mosaic_wcs) and not redo_astrometry):
            logging.info("wcs image already exist, skipping to the next image")
            continue

        # Solving
        logging.info("\n\n\nSolving field {0}".format(file_name[:-5]))
        run_solve_field(file_name[:-5], instrument, cpu_count=cpu_count)

        # Creating WCS file
        logging.info("Creating wcs mosaic file {0}\n\n\n".format(file_name))
        create_wcs_frame(os.path.abspath(file_name), instrument, mode="continue")


def solvefield(file_name):
    """
    Run command solve-field in directory dir_name. Note that the
    dir_name is obtained from the file name assuming a fixed
    length! Very bad!
    """
    #dir_name = file_name[:-30] + "_solve_field"
    print('\n\n\n******************')
    print(file_name)
    idx_dir = file_name.rfind('/')
    dir_name = file_name[:idx_dir+1]
    print('Directory Name:     ', dir_name)
    print('******************\n\n\n')
    logging.debug("solvefield: mef file: {0}".format(dir_name[:-24] + ".fits"))
    logging.debug("file_name: {0}".format(file_name))
    logging.debug("dir_name: {0}".format(dir_name))

    try:
        hdu_header = fits.getheader(file_name, ext=0)
    except Exception as e:
        print(e)
        logging.debug("solvefield: problem extracting keys from file {0}. Aborting".format(file_name))
        return

    crval1 = hdu_header["CRVAL1"]
    crval2 = hdu_header["CRVAL2"]
    crpix1 = hdu_header["CRPIX1"]
    crpix2 = hdu_header["CRPIX2"]

    pos_pars = "--ra " + "%3.6f" % crval1 + " --dec " + "%3.6f" % crval2 + " --radius=1.0 "
    scale_pars = " --scale-units arcsecperpix --scale-low 0.18 --scale-high 0.35 --overwrite"
    wcs_pars = " --crpix-x " + "%5d" % crpix1 + " --crpix-y " + "%5d" % crpix2 + " --no-tweak "
    solve_command_pars = " -D " + dir_name + " " + pos_pars + scale_pars + wcs_pars + "--no-plots --new-fits " + \
                         file_name[:-5] + "_newwcs.fits " + file_name
    solve_command_print = " -D " + dir_name + \
                          "\n       " + pos_pars + \
                          "\n     " + scale_pars + \
                          "\n     " + wcs_pars + \
                          "\n      --new-fits " + file_name[:-5] + "_newwcs.fits " + \
                          "\n      " + file_name
    logging.debug("solvefield: {0}".format(solve_command_print))
    os.system("/usr/local/opt/astrometry-net/bin/solve-field " + solve_command_pars)


def run_solve_field(argv: str, instrument, cpu_count: int):
    filename = argv + ".fits"
    dir_name = os.path.abspath(argv)
    try:
        # Create target Directory
        os.mkdir(dir_name)
        logging.debug("run_solve_field: directory {0} created ".format(dir_name))
    except FileExistsError:
        logging.debug("run_solve_field: directory {0} already exists".format(dir_name))

    # here we create a directory where we will save all data from solve-field
    # It saves each extension in the fits images as an individual fits image in a new folder
    # check if the fits image corresponding to an extension exists. If this is the case, then skipped to the next
    hdu_list = fits.open(filename)
    list_of_filenames = []
    ext_name_list = instrument.valid_ext_names

    for an_ext_name in ext_name_list:

        an_hdu = hdu_list[an_ext_name]
        ext_file_name = an_ext_name.replace('#', '_')
        solve_field_dir_name = dir_name + "/" + ext_file_name + "_solve_field/"

        fits_savename = solve_field_dir_name + "/" + ext_file_name + ".fits"
        if os.path.isfile(fits_savename):
            continue

        try:
            # Create target Directory
            os.mkdir(solve_field_dir_name)
            logging.debug("run_solve_field: solve-field directory {0} Created ".format(solve_field_dir_name))
        except Exception as e:
            logging.debug(e)
            logging.debug("run_solve_field: solve-field directory {0} already exists".format(solve_field_dir_name))
        fits.writeto(solve_field_dir_name + "/" + ext_file_name + ".fits", an_hdu.data, an_hdu.header, overwrite=True)
    hdu_list.close()
    logging.info("run_solve_field: processing extensions...")

    #list_of_extensions = ["ESO_CCD_#%2d" % (i,) for i in range(65, 97)]
    ext_name_list = instrument.valid_ext_names
    processlist = list()
    for extension in ext_name_list:
        ext_file_name = extension.replace('#', '_')
        solve_field_dir_name = dir_name + "/" + ext_file_name + "_solve_field/"
        if not os.path.exists(solve_field_dir_name + "/" + ext_file_name + ".wcs"):
            file_name = solve_field_dir_name + "/" + ext_file_name + ".fits"
            logging.debug("run_solve_field: {0}: adding extension: {1} to processpool: ".format(filename, extension, ))
            list_of_filenames.append(file_name)
            processlist.append([file_name])
            logging.debug("added.")
    logging.info("run_solve_field: number of extensions: {:02d}".format(len(list_of_filenames)))

    try:
        logging.debug("run_solve_field: creating processing pool.")
        pool = multiprocessing.Pool(processes=cpu_count)
        logging.debug("...done.")
    except Exception as e:
        logging.debug("exception found attempting multiprocessing pool...")
        print(e)
        pool = multiprocessing.Pool(processes=1)
    num_tasks = len(processlist)
    logging.debug("run_solve_field: number of tasks: {:02d}".format(num_tasks))
    #pool.imap_unordered(solvefield, list_of_filenames)
    result = pool.map_async(solvefield, list_of_filenames)
    result.wait()

    pool.close()
    logging.info("solve_field: ------------ done ----------")


class ExtWCS(object):
    """Very simple WCS class to contain WCS solution for
    each extension headers of a MEF file."""

    def __init__(self, extension_name, ctype1, ctype2, equinox, crval1, crval2, crpix1, crpix2,
                 cd1_1, cd1_2, cd2_1, cd2_2):
        self.name = extension_name
        self.wcs = {"CTYPE1": ctype1.strip("'"), "CTYPE2": ctype2.strip("'"), "EQUINOX": equinox,
                    "CRVAL1": crval1, "CRVAL2": crval2, "CRPIX1": crpix1, "CRPIX2": crpix2,
                    "CD1_1": cd1_1, "CD1_2": cd1_2, "CD2_1": cd2_1, "CD2_2": cd2_2, "THETA": np.arccos(cd1_1)}


def get_wcs_fromfile(wcs_file, ext_name):
    """This script reads the wcs file output from solve-field
    and returns a WCS structure with the WCS keywords receiving
    their values from the wcs file."""
    f = open(wcs_file, "r")
    wcs_lines = f.readlines()
    f.close()
    ctype1 = None
    ctype2 = None
    equinox = None
    crval1 = None
    crval2 = None
    crpix1 = None
    crpix2 = None
    cd1_1 = None
    cd1_2 = None
    cd2_1 = None
    cd2_2 = None
    for aline in wrap(wcs_lines[0], 80):
        field = aline.split()
        if 'CTYPE1' in aline:
            ctype1 = field[2]
            logging.debug('get_wcs_fromfile: CTYPE1: {0}'.format(ctype1, ))
        if 'CTYPE2' in aline:
            ctype2 = field[2]
            logging.debug('get_wcs_fromfile: CTYPE2: {0}'.format(ctype2, ))
        if 'EQUINOX' in aline:
            equinox = float(field[2])
            logging.debug('get_wcs_fromfile: EQUINOX: {0}'.format(equinox, ))
        if 'CRVAL1' in aline:
            crval1 = float(field[2])
            logging.debug('get_wcs_fromfile: CRVAL1: {0}'.format(crval1, ))
        if 'CRVAL2' in aline:
            crval2 = float(field[2])
            logging.debug('get_wcs_fromfile: CRVAL2: {0}'.format(crval2, ))
        if 'CRPIX1' in aline:
            crpix1 = float(field[2])
            logging.debug('get_wcs_fromfile: CRPIX1: {0}'.format(crpix1, ))
        if 'CRPIX2' in aline:
            crpix2 = float(field[2])
            logging.debug('get_wcs_fromfile: CRPIX2: {0}'.format(crpix2, ))
        if 'CD1_1' in aline:
            cd1_1 = float(field[2])
            logging.debug('get_wcs_fromfile: CD1_1: {0}'.format(cd1_1, ))
        if 'CD1_2' in aline:
            cd1_2 = float(field[2])
            logging.debug('get_wcs_fromfile: CD1_2: {0}'.format(cd1_2, ))
        if 'CD2_1' in aline:
            cd2_1 = float(field[2])
            logging.debug('get_wcs_fromfile: CD2_1: {0}'.format(cd2_1, ))
        if 'CD2_2' in aline:
            cd2_2 = float(field[2])
            logging.debug('get_wcs_fromfile: CD2_2: {0}'.format(cd2_2, ))
    thiswcs = ExtWCS(ext_name, ctype1, ctype2, equinox, crval1, crval2, crpix1, crpix2, cd1_1, cd1_2, cd2_1, cd2_2)
    return thiswcs


def create_wcs_frame(argv, instrument, mode="continue"):
    """Creates the <root>_pre_wcs.fits file from input
    <root>_pre.fits, the output of mefpp, by adding the
    WCS solutions found by solve-field for each extension.
    The file is written into the directory <root>_pre"""

    file_name = os.path.basename(argv)
    dir_name = os.path.abspath(file_name[:-5])
    logging.info('create_wcs_frame: file_name: {0}'.format(file_name))

    if os.path.isfile(file_name):
        logging.info('create_wcs_frame: file exists: {0}'.format(file_name))
    if os.path.isdir(dir_name):
        logging.info('create_wcs_frame: directory exists: {0}'.format(dir_name))

    hdu_primary_header = fits.getheader(file_name, ext=0)
    new_hdul = fits.HDUList()
    new_hdul.append(fits.PrimaryHDU(header=hdu_primary_header))

    # extension_name_list = ["ESO_CCD_#%d" % i for i in range(65, 97)]
    ext_name_list = instrument.valid_ext_names

    for ext_name in ext_name_list:
        ext_file_name = ext_name.replace("#", "_")
        solve_field_dir_name = dir_name + "/" + ext_file_name + "_solve_field/"
        logging.debug("create_wcs_frame: testing if solve field directory exists: {0}".format(solve_field_dir_name))
        if os.path.isdir(solve_field_dir_name):
            logging.debug("create_wcs_frame: solve field directory exists: {0}".format(solve_field_dir_name))
        else:
            logging.debug(
                "*** create_wcs_frame: solve field directory does not exists: {0}".format(solve_field_dir_name))
            break

        wcs_file = solve_field_dir_name + "/" + ext_file_name + ".wcs"
        if os.path.isfile(wcs_file):
            logging.info("create_wcs_frame: WCS file exists: {0}".format(wcs_file))
            wcs_fits = solve_field_dir_name + "/" + ext_file_name + "_newwcs.fits"
        else:
            logging.info("*** create_wcs_frame: **WCS file does not exists: {0}".format(wcs_file))
            # if the solved CCD does not exist, then skipped, effectively removing it from the final mosaic
            # later we should add the possibility to average or ignore it
            if mode == "remove":
                continue
            elif mode == "continue":
                wcs_fits = solve_field_dir_name + "/" + ext_file_name + ".fits"

        print("wcs_fits: {}".format(wcs_fits))
        image_hdu = fits.ImageHDU(data=fits.getdata(wcs_fits), header=fits.getheader(wcs_fits))
        new_hdul.append(image_hdu)

    logging.info('create_wcs_frame: creating {0}'.format(dir_name + "/" + file_name[:-5] + "_wcs.fits"))
    new_hdul.writeto(dir_name + "/" + file_name[:-5] + "_wcs.fits", output_verify="ignore", overwrite=True)
    new_hdul.close()


# WIP
# one of the three possible to deal with unsolved CCDs: averaging the solutions of the rest of column/row in the mosaic
# the other two being ignoring (left the original headers) and removing (removing that CCD from the corrected mosaic)
# def averaging_crpix():
    # here we are ready to create the modified MEF file with the corrected headers
    # reference array of success ccds
    # ccds = np.zeros(32, dtype='bool')

    # for an_hdu in hdu_list[1:]:
    #    header = an_hdu.header
    #    header_name = header['EXTNAME']
    #    if not header_name in failed_solvefield:
    #        for key, val in ext_wcs[header_name].wcs.items():
    #            header[key] = ext_wcs[header_name].wcs[key]
    #            i = int(header_name[-2:])
    #            ccds[i - 65] = True
    #            logging.info(
    #                "create_wcs_frame: header[{0}][{1}] = {2}".format(header_name, key, ext_wcs[header_name].wcs[key]))

    # logging.info("working with unsolved ccds")
    # for i in failed_solvefield:
    #    logging.info("failed ccds : {0}".format(i))
    # ccds = ccds.reshape(4, 8)

    # for an_hdu in hdu_list[1:]:
    #    header = an_hdu.header
    #    header_name = header["EXTNAME"]
    #    if header_name in failed_solvefield:
    #        i = int(header_name[-2:]) - 65
    #        l = int(i / 8)
    #        j = i - l * 8
    #        copied_headers = False
    #        # run over the column (crpix1)
    #        con = 0
    #        crpix1 = 0
    #        for ccd_i in range(4):
    #            if ccds[ccd_i, j]:
    #                # we take the crpix value and promediate between all the solved ccd along the column
    #                header_name_solved = "ESO_CCD_#{}".format(8 * ccd_i + j + 65)
    #                crpix1 += ext_wcs[header_name_solved].wcs["CRPIX1"]
    #                con += 1
    #                # we copied the headers the first time we find a reduced image.
    #                if not copied_headers:
    #                    for key, val in ext_wcs[header_name_solved].wcs.items():
    #                        header[key] = ext_wcs[header_name_solved].wcs[key]
    #                        copied_headers = True

    #                        # if con = 0, we skip this image due to lack of solved ccds
    #        if con == 0:
    #            print("Not enough CCDs solved, skipping this image")
    #            return

    #        crpix1 /= con
    #        # and over the row (crpix2)
    #        con = 0
    #        crpix2 = 0
    #        for ccd_i in range(8):
    #            if ccds[l, ccd_i]:
    #                header_name_solved = "ESO_CCD_#{}".format(8 * l + ccd_i + 65)
    #                crpix2 += ext_wcs[header_name_solved].wcs["CRPIX2"]
    #                con += 1

    #        if con == 0:
    #            print("Not enough CCDs solved, skipping this image")
    #            return

    #        crpix2 /= con
    #        # we update the crpix header
    #        header['CRPIX1'] = crpix1
    #        header['CRPIX2'] = crpix2
