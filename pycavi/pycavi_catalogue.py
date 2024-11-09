import numpy as np
from scipy.interpolate import RegularGridInterpolator  # for applying the illumination correction

# for reading the catalogues
from astropy.io import fits
from astropy.table import Table, hstack

# for cross matching the catalogues
from astropy.coordinates import SkyCoord
import astropy.units as u

# for check plots
import matplotlib.pyplot as plt

def getheaderfromframe(framepath, header):
    """
    Simple function to extract a single header from a fits frame

    Parameters:
        framepath: str, path to the fits frame
        header: str, header to extract from the frame

    Return:
        the header value
    """
    hdr = fits.getheader(framepath)
    return hdr[header]

def load_catalogue(catalogue_path, extnumber=2):
    """
    Load the fits catalogue as a astropy table object

    Parameters:
        catalogue_path: str, path of the catalogue to load
        extnumber: int, extension number of the data in the catalogue. Default value 2 for sextractor catalogues.

    Return:
        An astropy table containing the catalogue information
    """
    # the extension name varies with the catalogue. For the sextractor output, the extnumber is two
    hdul = fits.open(catalogue_path)
    table_data = hdul[extnumber].data
    hdul.close()
    output_table = Table(table_data)
    return output_table

def crossmatch_catalogues(cat_1, cat_2, max_sep=1.0,
                          radec_tag_1=['raj2000', 'dej2000'], 
                          radec_tag_2=['raj2000', 'dej2000']):
    """
    Perform a crossmatch between catalogue 1 and catalogue 2.
    Both catalogue must be Astropy Table objects.
    It returns a table whith the columns of both catalogues, so be sure the column names do not repeat among the catalogues.
    The resulting table will consist in the longest table with the shorter one horizontally stacked. The rows where the source in the longest
    catalogue is no present in the shorter one will be filled with nans.
    
    Parameters:
        cat_1: Table with the catalogue to cross match
        cat_2: Table with the catalogue to cross match
        max_sep: maximum tolerance in arcsec between two sources to match. Default 1 arcsec
        radec_tag_1: list with the tags for the ra and dec in catalogue 1
        radec_tag_2: list with the tags for the ra and dec in catalogue 2
        
    Output:
        table_matched: Astropy Table with the cross matched sources.
    """
    # first check which catalogue is the longer
    # assing the catalogues and tag acordingly
    if len(cat_1) >= len(cat_2):
        cat_long = cat_1
        cat_short = cat_2
        radec_long = radec_tag_1
        radec_short = radec_tag_2
    else:
        cat_long = cat_2
        cat_short = cat_1
        radec_long = radec_tag_2
        radec_short = radec_tag_1
        
    # do the cross match
    skycoord_long = SkyCoord(ra=cat_long[radec_long[0]]*u.degree, dec=cat_long[radec_long[1]]*u.degree)
    skycoord_short = SkyCoord(ra=cat_short[radec_short[0]]*u.degree, dec=cat_short[radec_short[1]]*u.degree)
    
    max_sep_thresh = max_sep * u.arcsec
    idx, d2d, _ = skycoord_long.match_to_catalog_sky(skycoord_short)
    sep_constraint = d2d < max_sep_thresh

    matches_short = cat_short[idx[sep_constraint]]

    # create the combined catalogue
    table_short_matches = {}
    for col in cat_short.colnames:
        aux_arr = 1.0*np.arange(len(cat_long))
        aux_arr[:] = np.nan
        aux_arr[sep_constraint] = matches_short[col]
        table_short_matches[col] = aux_arr

    table_short_matches = Table(table_short_matches)
    table_matched = hstack([cat_long, table_short_matches])
    return table_matched

