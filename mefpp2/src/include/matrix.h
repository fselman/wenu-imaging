/*-------------------------------------------------------------------------*/
/**
   @file    matrix.h
   @author  Nicolas Devillard
   @date    1994
   @version $Revision: 1.12 $
   @brief   basic 2d matrix handling routines
*/
/*--------------------------------------------------------------------------*/

/*
    $Id: matrix.h,v 1.12 2001/11/13 13:33:43 yjung Exp $
    $Author: yjung $
    $Date: 2001/11/13 13:33:43 $
    $Revision: 1.12 $
*/

#ifndef _MATRIX_H_
#define _MATRIX_H_

/*---------------------------------------------------------------------------
   								Includes
 ---------------------------------------------------------------------------*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/*---------------------------------------------------------------------------
   								Defines
 ---------------------------------------------------------------------------*/

#define mx_get(M,i,j)	((M)->m[(i)+(j)*(M)->nc])
#define mx_set(M,i,j,v)	(mx_get(M,i,j)=v)

/*---------------------------------------------------------------------------
   								New Types
 ---------------------------------------------------------------------------*/

/*-------------------------------------------------------------------------*/
/**
  @brief	matrix type
 */
/*-------------------------------------------------------------------------*/
typedef struct _MATRIX_ {
	double	*	m;
	int 		nr;
	int 		nc;
} matrix ;

/*---------------------------------------------------------------------------
  						Function ANSI C prototypes
 ---------------------------------------------------------------------------*/


/*-------------------------------------------------------------------------*/
/**
  @brief    Allocates a new matrix.
  @param    nr  Number of rows.
  @param    nc  Number of columns.
  @return   Pointer to newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_new(int nr, int nc) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Copy a matrix.
  @param    a   matrix to copy.
  @return   Pointer to newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_copy(matrix * a) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Frees memory associated to a matrix.
  @param    a   matrix to free.
  @return   void
 */
/*--------------------------------------------------------------------------*/
void matrix_del(matrix * a) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Multiplies 2 matrices.
  @param    a   matrix on the left side of the multiplication.
  @param    b   matrix on the right side of the multiplication.
  @return   matrix a*b.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_mul(matrix * a, matrix * b) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Inverts a matrix.
  @param    aa  (Square) matrix to invert
  @return   Newly allocated matrix.
 
  The matrix inversion procedure is hardcoded for optimized speed in
  the case of 1x1, 2x2 and 3x3 matrices. This function is not suitable
  for large matrices.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_invert(matrix * aa) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Transposes a matrix.
  @param    a   matrix to transpose.
  @return   Newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_transpose(matrix * a) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Compute the solution of an equation using a pseudo-inverse.
  @param    a   matrix.
  @param    b   matrix.
  @return   Pointer to newly allocated matrix.
 
  The equation is XA=B.
 
  The pseudo-inverse solution to this equation is defined as:
  \begin{verbatim}
  P = B.tA.inv(A.tA)
  \end{verbatim}
 
  P is solving the equation using a least-squares criterion.
  Demonstration left to the reader.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_leastsq(
        matrix  * a,
        matrix  * b) ;


/*-------------------------------------------------------------------------*/
/**
  @brief    Prints out a matrix on stdout.
  @param    m       matrix to print out
  @param    name    Name of the matrix to print out.
  @return   void
 
  The matrix name is printed out, then all values row by row.
  Used for debugging purposes mostly.
 */
/*--------------------------------------------------------------------------*/
void matrix_dump(
        matrix  *   m,
        char    *   name) ;


/* Checked column-pivoted Householder least squares (PR #227, ownership #75).
 * design: M rows by P columns, M >= P; rhs: M rows by 1, row-major.
 * Solves design * solution ~= rhs. This orientation differs from legacy
 * matrix_leastsq's XA=B contract. Work columns are design[:,k]*scales[k];
 * solution is returned in ORIGINAL coordinates/order, not scaled coordinates.
 * 0: owned diagnostic result (including rank deficiency); -1: invalid input,
 * allocation failure or nonfinite arithmetic, with *out unchanged.
 * out must address an empty (NULL) owner distinct from all borrowed inputs.
 * Inputs remain unchanged. 0 < rank_tolerance < 1 is relative to the largest
 * initial scaled column norm. Rank stops at the first rejected pivot.
 * A deficient system has solution==NULL and condition_available==0, never an
 * invented zero solution. residual_norm is the rank-truncated projection norm.
 * r is P by P, upper triangular in pivoted SCALED coordinates, for subsequent
 * triangular covariance solves. pivots[k] is the original column at position k.
 * scaled_condition_1 estimates ||R||_1 ||inverse(R)||_1 by triangular solves;
 * it is not the exact 2-norm condition number of the original design.
 */
typedef struct {
    int rank, columns, condition_available;
    matrix *solution;
    matrix *r;
    int *pivots;
    double residual_norm, scaled_condition_1;
} matrix_qr_result;
int matrix_leastsq_qr_checked(const matrix *design, const matrix *rhs,
    const double *column_scales, double rank_tolerance, matrix_qr_result **out);
void matrix_qr_result_del(matrix_qr_result *result);

#endif
