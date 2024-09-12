import os
import copy
import logging
import astroplan
import numpy as np
import pandas as pd
import urllib.request

from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy.optimize import minimize

from astroquery.sdss import SDSS

from astropy import units as u

from astropy.coordinates import SkyCoord, get_moon, EarthLocation, AltAz
from astropy.io import fits
from astropy.modeling import models, fitting
from astropy.nddata import Cutout2D
from astropy.stats import sigma_clipped_stats, gaussian_sigma_to_fwhm
from astropy.time import Time
from astropy.visualization import simple_norm
from astropy.wcs import WCS

from photutils import SkyCircularAperture, SkyCircularAnnulus, aperture_photometry

from pycavi import pycavi_tools


class ZPCalibration:
    """A class to contain a pandas dataframe with the data
    to calibrate frame and the zero points needed for the calibration."""

    # current available filters to work with
    _available_filters = ["u_SDSS", "g_SDSS", "r_SDSS", "i_SDSS", "z_SDSS",  "NB_659"]

    def __init__(self, frame, swarp_dir, calibration_dir, observatory, instrument,
                 mag_min, mag_max, 
                 ap_radius, ap_sky_r1, ap_sky_r2, 
                 query_calibrator, query_radius=0.7, query_min_mag=9.0, query_max_mag=19.0):
        """
        Class to manage the calibration of images from instrumental units (adu/s or e-/s) into proper physical units
        (erg/s/cm2/arcsec2).

        Parameters
        ----------
        frame: str
            the absolute path to the single image frame to be calibrated.
        swarp_dir: str
            the absolute path to the swarp directory where the swarped image is located
        calibration_dir: str
            the absolute path to the calibration folder where the calibration catalogues will be saved.
        mag_min: float
            Maximum magnitude value to be considered during the estimation of the zero point.
        mag_max: float
            Maximum magnitude value to be considered during the estimation of the zero point.
        ap_radius: float
            Aperture radius ,in arcsecs, when performing aperture photometry on frame.
        ap_sky_r1: float
            Inner radius, in arcsecs, for the annulus to estimate background around stars.
        ap_sky_r2: float
            Outer radius, in arcsecs, for the annulus to estimate background around stars.
        query_calibrator: str
            From which calibrator (server) download data for comparison. Currently "Skymapper" and "SDSS" are available.
        query_radius: float
            Radius around center for query to photometric catalogue table. Should minimally be sqrt of half width.
        query_min_mag: float
            Magnitud of brighter star to retrieve from photometric catalogue.
        query_max_mag: float
            Magnitude of fainter star to retrieve from photometric catalogue.
        """

        # ---------------- variables based on parameters passed to the class ----------------

        # Mosaic frame name and needed directories
        self.frame = frame.split("/")[-1]  # the frame name

        # we define swarp dir and position script there
        self.swarpdir = swarp_dir
        self.originaldir = None
        if self.swarpdir != os.getcwd():
            self.originaldir = os.getcwd()
            os.chdir(self.swarpdir)

        # creates the calibration folder
        self.calibrationdir = calibration_dir 
        if not os.path.isdir(self.calibrationdir):
            os.mkdir(self.calibrationdir)
            logging.info("Folder created successfully")
        else:
            logging.info("Folder already exists")

        # check if the symbolic link already exists, that means the calibration of that frame was already done.
        if os.path.islink(self.calibrationdir + "/" + self.frame):
            logging.info("Calibration on frame {} already completed. Leaving the class".format(self.frame))
            if self.originaldir is not None:
                os.chdir(self.originaldir)
            return

        # Provenance
        self.observatory = observatory
        self.instrument = instrument

        # variables needed to do the photometric calibration
        #
        self.query_calibrator = query_calibrator
        self.query_radius = query_radius
        self.query_min_mag = query_min_mag
        self.query_max_mag = query_max_mag

        self.mag_min = mag_min  # brightest magnitude to do calibartipn
        self.mag_max = mag_max  # fainter magnitude to do calibration

        # we add the raw magnitudes to self.df
        self.ap_radius = ap_radius
        self.sky_annulus_r1 = ap_sky_r1
        self.sky_annulus_r2 = ap_sky_r2

        # some variables not yet determined
        self.aperture = None
        self.sky_annulus = None
        self.factor_dn_to_flambda = None

        # --------------------------- data from swarp mosaic image ---------------------------

        # open Swarp mosaic and read data and headers
        logging.info('ZPCalibration: init: reading frame')
        self.data, self.hdu = fits.getdata(self.frame, header=True)

        # we get observing passband from title first, if not there, then looks in the header
        self.band = None
        for possible_filter in ZPCalibration._available_filters:
            if possible_filter in self.frame:
                self.band = possible_filter
        if self.band is None:
            self.band = pycavi_tools.keys_from_header(self.hdu, "FILTER").strip()

        # we try to get a value
        try:
            self.object = pycavi_tools.keys_from_header(self.hdu, instrument.object_key).strip().replace(" ", "_")
            print("OBJECT: {}".format(self.object))
        except:
            logging.info("could not set object name from headers. Using 'object'.")
            self.object = "object"

        # coordinates of the center of the field of the Swarp mosaic
        self.crval1, self.crval2 = pycavi_tools.keys_from_header(self.hdu, ["CRVAL1", "CRVAL2"])
        self.crval1 = float(self.crval1)
        self.crval2 = float(self.crval2)

        # plate scale from Swarp mosaic
        cdi_j = np.array(pycavi_tools.keys_from_header(self.hdu, ['CD1_1', 'CD1_2', 'CD2_1', 'CD2_2']))
        self.sx = np.sqrt(cdi_j[0] ** 2 + cdi_j[1] ** 2) * 3600.0
        self.sy = np.sqrt(cdi_j[2] ** 2 + cdi_j[3] ** 2) * 3600.0
        self.plate_scale = (self.sx + self.sy) / 2.0  # plate scale in arcseconds
        logging.info("ZPCalibration: plate_scale: %6.3f (sx: %6.3f - sy: %6.3f) arcsec/pix" % (
            self.plate_scale, self.sx, self.sy))

        # get wcs from Swarp mosaic
        logging.info('ZPCalibration: init: loading wcs info from frame')
        self.wcs = WCS(self.hdu)

        # ------------------  data from scamp images used to build the swarp molsaic ---------------------

        # read the list of images using in SWarp to get the child paths
        self.parents_list = []
        with open(self.frame[:-11] + ".list", "r") as f:
            lines = f.readlines()
        for line in lines:
            self.parents_list.append(line[:-1])  # remove the \n character at the end of the line

        # get average gain over extensions from first frame used by Swarp
        self.avg_gain = self.get_avg_gain_from_frame()

        # get avg airmass from frame list used to build Swarp mosaic
        self.avg_airmass = self.get_avg_airmass_from_frame()

        # orig sky level pos
        self.avg_exptime, self.total_exptime = self.get_avg_exptime_from_frames()

        # We read the catlogue to be used for the photometric calibration

        self.query_str = None
        if self.query_calibrator.lower() == "skymapper":
            self.df = self.get_skymapper_df()
        elif self.query_calibrator.lower() == "sdss":
            self.df = self.get_sdss_df()
        else:
            logging.info("Sorry, but for the moment only Skymapper and SDSS are available as calibrator.")
            logging.info("Finishing the run")
            return

        # creates the aperture objects
        #
        # this call fills the variables:
        # self.positions  = SkyCoord
        # self.aperture    = SkyCircularAperture
        # self.sky_annulus = SkyCircularAnnulus
        #                                     
        self.calibrators_apertures()

        # run aperture photometry in swarp frame using calibrators apertures
        # this call adds collumn  ["raw_mags_" + self.band] to df
        #
        self.do_phot()  # first run to get raw magnitudes and convertion factors

        # here we get the zero points:
        #    zp: to go from DNs in orig files to magnitudes
        #  zphc: to go from e/s to std magnitudes. To compare with Health Check values.
        #   zp2: to go from Flambda (in erg/s/cm**2/Angstrom) to std magnitudes
        # magzp: to go from DNs (in erg/s/cm**2 to std magnitudes)
        #
        self.filter_width = pycavi_tools.filter_width(self.band)
        self.plambda = pycavi_tools.plambda(self.band)
        self.extinctionCoeff = pycavi_tools.extinction_coeff(self.plambda, self.observatory)

        # zero point to convert raw magnitudes in Swarp frame to standard magnitudes
        self.zp = self.get_zp_from_df()
        logging.info('ZPCalibration: zp: {0} to go from ADUs in orig files to mags - ESO health check values'.format(self.zp))

        # zp as calculated by ESO Health Check script. Uses e/s and airmass = 1.0, not above atmosphere
        # frames were converted to e-/s in notebook 3's mefpp_normalize_science function.
        # These will be used for our QC.
        #
        self.zphc = self.zp + self.extinctionCoeff * self.avg_airmass
        logging.info('ZPCalibration: zphc: {:.3f} to go from e/s to std mags below atmosphere.'.format(self.zphc))

        # zero point to go from Flambda to standard AB magnitudes via Oke's
        # formula but instead of Fnu we use Flambda and the pivot wavelength.
        #
        self.zp2 = pycavi_tools.Flambda_zp(self.band)
        logging.info('ZPCalibration: zp2: {:.3f} to go from Flambda to std mags above atmosphere.'.format(self.zp2))

        # Imaging data should provide physical units of erg/s/cm^2. So we must
        # multiply DN by this factor
        self.factor_dn_to_flambda = 10 ** ((self.zp2 - self.zp) / 2.5)
        if self.zp2 is None:
            raise Exception("ZPCalibration: call to Flambda_zp returned None. Filter not in allowed list?")
        logging.info('ZPCalibration: zp2: {:.3f} to go from Flambda to AB mags'.format(self.zp2))
        
        # conversion factor to multiply mosaic DN to get Flambda in erg/s/cm2
        self.magzp = self.zp2 # the zero point value to use with the mosaic data
        logging.info('ZPCalibration: zp2: {:.3f} (from swarp mosaic DN to AB mags)'.format(self.zp2))
        logging.info('ZPCalibration:               (mosaic DN in erg/s/cm**2)')

        # proper imaging fluxes needs erg/s/cm**2
        #
        self.bunit = 'erg/s/cm**2'  # The DN will be in these units.

        # ----- Determining sky levels for Swarp input frames -------
        #
        # get sky levels in physical units. Note I multiplied by filter_width (not so the DNs)
        # so the units will be erg/s/cm**2
        #

        # get sky levels from orig files
        # these levels were substracted by swarp
        #
        self.orig_skies_adu = self.get_orig_sky_levels()
        self.orig_skies_phys = copy.deepcopy(self.orig_skies_adu)
        self.orig_skies_phys.update(
            (x, y * self.factor_dn_to_flambda ) for x, y in self.orig_skies_phys.items())

        sky_mean_list = []
        sky_std_list = []
        for key in self.orig_skies_phys:
            sky_mean_list.append(self.orig_skies_phys[key][0])
            sky_std_list.append(self.orig_skies_phys[key][1])
        self.mean_sky = np.nanmean(sky_mean_list)
        self.std_sky = np.nanmean(sky_std_list)
        self.magsky = self.get_mag_sky()

        # we get the std deviation of the sky from the data itself
        #
        self.mag_sky_std_dev = self.get_std_dev_mag_sky()
        # we get lunar parameters of original Swarp frames
        #
        self.orig_moon_distance, self.orig_moon_fli, \
            self.orig_moon_alt, self.orig_moon_az = self.get_moon_from_frames()

        # We get FITS keywords from ancestor frames for Phase 3
        key_list = ["PRODCATG", "EXPTIME", "TEXPTIME", "MJD-OBS", 
                    "MJD-END", "OBID1", "NCOMBINE", "PROG_ID",
                    "OBSTECH", "FLUXCAL", "PROCSOFT", "TIMESYS", "SATLEVEL"]
        self.phase3_keys, self.phase3_comment, self.phase3_cards = self.get_selected_keys_original(key_list)

        # create dictionary with keywords to be saved
        #
        self.keyword, self.comment, self.mefpp_header_cards = self.get_updated_keywords()

        # we save everything to file
        self.update_frame()

        # create a symbolic link to the updated image in the Calibration dir
        logging.info("Creating symbolic link to the updated frame")
        logging.info("{} -> {}".format(self.frame, self.calibrationdir + "/" + self.frame))
        os.symlink(self.swarpdir + "/" + self.frame, self.calibrationdir + "/" + self.frame)

        logging.info("ZPCalibration: all done. Celebrate with a cup of coffe :)")

    def get_avg_gain_from_frame(self):
        """
        Read the extension gains from all ancestor frame and return the avgerage value.
        Designing for OmegaCam and its 32 CCDs extensions.
        """
        logging.info('get_avg_gain_from_frame: reading original files used by Swarp to determine gains.')

        #ext_name_list = ["ESO_CCD_#%2d" % i for i in range(65, 97)]
        ext_name_list = self.instrument.valid_ext_names
        gains = {}
        for parent_image in self.parents_list:
            parent_name = parent_image.split("/")[-1]
            for extension in ext_name_list:
                header_i = fits.getheader(parent_image, extname=extension)
                gain_i = header_i[self.instrument.valid_ext_gain_dict[extension]]
                gains[parent_name + "_" + extension] = gain_i

        avg_gain = np.nanmean(list(gains.values()))
        std_gain = np.nanstd(list(gains.values()))
        logging.info('get_avg_gain_from_frame: avg_gain: {:.6f}'.format(avg_gain))

        for key in gains.keys():
            if abs(gains[key] - avg_gain) > 3 * std_gain:
                image_i = key.split("_")[0]
                ext_i = key.split("_")[1]
                logging.info("get_avg_gain_from_frame: the CCD {} at frame {} deviates significantly from the avg gain value".format(
                    ext_i, image_i))
                logging.info("get_avg_gain_from_frame: with a gain value of {:.6f}".format(gains[key]))

        return avg_gain

    def get_avg_airmass_from_frame(self):
        """Read the airmass header from the ancestor frame and average them"""
        logging.info('get_avg_airmass_from_frame: reading original files used by Swarp to determine airmass.')

        airmass_list = []
        for image in self.parents_list:
            hdr = fits.getheader(image)
            airm0 = hdr[self.instrument.airm_start_key]
            airm1 = hdr[self.instrument.airm_end_key]
            airmass_list.append(1.0/((1.0/airm1 + 1.0/airm0) / 2.0))
            logging.info("get_avg_airmass_from_frame: airmass for image {} : {:.4f}".format(image.split("/")[-1], (airm1 + airm0) / 2))
        return np.nanmean(airmass_list)

    def get_avg_exptime_from_frames(self):
        """
        Read exposure time from ancestor frames used by Swarp.
        Returns the average and total exposure times.
        """
        logging.info('get_avg_exptimes: read exposure time from files used by Swarp.')

        orig_expotime = []
        for image in self.parents_list:
            header_i = fits.getheader(image)
            exptime = header_i[self.instrument.inst_exp_key]
            orig_expotime.append(exptime)
            logging.info("Exposure time for image {} : {} seconds".format(image.split("/")[-1], exptime))

        avg_exptime = np.nanmean(orig_expotime)
        total_exptime = np.nansum(orig_expotime)
        logging.info("get_avg_exptime_from_frames: average exposure time of frames : {:.0f}".format(avg_exptime))
        logging.info("get_avg_exptime_from_frames: total exposire time of frames : {:.0f}".format(total_exptime))
        return avg_exptime, total_exptime

    def get_skymapper_df(self):
        """Read tke skymapper catalogue to get magnitudes of star in frame."""
        logging.info('get_skymapper_df: querying skymapper and creating pandas data frame with magnitudes.')

        self.query_str = "http://skymapper.anu.edu.au/sm-cone/public/query?RA=" + str(self.crval1) + "&DEC=" + \
                         str(self.crval2) + "&SR=" + str(self.query_radius) + "&VERB=3&RESPONSEFORMAT=CSV"
        logging.info('get_skymapper_df: {0}'.format(self.query_str))

        # doing the query if not already saved to file
        # if this is a csv, why not read it with pandas?
        # Answer: because this script writes it.
        #
        skymapper_raw = self.calibrationdir + "/skymapper_query_result_{}.csv".format(self.object)
        skymapper_clean = skymapper_raw[:-4] + "_clean.csv"
        self.phot_cal_file = skymapper_clean
        if os.path.isfile(skymapper_clean):
            logging.info("get_skymapper_df: clean catalogue found. Reading it.")
            skymapper_df = pd.read_csv(skymapper_clean)
        else:
            if os.path.isfile(skymapper_raw):
                logging.info("get_skymapper_df: Raw Skymapper file found. Reading it.")
                skymapper_df = pd.read_csv(skymapper_raw)
            else:
                logging.info("get_skymapper_df: Skymapper file does not exist. Downloading it.")
                with urllib.request.urlopen(self.query_str) as f:
                    charset = f.headers.get_content_charset()
                    line_list = f.read().decode(charset).split('\r\n')

                # and here we write to file
                logging.info("get_skymapper_df: Saving {0}".format(skymapper_raw.split('/')[-1]))
                with open(skymapper_raw, "w") as f:
                    for aline in line_list:
                        print(aline, file=f)
                logging.info('get_skymapper_df: Done.')
                skymapper_df = pd.read_csv(skymapper_raw)

            # we clean the df by selecting the data with flag and nimaflags == 0.
            clean_flags = skymapper_df["flags"].to_numpy() == 0
            clean_nimaflags = skymapper_df["nimaflags"].to_numpy() == 0
            # we are interested in stars mostly, so additionaly we select stars with class_star > 0.9
            clean_class_star = skymapper_df["class_star"].to_numpy() >= 0.9
            skymapper_df = skymapper_df[clean_flags & clean_nimaflags & clean_class_star]

            # select columns of interest from the clean df
            df_band_columns = ["g_psf", "e_g_psf", "r_psf", "e_r_psf", "i_psf", "e_i_psf", "z_psf", "e_z_psf"]
            df_pos_columns = ["raj2000", "dej2000"]
            df_id_columns = ["object_id"]
            df_star_class_columns = ["class_star"]
            df_total_columns = df_id_columns + df_pos_columns + df_star_class_columns + df_band_columns
            skymapper_df = skymapper_df[df_total_columns]
            skymapper_df = self.convert_sm_to_sdss(skymapper_df)
            skymapper_df.to_csv(skymapper_clean, index=False)

        return skymapper_df

    def convert_sm_to_sdss(self, df):
        """
        Convert magnitudes from Skymapper to SDSS.
        Based on the differences for synthetic spectra presented in Fig17, SM DR1 paper
        https://ui.adsabs.harvard.edu/abs/2018PASA...35...10W/abstract
        Does not take account the effects of reddening
        """
        # dictionary with the conversion for each sm filter available (griz)
        diff_from_color = {"g_psf": lambda x: round(-0.22 * x - 0.07, 2) if (x <= 1.5) else round(0.11 * x + 0.59, 2),
                           "r_psf": lambda x: round(0.03 * x, 2) if (x <= 1.5) else round(-0.05 * x + 0.12, 2),
                           "i_psf": lambda x: round(-0.04 * x + 0.01, 2) if (x <= 1.0) else round(-0.05 * x + 0.04, 2),
                           "z_psf": lambda x: round(-0.03 * x + 0.01, 2) if (x <= 2.0) else round(-0.12 * x + 0.22, 2)}
        sdss_mags = {}

        g_minus_i = df["g_psf"].to_numpy() - df["i_psf"].to_numpy()
        for filter_sm in diff_from_color.keys():
            sm_mags = df[filter_sm].to_numpy()
            mag_corr = np.array(list(map(diff_from_color[filter_sm], g_minus_i)))
            sdss_mags[filter_sm[0] + "_SDSS"] = sm_mags - mag_corr

        for filter_sdss in sdss_mags.keys():
            df[filter_sdss] = np.around(sdss_mags[filter_sdss], 4)

        return df

    def get_sdss_df(self):
        """Read tke sdss catalogue to get magnitudes of star in frame."""
        logging.info('get_sdss_df: querying SDSS and creating pandas data frame with magnitudes.')

        half_width_ra = self.query_radius
        half_width_dec = self.query_radius
        query="""SELECT
                    objid,ra,dec,flags,psfMag_u,Err_u,psfMag_g,Err_g,psfMag_r,Err_r,psfMag_i,Err_i,psfMag_z,Err_z,clean
                FROM STAR
                WHERE
                    ra BETWEEN {0} and {1} AND dec BETWEEN {2} and {3} and flags != 0
                AND
                    psfMag_u BETWEEN 9 AND 19.6
                AND
                    psfMag_g BETWEEN 9 AND 19.6
                AND
                    clean=1
""".format(self.crval1-half_width_ra, self.crval1+half_width_ra, self.crval2-half_width_dec, self.crval2+half_width_dec)

        sdss_astropy_table = SDSS.query_sql(query, data_release=17)
        if sdss_astropy_table is not None:
            sdss_df = sdss_astropy_table.to_pandas()
            sdss_df = sdss_df.rename(columns={'ra': 'raj2000', 'dec': 'dej2000', \
                                              'psfMag_u': 'u_psf', 'Err_u': 'e_u_psf', \
                                              'psfMag_g': 'g_psf', 'Err_g': 'e_g_psf', \
                                              'psfMag_r': 'r_psf', 'Err_r': 'e_r_psf', \
                                              'psfMag_i': 'i_psf', 'Err_i': 'e_i_psf', \
                                              'psfMag_z': 'z_psf', 'Err_z': 'e_z_psf', \
                                              'flags': 'class_star'})

            clean_flags = (sdss_df["u_psf"].to_numpy() > -9999) & \
                          (sdss_df["g_psf"].to_numpy() > -9999) & \
                          (sdss_df["r_psf"].to_numpy() > -9999) & \
                          (sdss_df["i_psf"].to_numpy() > -9999) & \
                          (sdss_df["z_psf"].to_numpy() > -9999)
            print(len(sdss_df))
            sdss_df = sdss_df[clean_flags]
            sdss_df['u_SDSS'] = sdss_df['u_psf']
            sdss_df['g_SDSS'] = sdss_df['g_psf']
            sdss_df['r_SDSS'] = sdss_df['r_psf']
            sdss_df['i_SDSS'] = sdss_df['i_psf']
            sdss_df['z_SDSS'] = sdss_df['z_psf']
            sdss_df['class_star'] = sdss_df['class_star']*0.0 + 0.99

            # now some rounding

            sdss_df['raj2000'] = sdss_df['raj2000'].round(6)
            sdss_df['dej2000'] = sdss_df['dej2000'].round(6)
            sdss_df['u_psf'] = sdss_df['u_psf'].round(3)
            sdss_df['e_u_psf'] = sdss_df['e_u_psf'].round(3)
            sdss_df['g_psf'] = sdss_df['g_psf'].round(3)
            sdss_df['e_g_psf'] = sdss_df['e_g_psf'].round(3)
            sdss_df['r_psf'] = sdss_df['r_psf'].round(3)
            sdss_df['e_r_psf'] = sdss_df['e_r_psf'].round(3)
            sdss_df['i_psf'] = sdss_df['i_psf'].round(3)
            sdss_df['e_i_psf'] = sdss_df['e_i_psf'].round(3)
            sdss_df['z_psf'] = sdss_df['z_psf'].round(3)
            sdss_df['e_z_psf'] = sdss_df['e_z_psf'].round(3)
            sdss_df['u_SDSS'] = sdss_df['u_SDSS'].round(3)
            sdss_df['g_SDSS'] = sdss_df['g_SDSS'].round(3)
            sdss_df['r_SDSS'] = sdss_df['r_SDSS'].round(3)
            sdss_df['i_SDSS'] = sdss_df['i_SDSS'].round(3)
            sdss_df['z_SDSS'] = sdss_df['z_SDSS'].round(3)

            print(len(sdss_df))

            # we write the csv file for further data checks
            sdss_raw = self.calibrationdir + "/sdss_query_result_{}.csv".format(self.object)
            sdss_clean = sdss_raw[:-4] + "_clean.csv"
            self.phot_cal_file = sdss_clean
            sdss_df.to_csv(sdss_clean, index=False)
            return sdss_df
        else:
            print('SDSS query returned no results.')
            return None

    def calibrators_apertures(self):
        """
        Read the ra and dec values from the df and returns the aperture and annulus objects from
        SkyCircularAperture and SkyCircularAnnulus from photutils.
        It uses the values given for circular aperture and annulus in arcsecs.
        """
        ra = np.array(self.df["raj2000"]) * u.deg
        dec = np.array(self.df["dej2000"]) * u.deg

        # Define positions and apertures
        logging.info("calibrators_apertures: creating aperture object")
        self.positions = SkyCoord(ra=ra, dec=dec, frame="icrs")
        self.aperture = SkyCircularAperture(self.positions, r=self.ap_radius * u.arcsec)
        self.sky_annulus = SkyCircularAnnulus(self.positions, self.sky_annulus_r1 * u.arcsec,
                                              self.sky_annulus_r2 * u.arcsec)



    def do_phot(self):
        """
        perform aperture photometry on the observed frame based on the position 
        of the stars in the reference catalogue, either SkyMapper or SDSS.
        Output: appends a column with the raw magnitudes measured in each reference
        catalogue position.
        """
        logging.info("do_phot: doing aperture photometry on frame.")
        phot_table = aperture_photometry(self.data, self.aperture, wcs=self.wcs, method="exact")
        for col in phot_table.colnames:
            if col != "id" and col != "sky_center":
                phot_table[col].info.format = "%.2f"  # for consistent table output

        phot_disk_area = self.aperture.to_pixel(self.wcs).area
        logging.info("do_phot: phot_disk_area in pixels: {}".format(phot_disk_area))

        # from the sky_annulus object get the mask of each annulus, then uses those mask to get their corresponding
        # data from the image. Perform a sigma clipped stats to obtain the median value.
        # the median value is already in value per area, so do not need to consider the area of the annulus
        # FSE CHECK

        logging.info("do_phot: estimating backgrounds.")
        annulus_masks = self.sky_annulus.to_pixel(self.wcs).to_mask(method='center')
        logging.info("do_phot: number of objects: {}".format(len(annulus_masks)))
        bkg_median = np.empty(len(annulus_masks))
        bkg_median[:] = np.nan
        for i in range(len(annulus_masks)):
            mask = annulus_masks[i]
            annulus_data = mask.multiply(self.data)
            #pycavi_tools.pycavi_qc_plot_hist(annulus_data, label='annulus_data values {}'.format(i), nbins=20, x_range="8-deciles", figname=None)
            if annulus_data is not None:  # if we have data we use it
                annulus_data_1d = annulus_data[mask.data > -0]
                _, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d, sigma_lower=3.0, sigma_upper=3.0)
                #print(median_sigclip)
                #pycavi_tools.pycavi_qc_plot_hist(annulus_data_1d, label='annulus_data values {}'.format(i), nbins=20, x_range="8-deciles", figname=None)
                bkg_median[i] = median_sigclip
                #print(bkg_median[i], phot_table["aperture_sum"][i])

        # with the bkg median value, we can subtract from the circular aperture
        # Note that the aper_sum_bkgsub array will have invalid entries in the
        # form of nan and 0.0 values.
        logging.info("do_phot: subtracting backgrounds.")
        aper_bkg = bkg_median * phot_disk_area
        aper_sum_bkgsub = np.array(phot_table["aperture_sum"] - aper_bkg)

        #for flux_val in np.nditer(aper_sum_bkgsub):
        #    print(flux_val)

        # Checking values
        pycavi_tools.pycavi_qc_plot_hist(aper_bkg, label='Background substracted aperture sums.', nbins=30, x_range="full", figname=None)
        pycavi_tools.pycavi_qc_plot_hist(aper_sum_bkgsub, label='Median aperture background', nbins=30, x_range="full", figname=None)

        logging.info("do_phot: Adding column with raw magnitudes to data frame.")
        # during test some points have fluxes below 1, in those cases, lets set the raw magnitude up to 99
        raw_mags = np.zeros_like(aper_sum_bkgsub)
        # FSE CHECK: is setting to 99.0 a good flag of a bad value
        raw_mags[aper_sum_bkgsub > 0] = -2.5 * np.log10(aper_sum_bkgsub[aper_sum_bkgsub > 0])
        raw_mags[aper_sum_bkgsub <= 0] = 99.0
        self.df["raw_mags_" + self.band] = np.around(raw_mags, 4)


        # we also get some morphological data
        ra = np.array(self.df["raj2000"]) * u.deg
        dec = np.array(self.df["dej2000"]) * u.deg
        x_positions, y_positions = self.wcs.world_to_pixel_values(ra, dec)
        # Define the cutout size for each source (in pixels)
        cutout_size = (20, 20)
        fwhm_values = []
        ellipticity_values = []
        theta_values = []
        # Create a PSF model (Gaussian PSF in this case)
        #psf_model = IntegratedGaussianPRF(sigma=4.0)  # Adjust sigma based on the expected FWHM
        for x, y in zip(x_positions, y_positions):

            # Check if the cutout would extend beyond the image boundaries
            x_min, x_max = int(x - cutout_size[0] / 2), int(x + cutout_size[0] / 2)
            y_min, y_max = int(y - cutout_size[1] / 2), int(y + cutout_size[1] / 2)

            image_shape = self.data.shape  # Image dimensions
            if x_min < 0 or x_max > image_shape[1] or y_min < 0 or y_max > image_shape[0]:
                # Skip this source if it goes beyond the image boundaries
                fwhm_values.append(np.nan)
                ellipticity_values.append(np.nan)
                theta_values.append(np.nan)
                continue

            position = (x, y)
            cutout = Cutout2D(self.data, position, cutout_size)

            # Fit a 2D Gaussian to the cutout to estimate FWHM and ellipticity
            y_grid, x_grid = np.mgrid[:cutout.shape[0], :cutout.shape[1]]
            gauss_init = models.Gaussian2D(amplitude=np.max(cutout.data), x_mean=cutout.shape[1]/2, y_mean=cutout.shape[0]/2)
            fit_p = fitting.LevMarLSQFitter()

            fitted_gauss = fit_p(gauss_init, x_grid, y_grid, cutout.data)

            # FWHM can be estimated from the standard deviation of the Gaussian fit
            x_stddev = fitted_gauss.x_stddev.value
            y_stddev = fitted_gauss.y_stddev.value
            theta = fitted_gauss.theta.value  # Rotation angle

            sigma_major = np.sqrt((x_stddev * np.cos(theta))**2 + (y_stddev * np.sin(theta))**2)
            sigma_minor = np.sqrt((x_stddev * np.sin(theta))**2 + (y_stddev * np.cos(theta))**2)
            # Convert to FWHM using the standard Gaussian to FWHM factor (2.355)
            fwhm_major = sigma_major * gaussian_sigma_to_fwhm
            fwhm_minor = sigma_minor * gaussian_sigma_to_fwhm

            fwhm_avg = (fwhm_major + fwhm_minor)/2.0  # Average FWHM

            # Ellipticity is defined as 1-b/a, where a and b are 
            # the Gaussian sigmas along the minoa and major axes.
            ellipticity = 1 - fwhm_minor/fwhm_major

            fwhm_values.append(fwhm_avg)
            ellipticity_values.append(ellipticity)
            theta_values.append(theta)

        self.fwhm_median = np.nanmedian(fwhm_values)*self.plate_scale # Median FWHM in arcsec
        self.ellipticity_median = np.nanmedian(ellipticity_values)    # Ellipticity defined as 1 - b/a
        self.theta_median = np.degrees(np.nanmedian(theta_values)) # Median position angle of stellar images in degrees
        logging.info("do_phot: **** median fwhm: {} ellipticity: {}  theta: {}".format(self.fwhm_median, self.ellipticity_median, self.theta_median))


        logging.info("do_phot: Done.")

    def get_zp_from_df(self):
        """
        Compute the zero point by comparing the raw magnitudes with the calibrator std mags.
        Filter dependent.

        In case of the NB_659 filter, It uses the color dependence of r_SDSS-NB_659 and r_SDSS-i_SDSS to compute
        the expected magnitude for NB_659.
        The color dependence was published by Drew+14, Table 4.
        https://ui.adsabs.harvard.edu/abs/2014MNRAS.440.2036D/abstract
        The data was published with respect Vega system, so in order to compare with Skymapper conversion to AB system
        must be done.

        In the case of the other available filters, (g,r,i,z), it compares the raw magnitude directly to their
        corresponding bandpass.

        """

        def lst_sqr(zp_test, *args):
            y_raw, y_exp = args
            return np.sum((y_exp - y_raw - zp_test) ** 2)

        def sigma_clip(y_raw, y_exp, niter=3):
            sel = np.ones(len(y_raw), dtype=bool)
            zp_get = 23.0
            for i in range(niter+1):
                minimize_solution = minimize(lst_sqr, x0=zp_get*np.ones(1), args=(y_raw[sel], y_exp[sel]),
                                             method="Nelder-Mead")
                res = y_exp - y_raw - minimize_solution.x[0]
                mean_res, std_res = np.mean(res), np.std(res)
                sel = np.abs(res - mean_res) < 3*std_res
                zp_get = round(minimize_solution.x[0], 3)
            return zp_get

        raw = self.df["raw_mags_" + self.band].to_numpy()

        if self.band == "NB_659":
            # Drew+14 colors for MS stars (Table4)
            # Changed from Vega to AB mags
            drew_r_i_ab = np.array([0.061, 0.068, 0.070, 0.071, 0.083, 0.096, 0.115, 0.142, 0.151, 0.162, 0.174, 0.190,
                                    0.210, 0.217, 0.227, 0.238, 0.269, 0.302, 0.366, 0.395, 0.443, 0.476, 0.491, 0.492,
                                    0.540, 0.571, 0.609, 0.616, 0.632, 0.66, 0.681, 0.735, 0.937, 1.002, 1.147, 1.325,
                                    1.381, 1.392])
            drew_r_ha_ab = np.array([0.232, 0.248, 0.235, 0.241, 0.229, 0.226, 0.225, 0.22, 0.217, 0.210, 0.199, 0.186,
                                     0.175, 0.173, 0.172, 0.172, 0.185, 0.207, 0.263, 0.288, 0.327, 0.351, 0.362, 0.362,
                                     0.394, 0.410, 0.425, 0.428, 0.435, 0.446, 0.455, 0.477, 0.564, 0.588, 0.644, 0.699,
                                     0.720, 0.722])

            # select colors r_SDSS, i_SDSS and raw, clean nans and infinites
            r_sdss = self.df["r_SDSS"].to_numpy()
            i_sdss = self.df["i_SDSS"].to_numpy()

            clean_nans = ~np.isnan(r_sdss) & ~np.isnan(i_sdss) & ~np.isnan(raw)
            clean_infinites = ~np.isinf(raw)
            clean_mags = (r_sdss >= self.mag_min) & (r_sdss <= self.mag_max) & (raw < 0)

            r_minus_i = r_sdss[clean_nans & clean_infinites & clean_mags] - \
                i_sdss[clean_nans & clean_infinites & clean_mags]
            r_minus_raw = r_sdss[clean_nans & clean_infinites & clean_mags] - \
                raw[clean_nans & clean_infinites & clean_mags]

            clean_color = (r_minus_i >= drew_r_i_ab[0]) & (r_minus_i <= drew_r_i_ab[-1])
            interp_data = np.interp(r_minus_i[clean_color], drew_r_i_ab, drew_r_ha_ab)
            pycavi_tools.pycavi_qc_plot_hist(r_minus_raw, label='r_SDSS - raw NB_659.', nbins=30, x_range="full")

            # use scipy minimize to find the zero point through least square minimization
            # do a sigma clipping before reach a zero point value.
            zp = sigma_clip(r_minus_raw[clean_color], interp_data)

        else:

            std_mags = self.df[self.band].to_numpy()

            # clean nans and infinites
            clean_nan = ~np.isnan(std_mags) & ~np.isnan(raw)
            clean_infinites = ~np.isinf(raw)
            clean_mag = (std_mags >= self.mag_min) & (std_mags <= self.mag_max) & (raw < 0)

            raw = raw[clean_nan & clean_mag & clean_infinites]
            std_mags = std_mags[clean_nan & clean_mag & clean_infinites]

            zp = sigma_clip(raw, std_mags)
            logging.info('df zero point: {}'.format(zp))

        return zp

    def get_orig_sky_levels(self):
        """Read original files used by Swarp to read the sky levels in ADUs."""
        logging.info('get_orig_sky_levels: reading original files used by Swarp to determine sky levels.')

        orig_skies_adu = {}
        c = 1
        for file_name in self.parents_list:

            parent_fits_name = file_name.split("/")[-1]
            ext_name_list = self.instrument.valid_ext_names
            median_list_image = np.empty(len(ext_name_list))
            median_list_image[:] = np.nan
            i = 0
            for extname in ext_name_list:
                data = fits.getdata(file_name, extname=extname)
                median_list_image[i] = np.nanmedian(data)
                i += 1

            sky_mean = np.nanmean(median_list_image)
            sky_std = np.nanstd(median_list_image)

            orig_skies_adu[parent_fits_name] = np.array([sky_mean, sky_std])
            logging.info("get_orig_sky_levels: sky %i/%i: %s" %
                         (c, len(self.parents_list), parent_fits_name,))
            logging.info('get_orig_sky_levels: sky %i/%i: %2.3f +- %2.3f' % (c, len(self.parents_list),
                                                                             orig_skies_adu[parent_fits_name][0],
                                                                             orig_skies_adu[parent_fits_name][1],))
            c += 1

        logging.info('get_orig_sky_levels: Done.')
        return orig_skies_adu

    def get_selected_keys_original(self, key_list=None):
        """Read original files used by Swarp to read a set of
        selectd keywords. It processes this list to return a
        list of values and comment fields to be inserted in
        the primqry headers of the calibrated file."""
        logging.info('get_selected_keys_original: reading selected FITS keys from original files used by Swarp.')

        if key_list == None:
            key_list = ["PROCATG","NCOMBINE", "EXPTIME", "TEXPTIME", "MJD-OBS", "MJD-END",
                        "PROG-ID", "OBSTECH", "FLUXCAL", "PROCSOFT", "TIMESYS", "SATLEVEL"]

        # We loop over frames reading values
        c = 1
        frame_keys = {}
        for file_name in self.parents_list:
            parent_fits_name = file_name.split("/")[-1]
            # we read the primary FITS header of the ancestor file i
            with fits.open(file_name) as hdul:
                hdr = hdul[0].header
                comments = hdr.comments

                for akey in key_list:
                    if akey in hdr:
                        avalue = hdr[akey]
                        acomment = comments[akey]
                    else:
                        avalue = "UNKNOWN"
                        acomment = "UNKNOWN"
                    if parent_fits_name not in frame_keys:
                        frame_keys[parent_fits_name]={}
                    frame_keys[parent_fits_name][akey] = (avalue,acomment)
                    logging.info("get_selected_keys_original:{}/{}  {}: {} = {} / {}".format(c, len(self.parents_list), parent_fits_name, akey, avalue, acomment))
            c += 1

        logging.info('get_selected_keys_original: Done.')

        # Phase3 keys are extracted from the ancestor files
        # some of them directly, but others need some further
        # processing. We create two dictionaries to contain them
        keyword = {}
        comment = {}

        # we then fill all the requested keywords with values from
        # the first frame.
        frame_list = list(frame_keys.keys())
        frame0 = frame_list[0]
        phase3_keys = list(frame_keys[frame0].keys())
        for akey in phase3_keys:
            keyword[akey] = frame_keys[frame0][akey][0]
            comment[akey] = frame_keys[frame0][akey][1]
            logging.info("get_selected_keys_original: {0} = {1} / {2}".format(akey, keyword[akey], comment[akey]))

        # some of the keys needs further processing
        # Some keys require looping over all frames:
        #
        # TEXPTIME
        # MJS-END
        # OBSIDi
        # PROG_ID, PROGIDi
        # so these will be overwritten with the proper values.
        #
        try:
            mjdobs = float('inf')
            if "MJD-OBS" in frame_keys[frame0]:
                for aframe in frame_keys.keys():
                    mjdobs = min(mjdobs, frame_keys[aframe]["MJD-OBS"][0])
                keyword["MJD-OBS"] = mjdobs
        except:
            logging.info("get_selected_keys_original: failed to get minimum MJD-OBS")

        # we set MJD-END to the MJD-END of the last frame
        try:
            mjdend = float('-inf')
            if "MJD-END" in frame_keys[frame0]:
                for aframe in frame_keys.keys():
                    mjdend = max(mjdend, frame_keys[aframe]["MJD-END"][0])
                keyword["MJD-END"] = mjdend
        except:
            logging.info("get_selected_keys_original: failed to get maximum MJD-END")

        # we set the total exposure time to the sume
        try:
            total_exptime = 0.0
            if "EXPTIME" in frame_keys[frame0]:
                for aframe in frame_keys.keys():
                    total_exptime += frame_keys[aframe]["EXPTIME"][0]
                keyword["TEXPTIME"] = total_exptime
        except:
            logging.info("get_selected_keys_original: failed to get TEXPTIME")

        logging.info("get_selected_keys_original: mjd-obs: {} mjd-end: {} delta: {} s texptime: {}".format(mjdobs, mjdend, (mjdend-mjdobs)*84600., total_exptime))

        # we set the satlevel to the avergage of the frames
        try:
            avg_satlevel = 0.0
            if "SATLEVEL" in frame_keys[frame0]:
                for aframe in frame_keys.keys():
                    avg_satlevel += frame_keys[aframe]["SATLEVEL"][0]
                keyword["SATLEVEL"] = avg_satlevel/len(frame_list)
        except:
            logging.info("get_selected_keys_original: failed to get average of SATLEVEL")

        # we check whether we have multiple OB.IDS
        #try:
        obid1 = []
        if "OBID1" in frame_keys[frame0]:
            for aframe in frame_keys.keys():
                obid1.append(frame_keys[aframe]["OBID1"][0])
            obid1_set = list(set(obid1))

        for i in range(len(obid1_set)):
            keyword[f"OBID{i+1}"] = obid1_set[i]
            comment[f"OBID{i+1}"] = frame_keys[frame0]["OBID1"][1] # assume same comment
        #except:
            #logging.info("get_selected_keys_original: failed to get list of OB IDs")

        # we check whether we have multiple PROG IDs
        # Note that ESO Phase3 is not consistent in
        # its treatment of OBID and PROGID...
        #
        # If there are multiple PROG_IDs we create new
        # keyword, so we also need the comment cards.
        #try:
        progid = []
        if "PROG_ID" in frame_keys[frame0]:
            for aframe in frame_keys.keys():
                progid.append(frame_keys[aframe]["PROG_ID"][0])
            progid_set = list(set(progid))
        print(progid_set)

        if len(progid_set) == 1:
            keyword["PROG_ID"] = progid_set[0]
        else:
            for i in range(len(progid_set)):
                keyword[f"PROGID{i+1}"] = progid_set[i]
                comment[f"PROGID{i+1}"] = frame_keys[frame0]["PROG_ID"][1]
            keyword["PROG_ID"] = "MULTI"
        #except:
        #   logging.info("get_selected_keys_original: failed to get list of PROG IDs")

        # we must change NCOMBINE as it comes with value 1
        ncombine = len(self.parents_list)
        keyword["NCOMBINE"] = ncombine
        comment["NCOMBINE"] = "Number of frames combined"

        # here we create the list of card tuples
        # note that here we add to a previous list
        mefpp_header_list = []
        for akey in keyword.keys():
            mefpp_header_list.append((akey, keyword[akey], comment[akey]))
            logging.info("{0} = {1} / {2}".format(akey, keyword[akey], comment[akey]))

        return keyword, comment, mefpp_header_list


    def get_mag_sky(self):
        """Calculate the surface brightness of sky in magnitudes per arcsec^2"""
        logging.info("get_mag_sky: surface brightness of sky in magnitudes per arcsec^2")

        # here we have mean_sky converted to erg/s/cm2, so we need to convert back to ADUs
        logging.info("get_mag_sky: self.mean_sky: {}".format(self.mean_sky))
        magsky = self.magzp - 2.5 * np.log10(self.mean_sky / self.plate_scale ** 2)
        logging.info("get_mag_sky: magsky: %6.3f mags/arcsec^2" % magsky)
        return magsky

    def get_std_dev_mag_sky(self):
        """Calculates the stad deviation of sky and returns it as an equivalent surface brightness."""
        logging.info("get_std_dev_mag_sky: standard deviation of sky in magnitudes per arcsec^2")
        std_dev = np.nanstd(self.data)
        logging.info("get_std_dev_mag_sky: std_dev: %.3e ADUs" % std_dev)

        # here we have sigma directly in ADUs
        mag_sky_std_dev = self.zphc - 2.5 * np.log10( std_dev / (self.plate_scale ** 2))
        logging.info("mag_sky_std_dev: %6.3f mags/arcsec^2" % mag_sky_std_dev)
        return mag_sky_std_dev

    def get_moon_from_frames(self):
        """Read original files used by Swarp to calculate lunar data."""
        logging.info("get_moon_from_frames: read files used by Swarp to read calculate lunar data.")

        orig_moon_fli = {}
        orig_moon_distance = {}
        orig_moon_alt = {}
        orig_moon_az = {}

        c = 1
        for image in self.parents_list:
            image_name = image.split("/")[-1]
            logging.info("get_moon_from_frames: Moon for %i/%i: %s" % (c, len(self.parents_list), image_name,))

            # get moon distance and FLI
            primary_header = fits.getheader(image)
            obs_time = Time(primary_header[self.instrument.dateobs_key], format='isot')
            ra = float(primary_header[self.instrument.ra_key]) * u.deg
            dec = float(primary_header[self.instrument.dec_key]) * u.deg
            tel_position = SkyCoord(ra=ra, dec=dec, frame='icrs')
            logging.info("get_moon_from_frames: DATE-OBS: %s" % self.instrument.dateobs_key)
            logging.info("get_moon_from_frames: obs_time: %s" % obs_time.value)
            logging.info("get_moon_from_frames: ra: %9.5f dec: %9.5f" % (ra.value, dec.value))

            # getting moon info  --- work a bit more to alos provide coordinates
            paranal = EarthLocation.of_site(self.observatory.lower())
            logging.info("get_moon_from_frames: observatory: {}".format(self.observatory.lower()))
            moon_coords = get_moon(obs_time, paranal)

            # moon distance to telescope pointing
            separation = moon_coords.separation(tel_position)
            orig_moon_distance[image_name] = separation.value

            # moon fractional illumination t time of observation
            fli = astroplan.moon_illumination(obs_time)  # fractional lunar illumination
            orig_moon_fli[image_name] = fli
            logging.info("get_moon_from_frames: moon distance: %4.1f -- FLI: %4.2f" % (separation.value, fli))

            moon_altaz = moon_coords.transform_to(AltAz(obstime=obs_time, location=paranal))
            orig_moon_alt[image_name] = moon_altaz.alt.value
            orig_moon_az[image_name] = moon_altaz.az.value
            logging.info("get_moon_from_frames: moon Alt: %3.2f Az: %2.2f" % (orig_moon_alt[image_name],
                                                                              orig_moon_az[image_name]))
            c += 1

        logging.info("get_moon_from_frames: Done.")
        return orig_moon_distance, orig_moon_fli, orig_moon_alt, orig_moon_az

    def get_updated_keywords(self):
        """Load dictionary with keywords to be writen to primary headers"""
        logging.info("get_keywords: getting the updated keywords")

        # we create PRO keywords to indicate frames that went into coadd.fits
        ancestor_frames_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d}".format(i + 1) for i in
                                range(len(self.orig_skies_phys))]
        sky_mean_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} SKYMEAN".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        sky_std_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} SKYSTD".format(i + 1) for i in
                        range(len(self.orig_skies_phys))]
        moon_fli_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} MOON FLI".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        moon_distance_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} MOON DISTANCE".format(i + 1) for i in
                              range(len(self.orig_skies_phys))]
        moon_alt_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} MOON ALT".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        moon_az_keys = ["HIERARCH ESO PYCAVI PRO ANCESTOR{:02d} MOON AZ".format(i + 1) for i in
                        range(len(self.orig_skies_phys))]

        # the keys are the keywords. The values the corresponding dictionary values.
        keyword = {}
        comment = {}
        i = 0
        zkeys = self.orig_skies_phys.keys()
        for akey in zkeys:
            logging.info("get_keywords: " + akey)
            logging.info("get_keywords: " + ancestor_frames_keys[i])

            # frames
            keyword[ancestor_frames_keys[i]] = akey
            comment[ancestor_frames_keys[i]] = "Input to Swarp %d" % (i + 1)
            logging.info("get_keywords: " + ancestor_frames_keys[i] + " = " + keyword[ancestor_frames_keys[i]] +
                         " / " + comment[ancestor_frames_keys[i]])

            keyword[sky_mean_keys[i]] = float("{:.5e}".format(self.orig_skies_phys[akey][0]))
            comment[sky_mean_keys[i]] = "Mean of sky %d" % (i + 1)
            logging.info("get_keywords: " + sky_mean_keys[i] + " = " + "%.3E" % (keyword[sky_mean_keys[i]]))

            keyword[sky_std_keys[i]] = float("{:.5e}".format(self.orig_skies_phys[akey][1]))
            comment[sky_std_keys[i]] = "Std dev of sky %d" % (i + 1)
            logging.info("get_keywords: " + sky_std_keys[i] + " = %.3E" % (keyword[sky_std_keys[i]]))

            keyword[moon_fli_keys[i]] = round(self.orig_moon_fli[akey],3)
            comment[moon_fli_keys[i]] = "Moon FLI of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_fli_keys[i] + " = {0}".format(keyword[moon_fli_keys[i]]))

            keyword[moon_distance_keys[i]] = round(self.orig_moon_distance[akey],3)
            comment[moon_distance_keys[i]] = "Moon distance of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_distance_keys[i] + " = {0}".format(keyword[moon_distance_keys[i]]))

            keyword[moon_alt_keys[i]] = round(self.orig_moon_alt[akey],3)
            comment[moon_alt_keys[i]] = "Moon Altitude of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_alt_keys[i] + " = {0}".format(keyword[moon_alt_keys[i]]))

            keyword[moon_az_keys[i]] = round(self.orig_moon_az[akey],3)
            comment[moon_az_keys[i]] = "Moon Azimuth of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_az_keys[i] + " = {0}".format(keyword[moon_az_keys[i]]))

            i += 1

        # here we deal with the fact that comments are transfered to COMMENT cards
        # by adding new keyword to hold comments. Note that we need to create
        # the list of keywords outside the for as the list will change as the
        # loop proceeds.
        key_list = list(keyword.keys())
        for akey in key_list:
            zcomment = comment[akey]
            name_str = akey+" INFO"
            if name_str not in keyword.keys():
                n_name = len(name_str.strip())
                nmax = 79 - n_name - 3
                if nmax > 0:
                    keyword[akey+" INFO"] = zcomment[0:nmax]
                else:
                    keyword[akey+" INFO"] = ""
                comment[akey] = ""
                comment[akey+" INFO"] = ""

        # we report several other values important to interpret data
        #
        cards = [["HIERARCH ESO PYCAVI PRO SKY UNITS", "erg/s/cm**2/arcsec**2", "Units of sky mean and std"],
                 ["HIERARCH ESO PYCAVI QC SKYMEAN", float("{:.5e}".format(self.mean_sky)), "Average sky mean and std"],
                 ["HIERARCH ESO PYCAVI QC SKYMEAN UNITS", "erg/s/cm**2/arcsec**2", "Units for QC SKYMEAN"],
                 ["HIERARCH ESO PYCAVI QC SKYSTD", float("{:.5e}".format(self.std_sky)), "Average sky std dev"],
                 ["HIERARCH ESO PYCAVI QC SKYSTD UNITS", "erg/s/cm**2/arcsec**2", "Units for QC SKYSTD"],
                 ["HIERARCH ESO PYCAVI QC ZPHC", round(self.zphc,3), "Zero point for data in e/s -- HC Plots"],
                 ["HIERARCH ESO PYCAVI QC BAND NAME", self.band, "Name of pass band"],
                 ["HIERARCH ESO PYCAVI QC BAND WIDTH", self.filter_width, "Width of pass band [Angstrom]"],
                 ["HIERARCH ESO PYCAVI QC BAND WAVELENGTH", self.plambda, "Pivot lambda of band [Angstrom]"],
                 ["HIERARCH ESO PYCAVI QC MAGSKY", round(self.magsky,3), "Sky brightness mags/arcsec^2"],
                 ["HIERARCH ESO PYCAVI QC DN2FLAM", float("{:.5e}".format(self.factor_dn_to_flambda)), "Conv. fact. mosaic DN to Flambda"],
                 ["HIERARCH ESO PYCAVI QC BUNIT", self.bunit, "Units of Data Numbers this frame"],
                 ["HIERARCH ESO PYCAVI QC PHO RAD", self.ap_radius, "Radius used aperture photometry"],
                 ["HIERARCH ESO PYCAVI QC PHO SKYR1", self.sky_annulus_r1, "Sky annulus r1 ap phot"],
                 ["HIERARCH ESO PYCAVI QC PHO SKYR2", self.sky_annulus_r2, "Sky annulus r2 ap phot"],
                 ["HIERARCH ESO PYCAVI QC PHO MAGMAX", self.mag_max, "max mag for photometric calibrators (faintest)"],
                 ["HIERARCH ESO PYCAVI QC PHO MAGMIN", self.mag_min, "min mag for photometric calibrators (brightest)"],
                 ["HIERARCH ESO PYCAVI QC PHO CALFILE", self.phot_cal_file.split('/')[-1], "cal file"],
                 ["HIERARCH ESO PYCAVI QC MAGZP", round(self.zp2,3), "ZP to AB magnitudes in BAND"],
                 ["HIERARCH ESO PYCAVI QC AVGAIRM", round(self.avg_airmass,3), "Average airmass of ancestor frames"],
                 ["HIERARCH ESO PYCAVI QC AVGGAIN", round(self.avg_gain), "Average gain of ancestor frames"]
                 ]

        # some phase3 cards
        for zcard in cards:
            zkey = zcard[0]
            zval = zcard[1]
            zcomment = zcard[2]
            keyword[zkey] = zval

            # fits writes comment field as a COMMENT file if card is too long
            # to avoid this I create a new card to contain only the comment
            name_str = zkey+" INFO"
            n_name = len(name_str.strip())
            nmax = 79 - n_name - 3
            if nmax > 0:
                keyword[zkey+" INFO"] = zcomment[0:nmax]
            else:
                keyword[zkey+" INFO"] = ""
            comment[zkey] = ""
            comment[zkey+" INFO"] = ""
            logging.info("get_keywords: " + zkey + " = " + "{0}".format(keyword[zkey]) + " / " + comment[zkey])

        # here we create the list of card tuples
        mefpp_header_list = []
        for akey in keyword.keys():
            mefpp_header_list.append((akey, keyword[akey], comment[akey]))

        # some phase3 cards
        phase3_cards = [["PSF_FWHM", round(self.fwhm_median,3), "Median FWHM  in arcsec"],
                        ["ELLIPTIC", round(self.ellipticity_median, 5), "Median ellipt. of sources 1 - b/a]"],
                        ["PSF_THET", round(self.theta_median, 1), "Median PA of sources in degrees"]]

        for zcard in phase3_cards:
            zkey = zcard[0]
            zval = zcard[1]
            zcomment = zcard[2]
            mefpp_header_list.append((zkey, zval, zcomment))

        return keyword, comment, mefpp_header_list

    def update_frame(self):
        """This procedure updates the values and headers of the original swarped image."""

        logging.info("update_frame: updating Data Numbers in self.data and adding headers to file.")

        with fits.open(self.frame, mode="update", output_verify="ignore") as hdul:
            hdr = hdul[0].header
            hdata = hdul[0].data

            # FSE CHECK: before writting new keywords we read the "HIERARCH ESO PYCAVI QC ADU2DN"
            #            keyword if it exists, we will need it at the end.
            #if "PYCAVI QC DN2FLAM" not in hdr.keys():
            if "BSCALE" not in hdr.keys():
                old_factor = 1.0
            else:
                old_factor = hdr["BSCALE"]

            logging.info('old_factor: {}'.format(old_factor))

            # FSE CHECK: we should use update better so as not to create duplicate entries.
            # we start with the selected headers that will go close to the beginning
            hdr.set("BUNIT", self.keyword["HIERARCH ESO PYCAVI QC BUNIT"],
                                   self.comment["HIERARCH ESO PYCAVI QC BUNIT"])
            hdr.set("MAGZP", round(self.keyword["HIERARCH ESO PYCAVI QC MAGZP"],3),
                                   self.comment["HIERARCH ESO PYCAVI QC MAGZP"])

            hdr.set("MAGSKY", round(self.keyword["HIERARCH ESO PYCAVI QC MAGSKY"],3),
                                   self.comment["HIERARCH ESO PYCAVI QC MAGSKY"])
            hdr.set("ABMAGLIM", round(self.magzp - 2.5*np.log10(5.0*self.keyword["HIERARCH ESO PYCAVI QC SKYSTD"]),3), "5-sigma magnitude limit")

            # the phase3 keys
            hdr.set("PHOTZP", round(self.keyword["HIERARCH ESO PYCAVI QC MAGZP"],3),
                              self.comment["HIERARCH ESO PYCAVI QC MAGZP"])
            hdr.set("PHOTSYS", "AB", "Photometric system AB or VEGA")

            #hdr["EXPTIME"] = (self.total_exptime, "Total exposure time (s)")
            # we continue with the full set of keywords near the end
            #        for zcard in cards:
            #zkey = zcard[0]
            #zval = zcard[1]
            #zcomment = zcard[2]
            cards_to_add = self.mefpp_header_cards
            for acard in cards_to_add:
                zkey = acard[0]
                zval = acard[1]
                zcomment = acard[2]
                hdr.set(zkey, zval, zcomment)

            # We add the phase3 keys
            # self.phase3_keys, self.phase3_comment, self.phase3_cards
            cards_to_add = self.phase3_cards
            for acard in cards_to_add:
                zkey = acard[0]
                zval = acard[1]
                zcomment = acard[2]
                hdr.set(zkey, zval, zcomment)

            # before final writing we remove empty comments
            comments_to_remove = [key for key, value in hdr.items() if key == 'COMMENT' and value.strip() == '']
            for comment in comments_to_remove:
                hdr.remove(comment)

            # we finally rewrite the data array
            #
            logging.info('update_frame: multipliying data by {}'.format(self.factor_dn_to_flambda))
            data_1d = hdul[0].section[10000:10100,10000:10100].flatten()
            print('update_frame: before update <data_1d>: {:.3E}'.format(np.nanmean(data_1d)))
            pycavi_tools.pycavi_qc_plot_hist(data_1d, 
                                             label='Pixel value distribution BEFORE applying factor_dn_to flambda.', 
                                             nbins=30, x_range="8-deciles", figname=None)
            factor = self.factor_dn_to_flambda/old_factor
            hdr.set("BSCALE", float("{:.8e}".format(factor)),
                                   comment="scale factor to apply to data")
            hdr.set("BZERO", 0.0,
                                   comment="numerical offset to apply to data")

            # we update the SATLEVEL accordingly
            if "SATLEVEL" in hdr.keys(): 
                satlevel = hdr["SATLEVEL"]*factor
                hdr.set("SATLEVEL",float("{:.5e}".format(satlevel)), "Saturation level in frame")
                hdr.set("MAGSATL",round(self.magzp - 2.5*np.log10(satlevel), 3), "Magnitude saturation level in frame")
            else:
                hdr.set("SATLEVEL", "UNKNOWN", "Saturation level in frame")
                hdr.set("MAGSATL", "UNKNOWN", "Magnitude saturation level in frame")

            # we finally deem the frame as calibrated
            hdr.set("FLUXCAL", "CALIBRATED")


            # here we reorder the headers
            # ChatGPT personal comm.
            #
            logging.info("update_frame: reordering headers...")

            # Separate non-HIERARCH and HIERARCH keywords along with their values and comments
            non_hierarch = []
            hierarch = []

            n_hierarch = 0
            n_nonhierarch = 0
            for key, value in hdr.items():
                comment = hdr.comments[key]  # Get the comment associated with the keyword
                if len(key) > 8:
                    n_hierarch+=1
                    hierarch.append((key, value, comment))
                else:
                    n_nonhierarch+=1
                    non_hierarch.append((key, value, comment))

            # Sort the HIERARCH keywords
            hierarch.sort(key=lambda x: x[0])

            # We create a new header
            new_header = fits.Header()

            # Now clear the current header
            #header_keys = list(hdr.keys())  # Get original header keys
            reserved_keys = ['COMMENT', 'HISTORY', 'END']
            #for key in header_keys:
                #if key not in reserved_keys:
                    #del hdr[key]

            # Add back the non-HIERARCH keywords first (with comments)
            for key, value, comment in non_hierarch:
                new_header[key] = (value, comment)

            # Add the sorted HIERARCH keywords at the end (with comments)
            for key, value, comment in hierarch:
                new_header[key] = (value, comment)

            # before final writing we remove empty comments
            comments_to_remove = [key for key, value in new_header.items() if key == 'COMMENT' and value.strip() == '']
            for comment in comments_to_remove:
                new_header.remove(comment)

            hdul[0].header = new_header
            hdul.flush()
            logging.info("update_frame: done, headers have been reordered successfully n_hierarch: {} n_nonhierarch: {}.".format(n_hierarch, n_nonhierarch))
            # --- END OF WITH STATEMENT ----

        # we check the data values
        x1 = self.instrument.img_sec_x1
        x2 = self.instrument.img_sec_x2
        y1 = self.instrument.img_sec_y1
        y2 = self.instrument.img_sec_y2
        with fits.open(self.frame, mode="readonly", output_verify="ignore") as hdul:
            hdr = hdul[0].header
            data_1d = hdul[0].section[x1:x2,y1:y2].flatten()
            print('update_frame: before update <data_1d>: {:.3E}'.format(np.nanmean(data_1d)))
            pycavi_tools.pycavi_qc_plot_hist(data_1d,
                                             label='Pixel value distribution AFTER applying factor_dn_to flambda.',
                                             nbins=30, x_range="8-deciles", figname=None)

        logging.info("update_frame: Image updated correctly")

