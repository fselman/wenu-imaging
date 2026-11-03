/*----------------------------------------------------------------------------*/
/**
   @file	detector.c
   @author	Yves Jung
   @date	June 2001
   @version	$Revision: 1.14 $
   @brief	All detector check functions
*/
/*----------------------------------------------------------------------------*/

/*
	$Id: detector.c,v 1.14 2003/08/18 14:21:28 yjung Exp $
	$Author: yjung $
	$Date: 2003/08/18 14:21:28 $
	$Revision: 1.14 $
*/

/*-----------------------------------------------------------------------------
   								Includes
 -----------------------------------------------------------------------------*/

#include "detector.h"
#include "doubles.h"
#include "dstats.h"
#include "random.h"
#include <stdint.h>
#include <string.h>

/*-----------------------------------------------------------------------------
   							Function codes	
 -----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------*/
/**
  @brief	Compute a flat-field out of a set of exposures.
  @param	twilight	Input cube.
  @return	1 newly allocated array of 3 newly allocated images.
  @see		cube_create_gainmap() cube_create_gainmap_proportional()

  The input is assumed to be a cube containing planes of different intensities 
  (usually increasing or decreasing). Typical inputs are: twilight data sets, 
  halogen lamp, or skies of different airmasses in the thermal regime.

  The output is a set of 3 images. The first image contains a regression map, 
  i.e. for each pixel position on the detector, a curve is plotted of the 
  pixel intensity in each plane against the median intensity of the plane. A 
  slope is fit, and the gain factor is stored into this first image.

  The second image contains the y-intercepts of the slope fit. It is usually 
  good to check it out in case of failures. 
  
  FSE 2024-07-19: cube_create_gainmap_proportional
  below assumes 0 intercept. The intercept image could be used to estimate
  shutter errors when needed, e.g. when analyzing linearity sequences.

  The third image contains the sum of squared errors for each fit.

  The fit is using a robust least-squares criterion rejecting outliers. This 
  is the algorithm to use with big telescopes like the VLT, which collect so 
  much light that objects are actually seen in the twilight sky.  It is also 
  recommended to jitter the twilight acquisition in this case (this is what is 
  done on ISAAC).

  The returned result is an array of 3 image pointers, that must be deallocated
  using free(). Each of the returned image pointers must have been previously 
  deallocated using image_del().

  Example:
  \begin{verbatim}
  image_t ** slopefit ;

  slopefit = cube_create_gainmap_robust(cube);
  ...
  if (slopefit[0]!=NULL) image_del(slopefit[0]);
  if (slopefit[1]!=NULL) image_del(slopefit[1]);
  if (slopefit[2]!=NULL) image_del(slopefit[2]);
  free(slopefit);
  \end{verbatim}
 */
/*----------------------------------------------------------------------------*/
image_t ** cube_create_gainmap_robust(cube_t * twilight)
{
	image_t		**	result ;
	image_t		*	gain ;
	image_t		*	intercept ;
	image_t		*	sq_err ;
	int				i, j, k, p ;
	double		*	slope ;
	double3		*	timeline ;
	double		*	plane_med ;

	if (twilight==NULL) return NULL ;

	/* Compute median for all planes */

	plane_med = malloc(twilight->np * sizeof(double));
	for (p=0 ; p<twilight->np ; p++) {
		compute_status("computing stats...", p, twilight->np, 1);
		plane_med[p] = (double)image_getmedian(twilight->plane[p]);
	}

	result = malloc(3 * sizeof(image_t*)) ;

	gain 		= image_new(twilight->lx, twilight->ly);
	intercept 	= image_new(twilight->lx, twilight->ly);
	sq_err 		= image_new(twilight->lx, twilight->ly);

	timeline = double3_new(twilight->np);

	/* Loop on all pixel positions */
	e_comment(1, "computing gains for all positions (long)...");
    for (j=0 ; j<gain->ly ; j++) {
        compute_status("fitting slopes", j, gain->ly, 1);
        k = j * gain->lx ;
        for (i=0 ; i<gain->lx ; i++) {
            /* extract time line */
            for (p=0 ; p<twilight->np ; p++) {
                timeline->x[p] = plane_med[p] ;
                timeline->y[p] = (double)twilight->plane[p]->data[k] ;
            }

            /* fit slope to this time line */
            slope = fit_slope_robust(timeline);
            /* set results in output images */
            intercept->data[k] 	= slope[0] ;
            gain->data[k] 		= slope[1] ;
            sq_err->data[k]		= slope[2] ;
            free(slope);
            k++ ;
        }
    }
	free(plane_med);
	double3_del(timeline);

	/* Return */
	result[0] = gain ;
	result[1] = intercept ;
	result[2] = sq_err ;
	return result ;
}


