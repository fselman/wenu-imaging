
/*---------------------------------------------------------------------------

  File name 	:	wfi.h
Author 		:	F. Selman
Created on	:	07 Mar 2005
Description	:	Definitions for WFI. The creation of this file is the
			first step toward an instrument independent library, as
			this file contains all the instrument specific parameters.
			The second step will be to put this info in a PAF file
			so that it does not need to be compiled in.

 *--------------------------------------------------------------------------*/

/*
   $Id: mefp_lib.h,v 1.3 2001/03/23 14:05:21 fselman Exp $
   $Author: fselman $
   $Date: 2001/03/23 14:05:21 $
   $Revision: 0.5 $
   */

/*---------------------------------------------------------------------------
  Includes
  ---------------------------------------------------------------------------*/

/*---------------------------------------------------------------------------
  Defines
  ---------------------------------------------------------------------------*/

/* The following parameters are WFI-wide */
#define MEF_ORIGIN				"ESO"
#define MEF_TELESCOPE				"MPI 2.2-m"
#define MEF_INSTRUMENT				"WFI"

#define MEF_RECIPE_KEY				"HIERARCH ESO REC"

/* Data product parameters */
#define MEF_DPR_CATG_KEY			"HIERARCH ESO DPR CATG"
#define MEF_DPR_CATG_COMMENT			"product frame category"
#define MEF_DPR_TYPE_KEY			"HIERARCH ESO DPR TYPE"
#define MEF_DPR_TYPE_COMMENT			"product frame type"

/* Prescan/Overscan region */
#define MEF_USE_PRESCAN				(0)
#define MEF_PRESCAN_X_KEY			"HIERARCH ESO REC FLAT PRSCX"
#define MEF_PRESCAN_X_COMMENT			"Prescan xmin xmax"
#define MEF_PRESCAN_X_MIN_CHIP1			(5)
#define MEF_PRESCAN_X_MAX_CHIP1			(48)
#define MEF_PRESCAN_X_MIN_CHIP2                 (5)
#define MEF_PRESCAN_X_MAX_CHIP2                 (48)
#define MEF_PRESCAN_X_MIN_CHIP3                 (5)
#define MEF_PRESCAN_X_MAX_CHIP3                 (48)
#define MEF_PRESCAN_X_MIN_CHIP4                 (5)
#define MEF_PRESCAN_X_MAX_CHIP4                 (48)
#define MEF_PRESCAN_X_MIN_CHIP5                 (2100)
#define MEF_PRESCAN_X_MAX_CHIP5                 (2142)
#define MEF_PRESCAN_X_MIN_CHIP6                 (2100)
#define MEF_PRESCAN_X_MAX_CHIP6                 (2142)
#define MEF_PRESCAN_X_MIN_CHIP7                 (2100)
#define MEF_PRESCAN_X_MAX_CHIP7                 (2142)
#define MEF_PRESCAN_X_MIN_CHIP8                 (5)
#define MEF_PRESCAN_X_MAX_CHIP8                 (48)


#define MEF_USE_OVERSCAN			(1)
#define MEF_OVERSCAN_X_KEY			"HIERARCH ESO REC FLAT OVSCX"
#define MEF_OVERSCAN_X_COMMENT			"Overscan xmin xmax"
#define MEF_OVERSCAN_X_MIN_CHIP1		(2100)
#define MEF_OVERSCAN_X_MAX_CHIP1		(2142)
#define MEF_OVERSCAN_X_MIN_CHIP2                (2100)
#define MEF_OVERSCAN_X_MAX_CHIP2                (2142)
#define MEF_OVERSCAN_X_MIN_CHIP3                (2100)
#define MEF_OVERSCAN_X_MAX_CHIP3                (2142)
#define MEF_OVERSCAN_X_MIN_CHIP4                (2100)
#define MEF_OVERSCAN_X_MAX_CHIP4                (2142)
#define MEF_OVERSCAN_X_MIN_CHIP5                (5)
#define MEF_OVERSCAN_X_MAX_CHIP5                (48)
#define MEF_OVERSCAN_X_MIN_CHIP6                (5)
#define MEF_OVERSCAN_X_MAX_CHIP6                (48)
#define MEF_OVERSCAN_X_MIN_CHIP7                (5)
#define MEF_OVERSCAN_X_MAX_CHIP7                (48)
#define MEF_OVERSCAN_X_MIN_CHIP8                (2100)
#define MEF_OVERSCAN_X_MAX_CHIP8                (2142)

