# Library with class definition for the mefpp_zp_skymapper.py motebook.
#
# This library is fully functional as of 2020-05-14.
#
# As it is it works only for bands
#
#         - r_SDSS
#         - NB_659
#
# -------------------------------------------------------------------
# TO DO
#
# - Add bands u_SDSS, g_SDSS, and i_SDSS
# - Add colour equation in zp determination
# - Add a different photometry catalogue for 
#   band B_JOHN, V_JHON
# - Linearity correction
# - Correction for field dependence of zp
# -------------------------------------------------------------------

#system utilities
import os
import glob
import copy
from textwrap import wrap

# to logg messages and debug
import logging

logging.basicConfig(
#    filename="test.log",
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
    )

# modules to query skymapper 
import urllib.request

# plotting module
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
from matplotlib.colors import LogNorm

# numeric and table data modules
import numpy as np
from numpy import errstate,isneginf,array
from scipy.optimize import fsolve

# dataframes module
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# module to read Fits files
from astropy.io import fits

# image visualization and World Coordinate System modules
from astropy.visualization import simple_norm
from astropy.wcs import WCS

# units and coordinate handling
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, get_moon, EarthLocation, AltAz
from astropy.stats import sigma_clipped_stats

# Moon quantities
import astroplan

# Apperture photometry module
from photutils import SkyCircularAperture, aperture_photometry, SkyCircularAnnulus

def getKeyListVal(filename, keys):
    keys_dict = {}
    with fits.open(filename) as hdu_list:
        primary_header = hdu_list[0].header
        for key in keys:
            keys_dict[key] = primary_header[key]
        return keys_dict


