from astropy.io import fits

zfile1 = "/Users/fselman/Pictures/OCAM/CPPup//science/CP_Pup/r_SDSS/2017-03-13T01:57:49/OMEGA.2017-03-13T02:36:57.286_pre/OMEGA.2017-03-13T02:36:57.286_pre_wcs.fits"
zfile2 = "/Users/fselman/Pictures/OCAM/CPPup//science/CP_Pup/r_SDSS/2017-03-13T01:57:49/OMEGA.2017-03-13T02:45:38.287_pre/OMEGA.2017-03-13T02:45:38.287_pre_wcs.fits"
hdul1 = fits.open(zfile1, mode='update')
header1 = hdul1[0].header


hdul2 = fits.open(zfile2, mode='update')
header2 = hdul2[0].header

print("obid: {} progid: {}".format(header1["OBID1"], header1["PROG_ID"]))
print("obid: {} progid: {}".format(header2["OBID1"], header2["PROG_ID"]))

# To test multiple OBID and PROGID Phasde3 keywords
#099.D-0533(A)	1662246

header1["OBID1"] = 1662247
header1["PROG_ID"] = "099.D-0534(A)"
header2["OBID1"] = 1662248
header2["PROG_ID"] = "099.D-0535(A)"

hdul1.flush()
hdul1.close()
hdul2.flush()
hdul2.close()

