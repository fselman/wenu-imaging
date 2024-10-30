import numpy as np

from astropy.io import fits
from astropy.table import Table, hstack

from astropy.coordinates import SkyCoord
import astropy.units as u

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
    