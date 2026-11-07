/*----------------------------------------------------------------------------*/
/**
   @file	optimization.c
   @author	Y. Jung
   @date	Feb 2003
   @version	$Revision: 1.3 $
   @brief	Optimization methods
*/
/*----------------------------------------------------------------------------*/

/*
	$Id: optimization.c,v 1.3 2003/10/24 11:32:18 yjung Exp $
	$Author: yjung $
	$Date: 2003/10/24 11:32:18 $
	$Revision: 1.3 $
*/

/*-----------------------------------------------------------------------------
   								Includes
 -----------------------------------------------------------------------------*/

#include <math.h>
#include "matrix.h"
#include "doubles.h"
#include "optimization.h"
#include "comm.h"

/*-----------------------------------------------------------------------------
   								Functions prototypes
 -----------------------------------------------------------------------------*/

static double min_test(
        double  **  x,
        double  *   y,
        double  *   x_sum,
        int         nb_dim,
        double (*func2min)(double *, double3 *),
        double3 *   pts_list,
        int         hi1_ind,
        double      factor) ;

/*-----------------------------------------------------------------------------
  							Function codes
 -----------------------------------------------------------------------------*/

/*----------------------------------------------------------------------------*/
/**
  @brief    Minimize a functions with several variables
  @param    x_est   nb_dim+1 initial vectors
  @param    delta_max   quality requested for convergence
  @param    func2min    function to minimize
  @param    pts_list    Anchor points
  @param    neval       nb of function evaluation
  @return   0 if ok, -1 otherwise 
 */
/*----------------------------------------------------------------------------*/
int minimize(
        double  **  x_est,
        int         nb_dim,
        double      delta_max,
        double (*func2min)(double *, double3 *),
        double3 *   pts_list,
        int     *   neval)
{
    double  *   y_est ;
    double  *   x_sum ;
    double      sum ;
    int         low_ind , 
                hi1_ind, 
                hi2_ind ;
    int         i, j ;
        
    double      delta, 
                y_test, 
                y_tmp ;

    /* Initialize */
    *neval = 0 ;

    /* Create and initialize y_est */
    y_est = malloc((nb_dim+1) * sizeof(double)) ;
    for (i=0 ; i<nb_dim+1 ; i++) y_est[i] = (*func2min)(x_est[i], pts_list) ;
    
    /* Create and initialize x_sum */
    x_sum = malloc(nb_dim * sizeof(double)) ;
    for (i=0 ; i<nb_dim ; i++) {
        sum = 0.0 ;
        for (j=0 ; j<nb_dim+1 ; j++) sum += x_est[j][i] ;
        x_sum[i] = sum ;
    }
    
    for (;;) {
        /* Find the lowest, highest and second highest values indexes */
        low_ind = 0 ;
        if (y_est[0] > y_est[1]) {
            hi1_ind = 0 ;
            hi2_ind = 1 ;
        } else {
            hi1_ind = 1 ;
            hi2_ind = 0 ;
        }
        for (i=0 ; i<nb_dim+1 ; i++) {
            if (y_est[i] < y_est[low_ind]) low_ind = i ;
            if (y_est[i] > y_est[hi1_ind]) {
                hi2_ind = hi1_ind ;
                hi1_ind = i ;
            } else if ((y_est[i] > y_est[hi2_ind]) && (i != hi1_ind)) hi2_ind=i;
        }

        /* Check the quality and stop if ok */
        delta = 2.0 * fabs(y_est[hi1_ind]-y_est[low_ind]) /
            (fabs(y_est[hi1_ind])+fabs(y_est[low_ind])+ 1.0e-10) ;
        if (delta < delta_max) {
            /* Quality reached */
            free(x_sum) ;
            free(y_est) ;
            e_comment(0, "Ok after %d iterations", *neval) ;
            return 0 ; 
        } else if (*neval >= MAX_NB_ITER) { 
            /* Check if neval still ok */
            free(x_sum) ;
            free(y_est) ;
            e_error("too many iterations") ;
            return -1 ;
        }
       
        /* Update neval */
        *neval += 2 ;

        /* Begin a new iteration */
        y_test = min_test(x_est, y_est, x_sum, nb_dim, func2min, pts_list, 
                hi1_ind, -1.0);
        if (y_test < y_est[low_ind]) {
            /* Better than the best, try additional extrapolation fac 2.0 */
            y_test=min_test(x_est, y_est, x_sum, nb_dim, func2min, pts_list,
                    hi1_ind,2.0);
        } else if (y_test > y_est[hi2_ind]) {
            /* The reflected point is worse than the second highest, look for */
            /* an intermediate lower pt (1d contraction) */
            y_tmp = y_est[hi1_ind] ;
            y_test=min_test(x_est, y_est, x_sum, nb_dim, func2min, pts_list,
                    hi1_ind,0.5);
            if (y_tmp < y_test) {
                /* This bad point does not want to improve */
                /* Contract around the lowest (best) point */
                for (i=0 ; i<nb_dim+1 ; i++) {
                    if (i != low_ind) {
                        for (j=0 ; j<nb_dim ; j++) {
                            x_est[i][j] = x_sum[j] = 
                                0.5 *(x_est[i][j] + x_est[low_ind][j]) ; 
                            y_est[i] = (*func2min)(x_sum, pts_list);
                        }
                    }
                }
                *neval += nb_dim ;
        
                /* Update x_sum */
                for (i=0 ; i<nb_dim ; i++) {
                    sum = 0.0 ;
                    for (j=0 ; j<nb_dim+1 ; j++) sum += x_est[j][i] ;
                    x_sum[i] = sum ;
                }
            }
        } else --(*neval) ;
    }
}
        