def clean_merged_catalogue(merged_catalogue):
    """
    Clean the merged catalogue by removing sources that were not detected on all the catalogues, and also average the celestial positions 
    but keep the rest of columns untouched, except for the names.
    The names of the columns will be changed to a lowercase version, while keeping the filter names.

    Parameters:
        merged_catalogue: the catalogue resulting from merging the sextrator outputs and the gaia catalogue used during the calibration process

    Output:
        a cleaned version of the catalogue.
    """
    # select the ra and dec columns from the input table
    ra = {}
    de = {}
    tags = []
    for col in merged_catalogue.colnames:
        if 'ALPHA_J2000' in col:
            tag = col[12:]  # the filter tag, eg, r_SDSS
            tags.append(tag)
            racol = 'ALPHA_J2000_'+tag
            decol = 'DELTA_J2000_'+tag
            ra[tag]=merged_catalogue[racol]
            de[tag]=merged_catalogue[decol]
    
    # remove the entries where there is a nan
    sel_nan = np.ones(len(merged_catalogue), dtype=bool)
    for tag in ra.keys():
        ra_data = ra[tag]
        sel_tag = np.isnan(ra_data)
        sel_nan = sel_nan & ~sel_tag
            
    # clean the catalogue
    clean_catalogue = merged_catalogue[sel_nan]
    
    # combine the ra and dec
    ra_comb = None
    de_comb = None
    for tag in tags:
        if ra_comb is None:
            ra_comb = clean_catalogue['ALPHA_J2000_'+tag]
            de_comb = clean_catalogue['DELTA_J2000_'+tag]
        else:
            ra_comb = np.vstack((ra_comb, clean_catalogue['ALPHA_J2000_'+tag])).T
            de_comb = np.vstack((de_comb, clean_catalogue['DELTA_J2000_'+tag])).T
    ra_mean = np.mean(ra_comb, axis=1)
    de_mean = np.mean(de_comb, axis=1)
    
    # remove alpha/delta j2000 columns
    clean_catalogue.remove_columns(['ALPHA_J2000_'+tag for tag in tags])
    clean_catalogue.remove_columns(['DELTA_J2000_'+tag for tag in tags])
    
    # add mean alpha and delta
    clean_catalogue['raj2000'] = ra_mean
    clean_catalogue['dej2000'] = de_mean

    # change the column names to lowercase
    for col in clean_catalogue.colnames:
        clean_catalogue.rename_column(col, col.lower())
    
    return clean_catalogue

def apply_kriggin_illumination_correction(kriggin_fits_path, catalogue_path):
    """
    Apply the illumination correction from Krigging method to the catalogue.
    It read the kriggin resulting fits file, determine the band, and apply the correction to the pycavi magnitudes in the catalogue.

    Parameters:
        kriggin_fits_path:str
            The path to the krigging fits file with the illumination correction
        catalogue_path:str
            The path to the catalogue which will be corrected by illumination

    Return:
        0 if the catalogue was already corrected, 1 if it was corrected during this run
    """
    kriggin_fits_data = fits.getdata(kriggin_fits_path)
    kriggin_fits_header = fits.getheader(kriggin_fits_path)
    catalogue_header = fits.getheader(catalogue_path)

    # check if the catalogue was already corrected for the given filter
    band = kriggin_fits_header['BAND']
    bands_corrected = []
    for key, val in catalogue_header.items():
        if 'ILLCOR' in key:
            if key == band:
                logging.info('Catalogue already corrected in band {}. Skipping band.'.format(band))
                return 0
            bands_corrected.append(val)

    # up to this point we are sure the catalogue has not been corrected on band, so we correct 
    n, m = np.shape(kriggin_fits_data)
    x_kriggin = 1.0*np.arange(m) / m
    y_kriggin = 1.0*np.arange(n) / n  # kriggin data between 0 and 1

    band = kriggin_fits_header['BAND'].lower()
    x_image = kriggin_fits_header['ORIG_W']
    y_image = kriggin_fits_header['ORIG_H']  # band, x, and y dimensiones of the image from the krigging headers
    
    catalogue = load_catalogue(catalogue_path, extnumber=1)
    
    mags_to_correct = []
    for col in catalogue.colnames:
        if 'mag_' in col and band in col:
            mags_to_correct.append(col)
    x_catalogue = catalogue['x_image_'+band] / x_image
    y_catalogue = catalogue['y_image_'+band] / y_image  # x/y position of the sources in the catalogue normalized from zero to one

    # here we do the interpolation of data
    # Use 'cubic' or 'quintic' for smoother interpolation  
    f = RegularGridInterpolator((x_kriggin, y_kriggin), kriggin_fits_data, method='cubic')  
    pts = np.vstack((y_catalogue, x_catalogue)).T

    mag_corr = f(pts)

    # here we update the data and the headers in the catalogue
    with fits.open(catalogue_path, mode='update') as hdul:
        # Access the primary header (extension 0)
        primary_header = hdul[0].header
        # Modify primary headers as needed
        primary_header['ILLCOR{:02d}'.format(len(bands_corrected))] = (band, 'Band with illumination correction applied')
        
        # Access the table data (extension 1) and convert it to an Astropy Table
        table_data = Table(hdul[1].data)
        for col in mags_to_correct:
            table_data[col] += mag_corr

        # Update the HDU with the modified table data
        hdul[1].data = table_data.as_array()    

    return 1

