
/*---------------------------------------------------------------------------

File name 	:	mef_cal.c
Version:	:	1.0
Author 		:	F. Selman
Created on	:	Sept 2000
Description	:	MEF flat-field creation recipe, from WFI by
			N. Devillard mutatis mutandi

 *--------------------------------------------------------------------------*/

/*
   $Id: mef_cal.c,v 1.19 2001/10/22 11:57:29 ndevilla Exp $
   $Author: ndevilla $
   $Date: 2001/10/22 11:57:29 $
   $Revision: 0.5 $
   */

/*---------------------------------------------------------------------------
  Includes
  ---------------------------------------------------------------------------*/

#include <unistd.h>
#include "eclipse.h"
#include "mefp_lib.h"

/*---------------------------------------------------------------------------
  Defines
  ---------------------------------------------------------------------------*/

#define OPT_XTNUM		1000
#define OPT_NOVERIFY            1002
#define OPT_PAFNAME             1003
#define OPT_BIASNAME		1005
#define OPT_BIASSUB		1007
#define OPT_BIASSAVE		1008
#define OPT_BIASKAPPA1		1009
#define OPT_DOMENAME		1010
#define OPT_DOMETHRESH		1011
#define OPT_DOMEMINFRAME	1012
#define OPT_DOMESAVE		1013
#define OPT_BPMNAME		1016
#define OPT_SKYNAME		1020
#define OPT_SKYTHRESH		1021
#define OPT_SKYMINFRAME		1022
#define OPT_SKYSAVE		1023
#define OPT_MFFNAME		1030
#define OPT_MFFSAVE		1035
#define OPT_SCANREJ		1041
#define OPT_PIXELREJ		1070
#define OPT_MEDIANREG		1080
#define OPT_KERNELSIZE		1090
#define OPT_SCINAME		2000
#define OPT_SATCHECK		2100
#define OPT_SATLEVEL		2200
#define OPT_SATMAX		2300
#define OPT_SPLIT		3100


static char recipe_version[] = "$Revision: 1.6.0 $";

static void usage(char *pname) ;
static char prog_desc[] = "MEF master calibration frames creation" ;

/*
qfits_header *fits_header_merge(qfits_header *, qfits_header *);
qfits_header *mef_header_primary(char *);
qfits_header *mef_header_ext(char *, int);
qfits_header *mef_header_eclipse(mef_bb *,char *);
void save_mef_hdrdump(image_t *,char *,qfits_header *,int);
*/