/* proper astrometric keywords */
#define MEF_CRVAL1_CHIP1			(1)
#define MEF_CRVAL2_CHIP1			(1)
#define MEF_CRPIX1_CHIP1			(49)
#define MEF_CRPIX2_CHIP1			(-4158)

#define MEF_CRVAL1_CHIP2                        (1)
#define MEF_CRVAL2_CHIP2                        (1)
#define MEF_CRPIX1_CHIP2                        (-2094)
#define MEF_CRPIX2_CHIP2                        (-4158)

#define MEF_CRVAL1_CHIP3                        (1)
#define MEF_CRVAL2_CHIP3                        (1)
#define MEF_CRPIX1_CHIP3                        (-4236)
#define MEF_CRPIX2_CHIP3                        (-4158)

#define MEF_CRVAL1_CHIP4                        (1)
#define MEF_CRVAL2_CHIP4                        (1)
#define MEF_CRPIX1_CHIP4                        (-6378)
#define MEF_CRPIX2_CHIP4                        (-4158)

#define MEF_CRVAL1_CHIP5                        (1)
#define MEF_CRVAL2_CHIP5                        (1)
#define MEF_CRPIX1_CHIP5                        (-6378)
#define MEF_CRPIX2_CHIP5                        (1)

#define MEF_CRVAL1_CHIP6                        (1)
#define MEF_CRVAL2_CHIP6                        (1)
#define MEF_CRPIX1_CHIP6                        (-4236)
#define MEF_CRPIX2_CHIP6                        (1)

#define MEF_CRVAL1_CHIP7                        (1)
#define MEF_CRVAL2_CHIP7                        (1)
#define MEF_CRPIX1_CHIP7                        (-2094)
#define MEF_CRPIX2_CHIP7                        (1)

#define MEF_CRVAL1_CHIP8                        (1)
#define MEF_CRVAL2_CHIP8                        (1)
#define MEF_CRPIX1_CHIP8                        (49)
#define MEF_CRPIX2_CHIP8                        (1)






#define MEF_SCANREJ_KEY				"HIERARCH ESO REC FLAT RJOVSC"
#define MEF_SCANREJ_COMMENT			"Rejection min max"
#define MEF_SCANREJ_MIN				(10)
#define MEF_SCANREJ_MAX				(10)

/* Cropping region */
/* Declared obsolete 22 Nov 2000 */
/*
#define WFI_CROP_X_MIN			(55)
#define WFI_CROP_X_MAX			(2090)
#define WFI_CROP_Y_MIN			(35)
#define WFI_CROP_Y_MAX			(4120)
*/

/* 
 * some important positional keywords
 * We enforce a single CRVALi for all chips
 */
#define MEF_REFPIX_X				(4101)
#define MEF_REFPIX_Y				(3950)


/* 2005-03-07 */
#define MEF_TRIMREG_KEY				"HIERARCH ESO REC FLAT TRIM"
#define MEF_TRIMREG_COMMENT			"xmin xmax ymin ymax"
#define MEF_CROP_X_MIN_CHIP1			(51)
#define MEF_CROP_X_MAX_CHIP1			(2094)
#define MEF_CROP_Y_MIN_CHIP1			(31)
#define MEF_CROP_Y_MAX_CHIP1			(4127)
#define MEF_CROP_X_MIN_CHIP2                    (51)
#define MEF_CROP_X_MAX_CHIP2                    (2094)
#define MEF_CROP_Y_MIN_CHIP2                    (31)
#define MEF_CROP_Y_MAX_CHIP2                    (4127)
#define MEF_CROP_X_MIN_CHIP3                    (51)
#define MEF_CROP_X_MAX_CHIP3                    (2094)
#define MEF_CROP_Y_MIN_CHIP3                    (31)
#define MEF_CROP_Y_MAX_CHIP3                    (4127)
#define MEF_CROP_X_MIN_CHIP4                    (51)
#define MEF_CROP_X_MAX_CHIP4                    (2094)
#define MEF_CROP_Y_MIN_CHIP4                    (31)
#define MEF_CROP_Y_MAX_CHIP4                    (4127)
#define MEF_CROP_X_MIN_CHIP5                    (49)
#define MEF_CROP_X_MAX_CHIP5                    (2092)
#define MEF_CROP_Y_MIN_CHIP5                    (2)
#define MEF_CROP_Y_MAX_CHIP5                    (4098)
#define MEF_CROP_X_MIN_CHIP6                    (49)
#define MEF_CROP_X_MAX_CHIP6                    (2092)
#define MEF_CROP_Y_MIN_CHIP6                    (2)
#define MEF_CROP_Y_MAX_CHIP6                    (4098)
#define MEF_CROP_X_MIN_CHIP7                    (49)
#define MEF_CROP_X_MAX_CHIP7                    (2092)
#define MEF_CROP_Y_MIN_CHIP7                    (2)
#define MEF_CROP_Y_MAX_CHIP7                    (4098)
#define MEF_CROP_X_MIN_CHIP8                    (51)
#define MEF_CROP_X_MAX_CHIP8                    (2094)
#define MEF_CROP_Y_MIN_CHIP8                    (2)
#define MEF_CROP_Y_MAX_CHIP8                    (4098)