def create_catalogue_checkplots(catalogue_path, band, magmin=13.0, magmax=17.0):
    """
    Create several check plots over the input catalogue to check the quality of the photometry, astrometry, and illumination correction.

    Parameters:
        catalogue_path: str. The absolute path to the catalogue to check.
        band: str. The band to analize (e.g. r_SDSS)
        magmin: float. Minimum magnitude in the reference catalogue used for some check plots. Default=13.0
        magmax: float. Maximum magnitude in the reference catalogue used for some check plots. Default=17.0
        
    Return:
        0 if everything was ok.
    """

    catalogue = load_catalogue(catalogue_path, extnumber=1)
    catalogue_headers = fits.getheader(catalogue_path, ext=0)
    basedir = catalogue_path.split('/')[:-1]
    basedir = '/'.join(basedir)

    target_name = catalogue_headers['OBJECT'].replace(' ','_')
    
    # photometric checks, differences with the gaia reference catalogue
    mag_py = catalogue['mag_petro_'+band.lower()]
    mag_gaia = catalogue[band+'_gaia']

    sel = (mag_gaia >= magmin) & (mag_gaia <= magmax)
    mean_dif = np.nanmean(mag_py[sel]-mag_gaia[sel])
    median_dif = np.nanmedian(mag_py[sel]-mag_gaia[sel])
    std_dif = np.nanstd(mag_py[sel]-mag_gaia[sel])
    stats_text = 'mean:{:.2f}\nmedian:{:.2f}\nstd:{:.2f}'.format(mean_dif, median_dif, std_dif)

    bins = np.arange(8, 20, 1)
    
    # pycavi versus gaia
    fig, ax = plt.subplots(ncols=2, width_ratios=(2,1), figsize=(7, 4.4), dpi=120)
    ax[0].scatter(mag_gaia, mag_py-mag_gaia, s=1, color='black')

    for i in range(len(bins)-1):
        sel_bin = (mag_gaia > bins[i]) & (mag_gaia < bins[i+1])
        median_bin = np.nanmedian(mag_py[sel_bin]-mag_gaia[sel_bin])
        std_bin = np.nanstd(mag_py[sel_bin]-mag_gaia[sel_bin])
        ax[0].errorbar(x=0.5*(bins[i]+bins[i+1]), y=median_bin, yerr=std_bin, xerr=0.5, marker='o', color='tab:orange', ms=2)
    
    ax[0].axhline(0, ls='--', color='tab:blue', zorder=-1)
    ax[0].axvline(magmin, ls='--', color='tab:blue', zorder=-1)
    ax[0].axvline(magmax, ls='--', color='tab:blue', zorder=-1)
    ax[0].set_ylim(-1,1)
    ax[0].invert_yaxis()
    ax[0].set_xlabel('Gaia [mag]')
    ax[0].set_ylabel('Pycavi - Gaia [mag]')
    
    ax[1].hist(mag_py[sel]-mag_gaia[sel], bins='fd', orientation='horizontal', color='black')
    ax[1].axhline(0, ls='--', color='tab:blue', zorder=-1)
    ax[1].text(x=0.05, y=0.95, s=stats_text, transform=ax[1].transAxes, bbox=dict(facecolor='oldlace'), va='top', ha='left')
    ax[1].set_ylim(-1,1)
    ax[1].invert_yaxis()
    ax[1].yaxis.set_ticklabels([])
    ax[1].set_xlabel('counts')
    
    fig.suptitle('Photometric validation Gaia DR3\n{} {}'.format(target_name, band))
    plt.tight_layout()
    plt.savefig(basedir+'/{}_photometric_validation_Gaia.png'.format(target_name), format='png', facecolor='white')
    plt.show()

    # Histogram of magnitudes
    fig, ax = plt.subplots(figsize=(7, 4.4), dpi=120)
    ax.hist(mag_gaia, bins=np.arange(8, 22.1, 0.1), histtype='step', label='Gaia DR3')
    ax.hist(mag_py, bins=np.arange(8, 22.1, 0.1), histtype='step', label='Pycavi')
    ax.legend(loc='upper left')
    ax.set_xlabel('Magnitude')
    ax.set_ylabel('Counts')
    ax.set_title('Objects detected Pycavi vs Gaia DR3\n{} {}'.format(target_name, band))
    plt.tight_layout()
    plt.savefig(basedir+'/{}_objects_detected_Gaia.png'.format(target_name), format='png', facecolor='white')
    plt.show()

    # Illumination correction cheking
    x_pxl = catalogue['x_image_'+band.lower()]
    y_pxl = catalogue['y_image_'+band.lower()]
    center_x = np.nanmax(x_pxl)/2
    center_y = np.nanmax(y_pxl)/2
    r_pxl = np.sqrt((x_pxl-center_x)**2 + (y_pxl-center_y)**2)
    theta_pxl = np.arctan2(y_pxl-center_y, x_pxl-center_x)
    
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(8, 8))
    ax[0,0].scatter(x_pxl[sel], mag_py[sel]-mag_gaia[sel], s=1, color='black')
    ax[0,0].set_xlabel('X [pxl]')
    
    ax[0,1].scatter(y_pxl[sel], mag_py[sel]-mag_gaia[sel], s=1, color='black')
    ax[0,1].set_xlabel('Y [pxl]')
    ax[0,1].yaxis.set_ticklabels([])
    
    ax[1,0].scatter(r_pxl[sel], mag_py[sel]-mag_gaia[sel], s=1, color='black')
    ax[1,0].set_xlabel('r [pxl]')
    
    ax[1,1].scatter(theta_pxl[sel], mag_py[sel]-mag_gaia[sel], s=1, color='black')
    ax[1,1].set_xlabel('Theta [rad]')
    ax[1,1].yaxis.set_ticklabels([])
    
    for axi in ax.flatten():
        axi.axhline(0, ls='--', lw=2, color='tab:blue', zorder=-1)
        axi.set_ylim(-0.25,0.25)
        axi.invert_yaxis()
    
    fig.supylabel('Pycavi - Gaia [mag]')
    fig.suptitle('Illumination correction checking\n{} {}'.format(target_name, band))
    plt.savefig(basedir+'/{}_illumination_correction_checking.png'.format(target_name), format='png', facecolor='white')
    plt.show()    
    
    # Astrometric validation
    ra_py = catalogue['raj2000']
    de_py = catalogue['dej2000']
    ra_gaia = catalogue['raj2000_gaia']
    de_gaia = catalogue['dej2000_gaia']

    mean_de = np.nanmean(de_gaia) * np.pi/180
    delta_ra = np.cos(mean_de) * (ra_py - ra_gaia) * 3600
    delta_de = (de_py - de_gaia) * 3600
    
    t = np.linspace(0, 2*np.pi, 100)
    x = np.cos(t)
    y = np.sin(t)
    
    fig, ax = plt.subplots(figsize=(7, 4.4), dpi=120)
    ax.scatter(delta_ra, delta_de, s=1, color='black')
    ax.plot(x, y, ls='--', color='tab:blue', label='1 arcsec', lw=2, zorder=-1)
    ax.axhline(-0.21/2, ls='--', lw=2, color='tab:orange', label='1 pxl', zorder=-1)
    ax.axhline(0.21/2, ls='--', lw=2, color='tab:orange', zorder=-1)
    ax.axvline(-0.21/2, ls='--', lw=2, color='tab:orange', zorder=-1)
    ax.axvline(0.21/2, ls='--', lw=2, color='tab:orange', zorder=-1)
    ax.legend(loc='upper left')
    ax.set_aspect(1)
    ax.set_xlabel(r'$\Delta$ RA [arcsec]')
    ax.set_ylabel(r'$\Delta$ Dec [arcsec]')
    ax.set_title('Astrometric validation Pycavi vs Gaia\n{} {}'.format(target_name, band))
    plt.tight_layout()
    plt.savefig(basedir+'/{}_astrometric_validation_Gaia.png'.format(target_name), format='png', facecolor='white')
    plt.show()

    return 0