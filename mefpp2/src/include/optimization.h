/*----------------------------------------------------------------------------*/
/**
   @file    optimization.h
   @author  Y. Jung
   @date    Feb 2003
   @version $Revision: 1.2 $
   @brief   Optimization routines
*/
/*----------------------------------------------------------------------------*/

/*
    $Id: optimization.h,v 1.2 2003/02/28 08:36:01 yjung Exp $
    $Author: yjung $
    $Date: 2003/02/28 08:36:01 $
    $Revision: 1.2 $
*/

#ifndef _OPTIMIZATION_H_
#define _OPTIMIZATION_H_

/*-----------------------------------------------------------------------------
   								Includes
 -----------------------------------------------------------------------------*/

#include "xmemory.h"
#include "doubles.h"

/*-----------------------------------------------------------------------------
   								Define
 -----------------------------------------------------------------------------*/

#define     MAX_NB_ITER     5000

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
        int     *   neval) ;

/* Checked context-aware extension, reviewed in PR #227. Legacy minimize is
 * unchanged. Callbacks receive borrowed PHYSICAL parameters, not scaled ones.
 * VALID must write a finite cost; INADMISSIBLE is a normal rejected model
 * point; ERROR (or an unknown status/nonfinite valid cost) aborts atomically.
 */
typedef enum {
    OPTIMIZATION_EVAL_ERROR = -1,
    OPTIMIZATION_EVAL_VALID = 0,
    OPTIMIZATION_EVAL_INADMISSIBLE = 1
} optimization_evaluation;
typedef optimization_evaluation (*optimization_cost)(
    const double *parameters, int dimensions, void *context, double *cost);
typedef struct {
    int dimensions;
    const double *initial_simplex; /* (P+1) by P, row-major, physical units */
    const double *scales;          /* P strictly positive parameter units */
    const double *lower, *upper;   /* P finite physical bounds, lower < upper */
    optimization_cost cost;
    void *context;
} optimization_problem;
typedef struct {
    size_t max_evaluations; /* all attempted points, including bound rejects */
    double parameter_tolerance; /* max vertex-to-best distance per scaled axis */
    double objective_tolerance; /* spread / max(1, largest absolute vertex cost) */
    double initial_rank_tolerance; /* explicit relative scaled edge-rank cutoff */
} optimization_options;
typedef enum {
    OPTIMIZATION_CONVERGED = 0,
    OPTIMIZATION_EVALUATION_LIMIT = 1
} optimization_status;
typedef struct {
    int dimensions;
    optimization_status status;
    double *parameters;     /* best physical parameters, P elements */
    double *scaled_simplex; /* owned final (P+1) by P dimensionless vertices */
    double *costs;          /* owned P+1 finite valid costs */
    double cost, parameter_spread, objective_spread;
    size_t evaluations, callback_calls, rejected_points, bound_rejections, iterations;
    int best_at_bound;      /* exact finite bound equality, not an uncertainty */
} optimization_result;
/* Returns 0 with owned result for convergence OR exhausted budget; inspect
 * status. Returns -1 on input, allocation, initial feasibility/rank, arithmetic
 * or hard callback failure; *out remains unchanged. out must be an empty owner
 * separate from all borrowed inputs. No input mutation, clipping, hidden
 * parameter scales or convergence defaults. At least P+1 attempts are required.
 * All initial vertices must be feasible and affinely independent at the stated
 * scaled rank tolerance. A converged simplex does not establish identifiability.
 */
int minimize_checked(const optimization_problem *problem,
    const optimization_options *options, optimization_result **out);
void optimization_result_del(optimization_result *result);

#endif