/*----------------------------------------------------------------------------*/
/**
  @brief	Compute a flat-field out of a set of exposures.
  @param	twilight	Input cube.
  @return	1 newly allocated array containing 2 newly allocated images.
  @see 		cube_create_gainmap
  @see		cube_create_gainmap_robust

  The input is assumed to be a cube containing planes of different intensities 
  (usually increasing or decreasing), from which any source of bias has been 
  removed. Typical inputs are: twilight data sets, halogen lamp, or skies of 
  different airmasses in the thermal regime. The input frame should have been 
  dark-subtracted or de-biased before entering this function.

  The output is an array of 2 images. The first image contains a regression map,
  i.e. for each pixel position on the detector, a curve is plotted of the pixel
  intensity in each plane against the median intensity of the plane. A slope is
  fit assuming a zero y-intercept, and the gain factor is stored into this 
  first image.

  The second image contains the sum of squared errors for each fit.

  The fit is using a robust slope fit criterion rejecting outliers. The slope 
  of each pixel is computed in all the input planes, and only the median slope
  is stored in output.

  The returned result is an array of 2 image pointers, that must be deallocated
  using free(). Each of the returned image pointers must have been previously 
  deallocated using image_del().

  Example:
  \begin{verbatim}
  image_t ** slopefit ;

  slopefit = cube_create_gainmap_proportional(cube);
  ...
  if (slopefit[0]!=NULL) image_del(slopefit[0]);
  if (slopefit[1]!=NULL) image_del(slopefit[1]);
  free(slopefit);
  \end{verbatim}

 */
/*----------------------------------------------------------------------------*/
image_t ** cube_create_gainmap_proportional(cube_t * twilight)
{
	image_t		**	result ;
	image_t		*	gain ;
	image_t		*	sq_err ;
	int				i, p ;
	double		*	slope ;
	double3		*	timeline ;
	double		*	plane_med ;
	int				step ;
	int				ly_step ;

	if (twilight==NULL) return NULL ;

	/* Compute median for all planes */
	plane_med = malloc(twilight->np * sizeof(double));
	for (p=0 ; p<twilight->np ; p++) {
		compute_status("computing stats...", p, twilight->np, 1);
		plane_med[p] = (double)image_getmedian(twilight->plane[p]);
	}

	result = malloc(2 * sizeof(image_t*)) ;

	gain 		= image_new(twilight->lx, twilight->ly);
	sq_err 		= image_new(twilight->lx, twilight->ly);

	timeline = double3_new(twilight->np) ;

	/* Loop on all pixel positions */
	step = 0 ;
	ly_step = 0 ;
	for (i=0 ; i<(gain->lx*gain->ly) ; i++) {
		/* Compute status message is handled here with 'step' */
		if (!step) {
			compute_status("computing gain...", ly_step, gain->ly, 1);
		}
		step++ ;
		if (step==gain->lx) {
			step=0 ;
			ly_step++ ;
		}
		/* extract time line */
		for (p=0 ; p<twilight->np ; p++) {
			timeline->x[p] = plane_med[p] ;
			timeline->y[p] = (double)twilight->plane[p]->data[i] ;
		}

		/* fit slope to this time line */
		slope = fit_proportional(timeline);
		/* set results in output images */
		gain->data[i] 		= slope[0] ;
		sq_err->data[i]		= slope[1] ;
		free(slope);
	}
	free(plane_med);
	double3_del(timeline);

	/* Return */
	result[0] = gain ;
	result[1] = sq_err ;
	return result ;
}