static double min_test(
        double  **  x,
        double  *   y,
        double  *   x_sum,
        int         nb_dim,
        double (*func2min)(double *, double3 *),
        double3 *   pts_list,
        int         hi1_ind,
        double      factor)
{
    double      *   x_test ;
    double          y_test ;
    double          factor1,
                    factor2 ;
    int             i ;

    /* Create and initialize x_test */
    x_test = malloc(nb_dim * sizeof(double)) ;
    factor1 = (1.0 - factor) / nb_dim ;
    factor2 = factor1 - factor ;
    for (i=0 ; i<nb_dim ; i++) 
        x_test[i] = x_sum[i]*factor1 - x[hi1_ind][i]*factor2 ;

    /* Apply the function on it */
    y_test = (*func2min)(x_test, pts_list);
    
    if (y_test < y[hi1_ind]) {
        y[hi1_ind] = y_test ;
        for (i=0 ; i<nb_dim ; i++) {
            x_sum[i] += x_test[i]-x[hi1_ind][i] ;
            x[hi1_ind][i] = x_test[i] ;
        }
    }
    free(x_test) ;
    return y_test ;
}


/* Checked extension reuses this module's reflection/expansion/contraction/
 * shrink structure. Legacy min_test cannot supply callback validity, bounds,
 * exact budgets or atomic ownership and is deliberately left unchanged. */
#include <stdint.h>
#include <limits.h>

void optimization_result_del(optimization_result *result)
{
    if (!result) return;
    if (result->parameters) free(result->parameters);
    if (result->scaled_simplex) free(result->scaled_simplex);
    if (result->costs) free(result->costs);
    free(result);
}

/* Internal status 2 means budget exhausted, distinct from callback states. */
static int optimization_evaluate(const optimization_problem *p,
    const optimization_options *o, optimization_result *r,
    const double *x, double *physical, double *cost)
{
    int j, rc;
    if (r->evaluations >= o->max_evaluations) return 2;
    ++r->evaluations;
    for (j=0; j<p->dimensions; ++j) {
        physical[j]=x[j]*p->scales[j];
        if (!isfinite(x[j]) || !isfinite(physical[j]) ||
            physical[j]<p->lower[j] || physical[j]>p->upper[j]) {
            ++r->rejected_points; ++r->bound_rejections;
            return OPTIMIZATION_EVAL_INADMISSIBLE;
        }
    }
    ++r->callback_calls;
    /* A callback which omits its promised output is a hard failure. */
    *cost=NAN;
    rc=p->cost(physical,p->dimensions,p->context,cost);
    if (rc==OPTIMIZATION_EVAL_INADMISSIBLE) { ++r->rejected_points; return rc; }
    if (rc!=OPTIMIZATION_EVAL_VALID || !isfinite(*cost)) return -1;
    return 0;
}

