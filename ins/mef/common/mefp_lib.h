
/*---------------------------------------------------------------------------

  File name 	:	mefp_lib.h
Author 		:	F. Selman
Created on	:	18 May 2000
Description	:	MEF library utilities, from
			wfi by N. Devillard, mutatis mutandi

 *--------------------------------------------------------------------------*/

/*
   $Id: mefp_lib.h,v 1.3 2001/03/23 14:05:21 fselman Exp $
   $Author: fselman $
   $Date: 2001/03/23 14:05:21 $
   $Revision: 0.5 $
   */

#ifndef _WFIP_LIB_H_
#define _WFIP_LIB_H_

/*---------------------------------------------------------------------------
  Includes
  ---------------------------------------------------------------------------*/

#include "eclipse.h"

/*---------------------------------------------------------------------------
  Defines
  ---------------------------------------------------------------------------*/

/* ---------------------------------------------------------------------
 * 							Structures
 * ---------------------------------------------------------------------*/
typedef struct _mef_ccd_ {
	char	extname[80];
	int	extnum;
	char	crtype1[80];
	char	crtype2[80];
	float	crval1;
	float	crval2;
	float	crpix1;
	float	crpix2;
	float	cd1_1;
	float	cd1_2;
	float	cd2_1;
	float	cd2_2;
	int	prescan_x[2];
	int	overscan_x[2];
	int	trimreg[4];
	float	ron;
	float	gain;
} mef_ccd ;

typedef struct _mef_bb_ {

	/* origing of data */
	char		*origin ;
	char		*telescope ;
	char		*instrument ;

	/* Input/Output file names */
	char	*	name_paf ;
	char    *   name_bias ;
	char    *   name_bias_o ;
	char	*	name_bpm ;
	char	*	name_bpm_o ;
	char    *   name_dome ;
	char    *   name_dome_o ;
	char    *   name_sky ;
	char    *   name_sky_o ;
	char	*	name_mf ;
	char    *   name_mf_o ;		/* name of file to store combined flat */

	int		noverify ;

	/* Parameters of detectors */
	int		nchips;
	int		nxts ;		/* number of extension being processed 	*/
	int     xtnum ;		/* extension being processed		*/
	int		correct_ref_pix; /* flag indicating whether to correct CRVALi and CRPIXi */
	
	/* pointer to ccd structures */
	mef_ccd		*ccd;

	/* Recipe keyword */
	char		*recipe_key ;

	/* Data product book keeping parameters */
	char		*dpr_catg_key ;
	char		*dpr_catg_val ;
	char		*dpr_catg_comment ;

	char		*dpr_type_key ;
	char		*dpr_type_val ;
	char		*dpr_type_comment ;

    char        *scipro_catg_key ;
    char        *scipro_catg_val ;
    char        *scipro_catg_comment ;

	/* Frame parameters */
	float		refpix_x ;
	float		refpix_y ;
	char	*	filter_key ;
	char	*	filter_val ;
	char	*	binx_key ;
	char	*	binx_val ;
	char	*	biny_key ;
	char	*	biny_val ;
	char	*	data_partition ;
	char	*	bias_partition ;
	char	*	flat_partition ;

	/* Overscan/prescan parameters */
	int		use_prescan;
	int		use_overscan;

	/* Bias parameters */
	char    *bias_frame_i_key ;
    char    *bias_frame_i_comment ;

	char	*master_bias_key ;
	char	*master_bias_comment ;
	int	    bias_subtract ;
	float	*bias_framethr_lo ;
	float	*bias_framethr_hi ;
    float   *bias_avg1;
    float   *bias_sig1;
	double	bias_kappa1 ;
	int		bias_minframe ;
	int		bias_save ;
    float * bias_stdev;
	float	*bias_median ; /* median of bias frames for each extension */
    float   *bias_scan_median ; /* median of the overscan or prescan */
    float   *bias_scan_stdev ; /* standard deviation of the overscan or prescan values */
    char    **bias_frame_name;
    int     bias_nframes;
	int		*bias_nplanes ;

	/* BPM parameters */
	int		bpm_proportional_flag;
	float	bpm_gainthr_lo;
	float	bpm_gainthr_hi;

	/* Dome parameters */
	char		*domeff_frame_i_key ;
	char		*domeff_frame_i_comment ;
	
	char        *dome_framethr_lo_key ;
    char    *dome_framethr_lo_comment ;
	double       dome_framethr_lo ;

	char        *dome_framethr_hi_key ;
	char        *dome_framethr_hi_comment ;
	double       dome_framethr_hi ;

	char		*dome_minframe_key ;
	char        *dome_minframe_comment ;
	int          dome_minframe ;

	int          dome_save ;
	float		*dome_median ;	/* median of dome frames for each extension */
    float       *dome_stdev ;
    float       *dome_scan_median ;  /* median of overscan of dome frames for each extension */
    float       *dome_scan_stdev ;
	int		    *dome_nplanes ;
    int         dome_nframes;
    char        **dome_frame_name;

	/* Sky parameters */
	char		*skyff_frame_i_key ;
	char		*skyff_frame_i_comment ;
	
	char		*sky_framethr_lo_key ;
	char        *sky_framethr_lo_comment ;
	double      sky_framethr_lo ;

	char       *sky_framethr_hi_key ;
	char       *sky_framethr_hi_comment ;
	double      sky_framethr_hi ;

	char       *sky_minframe_key ;
	char       *sky_minframe_comment ;
	int         sky_minframe ;

	int          sky_save ;
	float		*sky_median ; /* median of sky frames for each extension */
    float       *sky_stdev ;
    float       *sky_scan_median ; /* median of overscan of sky frames for each extension */
    float       *sky_scan_stdev ;
	int		    *sky_nplanes ;
    int         sky_nframes;
    char        **sky_frame_name;

	/* Combined flat parameters */
	float		*flat_median ;
    float       *flat_stdev;

	/* Pre/Over scan parameters */
	char		*prescan_x_key ;
	char		*prescan_x_comment ;

	char        *overscan_x_key ;
	char        *overscan_x_comment ;

	char		*scanrej_key ;
	char		*scanrej_comment ;
	int          scanrej[2] ;    /* min max */

	char       *trimreg_key ;
    char       *trimreg_comment ;

	/* Readout noise */
	char        *ccd_ron_key ;
	char		*ccd_ron_i_key ;
	char        *ccd_ron_comment ;

	/* Gain		*/
	char        *ccd_gain_key ;
	char		*ccd_gain_i_key ;
	char		*ccd_gain_comment ;

	/* Pixel rejection */
	char		*pixrej_lo_key ;
	char		*pixrej_lo_comment ;
	double       pixrej_lo ;

	char		*pixrej_hi_key ;
	char		*pixrej_hi_comment ;
	double       pixrej_hi ;

	/* Median region definition */
	char		*median_reg_key ;
	char		*median_reg_comment ;
	int          median_reg[4] ; /* xmin xmax ymin ymax */
	int          median_surf ;

	/* Smoothing kernel dimension */
	char		*kern_hsize_key ;
	char		*kern_hsize_comment ;
	int          kern_hsize ;

	/* science frames to be reduced parameters */
	char		*science_name_i ;
	char		**science_frame_name ;
    float       *science_scan_median ;  /* median of overscan of science frames for each extension */
    float       *science_scan_stdev ;
    double      *individual_frame_avg ; /* array to contain avg values of input frames of a given extension */
    double      *individual_frame_median ;
    double      *individual_frame_sigma ;
	int		    science_nframes ;

	/* saturation level threshold and max acceptable %age */
	int		    sat_check ;
	double		sat_level ;
	double		sat_max ;

	/* split key: if set we only split the files in image sections */
	char		*name_split;

} mef_bb ;