mef_bb * mef_bb_load (int argc, char *argv[])
{
	int             c ;
	int         display_params ;
	char * pafname ;
	mef_bb*   bb ;

	display_params = 0 ;

	bb = mef_bb_new();

	while (1) {
		int     option_index = 0 ;
		static struct option long_options[] =
		{
			{"license",         0, 0, OPT_LICENSE},
			{"help",            0, 0, OPT_HELP},
			{"version",         0, 0, OPT_VERSION},

			{"noverify",	    0, 0, OPT_NOVERIFY},

                        {"pafname",        0, 0, OPT_PAFNAME},

			{"xtnum",           1, 0, OPT_XTNUM},

			{"bias",            1, 0, OPT_BIASNAME},
			{"biassub",         0, 0, OPT_BIASSUB},
			{"biassave",        0, 0, OPT_BIASSAVE},
			{"biaskappa1",        1, 0, OPT_BIASKAPPA1},

			{"bpm",			1, 0, OPT_BPMNAME},

			{"dome",                1, 0, OPT_DOMENAME},
			{"domethr",             1, 0, OPT_DOMETHRESH},
			{"domemin",             1, 0, OPT_DOMEMINFRAME},
			{"domesave",    	0, 0, OPT_DOMESAVE},

			{"sky",                 1, 0, OPT_SKYNAME},
			{"skythr",              1, 0, OPT_SKYTHRESH},
			{"skymin",              1, 0, OPT_SKYMINFRAME},
			{"skysave",     	0, 0, OPT_SKYSAVE},

			{"mff",			1, 0, OPT_MFFNAME},
			{"mffsave",		1, 0, OPT_MFFSAVE},

			{"scanrej",     	1, 0, OPT_SCANREJ},

			{"pixrej",              1, 0, OPT_PIXELREJ},
			{"medianreg",   	1, 0, OPT_MEDIANREG},
			{"ksize",               1, 0, OPT_KERNELSIZE},

			{"science",		1, 0, OPT_SCINAME},
			{"nosat",		0, 0, OPT_SATCHECK},
			{"satlevel",		1, 0, OPT_SATLEVEL},
			{"satmax",		1, 0, OPT_SATMAX},

			{"split",              1, 0, OPT_SPLIT},

			{0, 0, 0, 0}

		} ;
		c = getopt_long(argc,
				argv,
				"Ldhx:",
				long_options,
				&option_index) ;
		if (c==-1)
			break ;
		switch(c)
		{

			/* Standard option: display license undocumented option */
			case OPT_LICENSE:
			case 'L':
				eclipse_display_license() ;
				return 0 ;

				/* Standard option : help */
			case OPT_HELP:
			case 'h':
				usage(argv[0]) ;
				break ;

				/* Standard option: version */
			case OPT_VERSION:
				print_eclipse_version() ;
				printf("qfits version: %s\n",qfits_version());
				printf("mefpp recipe version: %s\n", recipe_version);
				printf("-----\n");
				return NULL ;

			case OPT_NOVERIFY:
				bb->noverify = 1;
				break ;

                        case OPT_PAFNAME:
                                bb->name_paf = strdup(optarg);
                                break ;

				/* Local option: extension number to consider */
			case OPT_XTNUM:
			case 'x':
				bb->xtnum = atoi(optarg);
				break ;

				/* Local option: dump default values and exit */
			case 'd':
				display_params = 1 ;
				break ;

			case OPT_BIASNAME:
				bb->name_bias = strdup(optarg);
				break ;

			case OPT_BIASSUB:
				bb->bias_subtract = 1 ;
				break ;

			case OPT_BIASSAVE:
				bb->bias_save = 1 ;
				break ;

			case OPT_BIASKAPPA1:
				bb->bias_kappa1 = atof(optarg) ;
				break ;

			case OPT_BPMNAME:
				bb->name_bpm = strdup(optarg);
				break ;

			case OPT_DOMENAME:
				bb->name_dome = strdup(optarg);
				break ;

			case OPT_DOMETHRESH:
				sscanf(optarg, "%lg %lg",
						&(bb->dome_framethr_lo),
						&(bb->dome_framethr_hi));
				break;

			case OPT_DOMEMINFRAME:
				sscanf(optarg, "%d", &(bb->dome_minframe));
				break ;

			case OPT_DOMESAVE:
				bb->dome_save = 1 ;
				break;

			case OPT_SKYNAME:
				bb->name_sky = strdup(optarg);
				break ;

			case OPT_SKYTHRESH:
				sscanf(optarg, "%lg %lg",
						&(bb->sky_framethr_lo),
						&(bb->sky_framethr_hi));
				break ;
			case OPT_SKYMINFRAME:
				sscanf(optarg, "%d", &(bb->sky_minframe));
				break ;

			case OPT_SKYSAVE:
				bb->sky_save = 1 ;
				break;

			case OPT_MFFNAME:
				bb->name_mf 	= strdup(optarg);
				break;

			case OPT_MFFSAVE:
                                bb->name_mf_o      = strdup(optarg);
                                break;

			case OPT_SCANREJ:
				sscanf(optarg, "%d %d",
						&(bb->scanrej[0]),
						&(bb->scanrej[1]));
				break ;

			case OPT_PIXELREJ:
				sscanf(optarg, "%lg %lg",
						&(bb->pixrej_lo),
						&(bb->pixrej_hi));
				break ;

			case OPT_MEDIANREG:
				sscanf(optarg, "%d %d %d %d",
						&(bb->median_reg[0]),
						&(bb->median_reg[1]),
						&(bb->median_reg[2]),
						&(bb->median_reg[3]));
				bb->median_surf   = (bb->median_reg[1]-bb->median_reg[0]+1) *
					(bb->median_reg[3]-bb->median_reg[2]+1);

				break ;

			case OPT_SCINAME:
				bb->science_name_i = strdup(optarg);
				break ;

			case OPT_SATCHECK:
				bb->sat_check = 0;
				break;

			case OPT_SATLEVEL:
				bb->sat_level = atof(optarg);
				break;


			case OPT_SATMAX:
				bb->sat_max = atof(optarg);
				if ( (bb->sat_max<1e-4) || (bb->sat_max>(1.0-1e-4)) ) {
				   e_error("in --satmax option");
				   e_error("invalid percentage: should be in [0..1]");
				   mef_bb_del(bb);
				   return NULL;
				}
				break;

                        case OPT_SPLIT:
				bb->name_split = strdup(optarg);
				break;

			default:
				usage(argv[0]) ;
				e_comment(0,"Using %s as PAF name",bb->name_paf);
				break ;
		}

	}
	/* Get output file name */
	if ((argc-optind)>=1) {
	    bb->name_mf_o = strdup(argv[optind]);
	    e_comment(0,"Using %s as output master flat name",bb->name_mf_o);
	}

	if (display_params) {
		mef_bb_dump(bb, stdout);
	}
	return bb;
}

