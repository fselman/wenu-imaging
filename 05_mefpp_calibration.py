import os
import glob
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from astropy.visualization import simple_norm
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import fits
from zp_calibration import ZPCalibration
from mefpp_astromatic import SExtractor


def run_sextractor_on_frame(image_path, sex_path, rerun=False):
    """
    Run SExtractor on calibrated frame to get a catalogue of stars.

    ##########
    parameters

    image_path : str
        The path to the calibrated frame (symbolic link in the Calibration directory)
    sex_path : str
        The path corresponding to the sextractor folder, the logfile will be saved there
    rerun : bool
        If True, SExtractor will be running again on frame, independently if the output catalogue exists.
    """

    if os.path.isfile(image_path[:-5] + ".cat") and not rerun:
        logging.info("SExtractor output catalogue already exists. Skipping.")
        return

    frame_hdr = fits.getheader(image_path)

    config_dict = {
        # catalog
        "CATALOG_NAME": image_path[:-5] + ".cat",
        "CATALOG_TYPE": "ASCII_HEAD",
        "PARAMETERS_NAME": "sex_default.param",
        # extraction
        "DETECT_TYPE": "CCD",
        "DETECT_MINAREA": 5,
        "DETECT_THRESH": 1.5,
        "ANALYSIS_THRESH": 1.5,
        "FILTER": "Y",
        "FILTER_NAME": "default.conv",
        "DEBLEND_NTHRESH": 32,
        "DEBLEND_MINCONT": 0.005,
        "CLEAN": "Y",
        "CLEAN_PARAM": 1.0,
        "MASK_TYPE": "CORRECT",
        # photometry
        "PHOT_APERTURES": 20,
        "PHOT_AUTOPARAMS": "2.5, 3.5",
        "PHOT_PETROPARAMS": "2.0, 3.5",
        "SATUR_LEVEL": 50000.0,
        "SATUR_KEY": "SATURATE",
        "MAG_ZEROPOINT": frame_hdr["HIERARCH MEFPP QC MAGZP"],
        "MAG_GAMMA": 4.0,
        "GAIN": 2.6,
        "GAIN_KEY": "GAIN",
        "PIXEL_SCALE": 0,
        # star/galaxy separation
        "SEEING_FWHM": 1.2,
        "STARNNW_NAME": "default.nnw",
        # background
        "BACK_SIZE": 128,
        "BACK_FILTERSIZE": 3,
        "BACKPHOTO_TYPE": "LOCAL",
        # check image
        "CHECKIMAGE_TYPE": "NONE",
        "CHECKIMAGE_NAME": "check.fits",
        # Memory (change with caution!)
        "MEMORY_OBJSTACK": 3000,
        "MEMORY_PIXSTACK": 300000,
        "MEMORY_BUFSIZE": 1024,
        # Miscellaneous
        "VERBOSE_TYPE": "NORMAL",
        "HEADER_SUFFIX": ".head",
        "WRITE_XML": "N",
        "XML_NAME": "sex.xml"
    }

    param_dict = {
        # Star id
        "NUMBER": "Running object number",
        # star ra dec
        "ALPHA_J2000": "Right ascension of barycenter(J2000) [deg]",
        "DELTA_J2000": "Declination of barycenter(J2000)[deg]",
        # flux and mag
        "FLUX_BEST": "Best of FLUX_AUTO and FLUX_ISOCOR[count]",
        "FLUXERR_BEST": "RMS error for BEST flux[count]",
        "MAG_BEST": "Best of MAG_AUTO and MAG_ISOCOR[mag]",
        "MAGERR_BEST": "RMS error for MAG_BEST[mag]",
        # extraction flags
        "FLAGS": "Extraction flags",
        "FWHM_IMAGE": "FWHM assuming a gaussian core[pixel]",
        "ELLIPTICITY": "1 - B_IMAGE / A_IMAGE",
        "CLASS_STAR": "S/G classifier output"
    }

    logging.info("running SExtractor on calibrated frame..")
    se = SExtractor(image_path, sex_path, input_param=param_dict, input_config=config_dict)
    se.run_sextractor()
    logging.info("SExtractor finished successfully.")