/*----------------------------------------------------------------------------*/
/**
  @brief    Compute the readout noise in a rectangle.
  @param    diff    Input image, usually a difference frame.
  @param    zone    Zone where the readout noise is to be computed.
  @param    ron_hsize   to specify half size of squares (>0 to use default)
  @param    ron_nsamp   to specify the nb of samples (>0 to use default)
  @param    noise   Output parameter: noise in the frame.
  @param    error   Output parameter: error on the noise.
  @return   int 0 if Ok, -1 otherwise.

  This function is meant to compute the readout noise in a frame by means of a 
  MonteCarlo approach. The input is a frame, usually a difference between two 
  frames taken with the same settings for the acquisition system, although no 
  check is done on that, it is up to the caller to feed in the right kind of 
  frame.

  The provided zone is an array of four integers specifying the zone to take 
  into account for the computation. The integers specify ranges as xmin, xmax, 
  ymin, ymax, where these coordinates are given in the FITS notation (x from 1 
  to lx, y from 1 to ly and bottom to top). Specify NULL instead of an array of
  four values to use the whole frame in the computation.

  The algorithm will create typically 100 9x9 windows on the frame, scattered 
  optimally using a Poisson law. In each window, the standard deviation of all 
  pixels in the window is computed and this value is stored. The readout noise 
  is the median of all computed standard deviations, and the error is the 
  standard deviation of the standard deviations.

  Both values (noise and error) are returned by modifying a passed double. If 
  you do not care about the error, pass NULL.
 */
/*----------------------------------------------------------------------------*/
#define RECT_RON_HS         4
#define RECT_RON_SAMPLES    100
int image_rect_readout_noise(
	    image_t *   diff,
	    int     *   zone_def,
        int         ron_hsize,
        int         ron_nsamp,
	    double  *   noise,
	    double  *   error)
{
    double3     *   sample_reg ;
    int				rect[4] ;
    image_stats *   vig_stats ;
    double      *   rms_list ;
    double          rms_median ;
    double          rms_error ;
    int             zone[4];
    int             hsize ;
    int             nsamples ;
    int             i ;

    if (diff==NULL || noise==NULL) return -1 ;

    /* Initialize */
    if (ron_hsize < 0) hsize = RECT_RON_HS ;
    else               hsize = ron_hsize ;
    if (ron_nsamp < 0) nsamples = RECT_RON_SAMPLES ;
    else               nsamples = ron_nsamp ;

    /* Generate nsamples window centers in the image */
    if (zone_def!=NULL) {
        rect[0] = zone_def[0] + hsize + 1 ; /* xmin */
        rect[1] = zone_def[1] - hsize - 1 ; /* xmax */
        rect[2] = zone_def[2] + hsize + 1 ; /* ymin */
        rect[3] = zone_def[3] - hsize - 1 ; /* ymax */
    } else {
        rect[0] = hsize + 1 ;	            /* xmin */
        rect[1] = diff->lx - hsize - 1 ;	/* xmax */
        rect[2] = hsize + 1 ;	            /* ymin */
        rect[3] = diff->ly - hsize - 1 ;	/* ymax */
    }

    if ((rect[0]>=rect[1]) || (rect[2]>=rect[3])) {
        e_error("in readout noise: invalid region def");
        return -1 ;
    }

    /* Generate n+1 regions, because the first region is always at (0,0) */
    /* and it would bias the measurement. */
    sample_reg = generate_rect_poisson_points(rect, nsamples+1, nsamples+1) ;

    /* Now, for each window center, extract a vignette and compute the */
    /* signal RMS in it. Store this rms into a table. */
    rms_list = malloc(nsamples * sizeof(double));
    for (i=0 ; i<nsamples ; i++) {
        zone[0] = (int)sample_reg->x[i+1] - hsize ;
        zone[1] = (int)sample_reg->x[i+1] + hsize ;
        zone[2] = (int)sample_reg->y[i+1] - hsize ;
        zone[3] = (int)sample_reg->y[i+1] + hsize ;
        if ((vig_stats = image_getstats_opts(diff, NULL, NULL, zone)) == NULL) {
            e_error("computing stats on vignette");
            free(rms_list);
            double3_del(sample_reg);
            return -1 ;
        }
        rms_list[i] = (double)vig_stats->stdev;
        free(vig_stats);
    }
    double3_del(sample_reg);

    /* The final computed RMS is the median of all values.  */
    rms_median = double_median(rms_list, nsamples) ;
    (*noise) = rms_median ;
    if (error!=NULL) {
        /* The error is the rms of the rms */
        rms_error = double_rms(rms_list, nsamples) ;
        (*error) = rms_error ;
    }
    free(rms_list);
    return 0 ;
}