#define ALGPARTS		10
int mef_engine(mef_bb * bb)
{
	cube_t *	prep=NULL;
	image_t	*	flat_dome=NULL ;
	image_t	*	flat_sky=NULL ;
	image_t	*	flat_combined=NULL ;
	image_t *	bias=NULL;
	image_t 	*bpm=NULL;
	pixelmap	*bp_map=NULL;
	framelist *	flist ;
	framelist	*fnames;
	qfits_header	*fh;
	qfits_header	*fh_aux1, *fh_aux2;
	int		part ;
	int		xtnum;
	int		nxts;
	int	*	xts ;
	int		i, j ;
	int		zIndex ;
	int		p;
	char		name_o[FILENAMESZ];
	char		cval[80];

	/* if we request spliting we just do that */
	if (bb->name_split != NULL) {
           if ( (fnames = framelist_load(bb->name_split)) == NULL) {
             if (is_fits_file(bb->name_split)) {
                   fnames = framelist_new(1);
                   fnames->name[0] = strdup(bb->name_split);
             } else {
                   e_error("mef_engine: %s is not a framelist or a FITS file. Aborting", bb->name_split);
                   return -1 ;
             }
           }
           for (i=0 ; i<fnames->n ; i++) {
		e_comment(0, "---> Splitting file %s ---> %s", 
				get_basename(fnames->name[i]),
				get_rootname(get_basename(fnames->name[i])));
		mef_split(get_basename(fnames->name[i]), get_rootname(get_basename(fnames->name[i])), 0);
           }
           framelist_del(fnames);
	   return 0;
	}

	/* Check that input names are there */
	if (bb->science_name_i != NULL && ( bb->name_bias == NULL && 
					((bb->name_dome == NULL && bb->name_sky == NULL) || 
					bb->name_mf == NULL))) {
		e_error("no name provided for dome or sky");
		mef_bb_del(bb);
		return -1 ;
	}

	/* Further  validate the data sets for consistency */

	/* First the calibrating frames ... */
           
           //if (mef_valid_subset(bb,"bpm")) {
           //     e_error("Inconsistent data set. Either invalid FITS files,");
           //     e_error("multiple filters, or multiple binning factors in the data set.");
           //     mef_bb_del(bb);
           //     return -1;
           //}
          

           if (mef_valid_subset(bb,"bias")) {
                e_error("Inconsistent data set. Either invalid FITS files,");
                e_error("multiple filters, or multiple binning factors in the data set.");
                mef_bb_del(bb);
                return -1;
           }
           if (bb->name_dome!=NULL) {
              if (mef_valid_subset(bb,"dome")) {
                 e_error("Inconsistent data set. Either invalid FITS files,");
                 e_error("multiple filters, or multiple binning factors in the data set.");
                 mef_bb_del(bb);
                 return -1;
              }
           }
           if (bb->name_sky!=NULL) {
              if (mef_valid_subset(bb,"sky")) {
                 e_error("Inconsistent data set. Either invalid FITS files,");
                 e_error("multiple filters, or multiple binning factors in the data set.");
                 mef_bb_del(bb);
                 return -1;
              }
           }


	   /* ... then the science frames. */
	   if (mef_valid_subset(bb,"science")) {
                e_error("Inconsistent data set. Either invalid FITS files,");
                e_error("multiple filters, or multiple binning factors in the data set.");
                mef_bb_del(bb);
                return -1;
           }

	/* prepare to loop over extensions*/
	xtnum = bb->xtnum;
	if (xtnum<1) {
		if ((nxts = bb->nchips)<1) {
		  e_error("Attempting to handle detector with %d chips",bb->nchips);	
		  return -1;
		}
		xts = malloc(nxts * sizeof(int)) ;
		for (j=0 ; j<nxts ; j++) {
			xts[j]=j+1 ;
		}
	} else {
		nxts = 1 ;
		xts = malloc(nxts * sizeof(int)) ;
		xts[0] = xtnum ;
	}
	bb->nxts = nxts ;	/* we share the total number of extensions */
	/*
	 * Now that we know the number of extensions that
	 * we are processing we allocate space for a few
	 * important bookeeping variables. This will save
	 * us from having to do a "gain harmonization"
	 * later on.
	 */
	bb->bias_median  = (float *) malloc(nxts*sizeof(float));
	bb->bias_nplanes =   (int *) malloc(nxts*sizeof(int));
	bb->dome_median  = (float *) malloc(nxts*sizeof(float));
	bb->dome_nplanes =   (int *) malloc(nxts*sizeof(int));
	bb->sky_median   = (float *) malloc(nxts*sizeof(float));
	bb->sky_nplanes  =   (int *) malloc(nxts*sizeof(int));
	bb->flat_median  = (float *) malloc(nxts*sizeof(float));

	for (j=0 ; j<nxts ; j++) {
		bb->bias_median[j] 	= 0.0;
		bb->bias_nplanes[j] 	= 0;
		bb->dome_median[j] 	= 0.0;
		bb->dome_nplanes[j] 	= 0;
		bb->sky_median[j]  	= 0.0;
		bb->sky_nplanes[j]  	= 0;
		bb->flat_median[j] 	= 0.0;
	}


	/* Go extension after extension */
	e_comment(0, "---> START MEF calibration engine");
	for (j=0 ; j<nxts ; j++) {
		/*
		 * we set the extension we are working on
		 */
		bb->xtnum = xts[j];
		if (bb->nxts == 1) {    /* if we work in only one extension */
                    zIndex = 0;
                } else {                        /* we are working in all the extensions */
                    zIndex = bb->xtnum-1;
                }

		part = 0;

		e_comment(0,"---> Working in extension %d of %d\n\n",bb->xtnum,nxts);
		/*
		 * building/reading BIAS 
		 */

		/*
		 * if input name is FITS file we assume that it is an already constructed
		 * master bias 
		 */
		part++;
		e_comment(0,"---> [%d/%d] Part %d in %d: BIAS construction/reading",xts[j],nxts,part,ALGPARTS);
		if (is_fits_file(bb->name_bias) == 1) {
		    bias = mef_load_ext(bb->name_bias,bb->xtnum);
		    bb->bias_median[zIndex] = image_getmedian(bias);
		    bb->bias_nplanes[zIndex] = 1;
		    e_comment(1,"bias median value: %f",bb->bias_median[zIndex]);
		} else {
		    bias = mef_build_cal(bb, "bias");
		    e_comment(1,"back in the grid");
		    if (bias==NULL) {
			e_error("in bias  production: aborting");
			return -1 ;
		    }
		    if (bb->bias_save) {
			mef_save(bb,bias,"bias");
		    }
		    e_comment(1,"       bias_median = %f  bias_nplanes = %d",\
				    bb->bias_median[j], bb->bias_nplanes[j]);
		}

		/* 
		 * building/reading BPM 
		 */
		part++ ;
		e_comment(0,"---> [%d/%d] Part %d in %d: BPM construction/reading",xts[j],nxts,part,ALGPARTS);
		sprintf(cval,"%s_%02d.fits",bb->name_bpm,xts[j]);
		e_comment(0,"     reding file %s",cval);
		if (is_fits_file(cval) == 1) {
		    e_comment(1,"reading bad pixel map [%s]",cval);
		    bp_map = pixelmap_load(cval);
		    e_comment(1,"done");
		} else {
		    bp_map = (pixelmap *) mef_build_bpm(bb,bias);
		    if (bp_map == NULL) {
			e_error("in BPM production: aborting");
			if (bias != NULL) image_del(bias);
			return -1;
		    }
		}

		/*
		 * building/reading dome flat
		 */
		if (bb->name_dome != NULL) {
		    part++ ;
		    if (is_fits_file(bb->name_mf) != 1) {
		       e_comment(0,"---> [%d/%d] Part %d in %d: Dome flat construction",xts[j],nxts,part,ALGPARTS);
		       if (is_fits_file(bb->name_dome)) {
		           flat_dome = mef_load_ext(bb->name_dome,bb->xtnum);
		           bb->dome_median[zIndex] = image_getmedian(flat_dome);
                           bb->dome_nplanes[zIndex] = 1;
		           e_comment(1,"dome median value: %f",bb->dome_median[zIndex]);
                       } else {
		           flat_dome = mef_build_cal(bb, "dome");
		           if (flat_dome==NULL) {
		   	       e_error("in dome flat production: aborting");
		   	       return -1 ;
		           }
		           if (bb->dome_save) {
		   	       mef_save(bb, flat_dome, "dome");
		           }
		           e_comment(1,"       dome_median = %f  dome_nplanes = %d",\
				bb->dome_median[j], bb->dome_nplanes[j]);

		       }
		    } else {
		       e_comment(0,"---> [%d/%d] Part %d in %d: skipping dome flat construction",xts[j],nxts,part,ALGPARTS);
		    }
		}

		/*
		 * building/reading sky flat
		 */
		 if (bb->name_sky != NULL) {
		    part++ ;
		    if (is_fits_file(bb->name_mf) != 1) {
		       if (is_fits_file(bb->name_sky)) {
		           e_comment(0,"---> [%d/%d] Part %d in %d: skipping sky flat construction",xts[j],nxts,part,ALGPARTS);
		           flat_sky = mef_load_ext(bb->name_sky,bb->xtnum);
		           bb->sky_median[zIndex] = image_getmedian(flat_sky);
                           bb->sky_nplanes[zIndex] = 1;
		           e_comment(1,"sky median value: %f",bb->sky_median[zIndex]);
                       } else {
		           e_comment(0,"---> [%d/%d] Part %d in %d: Sky flat construction",xts[j],nxts,part,ALGPARTS);
		           flat_sky = mef_build_cal(bb, "sky");
		           if (flat_sky==NULL) {
			       e_error("in sky flat production: aborting");
			       image_del(flat_dome);
			       return -1 ;
		           }
		           if (bb->sky_save) {
		   	       mef_save(bb, flat_sky, "sky");
		           }
		           e_comment(1,"       sky_median = %f  sky_nplanes = %d",\
		    		bb->sky_median[j], bb->sky_nplanes[j]);

		       }
		    } else {
		       e_comment(0,"---> [%d/%d] Part %d in %d: skipping sky flat construction",xts[j],nxts,part,ALGPARTS);
		    }
		}

		/*
		 * building/reading master flat
		 */
		if ( ( bb->name_sky != NULL && bb->name_dome != NULL ) || bb->name_mf != NULL) {
		    part++ ;
		    e_comment(0,"---> Inside master flat part");
		    if (is_fits_file(bb->name_mf)==1) {
		        e_comment(0,"---> [%d/%d] Part %d in %d: skipping dome/sky combination",xts[j],nxts,part,ALGPARTS);
		        e_comment(1,"reading master flat from file %s",bb->name_mf);
		        flat_combined = mef_load_ext(bb->name_mf,bb->xtnum);
		        bb->flat_median[zIndex] = image_getmedian(flat_combined);
		        e_comment(1,"master flat median value: %f",bb->flat_median[zIndex]);
		    } else {
		        e_comment(0,"---> [%d/%d] Part %d in %d: Dome/Sky combination",xts[j],nxts,part,ALGPARTS);
		        if (bb->bias_subtract) {
		           flat_combined = mef_ff_combine(bb, flat_dome, flat_sky, bias, bp_map);
		        } else {
		           flat_combined = mef_ff_combine(bb, flat_dome, flat_sky, NULL, bp_map);
		        }
		        e_comment(1,"master flat median value: %f",bb->flat_median[zIndex]);

		        if (flat_combined==NULL) {
		    	    e_error("combining dome and sky to make flat");
		    	    return -1 ;
		        }
		        mef_save(bb, flat_combined, "combined");
		        if (flat_dome != NULL) { image_del(flat_dome);}
		        if (flat_sky != NULL) {image_del(flat_sky);}
		    }
		}



	    if (bb->science_name_i != NULL) {
		/*
		 * Loading input cube with science frames
		 */
		part++;
		e_comment(0,"---> [%d/%d] Part %d of %d: science frames loading.",xts[j],nxts,part,ALGPARTS,bb->science_name_i);
		
		prep = mef_cube_load(bb->science_name_i, bb->xtnum);
		e_comment(1,"Done.");

		if (prep==NULL) {
	           e_error("loading input data [%s]", bb->science_name_i);
	           return -1 ;
	        }

		/* Load frame names for error messages */
		if (is_fits_file(bb->science_name_i)==1) {
	            bb->np = 1 ;
	            bb->science_frame_name = malloc(sizeof(char*));
	            bb->science_frame_name[0] = strdup(bb->science_name_i);
	        } else {
                    flist = framelist_load(bb->science_name_i);
                    bb->np = flist->n ;
                    bb->science_frame_name = malloc(flist->n * sizeof(char*));
                    for (i=0 ; i<flist->n ; i++) {
                       bb->science_frame_name[i] = strdup(flist->name[i]);
		       e_comment(1,"Frame %d: %s",i,bb->science_frame_name[i]);
                    }
	            framelist_del(flist); 
	        }

		/* 
		 * Saturation check if requested
		 */
		part++;
		e_comment(0, "---> [%d/%d] Part %d of %d: checking saturation level", xts[j],nxts,part, ALGPARTS); 
		if (bb->sat_check) {
		   if (mef_saturation_check(prep, bb)!=0) {
			e_error("in saturation check: aborting");
			image_del(bias);
			image_del(flat_combined);
			cube_del(prep);
			return;
		   }
		} else {
		   e_comment(1, "saturation check skipped (on request)");
		}

		/* Overscan/prescan correction and trimming */
		part++;
		e_comment(0, "--> [%d/%d] Part %d of %d: applying overscan/prescan/trimming", xts[j], nxts, part, ALGPARTS);
		mef_cube_overscan_correction(prep,bb);

		/* Bias correction */

	         part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: bias subtraction", xts[j], nxts, part, ALGPARTS);
		 if (bias == NULL) {
		     e_error("no  bias frame [%s]", bb->name_bias);
		     cube_del(prep);
		     return -1 ;
	         }
		 if (cube_sub_im(prep, bias)!=0) {
	             e_error("in bias subtraction: aborting");
		     image_del(bias);
		     cube_del(prep);
		     return -1 ;
		 }

		
		 /* Flat-field correction */
		 part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: flatfield division", xts[j], nxts, part, ALGPARTS);
		 if (flat_combined == NULL) {
		     e_error("NULL pointer to  flat-field frame");
		     cube_del(prep);
		     return -1 ;
		 }
		 if (cube_div_im(prep, flat_combined)!=0) {
	             e_error("in flat-field division: aborting");
		     image_del(flat_combined);
		     cube_del(prep);
		     return -1 ;
		 }

		 /* Save results */
		 part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: saving results", xts[j], nxts, part, ALGPARTS);
		 /* Loop over planes in the input cube */
		 for (p=0 ; p<prep->np ; p++) {
		    /* Build output name */
		    sprintf(name_o, "%s_pre.fits", get_rootname(get_basename(bb->science_frame_name[p])));
		    e_comment(1, "saving calibrated extension %d of file %s into: [%s]", \
				    xts[j], bb->science_frame_name[p], name_o);
		    if (bb->xtnum == 1) {
		       /* Read FITS header from input file */
		       fh = qfits_header_read(bb->science_frame_name[p]);
		       if (fh==NULL) {
		          e_error("reading FITS header from [%s]", bb->science_frame_name[p]);
		          return -1 ;
		       }
		       /*
			* we make sure that the EXTEND keyword goes right after NAXIS
			*/
		       qfits_header_del(fh,"EXTEND");
		       qfits_header_add_after(fh,"NAXIS", "EXTEND","T","Extension may be present.",NULL);
		       /*...and that we have real*4 data */
		       sprintf(cval,"%d", BPP_DEFAULT);
		       qfits_header_mod(fh,"BITPIX",cval, "Bits per pixel");
		       save_mef_hdrdump(NULL,name_o,fh,BPP_DEFAULT);
		       qfits_header_destroy(fh);
		    }
		    e_comment(1, "reading extension header of file %s",bb->science_frame_name[p]);
		    fh_aux1 = mef_header_ext(bb->science_frame_name[p],bb);
		    e_comment(1, "done.");
		    e_comment(1, "building subset of main headers with proper NAXIS keywords");
		    fh_aux2 = mef_header_mainsubset(bb,prep->plane[p]);
		    e_comment(1, "done.");
		    e_comment(1, "merging headers");
		    fh = fits_header_merge(fh_aux1,fh_aux2);
		    e_comment(1, "done.");
		    e_comment(1, "deleting the SIMPLE keyword from the extension");
		    qfits_header_del(fh,"SIMPLE");
		    e_comment(1, "done.");
		    e_comment(1, "and finally changing BZERO to 0.0 and BSCALE to 1.0");
		    qfits_header_mod(fh,"BZERO","0.0","pixel=FITS*BSCALE+BZERO");
		    qfits_header_mod(fh, "BSCALE", "1.0", "pixel=FITS*BSCALE+BZERO");
		    e_comment(1, "done");
		    e_comment(1, "dumping extension headers and pixel data of extension %d calibrated %s frame",
				    xts[j],bb->science_frame_name[p]);
		    save_mef_hdrdump(prep->plane[p],name_o,fh,BPP_DEFAULT);
		    e_comment(1, "done.");

		    qfits_header_destroy(fh);
		    qfits_header_destroy(fh_aux1);
		    qfits_header_destroy(fh_aux2);
		 }
		 cube_del(prep);
	    }
	    if (bias != NULL) {
		e_comment(1, "deallocating bias memory");
		image_del(bias);
	    }
	    if (bp_map != NULL) {
		e_comment(1, "deallocating bp_map  memory");
		pixelmap_del(bp_map);
	    }
	    if (flat_combined != NULL) {
		e_comment(1, "deallocating flat_combined memory");
		image_del(flat_combined);
		e_comment(1, "done");
	    }
	}
	e_comment(0, "--> STOP  MEF calibration engine");
	return 0 ;
}
#undef ALGPARTS


