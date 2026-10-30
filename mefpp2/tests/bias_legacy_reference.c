/* Frozen mef_build_cal from 98454283341a5bbce641119bed686fa56ff9c44b.
 * Test-only independent arithmetic oracle; source body unchanged.
 * Input loading is replaced by an in-memory fixture loader. */
#include "mefp_lib.h"
cube_t *mef_bias_reference_load(char *name, int extension);
#define mef_cube_load mef_bias_reference_load
#define mef_build_cal mef_bias_reference
image_t * mef_build_cal(mef_bb * bb, char * what)
{
	cube_t	 *	i_cube ;
	image_t *	scancorr ;
	image_t *  	bias ;
	image_t *	stacked ;
	image_t *  	cur_p ;
	image_t *  	flat ;
	char	 *	name_i ;
	double		lo_thr, hi_thr ;
	int		minframe ;
	double		avg, avg1, sig1, kappa1 ;
    float      zmedian, zstdev;
	int		i, j, p ;
	int	 *	valid ;
	double		*all_means ;
	int		nval ;
	double		sigma ;
	pixelvalue * 	validpix ;
	pixelvalue	curpix ;
	double	    medval ;
    double      stdev_val ;
    double      *pixval_double;
	float		frame_median ;
    float       frame_variance ;
	int		frame_nplanes ;
	int		zIndex;
	char		cmt[5];
	float		normFactor ;

	/* Check entries */
	if (bb==NULL) return NULL ;
	if (!what || !*what) return NULL;

	/* Set parameters to requested frame type */
	e_comment(1, "setting input parameters...");
	if (!strcmp(what, "dome")) {
		name_i = bb->name_dome ;
		lo_thr = bb->dome_framethr_lo ;
		hi_thr = bb->dome_framethr_hi ;
		minframe = bb->dome_minframe ;
	} else if (!strcmp(what, "sky")) {
		name_i = bb->name_sky ;
		lo_thr = bb->sky_framethr_lo ;
		hi_thr = bb->sky_framethr_hi ;
		minframe = bb->sky_minframe ;
	} else if (!strcmp(what, "bias")) {
		name_i = bb->name_bias ;
		minframe = bb->bias_minframe ;
		kappa1   = bb->bias_kappa1 ;
	} else {
		e_error("unknown frame type [%s] should be 'dome' or 'sky'",what);
		return NULL ;
	}

	/* Load input cube */
	e_comment(1, "loading input cube [%s]", what);
	i_cube = mef_cube_load(name_i, bb->xtnum) ;
	if (i_cube==NULL) {
		e_error("loading input data: [%s]", name_i);
		return NULL ;
	}
	if (i_cube->np < minframe) {
		e_error("found only [%d] %s frames - need at least %d",
				i_cube->np,
				what,
				minframe);
		cube_del(i_cube);
		return NULL ;
	}

    /* we correct overscan and trim the cube */
    /* we do it before removing bad planes from
     * cube so we have the full input list represented.
     */
    e_comment(1, "applying overscan/prescan/trimming correction");
    mef_cube_overscan_correction(i_cube,bb, what);
    e_comment(1, "Done.");

	/* Compute average value for each frame, keep those in interval */
	all_means = malloc(i_cube->np*sizeof(double));
	nval = 0 ;
	avg1 = 0.00 ;
	for (i=0 ; i<i_cube->np ; i++) {
		compute_status("computing averages", i, i_cube->np, 1);
		all_means[i] = image_getmean(i_cube->plane[i]);
		avg1 += all_means[i] ;
		/*
		   if (debug_active()>1) {
		   printf("\n");
		   printf("avg/thr: %g [%g - %g]\n", avg, lo_thr, hi_thr);
		   }
		   */
	}
	avg1 /= (double) i_cube->np ;

	/* if we combine bias frame we do a slighltly different rejection */
	if (!strcmp(what, "bias")) {
		/* Compute average and sigma for rejection during bias calc. */
		sig1 = 0.0 ;
		for (i=0 ; i<i_cube->np ; i++) {
			sig1 += (all_means[i]-avg1)*(all_means[i]-avg1) ;
		}
		sig1 /= (double)(i_cube->np-1) ;
		sig1 = sqrt(sig1) ;

		lo_thr = avg1 - kappa1*sig1 ;
		hi_thr = avg1 +  kappa1*sig1 ;

        /* fill array for QC keywords */
        if (bb->nxts == 1) {    /* if we work in only one extension */
                zIndex = 0;
            } else {                        /* we are working in all the extensions */
                zIndex = bb->xtnum-1;
            }
        bb->bias_avg1[zIndex] = avg1;
        bb->bias_sig1[zIndex] = sig1;
        bb->bias_framethr_lo[zIndex] = lo_thr;
        bb->bias_framethr_hi[zIndex] = hi_thr;

		e_comment(1, "frame rejection setup:");
		e_comment(1, "average: %g", avg1);
		e_comment(1, "sigma  : %g", sig1);
		e_comment(1, "kappa  : %g", kappa1);
		e_comment(1, "low    : %g", lo_thr);
		e_comment(1, "high   : %g", hi_thr);
	}

	valid = malloc(i_cube->np * sizeof(int));
	nval = 0 ;
	e_comment(1, "frame rejection status:");
	for (i=0 ; i<i_cube->np ; i++) {
		if ((all_means[i]>lo_thr) && (all_means[i]<hi_thr)) {
			strcpy(cmt, "[X]");
			valid[i] = 1 ;
			nval++ ;
		} else {
			strcpy(cmt, "[ ]");
			valid[i] = 0 ;
		}
		e_comment(1, "%s %s frame %02d: %g", cmt, what, i+1, all_means[i]);
	}
	free(all_means);

	if (nval<minframe) {
		e_error("not enough frames to continue: %d", nval);
		free(valid);
		cube_del(i_cube);
		return NULL ;
	}

	/* Reduce cube to valid frames only */
	if (nval < i_cube->np) {
		e_comment(1, "reducing cube to valid planes only");
		cube_reject_planes(&i_cube, valid);
	}
	free(valid);

	/* Apply prescan/overscan/trimming correction 

	e_comment(1, "applying overscan/prescan/trimming correction");
	mef_cube_overscan_correction(i_cube,bb, what);
	e_comment(1, "Done.");

    *************************************************/

	/*
	 * If we are building the BIAS frame, we are almost done.
	 * We just combine the cube, and return the stacked image...
	 */

	if (!strcmp(what, "bias")) {
		e_comment(1, " %s frame stacking", what);
		stacked = cube_avg_median(i_cube);
		cube_del(i_cube);

		if (stacked==NULL) {
			e_error("in final combination: aborting");
			return NULL ;
		}
	 
		if (bb->nxts == 1) {    /* if we work in only one extension */
	            zIndex = 0;
	        } else {                        /* we are working in all the extensions */
	            zIndex = bb->xtnum-1;
	        }
		bb->bias_median[zIndex] = image_getmedian(stacked);
        bb->bias_stdev[zIndex] = image_getstdev(stacked);
		bb->bias_nplanes[zIndex] = nval;
        e_comment(1, "bias median: %f -- bias stdev: %f -- bias nplanes: %d", bb->bias_median[zIndex], bb->bias_stdev[zIndex], bb->bias_nplanes[zIndex]);
		return stacked;
	}


	/* CCD clip rejection */
	e_comment(1, "CCD clip rejection");
	e_comment(1,"gain = %f",((bb->ccd)+(bb->xtnum-1))->gain);
	e_comment(1,"ron  = %f",((bb->ccd)+(bb->xtnum-1))->ron);

	frame_median = 0.0;
    frame_variance = 0.0;
	frame_nplanes = 0;
    if (bb->nxts == 1) {    /* if we work in only one extension */
        zIndex = 0;
    } else {                        /* we are working in all the extensions */
        zIndex = bb->xtnum-1;
    }
	for (p=0 ; p<i_cube->np ; p++) {
		compute_status("clip rejection on frame", p, i_cube->np, 1);
		cur_p = i_cube->plane[p] ;

		avg = image_getmean(cur_p);
        zmedian = image_getmedian(cur_p);
        zstdev = image_getstdev(cur_p);
		sigma = sqrt(pow(((bb->ccd)+(bb->xtnum-1))->ron/((bb->ccd)+(bb->xtnum-1))->gain, 2.0) +
				(avg / ((bb->ccd)+(bb->xtnum-1))->gain));

        /* here we store the average and sigma values for QC */
        bb->individual_frame_avg[p] = avg;
        bb->individual_frame_median[p] = zmedian;
        bb->individual_frame_sigma[p] = zstdev;
        e_comment(1, "frame median: %f -- frame stdev: %f -- frame nplanes: %d", zmedian, zstdev, i_cube->np);
        e_comment(1, "frame median: %f -- frame stdev: %f -- frame nplanes: %d", bb->individual_frame_median[p], bb->individual_frame_sigma[p], i_cube->np);

		lo_thr = avg - bb->pixrej_lo * sigma ;
		hi_thr = avg + bb->pixrej_hi * sigma ;
		e_comment(1, "rejection interval");
		e_comment(1, "[%g - %g]]", lo_thr, hi_thr);
		/*
		   if (debug_active()>1) {
		   printf("avg= %g sigma= %g thr= [%g - %g]\n",
		   avg, sigma, lo_thr, hi_thr);
		   }
		   */

		/* Accumulate valid pixels in an array */
		validpix = malloc(bb->median_surf * sizeof(pixelvalue));
		nval = 0 ;
		for (j=0 ; j<cur_p->ly ; j++) {
			if (j>=bb->median_reg[2] && j<=bb->median_reg[3]) {
				for (i=0 ; i<cur_p->lx ; i++) {
					if (i>=bb->median_reg[0] && i<=bb->median_reg[1]) {
						curpix = cur_p->data[i+j*cur_p->lx];
						if (((double)curpix > lo_thr) &&
								((double)curpix < hi_thr)) {
							validpix[nval] = curpix ;
							nval ++ ;
						}
					}
				}
			}
		}
		if (nval<1) {
			e_error("no valid pixel found in frame %02d: aborting", p+1);
			cube_del(i_cube);
			free(validpix);
			return NULL ;
		}
		/* Get the median from the list of valid pixels */
		medval = (double) median_pixelvalue(validpix, nval);
        e_comment(1, "medval: %f",  medval);
        pixval_double = pixel2double_array(validpix, nval);

        for (j=0 ; j<nval ; j++) {
            pixval_double[j] -= medval;
        }

        stdev_val = double_rms(pixval_double, nval);
        free(pixval_double); /* Last use of flat statistics scratch (#123). */
		free(validpix);

		if (fabs(medval)<1e-4) {
			e_error("zero value for median: aborting");
			/* cube_del(i_cube); */
			/* return NULL ; */
		} else {
			/* Divide the frame by this value */
			for (i=0 ; i<(cur_p->lx * cur_p->ly) ; i++) {
				cur_p->data[i] /= medval ;
			}
			frame_median += medval ;
            frame_variance += stdev_val*stdev_val;
			frame_nplanes++ ;
		}
	}
	frame_median = frame_median / frame_nplanes ;
    frame_variance = frame_variance / frame_nplanes ;
    e_comment(1, "frame_median: %f -- frame_variance: %f", frame_median, frame_variance);
	if (bb->nxts == 1) {	/* if we work in only one extension */
		zIndex = 0;
	} else {			/* we are working in all the extensions */
		zIndex = bb->xtnum-1;
	}
	if (!strcmp(what,"dome")) {
		bb->dome_median[zIndex] = frame_median;
        bb->dome_stdev[zIndex] = sqrt(frame_variance);
		bb->dome_nplanes[zIndex] = frame_nplanes;
		normFactor = bb->dome_median[zIndex]/bb->dome_median[0];
	} else if (!strcmp(what,"sky")) {
		bb->sky_median[zIndex] = frame_median;
        bb->sky_stdev[zIndex] = sqrt(frame_variance);
		bb->sky_nplanes[zIndex] = frame_nplanes;
		normFactor = bb->sky_median[zIndex]/bb->sky_median[0];
	}


	/* Stack frames to single frames using a median */
	e_comment(1, "stacking cube to single frame");
	flat = cube_avg_median(i_cube);
	image_cst_op_local(flat,normFactor,'*');	/* we normalize to the median of first extension */
	cube_del(i_cube);

	if (flat==NULL) {
		e_error("in final stacking: aborting");
		return NULL ;
	}
	return flat ;
}