static void optimization_extremes(optimization_result *r, size_t *lo,
    size_t *hi, size_t *second)
{
    size_t i,j,n=(size_t)r->dimensions;
    double fscale=1,spread=0,q;
    *lo=*hi=0;
    for(i=0;i<=n;++i) {
        if(r->costs[i]<r->costs[*lo]) *lo=i;
        if(r->costs[i]>=r->costs[*hi]) *hi=i;
        if(fabs(r->costs[i])>fscale) fscale=fabs(r->costs[i]);
    }
    *second=(*hi==0)?1:0;
    for(i=0;i<=n;++i) if(i!=*hi && r->costs[i]>r->costs[*second]) *second=i;
    /* Division before subtraction avoids overflow for opposite large costs. */
    r->objective_spread=r->costs[*hi]/fscale-r->costs[*lo]/fscale;
    for(i=0;i<=n;++i) for(j=0;j<n;++j) {
        q=fabs(r->scaled_simplex[i*n+j]-r->scaled_simplex[*lo*n+j]);
        if(q>spread) spread=q;
    }
    r->parameter_spread=spread;
}

static void optimization_accept(optimization_result *r,size_t row,
    const double *x,double cost)
{
    size_t j,n=(size_t)r->dimensions;
    for(j=0;j<n;++j) r->scaled_simplex[row*n+j]=x[j];
    r->costs[row]=cost;
}

