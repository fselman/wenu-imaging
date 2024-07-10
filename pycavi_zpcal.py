import os
import copy
import logging
import astroplan
import numpy as np
import pandas as pd
import urllib.request
from astropy.wcs import WCS
from astropy.io import fits
from astropy.time import Time
from astropy import units as u
from scipy.optimize import minimize
from astropy.stats import sigma_clipped_stats
from astropy.coordinates import SkyCoord, get_moon, EarthLocation, AltAz
from photutils import SkyCircularAperture, SkyCircularAnnulus, aperture_photometry
from astroquery.sdss import SDSS
import pycavi_tools

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
            self.band = paycavi_tools.keys_from_header(self.hdu, "FILTER").strip()

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
        logging.info("do_phot: creating aperture object")
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

        # the keys are the keywords. The values the corresponding dictionary values.
        keyword = {}
        comment = {}

        # we create PRO keywords to indicate frames that went into coadd.fits
        ancestor_frames_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d}".format(i + 1) for i in
                                range(len(self.orig_skies_phys))]
        sky_mean_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} SKYMEAN".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        sky_std_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} SKYSTD".format(i + 1) for i in
                        range(len(self.orig_skies_phys))]
        moon_fli_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} MOON FLI".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        moon_distance_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} MOON DISTANCE".format(i + 1) for i in
                              range(len(self.orig_skies_phys))]
        moon_alt_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} MOON ALT".format(i + 1) for i in
                         range(len(self.orig_skies_phys))]
        moon_az_keys = ["HIERARCH MEFPP PRO ANCESTOR{:02d} MOON AZ".format(i + 1) for i in
                        range(len(self.orig_skies_phys))]

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

            keyword[sky_mean_keys[i]] = self.orig_skies_phys[akey][0]
            comment[sky_mean_keys[i]] = "Mean of sky %d" % (i + 1)
            logging.info("get_keywords: " + sky_mean_keys[i] + " = " + "%.3E" % (keyword[sky_mean_keys[i]]))

            keyword[sky_std_keys[i]] = self.orig_skies_phys[akey][1]
            comment[sky_std_keys[i]] = "Std dev of sky %d" % (i + 1)
            logging.info("get_keywords: " + sky_std_keys[i] + " = %.3E" % (keyword[sky_std_keys[i]]))

            keyword[moon_fli_keys[i]] = self.orig_moon_fli[akey]
            comment[moon_fli_keys[i]] = "Moon FLI of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_fli_keys[i] + " = {0}".format(keyword[moon_fli_keys[i]]))

            keyword[moon_distance_keys[i]] = self.orig_moon_distance[akey]
            comment[moon_distance_keys[i]] = "Moon distance of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_distance_keys[i] + " = {0}".format(keyword[moon_distance_keys[i]]))

            keyword[moon_alt_keys[i]] = self.orig_moon_alt[akey]
            comment[moon_alt_keys[i]] = "Moon Altitude of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_alt_keys[i] + " = {0}".format(keyword[moon_alt_keys[i]]))

            keyword[moon_az_keys[i]] = self.orig_moon_az[akey]
            comment[moon_az_keys[i]] = "Moon Azimuth of frame %d" % (i + 1)
            logging.info("get_keywords: " + moon_az_keys[i] + " = {0}".format(keyword[moon_az_keys[i]]))

            i += 1

        # we report several other values important to interpret data
        #
        cards = [["HIERARCH MEFPP PRO SKY UNITS", "10**(-15)*erg/s/cm**2/arcsec**2", "Units of sky mean and std"],
                 ["HIERARCH MEFPP QC SKYMEAN", self.mean_sky, "Average sky mean and std"],
                 ["HIERARCH MEFPP QC SKYMEAN UNITS", "10**(-15)*erg/s/cm**2/arcsec**2", "Units for QC SKYMEAN"],
                 ["HIERARCH MEFPP QC SKYSTD", self.std_sky, "Average sky std dev"],
                 ["HIERARCH MEFPP QC SKYSTD UNITS", "10**(-15)*erg/s/cm**2/arcsec**2", "Units for QC SKYSTD"],
                 ["HIERARCH MEFPP QC ZPHC", self.zphc, "Zero point for data in e/s -- HC Plots"],
                 ["HIERARCH MEFPP QC BAND NAME", self.band, "Name of pass band"],
                 ["HIERARCH MEFPP QC BAND WIDTH", self.filter_width, "Width of pass band [Angstrom]"],
                 ["HIERARCH MEFPP QC BAND WAVELENGTH", self.plambda, "Pivot lambda of band [Angstrom]"],
                 ["HIERARCH MEFPP QC MAGSKY", self.magsky, "Sky brightness mags/arcsec^2"],
                 ["HIERARCH MEFPP QC DN2FLAM", self.factor_dn_to_flambda, "Conv. fact. mosaic DN to Flambda"],
                 ["HIERARCH MEFPP QC BUNIT", self.bunit, "Units of Data Numbers this frame"],
                 ["HIERARCH MEFPP QC PHO RAD", self.ap_radius, "Radius used aperture photometry"],
                 ["HIERARCH MEFPP QC PHO SKYR1", self.sky_annulus_r1, "Sky annulus r1 ap phot"],
                 ["HIERARCH MEFPP QC PHO SKYR2", self.sky_annulus_r2, "Sky annulus r2 ap phot"],
                 ["HIERARCH MEFPP QC PHO MAGMAX", self.mag_max, "max mag for photometric calibrators (faintest)"],
                 ["HIERARCH MEFPP QC PHO MAGMIN", self.mag_min, "min mag for photometric calibrators (brightest)"],
                 ["HIERARCH MEFPP QC PHO CALFILE", self.phot_cal_file.split('/')[-1], "cal file"],
                 ["HIERARCH MEFPP QC MAGZP", self.zp2, "ZP to AB magnitudes in BAND"],
                 ["HIERARCH MEFPP QC AVGAIRM", self.avg_airmass, "Average airmass of ancestor frames"],
                 ["HIERARCH MEFPP QC AVGGAIN", self.avg_gain, "Average gain of ancestor frames"]
                 ]

        for zcard in cards:
            zkey = zcard[0]
            zval = zcard[1]
            zcomment = zcard[2]
            keyword[zkey] = zval
            comment[zkey] = zcomment
            logging.info("get_keywords: " + zkey + " = " + "{0}".format(keyword[zkey]) + " / " + comment[zkey])

        # here we create the list of card tuples
        mefpp_header_list = []
        for akey in keyword.keys():
            mefpp_header_list.append((akey, keyword[akey], comment[akey]))

        return keyword, comment, mefpp_header_list

    def update_frame(self):
        """This procedure updates the values and headers of the original swarped image."""

        logging.info("update_frame: updating Data Numbers in self.data and adding headers to file.")

        with fits.open(self.frame, mode="update", output_verify="ignore") as hdul:
            hdr = hdul[0].header
            hdata = hdul[0].data

            # FSE CHECK: before writting new keywords we read the "HIERARCH MEFPP QC ADU2DN"
            #            keyword if it exists, we will need it at the end.
            if "MEFPP QC DN2FLAM" not in hdr.keys():
                old_factor = 1.0
            else:
                old_factor = hdr["MEFPP QC DN2FLAM"]

            logging.info('old_factor: {}'.format(old_factor))

            # FSE CHECK: we should use update better so as not to create duplicate entries.
            # we start with the selected headers that will go close to the beginning
            hdr.update(BUNIT=self.keyword["HIERARCH MEFPP QC BUNIT"],
                                   comment=self.comment["HIERARCH MEFPP QC BUNIT"])
            hdr.update(MAGZP=self.keyword["HIERARCH MEFPP QC MAGZP"],
                                   comment=self.comment["HIERARCH MEFPP QC MAGZP"])

            hdr.update(MAGSKY=self.keyword["HIERARCH MEFPP QC MAGSKY"],
                                   comment=self.comment["HIERARCH MEFPP QC MAGSKY"])

            hdr.update({"HIERARCH MEFPP TOTEXP": self.total_exptime}, 
                                   comment="Total exposure time (s)")
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
                hdr.update({zkey: zval}, comment=zcomment)

            # we finally rewrite the data array
            #
            logging.info('update_frame: multipliying data by {}'.format(self.factor_dn_to_flambda))
            data_1d = hdul[0].section[10000:10100,10000:10100].flatten()
            print('update_frame: before update <data_1d>: {:.3E}'.format(np.nanmean(data_1d)))
            pycavi_tools.pycavi_qc_plot_hist(data_1d, 
                                             label='Pixel value distribution BEFORE applying factor_dn_to flambda.', 
                                             nbins=30, x_range="8-deciles", figname=None)
            factor = self.factor_dn_to_flambda/old_factor
            hdr.update(BSCALE=factor,
                                   comment="scale factor to apply to data")
            hdr.update(BZERO=0.0,
                                   comment="num,erical offset to apply to data")
            hdul.flush()

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