# ------------------------------------------------------------------------------------------------------
# This calibration check scrip needs the ZPCal object above.
# It will probably become obsolete in production.
#
def plot_calibration_check_zpcal(query_catalogue, sex_catalogue_path, zp_cal):
    """
    Creates 5 different check plots from the SExtractor photometry on the swarped OmegaCam frame.
    * Calibrated magnitudes vs Catalogue magnitudes
    * Catalogue - Calibrated magnitudes vs Catalogue magnitudes.
    * Catalogue - Calibrated magnitudes vs Catalogue colour. This one also check the systematic increase of magnitude
        in function of the distance from the center R.
    * Catalogue - Calibrated magnitudes vs R [distance from center] color coded Catalogue - Calibrated
    * A check image of the field
    
    ##########
    parameters
    
    phot_catalogue : str
        The path to the clean photometric reference catalogue created during the calibration process of the frame.
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
    phot_catalogue = pd.read_csv(query_catalogue)
    sex_catalogue = np.loadtxt(sex_catalogue_path)

    # first load the ra, dec and magnitudes from both catalogues.
    ra_skm = phot_catalogue["raj2000"].to_numpy()
    de_skm = phot_catalogue["dej2000"].to_numpy()
    ra_sex = sex_catalogue[:, 1]
    de_sex = sex_catalogue[:, 2]

    # select bands accordingly to frame band
    # if band is NB_659, then construct the scatter plot using r-i and r-Ha
    # in rest of cases uses g-band and band-OCam
    # except in g case where we use band-r and band-OCam
    if zp_cal.band == "NB_659":
        mag_skm = phot_catalogue["r_SDSS"].to_numpy()
        mag_side_skm = phot_catalogue["i_SDSS"].to_numpy()
        mag_skm_band = "r_SDSS"
        mag_side_skm_band = "i_SDSS"
    else:
        mag_skm = phot_catalogue[zp_cal.band].to_numpy()
        mag_skm_band = zp_cal.band
        if zp_cal.band == "g_SDSS":
            mag_side_skm = phot_catalogue["r_SDSS"].to_numpy()
            mag_side_skm_band = "r_SDSS"
        else:
            mag_side_skm = phot_catalogue["g_SDSS"].to_numpy()
            mag_side_skm_band = "g_SDSS"

    logging.info("Reading sextractor catalogue {}".format(sex_catalogue_path))
    mag_sex = sex_catalogue[:, 5]

    # select only sextractor best sources (flags == 0 and class_star > 0.9)
    flags = sex_catalogue[:, 7]
    class_star = sex_catalogue[:, 10]

    # it was flags==0 and class_star >0.3
    sel_best_stars = (flags == 0) & (class_star > 0.3)
    ra_sex = ra_sex[sel_best_stars]
    de_sex = de_sex[sel_best_stars]
    mag_sex = mag_sex[sel_best_stars]
    logging.info("number of valid entries in sex catalogue: {}".format(len(mag_sex)))

    # cross-match the skm and sex catalogues
    c_skm = SkyCoord(ra=ra_skm * u.degree, dec=de_skm * u.degree)
    c_sex = SkyCoord(ra=ra_sex * u.degree, dec=de_sex * u.degree)
    idx, d2d, _ = c_skm.match_to_catalog_sky(c_sex)

    max_sep = 1.0 * u.arcsec
    sep_constraint = d2d < max_sep

    # match the ra and dec positions
    ra_skm = ra_skm[sep_constraint]
    de_skm = de_skm[sep_constraint]
    ra_sex = ra_sex[idx[sep_constraint]]
    de_sex = de_sex[idx[sep_constraint]]

    # now we have matched the catalogues we can compare mag by mag
    mag_skm = mag_skm[sep_constraint]
    mag_side_skm = mag_side_skm[sep_constraint]
    mag_sex = mag_sex[idx[sep_constraint]]

    # we paint with the distance to the center
    rad_dist = np.sqrt((ra_skm - zp_cal.crval1)**2 + (de_skm - zp_cal.crval2)**2)

    data = zp_cal.data
    wcs = zp_cal.wcs

    mag_max = zp_cal.mag_max
    mag_min = zp_cal.mag_min

    # we plot the ocam vs skymapper relation
    fig = plt.figure(figsize=(15.7, 12.1), dpi=120)

    gs = gridspec.GridSpec(nrows=4, ncols=5, wspace=0.0)  # width_ratios=[1,1,1,1,1])
    ax1 = fig.add_subplot(gs[:-2, :-3])
    ax2 = fig.add_subplot(gs[-2, :-3], sharex=ax1)
    ax3 = fig.add_subplot(gs[:-1, -3:])
    ax4 = fig.add_subplot(gs[-1, :-3])
    ax5 = fig.add_subplot(gs[-1, -3:])
    

    # skm versus sextractor
    ax1.scatter(mag_skm, mag_sex,  color='black', s=2)
    ax1.set_xlim(8.0, mag_max+1.0)
    ax1.set_ylim(8.0, mag_max+1.0)
    ax1.set_xlabel("{} Catalogue".format(zp_cal.band))
    ax1.set_ylabel("{} OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax1.set_xlabel("r_SDSS Catalogue".format(zp_cal.band))

    # delta zp vs mag
    sigma_res = np.nanstd(mag_sex - mag_skm)
    ax2.scatter(mag_skm, mag_skm - mag_sex,  color='black', s=2)
    ax2.set_ylim(-10.0*sigma_res, 10.0*sigma_res)
    ax2.axhline(0.0, ls=':')
    ax2.axvline(mag_min, ls=':')
    ax2.axvline(mag_max, ls=':')
    ax2.set_xlabel("{} Catalogue".format(zp_cal.band))
    ax2.set_ylabel("{}\nCatalogue - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax2.set_ylabel("{} - {}\nCatalogue - OCam".format(mag_skm_band, zp_cal.band))

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
    select = (mag_skm > mag_min) & (mag_skm < mag_max)
    #
    plot4 = ax4.scatter(color[select & sigma_clip], mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip],  
                        c=rad_dist[select & sigma_clip], cmap="viridis", s=1)
    p4 = plt.colorbar(plot4, ax=ax4, label="R [deg]")
    ax4.axhline(0.0, ls=':')
    ax4.set_xlim(np.amin(color[select & sigma_clip]), np.amax(color[select & sigma_clip]))
    ax4.set_ylim(np.amin(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]), 
                 np.amax(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]))
    ax4.set_xlabel("{} - {} Catalogue".format(mag_side_skm_band, mag_skm_band))
    if zp_cal.band == "NB_659" or zp_cal.band == "g_SDSS":
        ax4.set_xlabel("{} - {} Catalogue".format(mag_skm_band, mag_side_skm_band))
    ax4.set_ylabel("{}\nCatalogue - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax4.set_ylabel("{} - {}\nCatalogue - OCam".format(mag_skm_band, zp_cal.band))

    # dmag versus radius
    plot5 = ax5.scatter(rad_dist[select & sigma_clip], mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip],  
                        c=color[select & sigma_clip], cmap="viridis", s=1)
    p5 = plt.colorbar(plot5, ax=ax5, label="{} - {} Skymapper".format(mag_side_skm_band, mag_skm_band))
    ax5.axhline(0.0, ls=':')
    ax5.set_xlim(np.amin(rad_dist[select & sigma_clip]), np.amax(rad_dist[select & sigma_clip]))
    ax5.set_ylim(np.amin(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]), 
                 np.amax(mag_skm[select & sigma_clip] - mag_sex[select & sigma_clip]))
    ax5.set_xlabel("R [deg]")
    if zp_cal.band == "NB_659" or zp_cal.band == "g_SDSS":
        ax5.set_ylabel("{} - {} Catalogue".format(mag_skm_band, mag_side_skm_band))
    else:
        ax5.set_ylabel("{}\nCatalogue - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax5.set_ylabel("{} - {}\nCatalogue - OCam".format(mag_skm_band, zp_cal.band))

    plt.tight_layout()
    logging.info("check plots created. Saving figure...")
    figname = zp_cal.calibrationdir + "/" + zp_cal.frame[:-5] + "_calibration_check.png"
    plt.savefig(figname)
 

# This checking script extracts all information from the headers of the frame
# and does apperture photometry the same way as ZPCal but it does not calculate
# zero points. It just a check from info in the frame itself.
#
def plot_calibration_check_frame(image_path, calibration_dir, swarp_dir):
    """
    Created 5 different check plots from the SExtractor photometry on the swarped OmegaCam frame.
    * Calibrated magnitudes vs Catalogue magnitudes
    * Catalogue - Calibrated magnitudes vs Catalogue magnitudes.
    * Catalogue - Calibrated magnitudes vs Catalogue colour. This one also check the systematic increase of magnitude
        in function of the distance from the center R.
    * Catalogue - Calibrated magnitudes vs R [distance from center] color coded Catalogue - Calibrated
    * A check image of the field
    
    ##########
    parameters
    
    phot_catalogue : str
        The path to the clean photometric reference catalogue created during the calibration process of the frame.
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

    logging.info("pycavi qc phot: creating check plots")

    # We first read the image whose photometry will be checked
    logging.info("pycavi qc phot: reading image {}".format(image_path.split('/')[-1]))
    zp_data, zp_hdu = fits.getdata(image_path, header=True)
    #print(list(zp_hdu.keys()))

    # we load some data from the image to be checked
    keys_to_extract = {'band': "ESO PYCAVI QC BAND NAME",
                       'crval1': "CRVAL1",
                       'crval2': "CRVAL2",
                       'mag_max': "ESO PYCAVI QC PHO MAGMAX",
                       'mag_min': "ESO PYCAVI QC PHO MAGMIN",
                       'phot_rad': "ESO PYCAVI QC PHO RAD",
                       'phot_skyr1': "ESO PYCAVI QC PHO SKYR1",
                       'phot_skyr2': "ESO PYCAVI QC PHO SKYR2",
                       'phot_calfile': "ESO PYCAVI QC PHO CALFILE",
                       'magzp': "MAGZP"}

    input_dict = {}
    for akey, avalue in keys_to_extract.items():
        if avalue in list(zp_hdu.keys()):
            input_dict[akey]=zp_hdu[avalue]
        else:
            logging.info("pycavi qc phot: **** missing key {} in headers".format(avalue))
            
    # we create a class to hold all these data
    class ZPcal:
        def __init__(self, input_dict, zdata, zhdu):
            self.band = input_dict['band']
            self.crval1 = input_dict['crval1']
            self.crval2 = input_dict['crval2']
            self.mag_max = input_dict['mag_max']
            self.mag_min = input_dict['mag_min']
            self.phot_rad = input_dict['phot_rad']
            self.phot_skyr1 = input_dict['phot_skyr1']
            self.phot_skyr2 = input_dict['phot_skyr2']
            self.phot_calfile = input_dict['phot_calfile']
            self.magzp = input_dict['magzp']
            self.data = zdata
            self.wcs = wcs = WCS(zhdu)
            self.aperture = None
            self.sky_annulus = None
        
    zp_cal = ZPcal(input_dict, zp_data, zp_hdu)

    query_catalogue_path = calibration_dir+'/'+zp_cal.phot_calfile
    logging.info("pycavi qc phot: reading catalogue used for query {}".format(query_catalogue_path.split('/')[-1]))
    phot_catalogue = pd.read_csv(query_catalogue_path)

    # first load the ra, dec and magnitudes from both catalogues.
    ra_std = phot_catalogue["raj2000"].to_numpy() * u.deg
    de_std = phot_catalogue["dej2000"].to_numpy() * u.deg

    # select bands accordingly to frame band
    # if band is NB_659, then construct the scatter plot using r-i and r-Ha
    # in rest of cases uses g-band and band-OCam
    # except in g case where we use band-r and band-OCam
    if zp_cal.band == "NB_659":
        mag_std = phot_catalogue["r_SDSS"].to_numpy()
        mag_side_std = phot_catalogue["i_SDSS"].to_numpy()
        mag_std_band = "r_SDSS"
        mag_side_std_band = "i_SDSS"
    else:
        mag_std = phot_catalogue[zp_cal.band].to_numpy()
        mag_std_band = zp_cal.band
        if zp_cal.band == "g_SDSS":
            mag_side_std = phot_catalogue["r_SDSS"].to_numpy()
            mag_side_std_band = "r_SDSS"
        else:
            mag_side_std = phot_catalogue["g_SDSS"].to_numpy()
            mag_side_std_band = "g_SDSS"
    logging.info("pycavi qc phot: number of valid entries in calibrator catalogue: {}".format(len(mag_std)))
    
    # we read the sextractor catalogue created by previous notebook.
    # After testing we will change to do photometry with do_phot in
    # the positions of the query catalogue.
    #
    #sex_catalogue_path = image_path[:-5]+'.cat'
    #logging.info("pycavi qc pho: reading sextractor catalogue {}".format(sex_catalogue_path))
    #sex_catalogue = np.loadtxt(sex_catalogue_path)
    #mag_sex = sex_catalogue[:, 5]
    #ra_sex = sex_catalogue[:, 1]
    #de_sex = sex_catalogue[:, 2]

    # select only sextractor best sources (flags == 0 and class_star > 0.9)
    #flags = sex_catalogue[:, 7]
    #class_star = sex_catalogue[:, 10]

    # it was flags==0 and class_star >0.3
    #sel_best_stars = (flags == 0) & (class_star > 0.3)
    #ra_sex = ra_sex[sel_best_stars]
    #de_sex = de_sex[sel_best_stars]
    #mag_sex = mag_sex[sel_best_stars]
    #logging.info("number of valid entries in sex catalogue: {}".format(len(mag_sex)))
    ################################################################################################

    # Photometry is done directly on the frame
    ra_frm = copy.deepcopy(ra_std)
    de_frm = copy.deepcopy(de_std)
    logging.info("pycavi qc phot:  creating aperture object")
    positions = SkyCoord(ra=ra_frm, dec=de_frm, frame="icrs")
    zp_cal.aperture = SkyCircularAperture(positions, r=zp_cal.phot_rad * u.arcsec)
    zp_cal.sky_annulus = SkyCircularAnnulus(positions, zp_cal.phot_skyr1 * u.arcsec,
                                                zp_cal.phot_skyr2 * u.arcsec)

    logging.info("pycavi qc phot: doing aperture photometry on frame.")
    phot_table = aperture_photometry(zp_cal.data, zp_cal.aperture, wcs=zp_cal.wcs, method="exact")
    for col in phot_table.colnames:
        if col != "id" and col != "sky_center":
            phot_table[col].info.format = "%.2f"  # for consistent table output
            
    phot_disk_area = zp_cal.aperture.to_pixel(zp_cal.wcs).area
    logging.info("pycavi qc phot: phot_disk_area in pixels: {}".format(phot_disk_area))


    logging.info("pycavi qc phot: estimating backgrounds.")
    annulus_masks = zp_cal.sky_annulus.to_pixel(zp_cal.wcs).to_mask(method='center')
    logging.info("pycavi qc phot: number of objects: {}".format(len(annulus_masks)))
    bkg_median = np.empty(len(annulus_masks))
    bkg_median[:] = np.nan
    for i in range(len(annulus_masks)):
        mask = annulus_masks[i]
        annulus_data = mask.multiply(zp_cal.data)
        if annulus_data is not None:  # if we have data we use it
            annulus_data_1d = annulus_data[mask.data > -0]
            mean_sigclip, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d, sigma_lower=3.0, sigma_upper=3.0)
            bkg_median[i] = median_sigclip

    # with the bkg median value, we can subtract from the circular aperture
    # Note that the aper_sum_bkgsub array will have invalid entries in the
    # form of nan and 0.0 values.
    logging.info("pycavi qc phot: subtracting backgrounds.")
    aper_bkg = bkg_median * phot_disk_area
    aper_sum_bkgsub = np.array(phot_table["aperture_sum"] - aper_bkg)
    raw_mags = np.zeros_like(aper_sum_bkgsub)
    # FSE CHECK: is setting to 99.0 a good flag of a bad value?
    raw_mags[aper_sum_bkgsub > 0] = zp_cal.magzp - 2.5 * np.log10(aper_sum_bkgsub[aper_sum_bkgsub > 0])
    raw_mags[aper_sum_bkgsub <= 0] = 99.0
    mag_sex = np.around(raw_mags, 4)
    good_sel = (raw_mags > 0) & (raw_mags < 20)
    logging.info("pycavi qc phot: number of good values {}".format(good_sel.sum()))
    mag_std = mag_std[good_sel]
    mag_side_std = mag_side_std[good_sel]
    mag_sex = mag_sex[good_sel]

    #####################################################################################################
    # cross-match the std and frame catalogues
    #c_std = SkyCoord(ra=ra_std[good_sel], dec=de_std[good_sel])
    #c_frm = SkyCoord(ra=ra_frm[good_sel], dec=de_frm[good_sel])
    #idx, d2d, _ = c_std.match_to_catalog_sky(c_frm)

    #max_sep = 1.0 * u.arcsec
    #sep_constraint = d2d < max_sep

    # match the ra and dec positions
    #ra_std = ra_std[sep_constraint]
    #de_std = de_std[sep_constraint]
    #ra_frm = ra_frm[idx[sep_constraint]]
    #de_frm = de_frm[idx[sep_constraint]]

    # now we have matched the catalogues we can compare mag by mag
    #mag_std = mag_std[sep_constraint]
    #mag_side_std = mag_side_std[sep_constraint]
    #mag_sex = mag_sex[idx[sep_constraint]]

    # we paint with the distance to the center
    rad_dist = np.sqrt((ra_std - zp_cal.crval1 * u.deg)**2 + (de_std - zp_cal.crval2 * u.deg)**2)[good_sel]

    data = zp_cal.data
    wcs = zp_cal.wcs

    mag_max = zp_cal.mag_max
    mag_min = zp_cal.mag_min

    # we plot the ocam vs skymapper relation
    fig = plt.figure(figsize=(15.7, 12.1), dpi=120)

    gs = gridspec.GridSpec(nrows=4, ncols=5, wspace=0.0)  # width_ratios=[1,1,1,1,1])
    ax1 = fig.add_subplot(gs[:-2, :-3])
    ax2 = fig.add_subplot(gs[-2, :-3], sharex=ax1)
    ax3 = fig.add_subplot(gs[:-1, -3:])
    ax4 = fig.add_subplot(gs[-1, :-3])
    ax5 = fig.add_subplot(gs[-1, -3:])
    

    # std versus sextractor
    ax1.scatter(mag_std, mag_sex,  color='black', s=2)
    ax1.set_xlim(8.0, mag_max+1.0)
    ax1.set_ylim(8.0, mag_max+1.0)
    ax1.set_xlabel("{} Catalogue".format(zp_cal.band))
    ax1.set_ylabel("{} OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax1.set_xlabel("r_SDSS Catalogue".format(zp_cal.band))

    # delta zp vs mag
    sigma_res = np.nanstd(mag_sex - mag_std)
    ax2.scatter(mag_std, mag_std - mag_sex,  color='black', s=2)
    ax2.set_ylim(-10.0*sigma_res, 10.0*sigma_res)
    ax2.axhline(0.0, ls=':')
    ax2.axvline(mag_min, ls=':')
    ax2.axvline(mag_max, ls=':')
    ax2.set_xlabel("{} Catalogue".format(zp_cal.band))
    ax2.set_ylabel("{}\nCatalogue - Frame".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax2.set_ylabel("{} - {}\nCatalogue - Frame".format(mag_std_band, zp_cal.band))

    norm = simple_norm(data, 'sqrt', percent=99)
    ax3.imshow(data, norm=norm)
    #zp_cal.aperture.to_pixel(wcs).plot(color='white', lw=1)

    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    # delta zp vs color
    color = mag_side_std - mag_std
    sigma_clip = (color >= np.nanquantile(color, 0.005)) & (color <= np.nanquantile(color, 0.995))
    
    # if band is g_sdss, invert the color to have g-r instead of r-g. Same for NB659 to have r-i instead of i-r
    if zp_cal.band == "g_SDSS" or zp_cal.band == "NB_659":
        color *= -1
    select = (mag_std > mag_min) & (mag_std < mag_max)
    #
    plot4 = ax4.scatter(color[select & sigma_clip], mag_std[select & sigma_clip] - mag_sex[select & sigma_clip],  
                        c=rad_dist[select & sigma_clip].value, cmap="viridis", s=1)
    p4 = plt.colorbar(plot4, ax=ax4, label="R [deg]")
    ax4.axhline(0.0, ls=':')
    #ymin = np.amin(mag_std[select & sigma_clip] - mag_sex[select & sigma_clip]
    #ymax = np.amax(mag_std[select & sigma_clip] - mag_sex[select & sigma_clip]
    ymin = -0.5
    ymax = +0.5
    ax4.set_xlim(np.amin(color[select & sigma_clip]), np.amax(color[select & sigma_clip]))
    ax4.set_ylim((ymin, ymax))
    ax4.set_xlabel("{} - {} Catalogue".format(mag_side_std_band, mag_std_band))
    if zp_cal.band == "NB_659" or zp_cal.band == "g_SDSS":
        ax4.set_xlabel("{} - {} Catalogue".format(mag_std_band, mag_side_std_band))
    ax4.set_ylabel("{}\nCatalogue - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax4.set_ylabel("{} - {}\nCatalogue - OCam".format(mag_std_band, zp_cal.band))

    # dmag versus radius
    plot5 = ax5.scatter(rad_dist[select & sigma_clip], mag_std[select & sigma_clip] - mag_sex[select & sigma_clip],  
                        c=color[select & sigma_clip], cmap="viridis", s=1)
    p5 = plt.colorbar(plot5, ax=ax5, label="{} - {} Skymapper".format(mag_side_std_band, mag_std_band))
    ax5.axhline(0.0, ls=':')
    ax5.set_xlim(np.amin(rad_dist[select & sigma_clip].value), np.amax(rad_dist[select & sigma_clip].value))
    ax5.set_ylim(ymin, ymax)
    ax5.set_xlabel("R [deg]")
    if zp_cal.band == "NB_659" or zp_cal.band == "g_SDSS":
        ax5.set_ylabel("{} - {} Catalogue".format(mag_std_band, mag_side_std_band))
    else:
        ax5.set_ylabel("{}\nCatalogue - OCam".format(zp_cal.band))
    if zp_cal.band == "NB_659":
        ax5.set_ylabel("{} - {}\nCatalogue - OCam".format(mag_std_band, zp_cal.band))

    plt.tight_layout()
    logging.info("check plots created. Saving figure...")
    figname = image_path[:-5] + "_qc_photcal_check.png"
    plt.savefig(figname)

def get_key_from_header(hdu, keys):
    """
    returns the value stored in the frame hdu headers
        
    Parameters
    ----------
    keys: str or list
        the key, a single value if a str is passed, or a list of keys to select from the headers.
     """
    if type(keys) == str:
        return hdu[keys]
    elif type(keys) == list:
        returned_values = []
        for key in keys:
            returned_values.append(hdu[key])
        return returned_values