/* Number of CCD chips on WFI */
#define MEF_NCHIPS				(8)	/* Number of CCD chips in camera */	
#define MEF_SATLEVEL				(65534)	/* Saturation level for pre-processing */
#define MEF_SATMAX				(0.05)	/* Maximal % of pixels > SATLEVEL       */

/* 2005-03-07 */
#define MEF_CCD_RON_KEY				"RDNOISE"
#define MEF_CCD_RON_I_KEY                    	"HIERARCH ESO DET OUT%d RON"
#define MEF_CCD_RON_COMMENT			"Read out noise"
#define MEF_CCD_RON_CHIP1			(5.1)	/* CCD read-out noise in e- 		*/
#define MEF_CCD_RON_CHIP2                       (5.4) 
#define MEF_CCD_RON_CHIP3                       (5.3)
#define MEF_CCD_RON_CHIP4                       (4.8)
#define MEF_CCD_RON_CHIP5                       (5.2)
#define MEF_CCD_RON_CHIP6                       (5.4)
#define MEF_CCD_RON_CHIP7                       (5.0)
#define MEF_CCD_RON_CHIP8                       (4.9)


/* 2005-03-07 */
#define MEF_CCD_GAIN_KEY			"GAIN"
#define MEF_CCD_GAIN_I_KEY                   	"HIERARCH ESO DET OUT%d GAIN"
#define MEF_CCD_GAIN_COMMENT			"CCD gain"
#define MEF_CCD_GAIN_CHIP1			(2.0)	/* CCD gain e-/ADUs   			*/
#define MEF_CCD_GAIN_CHIP2                      (2.1)
#define MEF_CCD_GAIN_CHIP3                      (2.3)
#define MEF_CCD_GAIN_CHIP4                      (2.0)
#define MEF_CCD_GAIN_CHIP5                      (2.1)
#define MEF_CCD_GAIN_CHIP6                      (2.1)
#define MEF_CCD_GAIN_CHIP7                      (2.2)
#define MEF_CCD_GAIN_CHIP8                      (2.2)



/* BIAS parameters for WFI */
#define MEF_BIAS_FRAME_I_KEY			"HIERARCH ESO REC BIAS"
#define MEF_BIAS_FRAME_I_COMMENT		"Input bias frame"


#define MEF_MASTER_BIAS_KEY			"HIERARCH ESO REC FLAT MBIAS"
#define MEF_MASTER_BIAS_COMMENT			"Master bias used"
#define MEF_BIAS_NAME_O				"WFI_MB"
#define MEF_BIAS_FRAMETHR_LO			(0)
#define MEF_BIAS_FRAMETHR_HI			(1000)
#define MEF_BIAS_KAPPA1				(2.0)
#define MEF_BIAS_FRAMENUM_MIN			(3)

/* BPM parameters */
#define MEF_BPM_NAME_O				"WFI_BPM"

#define MEF_BPM_PROPFLAG_KEY			"HIERARCH ESO REC BPM PROPFLAG"
#define MEF_BPM_PROPFLAG_COMMENT		"proportional flag for BPM creation"
#define MEF_BPM_PROPFLAG			(0)

#define MEF_BPM_LGAINTHR_KEY			"HIERARCH ESO REC BPM LGAINTHR"
#define MEF_BPM_LGAINTHR_COMMENT		"low gain threshold for BPM creation"
#define MEF_BPM_LGAINTHR			(0.6)