int minimize_checked(const optimization_problem *p,
    const optimization_options *o, optimization_result **out)
{
    optimization_result *r=NULL;
    matrix_qr_result *geometry=NULL;
    matrix edges,zero;
    double *centroid=NULL,*reflection=NULL,*trial=NULL,*physical=NULL,*edge_data=NULL;
    double yr,yc;size_t n,count,i,j,lo=0,hi=0,second=0;int rc,accepted;
    if(!p||!o||!out||*out||p->dimensions<1||!p->initial_simplex||!p->scales||
       !p->lower||!p->upper||!p->cost||
       !isfinite(o->parameter_tolerance)||o->parameter_tolerance<=0||
       !isfinite(o->objective_tolerance)||o->objective_tolerance<=0||
       !isfinite(o->initial_rank_tolerance)||o->initial_rank_tolerance<=0||
       o->initial_rank_tolerance>=1) return -1;
    n=(size_t)p->dimensions;
    if(n==SIZE_MAX || n+1>SIZE_MAX/n || (n+1)*n>SIZE_MAX/sizeof(double) ||
       o->max_evaluations<n+1) return -1;
    count=(n+1)*n;
    for(j=0;j<n;++j) if(!isfinite(p->scales[j])||p->scales[j]<=0||
       !isfinite(p->lower[j])||!isfinite(p->upper[j])||p->lower[j]>=p->upper[j]) return -1;
    for(i=0;i<count;++i) if(!isfinite(p->initial_simplex[i])||
       p->initial_simplex[i]<p->lower[i%n]||p->initial_simplex[i]>p->upper[i%n]) return -1;
    r=calloc(1,sizeof(*r));if(!r) goto fail;
    r->dimensions=p->dimensions;
    r->parameters=malloc(n*sizeof(double));
    r->scaled_simplex=malloc(count*sizeof(double));r->costs=malloc((n+1)*sizeof(double));
    centroid=malloc(n*sizeof(double));reflection=malloc(n*sizeof(double));
    trial=malloc(n*sizeof(double));physical=malloc(n*sizeof(double));
    edge_data=malloc(n*n*sizeof(double));
    if(!r->parameters||!r->scaled_simplex||!r->costs||!centroid||!reflection||
       !trial||!physical||!edge_data) goto fail;
    for(i=0;i<count;++i) {
        r->scaled_simplex[i]=p->initial_simplex[i]/p->scales[i%n];
        if(!isfinite(r->scaled_simplex[i])) goto fail;
    }
    /* Reuse the qualified checked QR rather than a new rank implementation. */
    for(i=0;i<n;++i) for(j=0;j<n;++j)
        edge_data[i*n+j]=r->scaled_simplex[(i+1)*n+j]-r->scaled_simplex[j];
    for(j=0;j<n;++j) { centroid[j]=0;trial[j]=1; }
    edges.m=edge_data;edges.nr=edges.nc=p->dimensions;
    zero.m=centroid;zero.nr=p->dimensions;zero.nc=1;
    if(matrix_leastsq_qr_checked(&edges,&zero,trial,o->initial_rank_tolerance,&geometry)
       || geometry->rank!=p->dimensions) goto fail;
    matrix_qr_result_del(geometry);geometry=NULL;
    for(i=0;i<=n;++i) {
        rc=optimization_evaluate(p,o,r,r->scaled_simplex+i*n,physical,r->costs+i);
        if(rc!=0) goto fail;
    }
    r->status=OPTIMIZATION_EVALUATION_LIMIT;
    for(;;) {
        optimization_extremes(r,&lo,&hi,&second);
        if(r->parameter_spread<=o->parameter_tolerance &&
           r->objective_spread<=o->objective_tolerance) { r->status=OPTIMIZATION_CONVERGED;break; }
        if(r->evaluations>=o->max_evaluations) break;
        ++r->iterations;
        for(j=0;j<n;++j) {
            long double sum=0;
            for(i=0;i<=n;++i) if(i!=hi) sum+=(long double)r->scaled_simplex[i*n+j]/n;
            centroid[j]=(double)sum;
            if(!isfinite(centroid[j])) goto fail;
            reflection[j]=centroid[j]+(centroid[j]-r->scaled_simplex[hi*n+j]);
        }
        yr=HUGE_VAL;
        rc=optimization_evaluate(p,o,r,reflection,physical,&yr);
        if(rc<0) goto fail;
        if(rc==2) break;
        if(rc==1) yr=HUGE_VAL;
        if(yr<r->costs[lo]) {
            for(j=0;j<n;++j) trial[j]=centroid[j]+2*(reflection[j]-centroid[j]);
            yc=HUGE_VAL;rc=optimization_evaluate(p,o,r,trial,physical,&yc);
            if(rc<0) goto fail;
            if(rc==0 && yc<yr) optimization_accept(r,hi,trial,yc);
            else optimization_accept(r,hi,reflection,yr);
            if(rc==2) break;
        } else if(yr<r->costs[second]) optimization_accept(r,hi,reflection,yr);
        else {
            int outside=yr<r->costs[hi];
            for(j=0;j<n;++j) trial[j]=.5*centroid[j]+.5*(outside?reflection[j]:r->scaled_simplex[hi*n+j]);
            yc=HUGE_VAL;rc=optimization_evaluate(p,o,r,trial,physical,&yc);
            if(rc<0) goto fail;
            if(rc==2) { if(outside) optimization_accept(r,hi,reflection,yr);break; }
            accepted=(rc==0 && (outside?yc<=yr:yc<r->costs[hi]));
            if(accepted) optimization_accept(r,hi,trial,yc);
            else for(i=0;i<=n;++i) if(i!=lo) {
                for(j=0;j<n;++j) trial[j]=.5*r->scaled_simplex[i*n+j]+.5*r->scaled_simplex[lo*n+j];
                rc=optimization_evaluate(p,o,r,trial,physical,&yc);
                if(rc<0) goto fail;
                if(rc==2) goto finish;
                /* Nonconvex feasibility: retain the old valid vertex on rejection. */
                if(rc==0) optimization_accept(r,i,trial,yc);
            }
        }
    }
finish:
    optimization_extremes(r,&lo,&hi,&second);r->cost=r->costs[lo];
    for(j=0;j<n;++j) {
        r->parameters[j]=r->scaled_simplex[lo*n+j]*p->scales[j];
        if(!isfinite(r->parameters[j])) goto fail;
        if(r->parameters[j]==p->lower[j]||r->parameters[j]==p->upper[j]) r->best_at_bound=1;
    }
    free(centroid);free(reflection);free(trial);free(physical);free(edge_data);
    *out=r;return 0;
fail:
    matrix_qr_result_del(geometry);
    if(centroid) free(centroid);
    if(reflection) free(reflection);
    if(trial) free(trial);
    if(physical) free(physical);
    if(edge_data) free(edge_data);
    optimization_result_del(r);return -1;
}