/* Output alias guards compare address distances without adding to pointers. */
static int gain_pair_overlaps(const void *a, size_t na, const void *b, size_t nb)
{
    uintptr_t x = (uintptr_t)a, y = (uintptr_t)b;
    if (a == NULL || b == NULL || na == 0 || nb == 0) return 0;
    return x <= y ? y-x < na : x-y < nb;
}

/* Checked composition of the existing Eclipse sample/pair estimators. */
int detector_gain_pair_checked(
    const image_t *flat_first, const image_t *flat_second,
    const image_t *bias_first, const image_t *bias_second,
    const pixelmap *selection, const int *zone,
    int with_mad, detector_gain_pair_result *out)
{
    const image_t *images[4];
    detector_gain_pair_result result;
    pixelmap *common;
    size_t n, i, p;
    int k, x, y, finite;
    double bias_mean, numerator, denominator;
    images[0] = flat_first; images[1] = flat_second;
    images[2] = bias_first; images[3] = bias_second;
    if (out == NULL || (with_mad != 0 && with_mad != 1)) return -1;
    for (k = 0; k < 4; ++k) {
        if (images[k] == NULL || images[k]->data == NULL ||
            images[k]->lx < 1 || images[k]->ly < 1 ||
            images[k]->lx > INT_MAX / images[k]->ly) return -1;
        if (images[k]->lx != images[0]->lx || images[k]->ly != images[0]->ly)
            return -1;
    }
    n = (size_t)images[0]->lx * (size_t)images[0]->ly;
    if (n > (size_t)-1 / sizeof(pixelvalue)) return -1;
    for (k = 0; k < 4; ++k)
        if (gain_pair_overlaps(out, sizeof(*out), images[k], sizeof(*images[k])) ||
            gain_pair_overlaps(out, sizeof(*out), images[k]->data,
                               n * sizeof(pixelvalue))) return -1;
    if (selection != NULL) {
        if (selection->data == NULL || selection->lx != images[0]->lx ||
            selection->ly != images[0]->ly ||
            gain_pair_overlaps(out, sizeof(*out), selection, sizeof(*selection)) ||
            gain_pair_overlaps(out, sizeof(*out), selection->data,
                               n * sizeof(*selection->data))) return -1;
        for (i = 0; i < n; ++i)
            if (selection->data[i] != PIXELMAP_0 &&
                selection->data[i] != PIXELMAP_1) return -1;
    }
    if (zone != NULL && gain_pair_overlaps(out, sizeof(*out), zone,
                                          4 * sizeof(*zone))) return -1;
    memset(&result, 0, sizeof(result));
    result.zone[0] = result.zone[2] = 1;
    result.zone[1] = images[0]->lx; result.zone[3] = images[0]->ly;
    if (zone != NULL) memcpy(result.zone, zone, sizeof(result.zone));
    if (result.zone[0] < 1 || result.zone[2] < 1 ||
        result.zone[1] > images[0]->lx || result.zone[3] > images[0]->ly ||
        result.zone[0] > result.zone[1] || result.zone[2] > result.zone[3])
        return -1;
    result.bpm_supplied = selection != NULL;
    result.gain_state = DETECTOR_GAIN_PAIR_TOO_FEW_PIXELS;
    common = pixelmap_new(images[0]->lx, images[0]->ly);
    if (common == NULL) return -1;
    memset(common->data, PIXELMAP_0, n * sizeof(*common->data));
    for (y = result.zone[2]-1; y < result.zone[3]; ++y) {
        for (x = result.zone[0]-1; x < result.zone[1]; ++x) {
            p = (size_t)y * (size_t)images[0]->lx + (size_t)x;
            ++result.region_pixels;
            if (selection != NULL && selection->data[p] == PIXELMAP_0) {
                ++result.bpm_excluded; continue;
            }
            finite = 1;
            for (k = 0; k < 4; ++k)
                if (!isfinite(images[k]->data[p])) finite = 0;
            if (!finite) { ++result.nonfinite_excluded; continue; }
            common->data[p] = PIXELMAP_1; ++result.valid_pixels;
        }
    }
    pixelmap_updatecount(common);
    for (k = 0; k < 4; ++k) {
        if (image_getstats_masked_checked(images[k], common, result.zone,
                with_mad, &result.levels[k]) != 0) goto fail;
    }
    if (image_pair_stats_checked(images[0], images[1], common, common,
            result.zone, with_mad, &result.flat_difference) != 0 ||
        image_pair_stats_checked(images[2], images[3], common, common,
            result.zone, with_mad, &result.bias_difference) != 0) goto fail;
    /* Arithmetic overflow must not silently change the common population. */
    if (result.flat_difference.valid_pixels != result.valid_pixels ||
        result.bias_difference.valid_pixels != result.valid_pixels) goto fail;
    if (result.valid_pixels > 0) {
        bias_mean = .5 * result.levels[2].mean + .5 * result.levels[3].mean;
        result.signal_first = result.levels[0].mean - bias_mean;
        result.signal_second = result.levels[1].mean - bias_mean;
        result.signals_available = 1;
        numerator = result.signal_first + result.signal_second;
        if (!isfinite(result.signal_first) || !isfinite(result.signal_second) ||
            !isfinite(numerator)) goto fail;
        if (result.signal_first > 0 && result.signal_second > 0) {
            result.fractional_mismatch =
                2.0 * fabs(result.signal_first/numerator - result.signal_second/numerator);
            result.mismatch_available = 1;
        }
        if (result.valid_pixels > 1) {
            result.flat_variance = result.flat_difference.stdev * result.flat_difference.stdev;
            result.bias_variance = result.bias_difference.stdev * result.bias_difference.stdev;
            denominator = result.flat_variance - result.bias_variance;
            result.photon_variance = denominator;
            result.ron_adu = result.bias_difference.stdev / sqrt(2.0);
            result.ron_available = 1;
            if (with_mad) {
                result.ron_mad_adu = (1.4826 / sqrt(2.0)) * result.bias_difference.mad;
                result.ron_mad_available = 1;
            }
            if (!isfinite(result.flat_variance) || !isfinite(result.bias_variance) ||
                !isfinite(denominator) || !isfinite(result.ron_adu) ||
                !isfinite(result.ron_mad_adu)) goto fail;
            if (numerator <= 0)
                result.gain_state = DETECTOR_GAIN_PAIR_NONPOSITIVE_SIGNAL;
            else if (denominator <= 0)
                result.gain_state = DETECTOR_GAIN_PAIR_NONPOSITIVE_VARIANCE;
            else {
                result.gain_e_per_adu = numerator / denominator;
                if (!isfinite(result.gain_e_per_adu) || result.gain_e_per_adu <= 0) goto fail;
                result.gain_state = DETECTOR_GAIN_PAIR_AVAILABLE;
            }
        }
    }
    pixelmap_del(common);
    *out = result;
    return 0;
fail:
    pixelmap_del(common);
    return -1;
}