#define MEF_BPM_HGAINTHR_KEY                    "HIERARCH ESO REC BPM HGAINTHR"
#define MEF_BPM_HGAINTHR_COMMENT		"high gain threshold for BPM creation"
#define MEF_BPM_HGAINTHR			(1.4)

/* flat field  parameters */
#define MEF_DOMEFF_FRAME_I_KEY			"HIERARCH ESO REC FLAT DOME"
#define MEF_DOMEFF_FRAME_I_COMMENT		"Input dome frame"

#define MEF_DOMEFF_NAME_O               	"WFI_DOMEFF"
#define MEF_DOMEFF_FRAMETHR_LO_KEY		"HIERARCH ESO REC FLAT LFRATHD"
#define MEF_DOMEFF_FRAMETHR_LO_COMMENT		"low frame threshold for dome"
#define MEF_DOMEFF_FRAMETHR_LO			(10000)

#define MEF_DOMEFF_FRAMETHR_HI_KEY		"HIERARCH ESO REC FLAT HFRATHD"
#define MEF_DOMEFF_FRAMETHR_HI_COMMENT		"high frame threshold for dome"
#define MEF_DOMEFF_FRAMETHR_HI			(45000)

#define MEF_DOMEFF_FRAMENUM_MIN_KEY		"HIERARCH ESO REC FLAT MINFRAD"
#define MEF_DOMEFF_FRAMENUM_MIN_COMMENT		"minimum number of frames for dome flat"
#define MEF_DOMEFF_FRAMENUM_MIN			(5)

#define MEF_SKYFF_FRAME_I_KEY			"HIERARCH ESO REC FLAT SKY"
#define MEF_SKYFF_FRAME_I_COMMENT		"Input sky frame"
#define MEF_SKYFF_NAME_O                	"WFI_SKYFF"
#define MEF_SKYFF_FRAMETHR_LO_KEY		"HIERARCH ESO REC FLAT LFRATHS"
#define MEF_SKYFF_FRAMETHR_LO_COMMENT		"low frame threshold for sky"
#define MEF_SKYFF_FRAMETHR_LO            	(10000)

#define MEF_SKYFF_FRAMETHR_HI_KEY		"HIERARCH ESO REC FLAT HFRATHS"
#define MEF_SKYFF_FRAMETHR_HI_COMMENT		"high frame threshold for sky"
#define MEF_SKYFF_FRAMETHR_HI            	(45000)

#define MEF_SKYFF_FRAMENUM_MIN_KEY		"HIERARCH ESO REC FLAT MINFRAS"
#define MEF_SKYFF_FRAMENUM_MIN_COMMENT		"minimum number of frames for sky flat"
#define MEF_SKYFF_FRAMENUM_MIN           	(5)

/* root name for master flat field */
#define MEF_FF_DEFAULTNAME               	"WFI_MFF"


#define MEF_FILTER_KEY				"HIERARCH ESO INS FILT1 NAME"
#define MEF_BINX_KEY				"HIERARCH ESO DET WIN1 BINX"
#define MEF_BINY_KEY				"HIERARCH ESO DET WIN1 BINY"

/* recipe parameters, eventually in a separate file */
#define MEF_PIXREJ_SIGMA_LO_KEY			"HIERARCH ESO REC FLAT LPIXSIG"
#define MEF_PIXREJ_SIGMA_LO_COMMENT         	"low sigma for pixel rejection"
#define	MEF_PIXREJ_SIGMA_LO			(3.0)

#define MEF_PIXREJ_SIGMA_HI_KEY             	"HIERARCH ESO REC FLAT HPIXSIG"
#define MEF_PIXREJ_SIGMA_HI_COMMENT         	"high sigma for pixel rejection"
#define MEF_PIXREJ_SIGMA_HI			(3.0)

#define MEF_MEDIAN_REG_KEY			"HIERARCH ESO REC FLAT MREGDEF"
#define MEF_MEDIAN_REG_COMMENT			"Region for median computation"
#define MEF_MEDIAN_REG_X1			(500)
#define MEF_MEDIAN_REG_X2			(1500)
#define MEF_MEDIAN_REG_Y1			(1500)
#define MEF_MEDIAN_REG_Y2			(2500)

#define MEF_KERN_HSIZE_KEY			"HIERARCH ESO REC FLAT KERNS"
#define MEF_KERN_HSIZE_COMMENT			"Smoothing kernel size"
#define MEF_KERN_HSIZE				(4)