/*---------------------------------------------------------------------------
  Function codes
  ---------------------------------------------------------------------------*/

mef_bb * mef_bb_new(void);

void mef_bb_del(mef_bb * bb);

void mef_bb_dump(mef_bb * bb, FILE * out);

int mef_split(char * name_i, char * name_o, int xtnum);

cube_t * mef_cube_load(char * filename, int xtnum);


image_t * mef_load_ext(char * filename, int xtnum);

int mef_is_extension(char * filename);

/*
image_t * mef_overscan_correction(
		image_t    *   mef_frame,
		int         *   prescan_x,
		int         *   overscan_x,
		int         *   rej_int,
		int         *   crop_reg,
		int	    use_prescan,
		int	    use_overscan
		) ;
*/
image_t * mef_overscan_correction(image_t * mef_frame, mef_bb *, int nplane, char * what);
int     mef_cube_overscan_correction(cube_t *,mef_bb *, char * what);

int mef_saturation_check(cube_t *, mef_bb *);

int mef_gradient_check(
		image_t    *   mef_frame,
		double          max_grad_level
		) ;
int    		mef_valid_subset(mef_bb *, char *) ;
qfits_header 	*mef_header_primary(char *);
qfits_header 	*mef_header_ext(char *, mef_bb *);
qfits_header 	*mef_header_mainsubset(mef_bb *, image_t *);
qfits_header 	*mef_header_eclipse(mef_bb *, char *);
qfits_header	*fits_header_merge(qfits_header *, qfits_header *);
char 		*mef_get_input_filename(mef_bb *bb, char *what);
char 		*mef_get_output_filename(mef_bb *bb, char *what);
qfits_header	*mef_get_headers_for( char *what, mef_bb * bb, image_t * zImage);
void	 	mef_save(mef_bb *bb, image_t *zImage, char *what);
void	 	save_mef_hdrdump(image_t *,char *,qfits_header *,int);
image_t 	*mef_build_cal(mef_bb *, char *);
image_t 	*mef_ff_combine(mef_bb *, image_t *, image_t *, image_t *,pixelmap *);
image_t		*mef_image_filter_flat(image_t *,int kern_size,pixelmap *);
pixelmap * mef_build_bpm(mef_bb *bb, image_t * bias);
#endif