#undef RECT_RON_HS
#undef RECT_RON_SAMPLES

/*----------------------------------------------------------------------------*/
/**
  @brief    Compute the readout noise in a ring.
  @param    diff    Input image, usually a difference frame.
  @param    zone    Center coordinates and ring radiuses (4 int)
  @param    noise   Output parameter: noise in the frame.
  @param    error   Output parameter: error on the noise.
  @return   int 0 if Ok, -1 otherwise.

  Same as image_rect_readout_noise, but Poisson dist. in a ring.

  This function is meant to compute the readout noise in a frame by means of a 
  MonteCarlo approach. The input is a frame, usually a difference between two 
  frames taken with the same settings for the acquisition system, although no 
  check is done on that, it is up to the caller to feed in the right kind of 
  frame.

  The provided zone is an array of four integers specifying the zone to take 
  into account for the computation. The integers specify ranges as x, y, r1, r2
  where these coordinates are given in the FITS notation (x from 1 to lx, y 
  from 1 to ly). The zone is a ring in this case.

  The algorithm will create typically 50 9x9 windows on the frame, scattered 
  optimally using a Poisson law in the ring. In each window, the standard 
  deviation of all pixels in the window is computed and this value is stored. 
  The readout noise is the median of all computed standard deviations, and the 
  error is the standard deviation of the standard deviations.

  Both values (noise and error) are returned by modifying a passed double. If 
  you do not care about the error, pass NULL.
 */
