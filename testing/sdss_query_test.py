from astroquery.sdss import SDSS

crval1 = 1.328522018634E+02
crval2 = 1.183058352428E+01
half_width_ra = 0.5
half_width_dec = 0.5
query="""SELECT 
objid,ra,dec,flags,psfMag_u,Err_u,psfMag_g,Err_g,psfMag_r,Err_r,psfMag_i,Err_i,psfMag_z,Err_z
FROM STAR
WHERE
ra BETWEEN {0} and {1} AND dec BETWEEN {2} and {3} and flags != 0
AND 
psfMag_u BETWEEN 9 AND 18.6
AND
psfMag_g BETWEEN 9 AND 18.6
""".format(crval1-half_width_ra, crval1+half_width_ra, crval2-half_width_dec, crval2+half_width_dec)

sdss_astropy_table = SDSS.query_sql(query)
if sdss_astropy_table is not None:
    sdss_df = sdss_astropy_table.to_pandas()
    sdss_df = sdss_df.rename(columns={'psfMag_u': 'u_psf', 'Err_u': 'e_u_psf', \
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

    sdss_df['ra'] = sdss_df['ra'].round(6)
    sdss_df['dec'] = sdss_df['dec'].round(6)
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
    sdss_df.to_csv('sdss_query_result.csv', index=False)
else:
    print('SDSS query returned no results.')
