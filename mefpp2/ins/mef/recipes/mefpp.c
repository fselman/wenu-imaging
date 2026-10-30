
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
#include <errno.h>
#include <ctype.h>
#include <float.h>
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
#define OPT_OUTPUT_DIR 3200
#define OPT_WORK_DIR 3201
#define OPT_LIST_BASE 3202
#define OPT_LOG_FILE 3203


static char recipe_version[] = "mefpp-2.0.0";

static void usage(char *pname) ;
static char prog_desc[] = "MEF master calibration frames creation" ;

/*
qfits_header *fits_header_merge(qfits_header *, qfits_header *);
qfits_header *mef_header_primary(char *);
qfits_header *mef_header_ext(char *, int);
qfits_header *mef_header_eclipse(mef_bb *,char *);
void save_mef_hdrdump(image_t *,char *,qfits_header *,int);
*/

		static struct option long_options[] =
		{
			{"license",         0, 0, OPT_LICENSE},
			{"help",            0, 0, OPT_HELP},
			{"version",         0, 0, OPT_VERSION},

			{"noverify",	    0, 0, OPT_NOVERIFY},

                        {"pafname",        1, 0, OPT_PAFNAME},
                        {"output-dir", 1, 0, OPT_OUTPUT_DIR},
                        {"work-dir", 1, 0, OPT_WORK_DIR},
                        {"list-base", 1, 0, OPT_LIST_BASE},
                        {"log-file", 1, 0, OPT_LOG_FILE},

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

/* getopt must be restarted after selecting configuration and informational
 * requests, before applying the existing processing overrides (#76). */
static void reset_options(void)
{
    /* eclipse.h maps optind to the bundled parser, on every supported OS. */
    optind = 0;
}

mef_bb * mef_bb_load (int argc, char *argv[], int *load_status)
{
	int             c ;
	int         display_params ;
	char * pafname = "mefpp.paf";
    char *end;
    double satmax;
    char * date_ptr;
    const char *output_dir = NULL, *work_dir = NULL, *list_base = NULL, *log_file = NULL;
    int explicit_paf = 0;
    mef_paths *paths = NULL;
	mef_bb*   bb ;

	display_params = 0 ;

    /* Configuration is selected before constructing any processing context. */
    *load_status = EXIT_FAILURE;
    reset_options();
    while (1) {
        int option_index = 0;
        c = getopt_long(argc, argv, "Ldhx:", long_options, &option_index);
        if (c == -1) break;
        switch (c) {
        case OPT_HELP:
        case 'h':
            usage(argv[0]);
            *load_status = EXIT_SUCCESS;
            return NULL;
        case OPT_VERSION:
            print_eclipse_version();
            printf("qfits version: %s\n", qfits_version());
            printf("mefpp recipe version: %s\n", recipe_version);
            *load_status = EXIT_SUCCESS;
            return NULL;
        case OPT_LICENSE:
        case 'L':
            eclipse_display_license();
            *load_status = EXIT_SUCCESS;
            return NULL;
        case OPT_PAFNAME:
            pafname = optarg; explicit_paf = 1;
            break;
        case OPT_OUTPUT_DIR: output_dir = optarg; break;
        case OPT_WORK_DIR: work_dir = optarg; break;
        case OPT_LIST_BASE: list_base = optarg; break;
        case OPT_LOG_FILE: log_file = optarg; break;
        case '?':
        case ':':
            return NULL;
        default:
            break;
        }
    }
    if (output_dir || work_dir || list_base || log_file) {
        if (!output_dir || !work_dir || !explicit_paf) {
            e_error("explicit paths require --pafname, --output-dir and --work-dir");
            return NULL;
        }
        paths = mef_paths_new(output_dir, work_dir, list_base, log_file);
        if (paths == NULL) return NULL;
        if (xmemory_set_tmpdir(mef_paths_work(paths)) != 0) {
            mef_paths_del(paths); return NULL;
        }
    }
    bb = mef_bb_new_from_paf(pafname);
    if (bb == NULL) { mef_paths_del(paths); return NULL; }
    bb->paths = paths;
    /* The PAF constructor seeds the legacy BPM discovery prefix. Explicit
     * execution accepts a BPM only when --bpm selects it (#159). */
    if (paths != NULL) { free(bb->name_bpm); bb->name_bpm = NULL; }
    reset_options();

	while (1) {
		int     option_index = 0 ;

		c = getopt_long(argc,
				argv,
				"Ldhx:",
				long_options,
				&option_index) ;
		if (c==-1)
			break ;
		switch(c)
		{

			case OPT_NOVERIFY:
				bb->noverify = 1;
				break ;

                        case OPT_OUTPUT_DIR:
                        case OPT_WORK_DIR:
                        case OPT_LIST_BASE:
                        case OPT_LOG_FILE:
                        case OPT_PAFNAME:
                                /* Already selected and copied during context construction. */
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
				free(bb->name_bias);
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
				free(bb->name_bpm);
                bb->name_bpm = strdup(optarg);
				break ;

			case OPT_DOMENAME:
				free(bb->name_dome);
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
				free(bb->name_sky);
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
				free(bb->name_mf);
                bb->name_mf 	= strdup(optarg);
				break;

			case OPT_MFFSAVE:
                                free(bb->name_mf_o);
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
				free(bb->science_name_i);
                bb->science_name_i = strdup(optarg);
				break ;

			case OPT_SATCHECK:
				bb->sat_check = 0;
				break;

			case OPT_SATLEVEL:
				bb->sat_level = atof(optarg);
				break;


			case OPT_SATMAX:
				errno = 0;
                satmax = strtod(optarg, &end);
                while (isspace((unsigned char)*end)) end++;
                if (end == optarg || *end != '\0' || errno == ERANGE ||
                    satmax != satmax || satmax > DBL_MAX || satmax < -DBL_MAX ||
                    satmax < 1e-4 || satmax > (1.0-1e-4)) {
				   e_error("in --satmax option");
				   e_error("invalid --satmax [%s]: expected a number in [0.0001..0.9999]", optarg);
				   mef_bb_del(bb);
				   return NULL;
                }
                bb->sat_max = satmax;
                break;

                        case OPT_SPLIT:
				free(bb->name_split);
                bb->name_split = strdup(optarg);
				break;

			default:
                usage(argv[0]);
                mef_bb_del(bb);
                return NULL;
		}

	}
	/* Get output file name */
	if ((argc-optind)>=1) {
	    free(bb->name_mf_o);
                bb->name_mf_o = strdup(argv[optind]);
	    e_comment(0,"Using %s as output master flat name",bb->name_mf_o);
	}

    if (bb->paths != NULL && mef_paths_bind(bb) != 0) {
        e_error("cannot resolve explicit input paths"); mef_bb_del(bb); return NULL;
    }
	if (display_params) {
        date_ptr = get_datetime_iso8601();
        e_comment(1,"date: %s", date_ptr);
		mef_bb_dump(bb, stdout);
	}
	*load_status = EXIT_SUCCESS;
	return bb;
}

#define ALGPARTS		10
/* Borrowed context: the successful loader caller releases bb exactly once (#75). */
int mef_engine(mef_bb * bb)
{
	cube_t *	prep=NULL;
	image_t	*	flat_dome=NULL ;
	image_t	*	flat_sky=NULL ;
	image_t	*	flat_combined=NULL ;
	image_t *	bias=NULL;
	image_t 	*bpm=NULL;
	pixelmap	*bp_map=NULL;
	framelist *	flist = NULL ;
	framelist	*fnames;
	qfits_header	*fh = NULL;
    qfits_header    *fh_ext = NULL;
	qfits_header	*fh_aux1 = NULL, *fh_aux2 = NULL;
	int		part ;
	int		xtnum;
	int		nxts;
	int	*	xts = NULL ;
	int		i, j ;
	int		zIndex ;
	int		p;
	char		name_o[FILENAMESZ];
    char    *   bias_xtname = NULL;
    char    *   bpm_xtname = NULL;
    char    *   dome_xtname = NULL;
    char    *   sky_xtname = NULL;
    char    *   mff_xtname = NULL;
    char    *   sci_xtname = NULL;
    char    *   cval_ptr;
	char		cval[FILENAMESZ];
    char        cval2[80];
    double   exptime, mjdobs, mjdend;
    float   science_mean, science_median, science_stdev;
    int     science_nplanes;


	/* if we request spliting we just do that */
	if (bb->name_split != NULL) {
           if ( (fnames = mef_paths_frames(bb->paths, bb->name_split)) == NULL) {
             if (is_fits_file(bb->name_split)) {
                   fnames = framelist_new(1);
                   fnames->name[0] = strdup(bb->name_split);
             } else {
                   e_error("mef_engine: %s is not a framelist or a FITS file. Aborting", bb->name_split);
                   return -1 ;
             }
           }
           if (mef_paths_split_preflight(bb, fnames) != 0) { framelist_del(fnames); return -1; }
           for (i=0 ; i<fnames->n ; i++) {
        char *split_root;
		e_comment(0, "---> Splitting file %s ---> %s", 
				get_basename(fnames->name[i]),
				get_rootname(get_basename(fnames->name[i])));
        split_root = mef_paths_output(bb->paths, get_rootname(get_basename(fnames->name[i])));
        if (split_root == NULL || mef_split(fnames->name[i], split_root, 0) != 0) {
            free(split_root);
            framelist_del(fnames);
            return -1;
        }
        free(split_root);
           }
           framelist_del(fnames);
	   return 0;
	}

	/* Check that input names are there */
	if (bb->science_name_i != NULL && ( bb->name_bias == NULL && 
					((bb->name_dome == NULL && bb->name_sky == NULL) || 
					bb->name_mf == NULL))) {
		e_error("no name provided for dome or sky");

		return -1 ;
	}

	/* Further  validate the data sets for consistency */

	/* First the calibrating frames ... */
           
           /*if (mef_valid_subset(bb,"bpm")) { */
           /*     e_error("Inconsistent data set. Either invalid FITS files,"); */
           /*     e_error("multiple filters, or multiple binning factors in the data set."); */
           /*     mef_bb_del(bb); */
           /*     return -1; */
           /*} */
           /* */
          
            /* the validation of the bias subset must come first because
             * all processings need a bias frame, except the BPM, but when
             * building the BPM the name of the bpm file is a framelist name
             * from input. The validation of the bias subset writes the bb->bias_partition
             * which is tipically "1x1".
             */
           if (mef_valid_subset(bb,"bias")) {
                e_error("mef_engine: valid bias: Inconsistent data set. Either invalid FITS files,");
                e_error("mef_engine: valid bias: multiple filters, or multiple binning factors in the data set.");

                return -1;
           }

           if (mef_valid_subset(bb,"bpm")) {
                e_error("mef_engine: valid bpm: Inconsistent data set. Either invalid FITS files,");
                e_error("mef_engine: valid bpm: multiple filters, or multiple binning factors in the data set.");

                return -1;
           }

           if (bb->name_dome!=NULL) {
              if (mef_valid_subset(bb,"dome")) {
                 e_error("mef_engine: valid dome: Inconsistent data set. Either invalid FITS files,");
                 e_error("mef_engine: valid dome: multiple filters, or multiple binning factors in the data set.");

                 return -1;
              }
           }
           if (bb->name_sky!=NULL) {
              if (mef_valid_subset(bb,"sky")) {
                 e_error("mef_engine: valid sky: Inconsistent data set. Either invalid FITS files,");
                 e_error("mef_engine: valid sky: multiple filters, or multiple binning factors in the data set.");

                 return -1;
              }
           }


	   /* ... then the science frames. */
	   if (mef_valid_subset(bb,"science")) {
                e_error("mef_engine: valid science: Inconsistent data set. Either invalid FITS files,");
                e_error("mef_engine: valid science: multiple filters, or multiple binning factors in the data set.");

                return -1;
           }

    if (mef_paths_preflight(bb) != 0) return -1;
	/* prepare to loop over extensions*/
	xtnum = bb->xtnum;
    bb->xtname      = NULL;
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
    bb->bias_stdev   =  (float *)  malloc(nxts*sizeof(float));
	bb->bias_nplanes =   (int *) malloc(nxts*sizeof(int));
    bb->bias_framethr_lo  =  (float *)  malloc(nxts*sizeof(float));
    bb->bias_framethr_hi  =  (float *)  malloc(nxts*sizeof(float));
    bb->bias_avg1  =  (float *)  malloc(nxts*sizeof(float));
    bb->bias_sig1  =  (float *)  malloc(nxts*sizeof(float));

	bb->dome_median  = (float *) malloc(nxts*sizeof(float));
    bb->dome_stdev   =  (float *) malloc(nxts*sizeof(float));
	bb->dome_nplanes =   (int *) malloc(nxts*sizeof(int));

	bb->sky_median   = (float *) malloc(nxts*sizeof(float));
    bb->sky_stdev    = (float *) malloc(nxts*sizeof(float));
	bb->sky_nplanes  =   (int *) malloc(nxts*sizeof(int));

	bb->flat_median  = (float *) malloc(nxts*sizeof(float));
    bb->flat_stdev   = (float *) malloc(nxts*sizeof(float));
    bb->combined_flat_median  = (float *) malloc(nxts*sizeof(float));
    bb->combined_flat_stdev   = (float *) malloc(nxts*sizeof(float));

	for (j=0 ; j<nxts ; j++) {
		bb->bias_median[j] 	= 0.0;
        bb->bias_stdev[j]  = 0.0;
        bb->bias_framethr_lo[j]  = 0.0;
        bb->bias_framethr_hi[j]  = 0.0;
        bb->bias_avg1[j]  = 0.0;
        bb->bias_sig1[j]  = 0.0;
		bb->bias_nplanes[j] 	= 0;

		bb->dome_median[j] 	= 0.0;
        bb->dome_stdev[j] = 0.0;

		bb->sky_median[j]  	= 0.0;
        bb->sky_stdev[j] = 0.0;
		bb->sky_nplanes[j]  	= 0;

		bb->flat_median[j] 	= 0.0;
        bb->flat_stdev[j]  = 0.0;

        bb->combined_flat_median[j]  = 0.0;
        bb->combined_flat_stdev[j]  = 0.0;
	}


	/* Go extension after extension */
	e_comment(0, "---> START MEF calibration engine");
	for (j=0 ; j<nxts ; j++) {
		/*
		 * we set the extension we are working on
		 */
		bb->xtnum = xts[j];
        bb->xtname = NULL;
		if (bb->nxts == 1) {    /* if we work in only one extension */
                    zIndex = 0;
                } else {                        /* we are working in all the extensions */
                    zIndex = bb->xtnum-1;
                }

		part = 0;

		e_comment(0,"---> Working in extension %d of %d\n\n",bb->xtnum,nxts);

        /* We read the BPM file if it exists to load the orig_bpm variable 
         *
         * This has to be async in order to write the name in the master bias
         * which is the first master product created. In the future the
         * statistics for QC will use the BPM.
         *
         * */
        e_comment(0,"---> BPM name reading if it exists");
        if (xts[j]==1 && (bb->paths == NULL || bb->name_bpm != NULL)) {
            cval_ptr = bb->paths ? strdup(bb->name_bpm) : mef_get_output_filename(bb,"bpm");
            sprintf(cval, "%s", cval_ptr);
            free(cval_ptr);
            if (is_fits_file(cval) == 1) {
                e_comment(1, "mef_engine: reading BPM file: %s", cval);

                if ((fh = qfits_header_read(cval)) == NULL) {
                    e_error("mef_engine: cannot read headers from file %s", cval);
                    free(xts); return -1;
                }
                free(bb->orig_bpm);
                bb->orig_bpm = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                free(bb->name_bpm);
                bb->name_bpm = strdup(cval);
                e_comment(1, "mef_engine: using BPM file %s with ORIGFILE: %s", bb->name_bpm, bb->orig_bpm);
                qfits_header_destroy(fh); fh = NULL;
            }
        }

		/*
		 * building/reading BIAS 
		 */

		/*
		 * if input name is FITS file we assume that it is an already constructed
		 * master bias 
		 */
        if (bb->name_bias != NULL) {
		    part++;
		    e_comment(0,"---> [%d/%d] Part %d in %d: BIAS construction/reading",xts[j],nxts,part,ALGPARTS);
		    if (is_fits_file(bb->name_bias) == 1) {
                e_comment(0,"---> [%d/%d] Part %d in %d: BIAS reading",xts[j],nxts,part,ALGPARTS);
                /* we extract the origfile name of the file */
                if ( (fh = mef_header_primary_at(bb->name_bias, bb->paths)) == NULL) {
                    e_error("mef_engine: can not read %s primary headers",bb->name_bias);
                    free(xts); return -1;
                }
                free(bb->orig_bias);
                bb->orig_bias = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                qfits_header_destroy(fh); fh = NULL;
                e_comment(1,"mef_engine: using bias FITS frame with ORIGFILE: %s", bb->orig_bias);


               /* we read the extension name from the bias frame. */
                if ( (fh_ext = qfits_header_readext(bb->name_bias,bb->xtnum)) != NULL) {

                    bb->xtname =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                    e_comment(1,"mef_engine: working on extension %s", bb->xtname);
                    qfits_header_destroy(fh_ext); fh_ext = NULL;
                }
    
                bias = mef_load_ext(bb->name_bias,bb->xtnum);
                bb->bias_median[zIndex] = image_getmedian(bias);
                bb->bias_stdev[zIndex] = image_getstdev(bias);
                bb->bias_nplanes[zIndex] = 1;
                e_comment(1,"bias median value: %f   bias std dev value: %f",bb->bias_median[zIndex], bb->bias_stdev[zIndex]);

		    } else {

            /* Load frame names for error messages */
                e_comment(0,"---> [%d/%d] Part %d in %d: BIAS construction",xts[j],nxts,part,ALGPARTS);
                flist = mef_paths_frames(bb->paths, bb->name_bias);
                bb->bias_nframes = flist->n ;
                bb->bias_frame_name = calloc(flist->n, sizeof(char*));
                bb->bias_scan_median = (float *)  malloc(flist->n*sizeof(float));
                bb->bias_scan_stdev = (float *)  malloc(flist->n*sizeof(float));
                for (i=0 ; i<flist->n ; i++) {
                    bb->bias_frame_name[i] = strdup(flist->name[i]);
                    bb->bias_scan_median[i] = 0.0;
                    bb->bias_scan_stdev[i] = 0.0;

                    /* we check extension names only on the first frame of the list.... */
                    if (i==0) {
                        if ( (fh_ext = qfits_header_readext(flist->name[i],bb->xtnum)) != NULL) {

                            bb->xtname =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                            e_comment(1,"mef_engine: working on extension %s", bb->xtname);
                            qfits_header_destroy(fh_ext); fh_ext = NULL;
                        }
                    }
                    e_comment(1,"Frame %d: %s",i,bb->bias_frame_name[i]);
                }
                framelist_del(flist); flist = NULL;


		        bias = mef_build_cal(bb, "bias");
		        e_comment(1,"back in the grid");
		        if (bias==NULL) {
			    e_error("in bias  production: aborting");
                free(xts); return -1 ;
		        }
		        if (bb->bias_save) {
			    if (mef_save(bb,bias,"bias") != 0) goto publication_failed;
		        }
		        e_comment(1,"       bias_median = %f  bias_nplanes = %d",\
				        bb->bias_median[j], bb->bias_nplanes[j]);
		    }
        }

		/* 
		 * building/reading BPM 
         *
         * Command: /opt/local/eclipse/bin/mefpp  --bpm bpm.list 2>&1 | tee mefpp.log
         *
		 */
        e_comment(1, "mef_engine: entering BPM part: name_bpm: %s  orig_bpm: %s", bb->name_bpm, bb->orig_bpm);
        if (bb->name_bpm != NULL) {
		    part++ ;
		    e_comment(0,"---> [%d/%d] Part %d in %d: BPM construction/reading",xts[j],nxts,part,ALGPARTS);

		    if (is_fits_file(bb->name_bpm) == 1) {

                /* we check the extension name which for the case of simple fits files is loaded in
                * the key ZNAME
                */
                if ((fh = qfits_header_read(bb->name_bpm)) == NULL) {
                    e_error("mef_engine: cannot read headers from file %s", bb->name_bpm);
                    free(xts); return -1;
                }
                if (xts[j]==1) {
                    free(bb->orig_bpm);
                    bb->orig_bpm = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                }
                qfits_header_destroy(fh); fh = NULL;

                /* we get the extension name from the extension headers */
                if ((fh_ext = qfits_header_readext(bb->name_bpm, bb->xtnum)) == NULL) {
                    e_error("mef_engine: cannot read headers from file %s", bb->name_bpm);
                    free(xts); return -1;
                }
                bpm_xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                qfits_header_destroy(fh_ext); fh_ext = NULL;

                if (bb->xtname == NULL) {

                    bb->xtname = strdup(bpm_xtname);
                    e_comment(1, "mef_engine: reading bad pixel map for extension %s", bb->xtname);
                } else {
                    e_comment(1, "mef_engine: reading bad pixel map for extension %s FROM extension %s", bb->xtname, bpm_xtname);
                }

                /* now we read the pixel map */
		        e_comment(1,"mef_engine: reading bad pixel map [%s]",bb->name_bpm);

                bp_map = pixelmap_loadext(bb->name_bpm, xts[j]);
		        e_comment(1,"mef_engine: done");
		    } else {
                sprintf(cval,"%02d",xts[j]);
                e_comment(1,"# ------------- BUILDING BAD PIXEL MASK %s --------------", cval);

                /* we first set the xtname variable in case we are building everything together... 
                * in this case here we check the extension name against that read during bias
                * reading or construction, as that came first.
                *
                * We check extension names only on the first frame of the list.... */
                e_comment(1,"mef_engine: loading framelist from  ascii file %s", bb->name_bpm);
                flist = mef_paths_frames(bb->paths, bb->name_bpm);
                if (flist==NULL) {
                    e_error("mef_engine: cannot load frame list [%s]", bb->name_bpm);
                    free(xts); return -1 ;
                }
                e_comment(1,"mef_engine: reading headers from %s", flist->name[0]);

                if ( (fh_ext = qfits_header_readext(flist->name[0],bb->xtnum)) != NULL) {
                    if (bb->xtname == NULL) {

                        bb->xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                        e_comment(1,"mef_engine: working on extension %s", bb->xtname);
                    } else {

                        bpm_xtname =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                        e_comment(1,"mef_engine: working on extension %s -- should be: %s", bpm_xtname, bb->xtname);
                    }
                    qfits_header_destroy(fh_ext); fh_ext = NULL;
                }


                bp_map = (pixelmap *) mef_build_bpm(bb,bias);
                framelist_del(flist); flist = NULL;
		        if (bp_map == NULL) {
			        e_error("in BPM production: aborting");
			        if (bias != NULL) image_del(bias); bias = NULL;
                        free(xts); return -1;
		        } else {
                    e_comment(1,"BPM created");
                    e_comment(1,"BPM with axes %d %d created%", bp_map->lx, bp_map->ly);
                }
		    }
        }

		/*
		 * building/reading dome flat
         *
         * command: /opt/local/eclipse/bin/mefpp --bias OCAM_MB_1x1.fits --dome dome.list --domesave 2>&1 | tee mefpp.log
         *
		 */
		if (bb->name_dome != NULL) {
		    part++ ;
		    if (is_fits_file(bb->name_mf) != 1) {
                if (is_fits_file(bb->name_dome)) {
                    e_comment(0,"---> [%d/%d] Part %d in %d: Skypping dome flat construction, reading it",xts[j],nxts,part,ALGPARTS);

                    /* we extract the origfile name of the file */
                    if ( (fh = mef_header_primary_at(bb->name_dome, bb->paths)) == NULL) {
                        e_error("mef_engine: can not read %s primary headers",bb->name_dome);
                        free(xts); return -1;
                    }
                    free(bb->orig_dome);
                    bb->orig_dome = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                    qfits_header_destroy(fh); fh = NULL;


                    /* we check the extension name 
                    */
                    if ((fh_ext = qfits_header_readext(bb->name_dome, bb->xtnum)) == NULL) {
                        e_error("mef_engine: cannot read headers from file %s extension %d", bb->name_dome, bb->xtnum);
                        free(xts); return -1;
                    }   
                    dome_xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                    qfits_header_destroy(fh_ext); fh_ext = NULL;
                    if (bb->xtname == NULL) {
                        e_comment(1, "mef_engine: EXTNAME should not be NULL at this point", dome_xtname);
                    } else {
                        e_comment(1, "mef_engine: reading dome ff pixel data for extension %s FROM extension %s", bb->xtname, dome_xtname);
                    }



                    e_comment(1,"mef_engine: using dome FITS frame with ORIGFILE: %s", bb->orig_dome);



		           flat_dome = mef_load_ext(bb->name_dome,bb->xtnum);
		           bb->dome_median[zIndex] = image_getmedian(flat_dome);
                           bb->dome_nplanes[zIndex] = 1;
		           e_comment(1,"dome median value: %f",bb->dome_median[zIndex]);
                } else {

                    e_comment(0,"---> [%d/%d] Part %d in %d: Dome flat construction",xts[j],nxts,part,ALGPARTS);

                    /* Load frame names for error messages */
                    flist = mef_paths_frames(bb->paths, bb->name_dome);
                    bb->dome_nframes = flist->n ;
                    bb->dome_frame_name = calloc(flist->n, sizeof(char*));
                    bb->dome_scan_median = (float *)  malloc(flist->n*sizeof(float));
                    bb->dome_scan_stdev = (float *)  malloc(flist->n*sizeof(float));
                    bb->individual_frame_avg = (double *) malloc(flist->n*sizeof(double));
                    bb->individual_frame_median = (double *) malloc(flist->n*sizeof(double));
                    bb->individual_frame_sigma = (double *) malloc(flist->n*sizeof(double));
                    for (i=0 ; i<flist->n ; i++) {
                        bb->dome_frame_name[i] = strdup(flist->name[i]);
                        bb->dome_scan_median[i] = 0.0;
                        bb->dome_scan_stdev[i] = 0.0;
                        bb->individual_frame_avg[i] = 0.0;
                        bb->individual_frame_median[i] = 0.0;
                        bb->individual_frame_sigma[i] = 0.0;

                        /* we check extension names only on the first frame of the list.... */
                        if (i==0) {
                            if ( (fh_ext = qfits_header_readext(flist->name[i],bb->xtnum)) != NULL) {

                                dome_xtname =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                                e_comment(1,"mef_engine: working on dome flat field extension %s -- should be %s", dome_xtname, bb->xtname);
                                qfits_header_destroy(fh_ext); fh_ext = NULL;
                            }
                        }

                        e_comment(1,"Frame %d: %s",i,bb->dome_frame_name[i]);
                    }

		            flat_dome = mef_build_cal(bb, "dome");
		            if (flat_dome==NULL) {
		   	            e_error("in dome flat production: aborting");
                    free(xts); return -1 ;
		            }
		            if (bb->dome_save) {
                if (mef_save(bb, flat_dome, "dome") != 0) goto publication_failed;
		            }
		            e_comment(1,"       dome_median = %f  dome_nplanes = %d",\
				    bb->dome_median[j], bb->dome_nplanes[j]);

                    /* and we free the array elementss */
                    for (i=0; i<bb->dome_nframes; i++) free(bb->dome_frame_name[i]);
                    free(bb->dome_frame_name); bb->dome_frame_name = NULL;
                    free(bb->dome_scan_median); bb->dome_scan_median = NULL;
                    free(bb->dome_scan_stdev); bb->dome_scan_stdev = NULL;
                    free(bb->individual_frame_avg); bb->individual_frame_avg = NULL;
                    free(bb->individual_frame_median); bb->individual_frame_median = NULL;
                    free(bb->individual_frame_sigma); bb->individual_frame_sigma = NULL;
                    framelist_del(flist); flist = NULL;

		        }
		    } else {
		        e_comment(0,"---> [%d/%d] Part %d in %d: skipping dome flat construction. We have the MFF.",xts[j],nxts,part,ALGPARTS);
		    }
		}

		/*
		 * building/reading sky flat
         *
         *  /opt/local/eclipse//bin/mefpp  --bias WFI_MB_1x1.fits  --dome WFI_DOMEFF_BB_B_99_ESO842_1x1.fits  --sky sky.list --skysave  --mffsave WFI_MFF 2>&1 | tee mefpp.log
         *
         *  Note 1: if you run it without --skysave then the only the MFF product will be created,
         *  and this one will have a MSKY keyword indicating "unknown".
         *
         *  Note 2: the argument to --mffsave is the root name. The software will add the data partition and fits extension -- _BB_B_99_ESO842_1x1.fits 
         *
		 */
		 if (bb->name_sky != NULL) {
		    part++ ;
		    if (is_fits_file(bb->name_mf) != 1) {
		       if (is_fits_file(bb->name_sky)) {
		           e_comment(0,"---> [%d/%d] Part %d in %d: skipping sky flat construction",xts[j],nxts,part,ALGPARTS);

                    /* we extract the origfile name of the file */
                    if ( (fh = mef_header_primary_at(bb->name_sky, bb->paths)) == NULL) {
                        e_error("mef_engine: can not read %s primary headers",bb->name_sky);
                        free(xts); return -1;
                    }
                    free(bb->orig_sky);
                    bb->orig_sky = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                    qfits_header_destroy(fh); fh = NULL;
                    e_comment(1,"mef_engine: using sky FITS frame with ORIGFILE: %s", bb->orig_sky);

                    /* we check the extension name 
                    */
                    if ((fh_ext = qfits_header_readext(bb->name_sky, bb->xtnum)) == NULL) {
                        e_error("mef_engine: cannot read headers from file %s extension %d", bb->name_sky, bb->xtnum);
                        free(xts); return -1;
                    }  
                    sky_xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                    qfits_header_destroy(fh_ext); fh_ext = NULL;
                    if (bb->xtname == NULL) {
                        e_comment(1, "mef_engine: EXTNAME should not be NULL at this point", sky_xtname);
                    } else {
                        e_comment(1, "mef_engine: reading sky ff pixel data for extension %s FROM extension %s", bb->xtname, sky_xtname);
                    }


		           flat_sky = mef_load_ext(bb->name_sky,bb->xtnum);
		           bb->sky_median[zIndex] = image_getmedian(flat_sky);
                           bb->sky_nplanes[zIndex] = 1;
		           e_comment(1,"sky median value: %f",bb->sky_median[zIndex]);
               } else {
		           e_comment(0,"---> [%d/%d] Part %d in %d: Sky flat construction",xts[j],nxts,part,ALGPARTS);

                   /* Load frame names for error messages */
                    flist = mef_paths_frames(bb->paths, bb->name_sky);
                    bb->sky_nframes = flist->n ;
                    bb->sky_frame_name = calloc(flist->n, sizeof(char*));
                    bb->sky_scan_median = (float *)  malloc(flist->n*sizeof(float));
                    bb->sky_scan_stdev = (float *)  malloc(flist->n*sizeof(float));
                    bb->individual_frame_avg = (double *) malloc(flist->n*sizeof(double));
                    bb->individual_frame_median = (double *) malloc(flist->n*sizeof(double));
                    bb->individual_frame_sigma = (double *) malloc(flist->n*sizeof(double));
                    for (i=0 ; i<flist->n ; i++) {
                        bb->sky_frame_name[i] = strdup(flist->name[i]);
                        bb->sky_scan_median[i] = 0.0;
                        bb->sky_scan_stdev[i] = 0.0;
                        bb->individual_frame_avg[i] = 0.0;
                        bb->individual_frame_median[i] = 0.0;
                        bb->individual_frame_sigma[i] = 0.0;


                        /* we check extension names only on the first frame of the list.... */
                        if (i==0) {
                            if ( (fh_ext = qfits_header_readext(flist->name[i],bb->xtnum)) != NULL) {

                                sky_xtname =  strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                                e_comment(1,"mef_engine: working on sky flat field extension %s -- should be %s", sky_xtname, bb->xtname);
                                qfits_header_destroy(fh_ext); fh_ext = NULL;
                            }
                        }


                        e_comment(1,"Frame %d: %s",i,bb->sky_frame_name[i]);
                    }
                    framelist_del(flist); flist = NULL;


		           flat_sky = mef_build_cal(bb, "sky");
		           if (flat_sky==NULL) {
			           e_error("in sky flat production: aborting");
			           image_del(flat_dome); flat_dome = NULL;
                       free(xts); return -1 ;
		           }
		           if (bb->sky_save) {
                if (mef_save(bb, flat_sky, "sky") != 0) goto publication_failed;
		           }
		           e_comment(1,"       sky_median = %f  sky_nplanes = %d",\
		    		bb->sky_median[j], bb->sky_nplanes[j]);

		       }
		    } else {
               e_comment(0,"---> [%d/%d] Part %d in %d: skipping sky flat construction. We have the MFF.",xts[j],nxts,part,ALGPARTS);

              if ( (fh = mef_header_primary_at(bb->name_mf, bb->paths)) == NULL) {
                  e_error("mef_engine: can not read %s primary headers",bb->name_mf);
                  free(xts); return -1;
              }
              free(bb->orig_mff);
              bb->orig_mff = strdup(qfits_header_getstr(fh,"ORIGFILE"));
              qfits_header_destroy(fh); fh = NULL;
              e_comment(1,"mef_engine: using master flat FITS frame with ORIGFILE: %s", bb->orig_mff);
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

                /* we extract the origfile name of the file */
                if ( (fh = mef_header_primary_at(bb->name_mf, bb->paths)) == NULL) {
                    e_error("mef_engine: can not read %s primary headers",bb->name_dome);
                    free(xts); return -1;
                }
                free(bb->orig_mff);
                bb->orig_mff = strdup(qfits_header_getstr(fh,"ORIGFILE"));
                qfits_header_destroy(fh); fh = NULL;
                e_comment(1,"mef_engine: using bias FITS frame with ORIGFILE: %s", bb->orig_mff);


                /* we check the extension name 
                */
                if ((fh_ext = qfits_header_readext(bb->name_mf, bb->xtnum)) == NULL) {
                    e_error("mef_engine: cannot read headers from file %s extension %d", bb->name_sky, bb->xtnum);
                    free(xts); return -1;
                }  
                mff_xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                qfits_header_destroy(fh_ext); fh_ext = NULL;
                if (bb->xtname == NULL) {
                    e_comment(1, "mef_engine: EXTNAME should not be NULL at this point");
                } else { 
                    e_comment(1, "mef_engine: reading sky ff pixel data for extension %s FROM extension %s", bb->xtname, mff_xtname);
                }



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
                    free(xts); return -1 ;
		        }
		        if (mef_save(bb, flat_combined, "combined") != 0) goto publication_failed;
		        if (flat_dome != NULL) { image_del(flat_dome); flat_dome = NULL;}
		        if (flat_sky != NULL) {image_del(flat_sky); flat_sky = NULL;}
		    }
		}



	    if (bb->science_name_i != NULL) {
		/*
		 * Loading input cube with science frames
         *
         * /opt/local/eclipse/bin/mefpp --bias WFI_MB_1x1.fits --mff WFI_MFF_BB_V_89_ESO843_1x1.fits --science science.list 2>&1 | tee mefpp.log
         *
		 */
		part++;
		e_comment(0,"---> [%d/%d] Part %d of %d: science frames loading.",xts[j],nxts,part,ALGPARTS,bb->science_name_i);
		
		prep = mef_cube_load_at(bb->science_name_i, bb->xtnum, bb->paths);
		e_comment(1,"Done.");

		if (prep==NULL) {
	           e_error("loading input data [%s]", bb->science_name_i);
               free(xts); return -1 ;
	        }

		/* Load frame names for error messages */
		if (is_fits_file(bb->science_name_i)==1) {
	            bb->science_nframes = 1 ;
	            bb->science_frame_name = calloc(1, sizeof(char*));
	            bb->science_scan_median = calloc(1, sizeof(float));
	            bb->science_scan_stdev = calloc(1, sizeof(float));
                if (bb->science_frame_name == NULL || bb->science_scan_median == NULL ||
                    bb->science_scan_stdev == NULL) { free(xts); return -1; }
	            bb->science_frame_name[0] = strdup(bb->science_name_i);
                if (bb->science_frame_name[0] == NULL) { free(xts); return -1; }
	        } else {
                    flist = mef_paths_frames(bb->paths, bb->science_name_i);
                    bb->science_nframes = flist->n ;
                    bb->science_frame_name = calloc(flist->n, sizeof(char*));
                    bb->science_scan_median = (float *)  malloc(flist->n*sizeof(float));
                    bb->science_scan_stdev = (float *)  malloc(flist->n*sizeof(float));
                    for (i=0 ; i<flist->n ; i++) {
                       bb->science_frame_name[i] = strdup(flist->name[i]);
                       bb->science_scan_median[i] = 0.0;
                       bb->science_scan_stdev[i] = 0.0;

                        /* we check the extension name of all science frames to be processed
                        */
                        if ((fh_ext = qfits_header_readext(flist->name[i], bb->xtnum)) == NULL) {
                            e_error("mef_engine: cannot read headers from file %s extension %d", flist->name[i], bb->xtnum);
                            free(xts); return -1;
                        }
                        sci_xtname = strdup(qfits_header_getstr(fh_ext, "EXTNAME"));
                        qfits_header_destroy(fh_ext); fh_ext = NULL;
                        if (bb->xtname == NULL) {
                            e_comment(1, "mef_engine: EXTNAME should not be NULL at this point");
                        } else {
                            e_comment(1, "mef_engine: %03d science extension %s should be %s", i, bb->xtname, sci_xtname);
                        }

		               e_comment(1,"Frame %d: %s",i,bb->science_frame_name[i]);
                       free(sci_xtname); sci_xtname = NULL;
                    }
	            framelist_del(flist); flist = NULL;
	        }

		/* 
		 * Saturation check if requested
		 */
		part++;
		e_comment(0, "---> [%d/%d] Part %d of %d: checking saturation level", xts[j],nxts,part, ALGPARTS); 
		if (bb->sat_check) {
		   if (mef_saturation_check(prep, bb)!=0) {
			e_error("in saturation check: aborting");
			image_del(bias); bias = NULL;
			image_del(flat_combined); flat_combined = NULL;
			cube_del(prep); prep = NULL;
            free(xts); return -1; /* FSE 2024-05-20 */
		   }
		} else {
		   e_comment(1, "saturation check skipped (on request)");
		}

		/* Overscan/prescan correction and trimming */
		part++;
		e_comment(0, "--> [%d/%d] Part %d of %d: applying overscan/prescan/trimming", xts[j], nxts, part, ALGPARTS);
		mef_cube_overscan_correction(prep,bb, "science");

		/* Bias correction */

	         part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: bias subtraction", xts[j], nxts, part, ALGPARTS);
		 if (bias == NULL) {
		     e_error("no  bias frame [%s]", bb->name_bias);
		     cube_del(prep); prep = NULL;
             free(xts); return -1 ;
	         }
		 if (cube_sub_im(prep, bias)!=0) {
	             e_error("in bias subtraction: aborting");
		     image_del(bias); bias = NULL;
		     cube_del(prep); prep = NULL;
             free(xts); return -1 ;
		 }

		
		 /* Flat-field correction */
		 part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: flatfield division", xts[j], nxts, part, ALGPARTS);
		 if (flat_combined == NULL) {
		     e_error("NULL pointer to  flat-field frame");
		     cube_del(prep); prep = NULL;
             free(xts); return -1 ;
		 }
		 if (cube_div_im(prep, flat_combined)!=0) {
	             e_error("in flat-field division: aborting");
		     image_del(flat_combined); flat_combined = NULL;
		     cube_del(prep); prep = NULL;
             free(xts); return -1 ;
		 }


		 /* Save results */
		 part++;
		 e_comment(0, "--> [%d/%d] Part %d of %d: saving results", xts[j], nxts, part, ALGPARTS);
		 /* Loop over planes in the input cube */
		 for (p=0 ; p<prep->np ; p++) {

		    /* Build output name */
            {
                char leaf[FILENAMESZ], *destination;
                if (strlen(get_basename(bb->science_frame_name[p])) + 20 >= sizeof(leaf)) goto publication_failed;
                sprintf(leaf, "%s_pre.fits", get_rootname(get_basename(bb->science_frame_name[p])));
                destination = mef_paths_output(bb->paths, leaf);
                if (destination == NULL) goto publication_failed;
                strcpy(name_o, destination); free(destination);
            }
		    e_comment(1, "saving calibrated extension %d of file %s into: [%s]", \
				    xts[j], bb->science_frame_name[p], name_o);

            /* some statistics for WC */
            science_median = image_getmedian(prep->plane[p]);
            science_mean = image_getmean(prep->plane[p]);
            science_stdev = image_getstdev(prep->plane[p]);
            science_nplanes = prep->np;
            e_comment(1, "science mean: %f -- science median: %f -- science stdev: %f -- science nplanes: %d", science_mean, science_median, science_stdev, science_nplanes);

		    if (bb->xtnum == 1) {
		       /* Read PRIMARY FITS header from input file */
		       fh = qfits_header_read(bb->science_frame_name[p]);
		       if (fh==NULL) {
		          e_error("reading FITS header from [%s]", bb->science_frame_name[p]);
                  free(xts); return -1 ;
		       }
		       /*
			* we make sure that the EXTEND keyword goes right after NAXIS
			*/
		       qfits_header_del(fh,"EXTEND");
		       qfits_header_add_after(fh,"NAXIS", "EXTEND","T","Extension may be present.",NULL);
		       /*...and that we have real*4 data */

		       sprintf(cval,"%d", BPP_DEFAULT);
		       qfits_header_mod(fh,"BITPIX",cval, "Bits per pixel");


               /* Here we modify the origfile key */
               mef_create_orig_filename(bb, "science");
               qfits_header_mod(fh, "ORIGFILE", bb->orig_science, "Original file name");

               /* Ugly but with a fast computer even milisecond porosity will result in files with the same ORIGFILE name */
               sleep(1);

               /* Keys needed for ESO Phase3 */

               /* Program identification key -- from mefpp.paf */
               cval_ptr = qfits_header_getstr(fh, "HIERARCH ESO OBS PROG ID");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "PI-COI","PROG_ID", cval_ptr, "Program identification", NULL);
               }
               
               /* Observation identification */
               cval_ptr = qfits_header_getstr(fh, "HIERARCH ESO OBS ID");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "PROG_ID","OBID1", cval_ptr, "Observation block ID", NULL);
               }

               /* Number of images combined - only 1 during the pre-processing stage */
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "OBID1","NCOMBINE", "1", "Number of observations combined", NULL);
               }

               /* OBSTECH key -- from mefpp.paf */
               cval_ptr = qfits_header_getstr(fh, "HIERARCH ESO DPR TECH");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "INSTRUME","OBSTECH", cval_ptr, "Observation technique", NULL);
               }

               /* a simple calculation of MJD-END. */
               exptime = atof(qfits_header_getstr(fh, "EXPTIME"));
               mjdobs = atof(qfits_header_getstr(fh, "MJD-OBS"));
               mjdend = mjdobs + exptime/86400.;
               sprintf(cval, "%.8f", mjdend);
               e_comment(1, "frame: %s  --  mjdobs: %f  exptime: %f  mjdend: %f  cval: %s",bb->science_frame_name[p],  mjdobs, exptime, mjdend, cval);
               qfits_header_add_after(fh, "MJD-OBS", "MJD-END", cval, "End of exposure MJD", NULL);

               /* we set the time system explicitly */
               cval_ptr = qfits_header_getstr(fh, "UTC");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "UTC","TIMESYS", "UTC", "Time system", NULL);
               }

               /* Processing software version */
               sprintf(cval, recipe_version);
               sprintf(cval2, "Built on eclipse-%s", get_eclipse_version());
               qfits_header_add_after(fh, "TIMESYS", "PROCSOFT", cval, cval2, NULL);

               /* Product category key */
               qfits_header_add_after(fh,"PROCSOFT", bb->phase3_prodcatg_keyname, 
                                                     bb->phase3_prodcatg_val_science, 
                                                     bb->phase3_prodcatg_comment, NULL);

               /* FLUXCAL key */
               qfits_header_add_after(fh, bb->phase3_prodcatg_keyname, bb->phase3_fluxcal_keyname, 
                                                                      bb->phase3_fluxcal_val, 
                                                                      bb->phase3_fluxcal_comment, NULL);

               /* we rename the RADECSYS key to RADESYS -- from mefpp.paf */
               cval_ptr = qfits_header_getstr(fh, "RADECSYS");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "RADECSYS", bb->phase3_radesys_keyname, 
                                                          cval_ptr, 
                                                          bb->phase3_radesys_comment, NULL); 
                   qfits_header_del(fh,"RADECSYS");
               }
               
               /* we set the filter keyword according to the p3std -- from mefpp.paf */
               cval_ptr = qfits_header_getstr(fh, "HIERARCH ESO INS FILT1 NAME");
               if (cval_ptr!=NULL) {
                   qfits_header_add_after(fh, "EXPTIME","FILTER", cval_ptr, "Filter name", NULL);
               }

               /* We report in the header the ORIGFILE name of the master bpm, bias and flat used */
               qfits_header_add(fh, bb->master_bpm_key, bb->orig_bpm, bb->master_bpm_comment, NULL);
               qfits_header_add(fh, bb->master_bias_key, bb->orig_bias, bb->master_bias_comment, NULL);
               qfits_header_add(fh, bb->master_flat_key, bb->orig_mff, bb->master_flat_comment, NULL);

               /* The saturation level and maximum fraction of pixels allowed to go saturated */
               sprintf(cval, "%7.1f", bb->sat_level);
               qfits_header_add_after(fh, bb->phase3_prodcatg_keyname, "SATLEVEL", cval, "Original saturation level of frame", NULL);
               sprintf(cval, "%5.3f", bb->sat_max);
               qfits_header_add_after(fh,"SATLEVEL", "SATNMAX", cval, "Max fraction of pixel saturated", NULL);

		       if (mef_hdrpix_dump(NULL,name_o,fh,BPP_DEFAULT) != 0) goto publication_failed;
		       qfits_header_destroy(fh); fh = NULL;
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

            /* here we add the header keys giving the prescan, overscan and trim regions*/
            /* REC.FLAT.PRSCX */
            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[0]);
            sprintf(cval2, "%s X1", bb->prescan_x_key);
            qfits_header_add(fh, cval2, cval, bb->prescan_x_comment, NULL);

            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->prescan_x)[1]);
            sprintf(cval2, "%s X2", bb->prescan_x_key);
            qfits_header_add(fh, cval2, cval, bb->prescan_x_comment, NULL);

            /* REC.FLAT.OVSCX */
            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[0]);
            sprintf(cval2, "%s X1", bb->overscan_x_key);
            qfits_header_add(fh, cval2, cval, bb->overscan_x_comment, NULL);

            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->overscan_x)[1]);
            sprintf(cval2, "%s X2", bb->overscan_x_key);
            qfits_header_add(fh, cval2, cval, bb->overscan_x_comment, NULL);

            /* REC.BIAS.TRIM */
            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[0]);
            sprintf(cval2, "%s X1", bb->trimreg_key);
            qfits_header_add(fh, cval2, cval, bb->trimreg_comment, NULL);

            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[1]);
            sprintf(cval2, "%s X2", bb->trimreg_key);
            qfits_header_add(fh, cval2, cval, bb->trimreg_comment, NULL);

            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[2]);
            sprintf(cval2, "%s Y1", bb->trimreg_key);
            qfits_header_add(fh, cval2, cval, bb->trimreg_comment, NULL);

            sprintf(cval, "%d", (((bb->ccd)+(bb->xtnum-1))->trimreg)[3]);
            sprintf(cval2, "%s Y2", bb->trimreg_key);
            qfits_header_add(fh, cval2, cval, bb->trimreg_comment, NULL);

            /* Now we add scan qc keywords */
            sprintf(cval,"HIERARCH ESO MPP QC SCAN MEDIAN");
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->science_scan_median[p]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh, cval, cval2, "Median value of scan pixels frame i.", NULL);

            sprintf(cval,"HIERARCH ESO MPP QC SCAN STDEV");
            e_comment(1, "key: %s", cval);
            sprintf(cval2, "%f", bb->science_scan_stdev[p]);
            e_comment(1, "val: %s", cval2);
            qfits_header_add(fh, cval, cval2, "Std deviation of scan pixels frame i.", NULL);

            sprintf(cval, "%f", science_mean);
            qfits_header_add(fh, "HIERARCH ESO MPP QC FRMEAN", cval, "Mean of pixel values.", NULL);

            sprintf(cval, "%f", science_median);
            qfits_header_add(fh, "HIERARCH ESO MPP QC FRMEDIAN", cval, "Median of pixel values.", NULL);

            sprintf(cval, "%f", science_stdev);
            qfits_header_add(fh, "HIERARCH ESO MPP QC FRSTDEV", cval, "Stdev of pixel values.", NULL);

		    e_comment(1, "dumping extension headers and pixel data of extension %d calibrated %s frame",
				    xts[j],bb->science_frame_name[p]);
		    if (mef_hdrpix_dump(prep->plane[p],name_o,fh,BPP_DEFAULT) != 0) goto publication_failed;
		    e_comment(1, "done.");

		    qfits_header_destroy(fh); fh = NULL;
		    qfits_header_destroy(fh_aux1); fh_aux1 = NULL;
		    qfits_header_destroy(fh_aux2); fh_aux2 = NULL;
		 }
		 cube_del(prep); prep = NULL;
	    }

	    if (bias != NULL) {
		    e_comment(1, "deallocating bias memory");
		    image_del(bias); bias = NULL;
            e_comment(1, "done.");
	    }
	    if (bp_map != NULL) {
		    e_comment(1, "deallocating bp_map  memory");
		    pixelmap_del(bp_map); bp_map = NULL;
            e_comment(1, "done.");
	    }
	    if (flat_combined != NULL) {
		    e_comment(1, "deallocating flat_combined memory");
		    image_del(flat_combined); flat_combined = NULL;
		    e_comment(1, "done");
	    }
        /* Last use of per-extension metadata after every product is published (#124). */
        mef_bb_clear_work(bb);
        free(bias_xtname); bias_xtname = NULL;
        free(bpm_xtname); bpm_xtname = NULL;
        free(dome_xtname); dome_xtname = NULL;
        free(sky_xtname); sky_xtname = NULL;
        free(mff_xtname); mff_xtname = NULL;
        free(sci_xtname); sci_xtname = NULL;
	}
    free(xts);
	e_comment(0, "--> STOP  MEF calibration engine");
	return 0 ;

