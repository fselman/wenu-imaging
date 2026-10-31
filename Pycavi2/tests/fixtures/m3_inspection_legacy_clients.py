"""Unmodified function bodies retained from 3a61df627edfdbb1ef43cc3c956dff74bd28c066 for
shared-convention regression only. Original modules: pycavi_associate_reduction.py
and pycavi_solve.py. Not imported as a production module. Refs #159.
"""

def mefpp_normalize_science(sci_part_list, instrument, apply_light_corr=False):
    """
    Convert images from raw adu to e-/s units by multiplying by the avg gain and dividing by the exptime.
    In case of u,g,r and i_SDSS filters, It can also apply the light correction if requested.
    """
    for sci_part in set(sci_part_list):
        # average gain for the image, then divide all image by this avg
        # define the image parameters
        basepath = sci_part.base_path
        data_path = glob.glob(basepath + '/*_pre.fits')

        ext_name_list = instrument.valid_ext_names
        gain_name_dict = instrument.valid_ext_gain_dict
        #ext_name_list = ["ESO_CCD_#%2d" % i for i in range(65, 97)]

        for image_name in data_path:

            # read all the ccd headers to store the avg gain value
            avg_gain = 0

            jj = 0
            for ext_name in ext_name_list:
                #print("mefpp_normalize_science: \nimage_name: {}  \next_name: {}".format(image_name, ext_name))
                ext_head = fits.getheader(image_name, extname=ext_name)
                gain = ext_head[gain_name_dict[ext_name]]
                avg_gain += gain
                jj+=1
            avg_gain /= instrument.next_valid
            if jj != instrument.next_valid:
                raise Exception("number of valid extensions from instrument config not equal with number of use=True values in same file")

            image_head = fits.getheader(image_name, 0)
            if apply_light_corr and  image_head[instrument.filt_key] in ["u_SDSS", "g_SDSS", "r_SDSS", "i_SDSS"]:
                light_coeffs = get_lightcorrection_coeffs(image_head[instrument.filt_key], instrument)
                if light_coeffs is not None and instrument.correct_light_concentration:
                    apply_light_corr = True
                else:
                    apply_light_corr = False

            with fits.open(image_name, mode="update", output_verify="ignore") as hdul:

                # we add some keywords in the primary headers to make
                # astromatic notebooks independent of the instrument
                #
                header0 = hdul[0].header

                # translate filter keyword
                zfilter = 'NOT_FOUND'
                try:
                    zfilter = header0[instrument.filt_key]
                except:
                    logging.debug('mefpp_normalize_science: failed to determine FILTER. Setting it to NOT_FOUND')

                if 'FILTER' not in header0.keys():
                    try:
                        header0.insert('LST', ('FILTER', zfilter, 'pycavi: Filter used for observation'), after=True)
                        logging.info('mefpp_normalize_science: Setting FITS key FILTER to ' + zfilter)
                    except:
                        logging.debug('mefpp_normalize_science: failed to insert keyword FILTER after keyword LST')

                # translate airmass keyword
                try:
                    airmass_start = header0[instrument.airm_start_key]
                    airmass_end = header0[instrument.airm_end_key]
                    airmass_obs = 1.0/((1.0/airmass_start + 1.0/airmass_end) / 2.0)
                except:
                    airmass_obs = 1.0
                    logging.debug('mefpp_normalize_science: failed to determine airmass. Setting it to 1.0')

                try:
                    header0.insert('FILTER', ('AIRMASS', round(airmass_obs, 3), 'pycavi: Average airmass of frame'), after=True)
                    logging.info('mefpp_normalize_science: Setting AIRMASS to {0:5.3f}'.format(airmass_obs))
                except:
                    logging.debug('mefpp_normalize_science: failed to insert keyword AIRMASS after FILTER')


                header0["BUNIT"] = ("e-/s", "units of image pixels")
                exptime = header0["EXPTIME"]

                # we also update the saturation key TBD

                for ext_name in ext_name_list:

                    ext_data = hdul[ext_name].data
                    # apply light correction if the filter support it
                    if apply_light_corr:
                        header0["HIERARCH ESO PYCAVI LIGHTCOR"] = "True"
                        ext_head = hdul[ext_name].header
                        logging.info("mefpp_normalize_science: applying light correction.")
                        apply_light_correction(light_coeffs, ext_data, ext_head, instrument)
                    else:
                        header0["HIERARCH ESO PYCAVI LIGHTCOR"] = "False"
                        logging.info("mefpp_normalize_science: NO light correction.")
                    ext_data *= avg_gain / exptime  # converting raw adus into e-/s

                # we update the SATLEVEL key necessary for downstream processing

                if 'SATLEVEL' in header0.keys():
                    try:
                        satlevel = header0["SATLEVEL"]
                        header0["HIERARCH ESO PYCAVI ORIGSAT"] = (satlevel, "Original saturation level in raw frames")
                        satlevel *= avg_gain / exptime
                        header0["SATLEVEL"] = (satlevel, "Saturation level of frame in [e/s]")
                        header0.insert("SATLEVEL", ("ONEADU", avg_gain / exptime, "e/s corresponding to 1 [ADU]"), after=True)
                    except:
                        logging.info('mefpp_normalize_science: could not update SATLEVEL key')
                else:
                    logging.info('mefpp_normalize_science: no SATLEVEL key in primary header')

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

    hdu_primary_header = science_exposure_header(fits.getheader(file_name, ext=0))
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
        detector_header = detector_science_header(fits.getheader(wcs_fits), hdu_primary_header)
        image_hdu = fits.ImageHDU(data=fits.getdata(wcs_fits), header=detector_header)
        new_hdul.append(image_hdu)

    logging.info('create_wcs_frame: creating {0}'.format(dir_name + "/" + file_name[:-5] + "_wcs.fits"))
    new_hdul.writeto(dir_name + "/" + file_name[:-5] + "_wcs.fits", output_verify="ignore", overwrite=True, checksum=True)
    new_hdul.close()