def plot_calibration_check(skymap_catalogue_path, sex_catalogue_path, zp_cal):
    """
    Created 4 different check plots from the SExtractor photometry on the swarped OmegaCam frame.
    * Skymapper vs OmegaCam magnitudes
    * Skymapper vs Skymapper - OmegaCam magnitudes
    * Skymapper color vs Skymapper - OmegaCam magnitudes. This one also check the systematic increase of magnitude
        in function of the distance from the center R.
    * A check plot of the field

    ##########
    parameters

    skymap_catalogue_path : str
        The path to the clean Skymapper catalogue created during the calibration process of the frame.
    sex_catalogue_path : str
        The path to the SExtractor output catalogue with the photometry of the frame.
    zp_cal : ZPCalibration
        The calibration object containing important information regarding the frame.

    ######
    output

    calibration image:
        A png image named OBJECT_BAND_calibration_check.png containing the aforementioned plots. It is saved on the
        calibration directory.

    """

    logging.info("Creating check plots")
    skymap_catalogue = pd.read_csv(skymap_catalogue_path)
    sex_catalogue = np.loadtxt(sex_catalogue_path)

    # first load the ra, dec and magnitudes from both catalogues.
    ra_skm = skymap_catalogue["raj2000"].to_numpy()
    de_skm = skymap_catalogue["dej2000"].to_numpy()
    ra_sex = sex_catalogue[:, 1]
    de_sex = sex_catalogue[:, 2]

    # select bands accordingly to frame band
    # if band is NB_659, then construct the scatter plot using r-i and r-Ha
    # in rest of cases uses g-band and band-OCam
    # except in g case where we use band-r and band-OCam
    if zp_cal.band == "NB_659":
        mag_skm = skymap_catalogue["r_SDSS"].to_numpy()
        mag_side_skm = skymap_catalogue["i_SDSS"].to_numpy()
        mag_skm_band = "r_SDSS"
        mag_side_skm_band = "i_SDSS"
    else:
        mag_skm = skymap_catalogue[zp_cal.band].to_numpy()
        mag_skm_band = zp_cal.band
        if zp_cal.band == "g_SDSS":
            mag_side_skm = skymap_catalogue["r_SDSS"].to_numpy()
            mag_side_skm_band = "r_SDSS"
        else:
            mag_side_skm = skymap_catalogue["g_SDSS"].to_numpy()
            mag_side_skm_band = "g_SDSS"

    mag_sex = sex_catalogue[:, 5]

    # select only sextractor best sources (flags == 0 and class_star > 0.9)
    flags = sex_catalogue[:, 7]
    class_star = sex_catalogue[:, 10]
    sel_best_stars = (flags == 0) & (class_star > 0.9)
    ra_sex = ra_sex[sel_best_stars]
    de_sex = de_sex[sel_best_stars]
    mag_sex = mag_sex[sel_best_stars]

    # cross-match the skm and sex catalogues
    c_skm = SkyCoord(ra=ra_skm * u.degree, dec=de_skm * u.degree)
    c_sex = SkyCoord(ra=ra_sex * u.degree, dec=de_sex * u.degree)
    idx, d2d, _ = c_skm.match_to_catalog_sky(c_sex)

    max_sep = 1.0 * u.arcsec
    sep_constraint = d2d < max_sep

    # match the ra and dec positions
    ra_skm = ra_skm[sep_constraint]
    de_skm = de_skm[sep_constraint]

    # now we have matched the catalogues we can compare mag by mag
    mag_skm = mag_skm[sep_constraint]
    mag_side_skm = mag_side_skm[sep_constraint]
    mag_sex = mag_sex[idx[sep_constraint]]

    # we paint with the distance to the center
    rad_dist = np.sqrt((ra_skm - zp_cal.crval1) ** 2 + (de_skm - zp_cal.crval2) ** 2)

    data = zp_cal.data
    wcs = zp_cal.wcs

    # we plot the ocam vs skymapper relation
    fig = plt.figure(figsize=(15.7, 12.1), dpi=120)

    gs = gridspec.GridSpec(nrows=4, ncols=5, wspace=0.0)  # width_ratios=[1,1,1,1,1])
    ax1 = fig.add_subplot(gs[:-2, :-3])
    ax2 = fig.add_subplot(gs[-2, :-3], sharex=ax1)
    ax3 = fig.add_subplot(gs[:-1, -3:])
    ax4 = fig.add_subplot(gs[-1, :])

    # skm versus sextractor
    ax1.scatter(mag_skm, mag_sex, color='black', s=2)
    ax1.set_xlim(8.0, zp_cal.mag_max + 1.0)
    ax1.set_ylim(8.0, zp_cal.mag_max + 1.0)
    ax1.set_xlabel("{} Skymapper".format(zp_cal.band))
    ax1.set_ylabel("{} OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax1.set_xlabel("r_SDSS Skymapper".format(zp_cal.band))

    # delta zp vs mag
    sigma_res = np.nanstd(mag_sex - mag_skm)
    ax2.scatter(mag_skm, mag_skm - mag_sex, color='black', s=2)
    ax2.set_ylim(-10.0 * sigma_res, 10.0 * sigma_res)
    ax2.axhline(0.0, ls=':')
    ax2.axvline(mag_min, ls=':')
    ax2.axvline(mag_max, ls=':')
    ax2.set_xlabel("{} Skymapper".format(zp_cal.band))
    ax2.set_ylabel("{}\nSkymapper - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax2.set_ylabel("{} - {}\nSkymapper - OCam".format(mag_skm_band, zp_cal.band))

    norm = simple_norm(data, 'sqrt', percent=99)
    ax3.imshow(data, norm=norm)
    zp_cal.aperture.to_pixel(wcs).plot(color='white', lw=1)

    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    # delta zp vs color
    color = mag_side_skm - mag_skm
    sigma_clip = (color >= np.nanquantile(color, 0.005)) & (color <= np.nanquantile(color, 0.995))

    # if band is g_sdss, invert the color to have g-r instead of r-g. Same for NB659 to have r-i instead of i-r
    if zp_cal.band == "g_SDSS" or zp_cal.band == "NB_659":
        color *= -1
    select = (mag_skm > zp_cal.mag_min) & (mag_skm < zp_cal.mag_max)
    #
    plot4 = ax4.scatter(color[select & sigma_clip], mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip],
                        c=rad_dist[select & sigma_clip], cmap="viridis", s=1)
    plt.colorbar(plot4, ax=ax4, label="R [deg]")
    ax4.axhline(0.0, ls=':')
    ax4.set_xlim(np.amin(color[select & sigma_clip]), np.amax(color[select & sigma_clip]))
    ax4.set_ylim(np.amin(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]),
                 np.amax(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]))
    ax4.set_xlabel("{} - {} Skymapper".format(mag_side_skm_band, mag_skm_band))
    if zp_cal.band == "NB_659" or zp_cal.band == "g_SDSS":
        ax4.set_xlabel("{} - {} Skymapper".format(mag_skm_band, mag_side_skm_band))
    ax4.set_ylabel("{}\nSkymapper - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax4.set_ylabel("{} - {}\nSkymapper - OCam".format(mag_skm_band, zp_cal.band))

    plt.tight_layout()
    logging.info("check plots created. Saving figure...")
    figname = zp_cal.calibrationdir + "/" + zp_cal.frame[:-5] + "_calibration_check.png"
    plt.savefig(figname)


if __name__ == "__main__":

    root_dir = ""  # the root directory where the calibrated and science images will go
    reduced_science_dir = root_dir + "science/science/"
    log_dir = root_dir + "logs/"

    log_file_swarp = log_dir + "/pymeffpp_swarp.log"
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                        handlers=[
                            logging.FileHandler(log_file_swarp),
                            logging.StreamHandler()])
    logging.getLogger().setLevel(logging.INFO)

    images_to_calibrate = []
    for image in glob.glob(reduced_science_dir + "/*/Swarp_dir/*.list"):
        images_to_calibrate.append(image[:-5]+".fits")
    images_to_calibrate.sort()

    mag_min = 13.5  # minimum magnitude to consider from skymapper catalogue when determining zero point
    mag_max = 17.5  # maximum magnitude to consider from skymapper catalogue when determining zero point
    aperture_radius = 4.0  # aperture in arcsec when performing aperture photometry on frame
    ap_sky_r1 = 6.0  # annulus inner radius to determine background around stars during aperture photometry
    ap_sky_r2 = 9.0  # annulus outer radius to determine background around stars during aperture photometry

    for image in images_to_calibrate:

        logging.info("Starting to work on frame {}".format(image.split("/")[-1]))
        zpcal = ZPCalibration(image, calibrator="Skymapper", mag_min=mag_min, mag_max=mag_max,
                              ap_radius=aperture_radius, ap_sky_r1=ap_sky_r1, ap_sky_r2=ap_sky_r2)
        os.chdir(zpcal.basedir + "/" + zpcal.calibrationdir)
        run_sextractor_on_frame("./"+zpcal.frame, "../Sextractor_dir")

        skymap_catalogue_path_frame = "skymapper_query_result_{}_clean.csv".format(zpcal.object)
        sex_catalogue_path_frame = zpcal.frame[:-5] + ".cat"
        plot_calibration_check(skymap_catalogue_path_frame, sex_catalogue_path_frame, zpcal)
        logging.info("Frame {} successfully calibrated".format(zpcal.frame))

    logging.info("-------Done-------")