/*----------------------------------------------------------------------------*/
#define RING_RON_HLX     4
#define RING_RON_HLY     4
#define RING_RON_SAMPLES     50
int image_ring_readout_noise(
	    image_t *   diff,
	    int     *   zone_def,
	    double  *   noise,
	    double  *   error)
{
    double3     *   sample_reg ;
    image_stats *   vig_stats ;
    double      *   rms_list ;
    double          rms_median ;
    double          rms_error ;
    int             zone[4];
    int             nb_valid_samples ;
    int             i, j ;

    /* Test Inputs */
    if (diff==NULL || noise==NULL || zone_def==NULL) return -1 ;
    if (zone_def[2] >= zone_def[3]) return -1 ; 

    /* Generate n+1 regions, because the first region is always at a given */
    /* position and it would bias the measurement. */
    sample_reg = generate_ring_poisson_points(zone_def, RING_RON_SAMPLES+1, 
            RING_RON_SAMPLES+1) ;

    /* Count the valid samples  */
    nb_valid_samples = 0 ;
    for (i=1 ; i<=RING_RON_SAMPLES ; i++) {
        zone[0]=zone_def[0]+sample_reg->x[i]*cos(sample_reg->y[i])-RING_RON_HLX;
        zone[1]=zone_def[0]+sample_reg->x[i]*cos(sample_reg->y[i])+RING_RON_HLX;
        zone[2]=zone_def[1]+sample_reg->x[i]*sin(sample_reg->y[i])-RING_RON_HLY;
        zone[3]=zone_def[1]+sample_reg->x[i]*sin(sample_reg->y[i])+RING_RON_HLY;
        if ((zone[0] > 0) && (zone[1] <= diff->lx) && (zone[2] > 0) &&
                (zone[3] <= diff->ly)) nb_valid_samples++ ;
    }
   
    /* Check if there are enough valid samples */
    if (nb_valid_samples < RING_RON_SAMPLES/4) {
        e_error("not enough samples to compute noise - abort") ;
        double3_del(sample_reg) ;
        return -1 ;
    }
    
    /* Now, for each valid sample, extract a vignette and compute the RMS */
    rms_list = malloc(nb_valid_samples * sizeof(double));
    j = 0 ;
    for (i=1 ; i<=RING_RON_SAMPLES ; i++) {
        zone[0]=zone_def[0]+sample_reg->x[i]*cos(sample_reg->y[i])-RING_RON_HLX;
        zone[1]=zone_def[0]+sample_reg->x[i]*cos(sample_reg->y[i])+RING_RON_HLX;
        zone[2]=zone_def[1]+sample_reg->x[i]*sin(sample_reg->y[i])-RING_RON_HLY;
        zone[3]=zone_def[1]+sample_reg->x[i]*sin(sample_reg->y[i])+RING_RON_HLY;
        if ((zone[0] > 0) && (zone[1] <= diff->lx) && (zone[2] > 0) &&
                (zone[3] <= diff->ly)) {
            if ((vig_stats=image_getstats_opts(diff, NULL, NULL, zone))==NULL) {
                e_error("computing stats on vignette");
                free(rms_list);
                double3_del(sample_reg) ;
                return -1 ;
            }
            rms_list[j] = (double)vig_stats->stdev ;
            free(vig_stats) ;
            j++ ;
        }
    }
    double3_del(sample_reg) ;

    /* The final computed RMS is the median of all values.  */
    rms_median = double_median(rms_list, nb_valid_samples);
    (*noise) = rms_median ;
    if (error != NULL) {
        /* The error is the rms of the rms */
        rms_error = double_rms(rms_list, nb_valid_samples);
        (*error) = rms_error ;
    }
    free(rms_list);
    return 0 ;
}
#undef RING_RON_HLX
#undef RING_RON_HLY
#undef RING_RON_SAMPLES


/*----------------------------------------------------------------------------*/
/**
  @brief	Compute the linearity of the detector
  @param	in	input cube
  @param	dit	list of DIT values
  @param    deg degree of the fit
  @return	cube with deg+1 images (deg coeffs & rms)
 */