publication_failed:
    /* Only new publication errors enter here; the caller still owns bb. */
    if (fh != NULL) qfits_header_destroy(fh);
    if (fh_ext != NULL) qfits_header_destroy(fh_ext);
    if (fh_aux1 != NULL) qfits_header_destroy(fh_aux1);
    if (fh_aux2 != NULL) qfits_header_destroy(fh_aux2);
    if (flist != NULL) framelist_del(flist);
    if (prep != NULL) cube_del(prep);
    if (bias != NULL) image_del(bias);
    if (bp_map != NULL) pixelmap_del(bp_map);
    if (flat_dome != NULL) image_del(flat_dome);
    if (flat_sky != NULL) image_del(flat_sky);
    if (flat_combined != NULL) image_del(flat_combined);
    free(bias_xtname);
    free(bpm_xtname);
    free(dome_xtname);
    free(sky_xtname);
    free(mff_xtname);
    free(sci_xtname);
    free(xts);
    return -1;
}
#undef ALGPARTS


/*---------------------------------------------------------------------------
  Main	
  ---------------------------------------------------------------------------*/

int main(int argc, char *argv[])
{

	mef_bb*	bb ;
    int load_status;
    int engine_status;

	/*printf("argc = %d\n\n",argc);*/
	printf("\n\n\n ----------> MEFPP REDUCTION ENGINE. VERSION: %s <----------\n\n\n", recipe_version);
	if (argc == 1) {
          usage(argv[0]);
	  return EXIT_FAILURE;
        }

	/* Initialize eclipse environment */
	printf("\nInitializing eclipse environment");
	eclipse_init() ;

	/* Get parameters for processing */
	printf("\nLoading parameters...\n");
	if ( (bb = mef_bb_load(argc,argv,&load_status)) == NULL ) {
       return load_status;
    }

	/* Startup MEF calibration  engine */

	engine_status = mef_engine(bb);
    if (mef_paths_finish(bb->paths) != 0) engine_status = -1;
	mef_bb_del(bb);

	if (debug_active()) xmemory_status() ;
	return engine_status == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
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
                        "\t--output-dir DIR  Explicit mode: existing output directory\n"
                        "\t--work-dir DIR    Explicit mode: existing scratch directory\n"
                        "\t--list-base DIR   Recorded base for relative list members\n"
                        "\t--log-file FILE   Fresh log (default: work-dir/mefpp.log)\n"
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

} 