/*---------------------------------------------------------------------------
  Main	
  ---------------------------------------------------------------------------*/

int main(int argc, char *argv[])
{

	mef_bb*	bb ;

	/*printf("argc = %d\n\n",argc);*/
	printf("\n\n\n ----------> MEFPP REDUCTION ENGINE. VERSION: %s <----------\n\n\n", recipe_version);
	if (argc == 1) {
          usage(argv[0]);
	  return -1;
        }

	/* Initialize eclipse environment */
	printf("\nInitializing eclipse environment");
	eclipse_init() ;

	/* Get parameters for processing */
	printf("\nLoading parameters...\n");
	if ( (bb = mef_bb_load(argc,argv)) == NULL ) {
	   return 0;
	}

	/* Startup MEF calibration  engine */

	mef_engine(bb);
	mef_bb_del(bb);

	if (debug_active()) xmemory_status() ;
	return 0 ;
} 



/*
 * This function only gives the usage for the program
 */

	static void
usage(char *pname)
{
	hello_world(pname, prog_desc) ;
	printf("use : %s [options] <MEF extension> [outname]\n", pname) ;
	printf(
			"options are:\n"
			"\t--pafname <name>   Name of PAF file, full path should be given\n"
			"\t-x or --xtnum <n>  Xtension to consider (0=all)\n"
			"\n"
			"\t--split	      Name of file or of framelist with files to split\n"
			"\n"
			"\t--bias <name>      Name of a bias to subtract (optional)\n"
			"\t--biassave         Switch to save the newly created bias frame\n"
			"\n"
			"\t--bpm <name>	      Name of list of files for bpm creation\n"
			"\n"
			"\t--dome <name>      Name of the dome input list\n"
			"\t--domethr 'lo hi'  Low and high threshold for dome frames\n"
			"\t--domemin <n>      Min number of frames for dome flat\n"
			"\t--domesave         Save dome flat to flat_dome.fits in cwd\n"
			"\n"
			"\t--sky <name>       Name of sky input list\n"
			"\t--skythr 'lo hi;   Low and high threshold for sky frames\n"
			"\t--skymin <n>       Min number of frames for sky flat\n"
			"\t--skysave          Save sky flat to flat_sky.fits in cwd\n"
			"\n"
			"\t--mff <name>	      Name of master flat field to create/to use\n"
			"\t--mffsave	      Switch to save a newly created master flat field\n"
			"\t--scanrej 'min max' Scan rejection definition\n"
			"\n"
			"\t--science	      List of science frames to reduce\n"
			"\n"
			"\t--pixrej 'lo hi'   Pixel rejection sigma threshold\n"
			"\t--medianreg 'xmin xmax ymin ymax'  Median region definition\n"
			"\n"
			"\t--ksize <n>        Smoothing kernel size\n"
			"\n"
			"\t-d                 Print out configuration parameters and run\n"
			"\n\n");
	exit(1) ;
} 