# Only skymapper defined and only for r_SDSS and NB_659
# but it should be easily extensible
#
class ZPCalibration:    
    """A class to contain a pandas dataframe with the data
    to calibrate frame and the zero points needed for the calibration."""
    def __init__(self, frame, calibrator, mlim, mag_min, mag_max, dmag_filter, ap_radius, ap_sky_r1, ap_sky_r2):
        self.frame = frame

        self.basedir = os.path.dirname(frame)
        logging.info('ZPCalibration: basedir: %s'%self.basedir)
        
        # open image and read
        logging.info('ZPCalibration: init: reading frame')
        self.data, self.hdu = fits.getdata(self.frame, header=True)
        #print(self.hdu.tostring(sep='\n'))
        
        # get wcs
        logging.info('ZPCalibration: init: loading wcs info from frame')
        self.wcs = WCS(self.frame)
        
        # plate scale
        cdi_j = np.array(list(getKeyListVal(self.frame, ['CD1_1', 'CD1_2', 'CD2_1', 'CD2_2']).values()))
        self.sx = np.sqrt(cdi_j[0]**2+cdi_j[1]**2)*3600.0
        self.sy = np.sqrt(cdi_j[2]**2+cdi_j[3]**2)*3600.0
        self.plate_scale = (self.sx+self.sy)/2.0 # plate scale in arcseconds
        logging.info('ZPCalibration: plate_scale: %6.3f (sx: %6.3f - sy: %6.3f) arcsec/pix'%(self.plate_scale, self.sx, self.sy))

        
        # get average gain from first frame used by Swarp
        self.avg_gain = self.getAvgGainFromFrame()

        # some variables not yet determined
        self.aperture = None
        self.convFactor_ADU_Flambda = None
        
        ## orig sky level pos
        self.orig_exptime = self.getAvgExpTimeFromFrames()
        self.avg_exptime = np.mean(list(self.orig_exptime.values())) # we keep visible list nature
        # orig sky level pos
        
        # information needed to do the photometric calibration
        #
        self.calibrator = calibrator # Name of calibrator, for now only skymapper
        self.mlim = mlim # faintest magnitude to download from catalogue
        self.mag_min =  mag_min # brightest magnitude to do calibartipn
        self.mag_max = mag_max # fainter magnitude to do calibration
        self.dmag_filter = dmag_filter # width around magnitude line to do sigma clipping
        
        # we get observing passband from headers
        #
        self.band = getKeyListVal(frame, ['FILTER'])['FILTER'].strip() 
        
        # coordinates of the center of the field
        self.crval1 = float(getKeyListVal(frame, ['CRVAL1'])['CRVAL1'])
        self.crval2 = float(getKeyListVal(frame, ['CRVAL2'])['CRVAL2'])

        # we load the df with the calibrator data
        # we need positions and magnitudes
        #
        if calibrator == 'skymapper':
            self.df = self.getSkyMapperDf()
        else:
            self.df = None
            
        # Now we load the dataframe with the raw magnitudes in band self.band
        # Note that self.band will be the name of the column of the data frame
        
        # we add the raw magnitudes to self.df
        self.ap_radius = ap_radius
        self.sky_annulus_r1 = ap_sky_r1
        self.sky_annulus_r2 = ap_sky_r2
        self.doPhot() # first run to get raw magnitudes and convertion factors
        
        # here we get the zero points:
        #    zp: to go from ADUs in orig files to magnitudes
        #  zphc: to go from e/s to std magnitudes. To compare with Health Check values.
        #   zp2: to go from Flambda (in erg/s/cm**2/Angstrom) to std magnitudes
        # magzp: to go from DNs (in erg/s/cm**2 to std magnitudes)
        #
        self.zp, self.slope, self.sigma = self.getZP()
        logging.info('ZPCalibration: zp: {0} to go from ADUs in orig files to mags'.format(self.zp))
        
        self.zphc = self.zp+2.5*np.log10(self.avg_gain/self.avg_exptime) # correct gain from ADU to e/s
        logging.info('ZPCalibration: zphc: {0} to go from e/s to std mags.'.format(self.zphc))
        
        self.zp2 = self.getPhysicalUnitsZP()
        logging.info('ZPCalibration: zp2: {0} to go from Flambda to std mags'.format(self.zp2))
  
        self.filterWidth = self.getFilterWidth(self.band)
        self.filterPivotWavelength = self.getPivotWavelength(self.band)
        self.magzp = self.zp2 + \
                    2.5*np.log10(self.filterWidth) + \
                    2.5*np.log10(10**(15)) + \
                    2.5*np.log10(1.0/self.plate_scale**2) # DN in 10**(-15)erg/s/cm**2/asec**2
        logging.info('ZPCalibration: magzp: {0} (from DN to AB mags)'.format(self.magzp))
        
        # We get the conversion factor to Flambda in erg/s/cm^2/Angstrom
        # Imaging data should provide physical units of erg/s/cm^2/arcsec^2
        # We multiply by 10**15 to have numbers closer to 1 for usual objects
        # Note that the magzp was adjusted similarly
        #
        self.convFactor_ADU_Flambda = 10**((self.zp2 - self.zp)/2.5)                
        self.convFactor_ADU_DN = 10**(15)*self.convFactor_ADU_Flambda*self.filterWidth/self.plate_scale**2
        
        
        # Now that we have convFactor_ADU_Flambda we get the std magnitudes
        # here we add std_mags column  to self.df
        self.doPhot() # at this point it will do the photometry on physical values

        # the DN units once we multiply by self.convFactor_ADU_Flambda
        # These are the units required to convert to AB magnitudes by simply 
        # integrating over circular area around stars.
        # It also gives the proper mags/arcsec*2 values by integrating
        # over sky area.
        # But proper imaging fluxes needs erg/s/cm**2
        #
        self.bunit = '10**(-15)*erg/s/cm**2/arcsec**2' # The DN will be in these units.
        
                
        # ----- Determining sky levels for Swarp input frames -------
        #
        # get sky levels in physical units. Note I multiplied by filterWidth (not so the DNs)
        # so the units will be erg/s/cm**2
        #
                
        # get sky levels from orig files
        # these levels were substracted by swarp 
        #
        self.orig_skies_adu = self.getOrigSkyLevels()
        self.orig_skies_phys = copy.deepcopy(self.orig_skies_adu)
        self.orig_skies_phys.update((x, y*self.convFactor_ADU_Flambda*self.filterWidth) for x, y in self.orig_skies_phys.items())

        sky_mean_list = []
        sky_std_list = []
        for key in self.orig_skies_phys:
            sky_mean_list.append(self.orig_skies_phys[key][0])
            sky_std_list.append(self.orig_skies_phys[key][1])
        self.mean_sky = np.mean(sky_mean_list)
        self.std_sky = np.mean(sky_std_list)
        self.magsky = self.getMagSky(self.mean_sky)
        
        # we get the std deviation of the sky from the data itself
        #
        self.mag_sky_std_dev = self.getStdDevMagSky(self.data)
        
        # we get lunar parameters of original Swarp frames
        #
        self.orig_moon_distance, self.orig_moon_fli, \
        self.orig_moon_alt, self.orig_moon_az = self.getMoonFromFrames()
        
        # create dictionary with keywords to be saved
        #
        self.keyword, self.comment, self.mefpp_header_cards = self.getKeywords()
        
        # we save everything to file
        self.writeToFile()
        
    def getStdDevMagSky(self, data):
        """Calculates the stad deviation of sky and returns it as
        an equivalend surface brightness."""
        logging.info('\ngetStdDevMagSky: standard deviation of sky in magnitudes per arcsec^2')
        std_dev = np.nanstd(data)
        logging.info('getStdDevMagSky: std_dev: %.3e ADUs'%(std_dev))
        
        # here we have sigma directly in ADUs
        mag_sky_std_dev = -2.5*np.log10(self.convFactor_ADU_DN*std_dev/(self.plate_scale**2)) + self.magzp
        logging.info('getStdDevMagSky: mag_sky_std_dev: %6.3f mags/arcsec^2'%(mag_sky_std_dev))
        return mag_sky_std_dev

    def getMagSky(self, mean_sky):
        "Calculate the surface brightness of sky in magnitudes per arcsec^2"
        logging.info('\ngetMagSky: surface brightness of sky in magnitudes per arcsec^2')
        
        # here we have mean_sky converted to erg/s/cm2 so we ned to convert back to ADUs
        magsky = -2.5*np.log10(self.convFactor_ADU_DN*mean_sky/(self.convFactor_ADU_Flambda*self.filterWidth*self.plate_scale**2)) + self.magzp
        logging.info('getMagSky: magsky: %6.3f mags/arcsec^2'%(magsky))
        return magsky

    def getAvgGainFromFrame(self):
        """Read the extension gains from first ancestor frame and return list."""
        logging.info('\ngetAvgGainFromFrame: reading original files used by Swarp to determine gains.')
        ext_name_list = ["ESO_CCD_#%2d"%(i) for i in range(65,97)]
        list_to_process = glob.glob(self.basedir+'/OMEGA.*_pre/OMEGA.*_pre_wcs.fits')
        
        file_name = list_to_process[0]
        gain_list = []
        for extname in ext_name_list:
            hdr = fits.getheader(file_name, extname=extname)
            gain_list.append(hdr['HIERARCH ESO DET OUT1 CONAD'])
        avg_gain = np.mean(gain_list)
        logging.info('getAvgGainFromFrame: avg_gain: {0}'.format(avg_gain))
        
        return avg_gain

    def getAvgExpTimeFromFrames(self):
        """Read exposure time from original files used by Swarp."""
        logging.info('\ngetAvgExpTimes: read exposure time from files used by Swarp.')
        
        list_to_process = glob.glob(self.basedir+'/OMEGA.*_pre/OMEGA.*_pre_wcs.fits')
        
        orig_expotime = {}
        
        if len(list_to_process) > 0:
            i = 0
            for file_name in list_to_process:
                
                base_name = os.path.basename(file_name)            
                primary_header = fits.getheader(file_name)                
                if i < len(list_to_process):
                    logging.info('\ngetAvgExpTimeFromFrames: EXPTIME for %i/%i: %s' % 
                          (i+1, len(list_to_process), base_name,))
                    
                    # get exposure time
                    primary_header = fits.getheader(file_name)
                    exptime = primary_header['EXPTIME']
                    orig_expotime[base_name] = exptime
                    logging.info('getAvgExpTimeFromFrames: exptime: %s'%(exptime)) 
                i += 1                
        logging.info('getAvgExpTimeFromFrames: Done.')
        return orig_expotime
    
    
    
    def getMoonFromFrames(self):
        """Read original files used by Swarp to calculate lunar data."""
        logging.info('\ngetMoonFromFrames: read files used by Swarp to read calculate lunar data.')
        
        list_to_process = glob.glob(self.basedir+'/OMEGA.*_pre/OMEGA.*_pre_wcs.fits')
        
        orig_moon_fli = {}
        orig_moon_distance = {}
        orig_moon_alt = {}
        orig_moon_az = {}
        
        if len(list_to_process) > 0:
            i = 0
            for file_name in list_to_process:
                
                base_name = os.path.basename(file_name)
                
                primary_header = fits.getheader(file_name)
                
                if i < len(list_to_process):
                    #hdu_list = fits.open(file_name)
                    

                    logging.info('\ngetMoonFromFrames: Moon for %i/%i: %s' % 
                          (i+1, len(list_to_process), base_name,))
                    
                    # get moon distance and FLI
                    primary_header = fits.getheader(file_name)
                    obs_time = Time(primary_header['DATE-OBS'], format='isot')
                    ra = float(primary_header['RA'])*u.deg
                    dec = float(primary_header['DEC'])*u.deg
                    tel_position = SkyCoord(ra=ra, dec=dec,frame='icrs')
                    logging.info('getMoonFromFrames: obs_time: %s'%(obs_time.value))
                    logging.info('getMoonFromFrames: ra: %9.5f dec: %9.5f'%(ra.value, dec.value))
                    
                    # getting moon info
                    paranal = EarthLocation.of_site('paranal')
                    moon_coords = get_moon(obs_time, paranal)
                    
                    # moon distance to telescope pointing
                    separation = moon_coords.separation(tel_position)
                    orig_moon_distance[base_name] = separation.value
                    
                    # moon fractional illumination t time of observation
                    fli = astroplan.moon_illumination(obs_time) # fractional lunar illumination
                    orig_moon_fli[base_name] = fli
                    logging.info('getMoonFromFrames: moon distance: %4.1f -- FLI: %4.2f'%(separation.value, fli))
                    
                    moon_AltAz = moon_coords.transform_to(AltAz(obstime=obs_time,location=paranal))
                    orig_moon_alt[base_name] = moon_AltAz.alt.value
                    orig_moon_az[base_name] = moon_AltAz.az.value
                    logging.info('getMoonFromFrames: '+'moon Alt: {0} Az: {1}'.format(orig_moon_alt[base_name], orig_moon_az[base_name]))
                i += 1                
        logging.info('getMoonFromFrames: Done.')
        return orig_moon_distance, orig_moon_fli, orig_moon_alt, orig_moon_az
        
    def getOrigSkyLevels(self):
        """Read original files used by Swarp to read the sky levels in ADUs."""
        logging.info('\ngetOrigSkyLevels: reading original files used by Swarp to determine sky levels.')
        ext_name_list = ["ESO_CCD_#%2d"%(i) for i in range(65,97)]

        list_to_process = glob.glob(self.basedir+'/OMEGA.*_pre/OMEGA.*_pre_wcs.fits')

        orig_skies_adu = {}        

        if len(list_to_process) > 0:
            i = 0
            for file_name in list_to_process:
                
                base_name = os.path.basename(file_name)
                                
                if i < len(list_to_process):
                    #hdu_list = fits.open(file_name)
                    
                    # get sky levels and gains
                    median_list = []
                    for extname in ext_name_list:
                        hdr = fits.getheader(file_name, extname=extname)
                        data = fits.getdata(file_name, extname=extname)
                        median_list.append(np.nanmedian(data))

                    median_list = np.array(median_list)            
                    sky_mean = np.nanmean(median_list)            
                    sky_std = np.nanstd(median_list) 
                    
                    orig_skies_adu[base_name] = np.array([sky_mean, sky_std])
                    logging.info('\ngetOrigSkyLevels: sky %i/%i: %s' % 
                          (i+1, len(list_to_process), base_name,))
                    logging.info('getOrigSkyLevels: sky %i/%i: %5.1f +- %5.1f' % 
                          (i+1, len(list_to_process),  \
                              orig_skies_adu[base_name][0], orig_skies_adu[base_name][1],))
                    
                i += 1                
        logging.info('getOrigSkyLevels: Done.')
        #raise Exception('getOrigSkyLevels: -- Testing ---')
        return orig_skies_adu
    
    def getSkyMapperDf(self):
        """Read tke skymapper catalogue to get magnitudes of star in frame."""
        logging.info('\ngetSkyMapper: querying skymapper and creating pandas data frame with magnitudes.')

        # reading wcs infor to create the query
        #
        coord = getKeyListVal(self.frame, ['CRVAL1', 'CRVAL2'])
        ra_str = ("%-10.5f" % coord['CRVAL1']).strip()
        de_str = ("%-10.5f" % coord['CRVAL2']).strip()
        radius = '0.7'
        self.query_str = "http://skymapper.anu.edu.au/sm-cone/public/query?RA="+ra_str+"&DEC="+de_str+"&SR=0.80&VERB=3&RESPONSEFORMAT=CSV"
        logging.info('getSkyMapper: {0}'.format(self.query_str))

        # doing the query if not already saved to file
        #
        if os.path.isfile(self.basedir+'/'+'skymapper_query_result.csv'):
            with open(self.basedir+'/'+'skymapper_query_result.csv') as f:
                logging.info('getSkyMapper: {0} exists. Reading it.'.format(self.basedir+'/'+'skymapper_query_result.csv'))
                line_list = f.readlines()
        else:
            logging.info('getSkyMapper: {0} does not exist. Downloading it.'.format(self.basedir+'/'+self.query_str))
            with urllib.request.urlopen(self.query_str) as f:
                charset = f.headers.get_content_charset()
                # print(charset)
                line_list = f.read().decode(charset).split('\r\n')
            
            # and here we write to file
            logging.info('getSkyMapper: Saving {0}'.format(self.basedir+'/'+'skymapper_query_result.csv'))
            with open(self.basedir+'/'+'skymapper_query_result.csv', 'w') as f:
                for aline in line_list:
                    print(aline, file=f)
            logging.info('getSkyMapper: Done.')
        
        # Create pandas data frame. Set column 1 as the header column
        #
        logging.info('getSkyMapper: Creating pandas dataframe df_cat with phot data.')
        df_cat = pd.DataFrame([x.split(',') for x in line_list])
        df_cat.columns = df_cat.iloc[0]
        logging.info('getSkyMapper: Done.')
        
        # we select only relevant collumns -- FILTER DEPENDENT
        #
        if self.band == 'r_SDSS' or self.band == 'NB_659':
            df_band_columns = ['g_psf', 'e_g_psf', 'r_psf', 'e_r_psf']
            df_pos_columns = ['raj2000', 'dej2000']
            df_total_columns = ['object_id']+df_pos_columns+['class_star'] + df_band_columns
            df_cat = df_cat[df_total_columns][1:]
            
            # update Class accordingly
            self.ref_band_name = 'sm_r_SDSS'
            self.ref_sideband_name = 'sm_g_SDSS'

        # we replace empty values by nan
        #
        for column in df_pos_columns+df_band_columns:
            df_cat[column]=df_cat[column].replace('',np.nan).astype(float)
            df_cat[column] = df_cat[column].astype('float64')        

        # we select according to mlim and columns with valid coords
        #
        bool_select = (df_cat['r_psf'] < self.mlim) & \
            (df_cat['g_psf'] < self.mlim) & \
            (df_cat['raj2000'] == df_cat['raj2000']) & \
            (df_cat['dej2000'] == df_cat['dej2000'])
        df_cat = df_cat[bool_select]   

        # we rename collumns to have a uniform interface for all calibrators
        #
        df_cat.rename(columns={'raj2000': 'ra', 'dej2000': 'dec', \
                     'r_psf': 'ref_band', 'e_r_psf': 'ref_band_e', \
                    'g_psf': 'ref_sideband', 'e_g_psf': 'ref_sideband_e'}, inplace=True)

    
        return df_cat
        

    def doPhot(self):
        """Doing aperture photometry using positions of stars from sky mapper.
           It sets the following class variables:
            - self.aperture
            - self.data
            - self.hdr
            - self.wcs
            - Add column raw_mags to self.df"""
        logging.info('\ndoPhot: aperture photometry routine.')
    
        if self.aperture is None:
            ra = np.array(self.df['ra'])*u.deg
            dec = np.array(self.df['dec'])*u.deg

            # Define positions and apertures
            logging.info('doPhot: creating aperture object')
            positions = SkyCoord(ra=ra, dec=dec,frame='icrs')
            self.aperture = SkyCircularAperture(positions, r=self.ap_radius * u.arcsec)
            self.sky_annulus = SkyCircularAnnulus(positions, self.sky_annulus_r1*u.arcsec, self.sky_annulus_r2*u.arcsec) 

        if self.convFactor_ADU_Flambda is None:
            # we do the aperture photometry -- first good enough version.
            # For a better approach we should do curve of growth..
            #
            logging.info('doPhot: doing aperture photometry on frame.')
            phot_table = aperture_photometry(self.data, [self.aperture, self.sky_annulus], wcs=self.wcs)
            for col in phot_table.colnames:
                if 'aperture_sum' in col:
                    phot_table[col].info.format = '%.8g'  # for consistent table output

            phot_disk_area = self.aperture.to_pixel(self.wcs).area
            phot_sky_area = self.sky_annulus.to_pixel(self.wcs).area

            # we do a sigma clipped median estimate of the background
            logging.info('doPhot: estimatimg backgrounds.')
            ap_pix = self.aperture.to_pixel(self.wcs)
            sky_pix = self.sky_annulus.to_pixel(self.wcs)
            disk_masks = ap_pix.to_mask(method='center')
            annulus_masks = sky_pix.to_mask(method='center')
            bkg_median = []
            j = 0
            j_good = 0
            for mask in annulus_masks:
                annulus_data = mask.multiply(self.data)
                
                if annulus_data is not None: #  target outside of image -> mask multiply returns None
                    annulus_data_1d = annulus_data[mask.data > 0]
                    if j < -1:
                        fig = plt.figure()
                        plt.imshow(annulus_data, norm=LogNorm(vmin=0.01, vmax=10000.0))
                        plt.colorbar()
                        plt.show()
                        input("Press Enter to continue...")
                        disk_data = disk_masks[j].multiply(self.data)
                        plt.imshow(disk_data, norm=LogNorm(vmin=0.01, vmax=10000.0))
                        plt.colorbar()
                        plt.show()
                        input("Press Enter to continue...")
                    _, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d)
                    bkg_median.append(median_sigclip)
                    j_good+= 1
                else:
                    bkg_median.append(0.0)
                j+=1
            bkg_median = np.array(bkg_median)
            logging.info('doPhot: {0} masked stars found ot of {1}.'.format(j_good, j))
            #bkg_mean = phot_table['aperture_sum_1'] / phot_sky_area
            logging.info('doPhot: subtracting backgrounds.')
            bkg_sum = bkg_median * phot_disk_area
            
            phot_table['annulus_median'] = bkg_median
            phot_table['aper_bkg'] = bkg_median * phot_disk_area
            logging.info('doPhot: appending column aper_sum_bkgsub to photometric table.')
            phot_table['aper_sum_bkgsub'] = phot_table['aperture_sum_0'] - phot_table['aper_bkg']
            phot_table['aper_sum_bkgsub'].info.format = '%.8g'  # for consistent table out
            phot_table.show_in_notebook()
            
            # we read the magnitudes from the tables ocam_band
            # df1 = df1.assign(e=pd.Series(np.random.randn(sLength)).values)
            logging.info('doPhot: Add column with raw magnitudes to data frame.')
            #self.df = self.df.assign(raw_mags=pd.Series(-2.5*np.log10(np.array(phot_table['aper_sum_bkgsub']))).values)
            self.df = self.df.assign(raw_mags=pd.Series(-2.5*np.log10(np.array(phot_table['aperture_sum_0']))).values)
            logging.info('doPhot: Done.')
        
        else: # we have convertion to physical units, so we proceed in a slightly modified way
            logging.info('doPhot: photometry on frame with pixel values in physical magnitudes.')

            # Note that we are not updating the values of self.data here. That should be
            # requested explicitly with method self.updateFileOnDisk()
            #
            phot_table = aperture_photometry(self.data*self.convFactor_ADU_Flambda, [self.aperture, self.sky_annulus], wcs=self.wcs)
            for col in phot_table.colnames:
                if 'aperture_sum' in col:
                    phot_table[col].info.format = '%.8g'  # for consistent table output

            phot_disk_area = self.aperture.to_pixel(self.wcs).area
            phot_sky_area = self.sky_annulus.to_pixel(self.wcs).area

            # we do a sigma clipped median estimate of the background
            logging.info('doPhot: estimatimg backgrounds.')
            disk_masks = self.aperture.to_pixel(self.wcs).to_mask(method='center')
            annulus_masks = self.sky_annulus.to_pixel(self.wcs).to_mask(method='center')
            bkg_median = []
            j = 0
            j_good = 0
            for mask in annulus_masks:
                annulus_data = mask.multiply(self.data)
                if annulus_data is not None: #  if we have data we use it
                    annulus_data_1d = annulus_data[mask.data > 0]
                    if j < -1:
                        fig = plt.figure()
                        plt.imshow(annulus_data)
                        plt.colorbar()
                        plt.show()
                        input("Press Enter to continue...")
                        disk_data = disk_masks[j].multiply(self.data)
                        plt.imshow(disk_data)
                        plt.colorbar()
                        plt.show()
                        input("Press Enter to continue...")
                    _, median_sigclip, _ = sigma_clipped_stats(annulus_data_1d)
                    bkg_median.append(median_sigclip)
                    j_good += 1
                else:
                    bkg_median.append(0.0) 
                j+=1
            
            bkg_median = np.array(bkg_median)
            logging.info('doPhot: {0} masked stars found out of {1}'.format(j_good, j))
            #bkg_mean = phot_table['aperture_sum_1'] / phot_sky_area
            logging.info('doPhot: subtracting backgrounds.')
            bkg_sum = bkg_median * phot_disk_area
            
            phot_table['annulus_median'] = bkg_median
            phot_table['aper_bkg'] = bkg_median * phot_disk_area
            logging.info('doPhot: appending column aper_sum_bkgsub to photometric table.')
            phot_table['aper_sum_bkgsub'] = phot_table['aperture_sum_0'] - phot_table['aper_bkg']
            phot_table['aper_sum_bkgsub'].info.format = '%.8g'  # for consistent table out
            #print(phot_table)
            
            # we add column with standard magnitude to self.df
            #ocam_band = -2.5*np.log10(np.array(phot_table['aper_sum_bkgsub'])) + self.getPhysicalUnitsZP()
            # we use the non-backgound subtracted fluxes
            ocam_band = -2.5*np.log10(np.array(phot_table['aperture_sum_0'])) + self.getPhysicalUnitsZP()
            logging.info('doPhot: adding column with std_mags to data frame.')
            self.df = self.df.assign(std_mags=pd.Series(ocam_band).values)        
            logging.info('doPhot: Done.')
            
            # before leaving we save the photometry as a csv file
            logging.info('doPhot: saving photometry table to file {0}'.format('meff_zp_'+self.calibrator+'_phot.tsv'))
            self.df.to_csv(self.basedir+'/mefpp_zp_'+self.calibrator+'_phot.tsv', sep='\t', encoding='utf-8', index=False)
            logging.info('doPhot: Done.')
            
        # display(self.df)
  
    

    def getZP(self):
        """Calculates the zero point using the reference catalogue."""
        logging.info('\ngetZP: calculating zero points.')
        ref_band = np.array(self.df['ref_band'])
        ref_sideband = np.array(self.df['ref_sideband'])
        ocam_band = np.array(self.df['raw_mags'])
        
        X = []
        Xg = []
        Y = []
        for i in range(len(ref_band)):
            if (ref_band[i] == ref_band[i]) and \
                not (np.isinf(ocam_band[i]) or np.isnan(ocam_band[i])) and \
                (ref_band[i] > self.mag_min and ref_band[i] < self.mag_max):
                X.append(ref_band[i])
                Xg.append(ref_sideband[i])
                Y.append(ocam_band[i])

        X = np.array(X)
        Xg = np.array(Xg)
        Y = np.array(Y)
        
        # needs to modify this to force slope=1.00
        # m_raw = 1.00*m_ref + model[0] requires that we return -model[1] as zp
        
        s = 1.0000
        c = fsolve(lambda i: ((Y - (s*X + i))**2).sum(), 0.) # ((Y - (s*X + i))**2).sum()
        model = (s, c[0])

        # we do one iteration of sigma clipping
        X1 = []
        Xg1 = []
        Y1 = []
        for i in range(len(X)):
            ypred = model[0]*X[i] + model[1]
            if np.abs(Y[i] - ypred) < self.dmag_filter:
                X1.append(X[i])
                Xg1.append(Xg[i])
                Y1.append(Y[i])

        X1 = np.array(X1)
        Xg1 = np.array(Xg1)
        Y1 = np.array(Y1)

        # we fix slope to be 1.000 need to add colour term...
        s = 1.0000
        c = fsolve(lambda i: ((Y1 - (s*X1 + i))**2).sum(), c[0]) # ((Y - (s*X + i))**2).sum()
        model = (s, c[0])
        
        logging.debug('getZP: model: %8.4f %8.4f'%(model[0], model[1],))
        #model = np.polyfit(X1, Y1, 1)
    
        # with respect to this model
        ocam_prediced_mag = []
        for i in range(len(ref_band)):
            ocam_prediced_mag = np.append(ocam_prediced_mag, model[0]*ref_band[i] + model[1])
    
        # filter nan and inf values
        good_values1 = ~np.isnan(ocam_band)
        good_values2 = ~np.isinf(ocam_band)
        good_values = good_values1 & good_values2
    
        sigma = np.std(ocam_band[good_values] - ocam_prediced_mag[good_values])
    
        slope = model[0]
        zp = model[1]
        return -zp, slope, sigma
    
    def getFlambdaZP(self, lam):
        """Calculates zero point to go from physical flux to AB magnitudes."""
        logging.info('\ngetFlambdaZP: get zero point to go from physical flux to AB magnitudes.')
        zp = -2.5*np.log10(3.34*10**(-19)) -5.0*np.log10(lam) - 48.60
        return zp

    # Girardi 2004: https://www.aanda.org/articles/aa/full/2004/28/aa0250-04/aa0250-04.html
    # SSDS DR1: http://classic.sdss.org/dr1/algorithms/fluxcal.html
    # 

    def getFilterWidth(self, band):
        """Filter widths for OCAM band passes"""
        pivWave = {'u_SDSS': 560.0,
              'g_SDSS': 1340.0,
              'r_SDSS': 1350.0,
              'NB_659':  105.0, # This is the VPHAS+ filter
              'i_SDSS': 1550.0,
              'z_SDSS':  800.0,
              'B_JOHN': 1030.0, # This is the Bessell B isophotal mag
              'V_JOHN':  980.0} # This is the Bessel V isophotal mag
    
        if band in pivWave.keys():
            return pivWave[band]
        else:
            raise Exception('getFilterWidth: unrecognize filter pass band %s'%(band))        
        
    def getAB_delta(self, band):
        """Delta magnitude from Vega to AB system."""
        abDelta = {'u_SDSS': 0.0,
              'g_SDSS': 0.0,
              'r_SDSS': 0.0,
              'NB_659': 0.0,
              'i_SDSS': 0.0,
              'z_SDSS': 0.0,
              'B_JOHN': 0.04, # This is the Bessell B isophotal mag
              'V_JOHN': 0.0} # This is the Bessel V isophotal mag
    
        if band in abDelta.keys():
            return abDelta[band]
        else:
            raise Exception('getAB_delta: unrecognize filter pass band %s'%(band))
    
    def getPivotWavelength(self, band):
        """Returns the pivot wavelength needed in the
        conversion from AB magnitudes to physical flux."""
        pivWave = {'u_SDSS': 3557.0,
              'g_SDSS': 4702.0,
              'r_SDSS': 6175.0,
              'NB_659': 6590.0,
              'i_SDSS': 7491.0,
              'z_SDSS': 8946.0,
              'B_JOHN': 4371.0, # This is the Bessell B isophotal mag
              'V_JOHN': 5478.0} # This is the Bessel V isophotal mag
    
        if band in pivWave.keys():
            return pivWave[band]
        else:
            raise Exception('getPivotWavelength: unrecognize filter pass band %s'%(band))
    
    # Get the zero point when DN are in physical unitsç
    # of erg/s/cm^-2/Angstrom
    def getPhysicalUnitsZP(self):
        """Returns the zero point to add to -2.5log(flux)
        to get the AB magnitudes in band self.band from calibrated frame."""
        return -2.5*np.log10(3.34*10**(-19)) - 5.0*np.log10(self.getPivotWavelength(self.band)) - 48.60
 
        
    def getKeywords(self):
        """Load dictionary with keywords to be writen to primary headers"""
        logging.info('\ngetKeywords: ')

        # the keys are the keywords. The values the corresponding dictionary values.
        keyword = {}
        comment = {}
        
        # we create PRO keywords to indicate frames that went into coadd.fits
        ancestor_frames_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d}'.format(i+1) for i in range(len(self.orig_skies_phys))]
        sky_mean_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} SKYMEAN'.format(i+1) for i in range(len(self.orig_skies_phys))]
        sky_std_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} SKYSTD'.format(i+1) for i in range(len(self.orig_skies_phys))]
        moon_fli_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} MOON FLI'.format(i+1) for i in range(len(self.orig_skies_phys))]
        moon_distance_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} MOON DISTANCE'.format(i+1) for i in range(len(self.orig_skies_phys))]
        moon_alt_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} MOON ALT'.format(i+1) for i in range(len(self.orig_skies_phys))]
        moon_az_keys = ['HIERARCH MEFPP PRO ANCESTOR{:02d} MOON AZ'.format(i+1) for i in range(len(self.orig_skies_phys))]
                        
        i=0
        zkeys = self.orig_skies_phys.keys()
        for akey in zkeys:
            logging.info('getKeywords: '+akey)
            logging.info('getKeywords: '+ancestor_frames_keys[i])
            
            # frames 
            keyword[ancestor_frames_keys[i]] = akey
            comment[ancestor_frames_keys[i]] = 'Input to Swarp %d' % (i+1)
            logging.info('getKeywords: '+ancestor_frames_keys[i]+' = '+keyword[ancestor_frames_keys[i]]+ \
                                                    ' / '+comment[ancestor_frames_keys[i]])
            
            keyword[sky_mean_keys[i]] = self.orig_skies_phys[akey][0]
            comment[sky_mean_keys[i]] = 'Mean of sky %d' % (i+1)
            logging.info('getKeywords: '+sky_mean_keys[i]+' = '+'%.3E'%(keyword[sky_mean_keys[i]]))
                         
            keyword[sky_std_keys[i]] = self.orig_skies_phys[akey][1]
            comment[sky_std_keys[i]] = 'Std dev of sky %d' % (i+1)
            logging.info('getKeywords: '+sky_std_keys[i]+' = '+'%.3E'%(keyword[sky_std_keys[i]]))
                        
            keyword[moon_fli_keys[i]] = self.orig_moon_fli[akey]
            comment[moon_fli_keys[i]] = 'Moon FLI of frame %d' % (i+1)
            logging.info('getKeywords: '+moon_fli_keys[i]+' = '+'{0}'.format(keyword[moon_fli_keys[i]]))
            
            keyword[moon_distance_keys[i]] = self.orig_moon_distance[akey]
            comment[moon_distance_keys[i]] = 'Moon distance of frame %d' % (i+1)
            logging.info('getKeywords: '+moon_distance_keys[i]+' = '+'{0}'.format(keyword[moon_distance_keys[i]]))

            keyword[moon_alt_keys[i]] = self.orig_moon_alt[akey]
            comment[moon_alt_keys[i]] = 'Moon Altitude of frame %d' % (i+1)
            logging.info('getKeywords: '+moon_alt_keys[i]+' = '+'{0}'.format(keyword[moon_alt_keys[i]]))
            
            keyword[moon_az_keys[i]] = self.orig_moon_az[akey]
            comment[moon_az_keys[i]] = 'Moon Azimuth of frame %d' % (i+1)
            logging.info('getKeywords: '+moon_az_keys[i]+' = '+'{0}'.format(keyword[moon_az_keys[i]]))
            
            i+=1

        # we report several other values important to interpret data
        #
        cards = [['HIERARCH MEFPP PRO SKY UNITS', '10**(-15)*erg/s/cm**2/arcsec**2', 'Units of sky mean and std'],
                 ['HIERARCH MEFPP QC SKYMEAN', self.mean_sky, 'Average sky mean and std'],
                 ['HIERARCH MEFPP QC SKYMEAN UNITS', '10**(-15)*erg/s/cm**2/arcsec**2', 'Units for QC SKYMEAN'],
                 ['HIERARCH MEFPP QC SKYSTD',  self.std_sky, 'Average sky std dev'],
                 ['HIERARCH MEFPP QC SKYSTD UNITS', '10**(-15)*erg/s/cm**2/arcsec**2', 'Units for QC SKYSTD'],
                 ['HIERARCH MEFPP QC ZPHC', self.zphc, 'Zero point for data in e/s -- HC Plots'],
                 ['HIERARCH MEFPP QC BAND NAME', self.band, 'Name of pass band'],
                 ['HIERARCH MEFPP QC BAND WIDTH', self.filterWidth, 'Width of pass band [Angstrom]'],
                 ['HIERARCH MEFPP QC BAND WAVELENGTH', self.filterPivotWavelength, 'Pivot lambda of band [Angstrom]'],
                 ['HIERARCH MEFPP QC MAGSKY', self.magsky, 'Sky brightness mags/arcsec^2'],
                 ['HIERARCH MEFPP QC ADU2FLAM', self.convFactor_ADU_Flambda, 'Conv. fact. ADUs to Flambda'],
                 ['HIERARCH MEFPP QC ADU2DN', self.convFactor_ADU_DN, 'Conv. fact. used ADUs to DN'],
                 ['HIERARCH MEFPP QC BUNIT', self.bunit, 'Units of Data Numbers this frame'],
                 ['HIERARCH MEFPP QC PHO RAD', self.ap_radius, 'Radius used aperture photometry'],
                 ['HIERARCH MEFPP QC PHO SKYR1', self.sky_annulus_r1, 'Sky annulus r1 ap phot'],
                 ['HIERARCH MEFPP QC PHO SKYR2', self.sky_annulus_r2, 'Sky annulus r2 ap phot'],
                 ['HIERARCH MEFPP QC MAGZP', self.magzp, 'ZP to AB magnitudes in BAND']]

        
        for zcard in cards:
            zkey = zcard[0]
            zval = zcard[1]
            zcomment = zcard[2]
            keyword[zkey] = zval
            comment[zkey] = zcomment
            logging.info('getKeywords: '+zkey+' = '+"{0}".format(keyword[zkey])+' / '+comment[zkey])

        # here we create the list of card tuples
        mefpp_header_list = []
        for akey in keyword.keys():
            mefpp_header_list.append((akey, keyword[akey], comment[akey]))
        
        return keyword, comment, mefpp_header_list
    
    def writeToFile(self, filename=None):
        """This procedure has to be called explicitly to write the new DN values and headers to file."""

        logging.info('\nwriteToFile: updating Data Numbers in self.data and adding headers to file.')
        
        # temporary delete - while debugging script
        #self.hdu.remove('HIERARCH MAG_ZEROPOINT')
        #self.hdu.remove('MAGZP')
        
        # we start with the selected headers that will go close to the beginning
        self.hdu.insert('EQUINOX',('BUNIT', self.keyword['HIERARCH MEFPP QC BUNIT'], self.comment['HIERARCH MEFPP QC BUNIT']))
        self.hdu.insert('EQUINOX',('MAGZP', self.keyword['HIERARCH MEFPP QC MAGZP'], self.comment['HIERARCH MEFPP QC MAGZP']))
        self.hdu.insert('EQUINOX',('MAGSKY', self.keyword['HIERARCH MEFPP QC MAGSKY'], self.comment['HIERARCH MEFPP QC MAGSKY']))
        
        # we continue with the full set of keywords near the end
        cards_to_add = self.mefpp_header_cards
        for acard in cards_to_add:
            self.hdu.append(acard)
            
        # we finally rewrite the data array
        self.data = self.data*self.convFactor_ADU_DN
        
        # and here we write to file
        #print(self.hdu.tostring(sep='\n'))
        fits.writeto(self.basedir+'/'+'test.fits', self.data, self.hdu, overwrite=True)
        
        