/*----------------------------------------------------------------------------*/
cube_t * detector_linearity_fit(
		cube_t	*	in, 
		double	*	dit,
        int         deg)
{
    cube_t      *   fitres ;
    image_t     *   timeline ;
    int             pos ;
    int             npix ;
    double          f, f_prod ;
    double          y, err, sq_err ;
    matrix      *   mx, 
				*	ma, 
				*	mb ;
    int             i, j, k, l ;

    if (in==NULL || dit==NULL) return NULL ;
    if ((deg!=3) && (deg!=4)) return NULL ;

    /* Allocate deg+1 images to store the results */
    fitres = cube_new(in->lx, in->ly, deg+1);
    for (k=0 ; k<deg+1 ; k++) {
        fitres->plane[k] = image_new(in->lx, in->ly);
    }

    /* Loop over all pixels */
    npix = in->lx * in->ly ;

    /* Create matrices */
    ma = matrix_new(deg, in->np);
    mb = matrix_new(1, in->np);

    /*
     * Sorry for the double loop, it is not truly needed.
     * The only interest is to put a compute_status that
     * does not print out too often, otherwise it slows down
     * the already heavy computation.
     */
    for (j=0 ; j<in->ly ; j++) {
        compute_status("fitting polynomial...", j, in->ly, 1);
        for (i=0 ; i<in->lx ; i++) {
            pos = i + j * in->lx ;

            /* Extract time line */
            timeline = cube_get_z(in, pos);
            if (timeline==NULL) {
                e_error("extracting time line at pos %d: aborting", pos);
                cube_del(fitres);
                return NULL ;
            }

            /* Fill in matrices */
            for (k=0 ; k<in->np ; k++) {
                f = (double)timeline->data[k] ;
                f_prod = f ;
                for (l=0 ; l<deg ; l++) {
                    ma->m[k+l*in->np] = f_prod ;
                    f_prod *= f ;
                }
                mb->m[k] = dit[k] ;
            }

            /* Solve least-squares */
            mx = matrix_leastsq(ma,mb) ;
            if (mx == NULL) {
                for (k=0 ; k<deg+1 ; k++) 
                    fitres->plane[k]->data[pos] = 0 ;
            } else {
                /* Store results in a, b, c, d? images */
                for (k=0 ; k<deg ; k++) 
                    fitres->plane[k]->data[pos] = (pixelvalue)mx->m[k] ;

                /* Goodness of fit */
                sq_err=0 ;
                for (k=0 ; k<in->np ; k++) {
                    /* Computed by model */
                    y = 0.0 ;
                    for (l=0 ; l<deg ; l++) y += mx->m[l]*ma->m[k+l*in->np] ;
                    
                    /* Error between model and reality */
                    err = y - mb->m[k] ;
                    sq_err += err * err ;
                }
                sq_err /= (double)in->np ;
                fitres->plane[deg]->data[pos] = (pixelvalue)sq_err ;
                matrix_del(mx);
            }
            image_del(timeline);
        }
    }

    /* Delete matrices */
    matrix_del(ma);
    matrix_del(mb);

    return fitres ;
}

/*----------------------------------------------------------------------------*/
/**
  @brief    Correct detector non linearity
  @param    in  input cube to correct (modified)
  @param    coeff_a     a coefficients
  @param    coeff_b     b coefficients
  @param    coeff_c     c coefficients
  @return   0 if ok, -1 otherwise
 */
/*----------------------------------------------------------------------------*/
int cube_correct_detlin(
        cube_t  *   in,
        image_t *   coeff_a,
        image_t *   coeff_b,
        image_t *   coeff_c)
{
    double      coeff_1 ;
    double      coeff_2 ;
    double      val ;
    int         i, j ;

    /* Test inputs */
    if ((in==NULL) || (coeff_a==NULL) || (coeff_b==NULL) || (coeff_c==NULL))
        return -1 ;
    if ((in->lx!=coeff_a->lx)||(in->lx!=coeff_b->lx)||(in->lx!=coeff_c->lx)) {
        e_error("incompatible size - abort") ;
        return -1 ;
    }
    if ((in->ly!=coeff_a->ly)||(in->ly!=coeff_b->ly)||(in->ly!=coeff_c->ly)) {
        e_error("incompatible size - abort") ;
        return -1 ;
    }

    /* Loop on each pixel */
    for (i=0 ; i<in->lx * in->ly ; i++) {
        /* Compute the coefficients */
        if (fabs(coeff_a->data[i]) < 1e-30) {
            coeff_1 = coeff_2 = (double)0.0 ;
        } else {
            coeff_1 = (double)coeff_b->data[i] / (double)coeff_a->data[i] ; 
            coeff_2 = (double)coeff_c->data[i] / (double)coeff_a->data[i] ; 
        }
        /* Correct this pixel in each plane */
        for (j=0 ; j<in->np ; j++) { 
            val = (double)(in->plane[j])->data[i] ;
            (in->plane[j])->data[i]=(pixelvalue)(val + coeff_1 * val * val + 
                                                 coeff_2 * val * val * val) ;
        }
    }
    return 0 ;
}
