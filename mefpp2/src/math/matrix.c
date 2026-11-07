/*-------------------------------------------------------------------------*/
/**
   @file	matrix.c
   @author	Nicolas Devillard
   @date	1994
   @version	$Revision: 1.10 $
   @brief	basic 2d matrix handling routines
*/
/*--------------------------------------------------------------------------*/

/*
	$Id: matrix.c,v 1.10 2001/11/13 13:33:46 yjung Exp $
	$Author: yjung $
	$Date: 2001/11/13 13:33:46 $
	$Revision: 1.10 $
*/

/*----------------------------------------------------------------------------
   								Includes
 ---------------------------------------------------------------------------*/

#include "matrix.h"
#include "comm.h"

/*----------------------------------------------------------------------------
   								Macros
 ---------------------------------------------------------------------------*/

#define dtiny(a) ((a)<0?(a)> -1.e-30:(a)<1.e-30)

/*----------------------------------------------------------------------------
						Private function prototypes
 ---------------------------------------------------------------------------*/

static int matrix_gausspiv(double *ptra, double *ptrc, int n);

/*----------------------------------------------------------------------------
  							Function codes
 ---------------------------------------------------------------------------*/


/*-------------------------------------------------------------------------*/
/**
  @brief    Allocates a new matrix.
  @param    nr  Number of rows.
  @param    nc  Number of columns.
  @return   Pointer to newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_new(int nr, int nc)
{
	matrix	*	b;
	b = (matrix*)calloc(1, sizeof(matrix));
	b->m = (double*)calloc(nr*nc,sizeof(double));
	b->nr= nr;
	b->nc= nc;
	return b;
}


/*-------------------------------------------------------------------------*/
/**
  @brief    Copy a matrix.
  @param    a   matrix to copy.
  @return   Pointer to newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_copy(matrix * a)
{
    matrix * b = matrix_new(a->nr,a->nc);
    if (b!=NULL) {
        register int s = a->nr*a->nc;
        register double *mm = b->m+s;
        register double *am = a->m+s;
        while (s--) *--mm = *--am;
    }
    return b;
}


/*-------------------------------------------------------------------------*/
/**
  @brief    Frees memory associated to a matrix.
  @param    a   matrix to free.
  @return   void
 */
/*--------------------------------------------------------------------------*/
void matrix_del(matrix * a)
{
	if (a == NULL) return ;
	if (a->m != NULL) free(a->m) ;
	free(a) ;
	return ;
}


/*-------------------------------------------------------------------------*/
/**
  @brief    Multiplies 2 matrices.
  @param    a   matrix on the left side of the multiplication.
  @param    b   matrix on the right side of the multiplication.
  @return   matrix a*b.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_mul(matrix * a, matrix * b)
{
	matrix			*	c, 
					*	d ;
	int 				n1, 
						n2, 
						n3 ;
	register double	*	a0;
	register double *	c0;
	register double *	d0;
	register int 		i,j,k;

	/* Initialize */
	n1 = a->nr ;
	n2 = a->nc ;
	n3 = b->nc ;

	
	if(n2 != b->nr) return NULL;
	c = matrix_new(n1,n3);
	d = matrix_transpose(b);

	for (i=0,c0=c->m ; i<n1 ; i++)
		for (j=0,d0=d->m ; j<n3 ; j++,c0++)
			for (k=0,*c0=0,a0=a->m+i*n2 ; k<n2 ; k++) *c0 += *a0++ * *d0++;
	matrix_del(d);
	return c;
}


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
matrix * matrix_invert(matrix * aa)
{
    matrix		*	bb ;
	matrix		*	temp ;
    int 			test ;
	double 			det ;
	register double	ted ;
	double			a, b, c, d, e, f, g, h, i ;
	/* Initialize */
	test = 1 ;

    if(aa->nr!=aa->nc) return NULL ; 
    bb = matrix_new(aa->nr, aa->nc) ;

    if(aa->nr==1) {
        det= *(aa->m) ;
        if (dtiny(det)) test = 0 ;
        ted = 1. / det ;
        *(bb->m) = ted ;
    } else if (aa->nr == 2) {
        register double *mm=aa->m;
        a = *(mm++) ;
		b = *(mm++) ;
        c = *(mm++) ;
		d = *(mm) ;
        det = a*d - b*c ;
        if (dtiny(det)) test = 0 ;
        ted = 1. / det ;
        mm = bb->m ;
        *(mm++) = d*ted ;
		*(mm++) = -b*ted ;
        *(mm++) = -c*ted ;
		*(mm) = a*ted ;
    } else if (aa->nr == 3) {
        register double *mm=aa->m ;
        a = *(mm++) ;
		b = *(mm++) ;
		c = *(mm++) ;
        d = *(mm++) ;
		e = *(mm++) ;
		f = *(mm++) ;
        g = *(mm++) ;
		h = *(mm++) ;
		i = *(mm) ;
        det = a*e*i - a*h*f - b*d*i + b*g*f + c*d*h - c*g*e ;
        if (dtiny(det)) test = 0 ;
        ted = 1. /det ;
        mm = bb->m ;
        *(mm++) = (e*i - f*h) * ted ;
		*(mm++) = (c*h - b*i) * ted ;
		*(mm++) = (b*f - e*c) * ted ;
        *(mm++) = (f*g - d*i) * ted ;
		*(mm++) = (a*i - g*c) * ted ;
		*(mm++) = (d*c - a*f) * ted ;
        *(mm++) = (d*h - g*e) * ted ;
		*(mm++) = (g*b - a*h) * ted ;
		*(mm) = (a*e - d*b) * ted ;
    } else {
        temp=matrix_copy(aa);
        if(matrix_gausspiv(temp->m,bb->m,aa->nr)==0) test=0;
        matrix_del(temp);
    }
    if (test == 0) return NULL ;

    return bb ;
}



/*-------------------------------------------------------------------------*/
/**
  @brief    Transposes a matrix.
  @param    a   matrix to transpose.
  @return   Newly allocated matrix.
 */
/*--------------------------------------------------------------------------*/
matrix * matrix_transpose(matrix * a)
{
	register int		nc, 
						nr	;
	register double	*	a0 ;
	register double *	b0 ;
	register int 		i, j ;
	matrix 			*	b ;

	/* Initialize */
	nc = a->nc ;
	nr = a->nr ;
	b = matrix_new(nc, nr) ;
	if (b == NULL) return NULL ;

	for (i=0,b0=b->m ; i<nc ; i++)
		for (j=0,a0=a->m+i ; j<nr ; j++,a0+=nc,b0++) *b0 = *a0 ;
	return b ;
}


/*-------------------------------------------------------------------------*/
/**
  @brief    Line simplification with Gauss method.
  @param    ptra    A matrix line.
  @param    ptrc    A matrix line.
  @param    n       Number of rows in each line.
  @return   int 1 if Ok, 0 else.
 
  This function is used only for the general case in matrix inversion.
 */
/*--------------------------------------------------------------------------*/
static int matrix_gausspiv(double *ptra, double *ptrc, int n)
/* c(n,n) = a(n,n)^-1 */
{
#define ABS(a) (((a) > 0) ? (a) : -(a))
	register int		i, j, k, l ;
	int 				maj ;
	double 				max, r, t ;  
	double 			*	ptrb ;

	ptrb = (double*)calloc(n*n, sizeof(double)) ;
	for (i=0 ; i<n ; i++) ptrb[i*n+i] = 1.0 ;

	for (i=1 ; i<=n ; i++) {
		/* Search max in current column  */
		max = ABS(*(ptra + n*i-n)) ;
		maj = i ;
		for (j=i ; j<=n ; j++)
			if (ABS(*(ptra+n*j+i-n-1)) > max) {
				maj = j ;
				max = ABS(*(ptra+n*j+i-n-1)) ;
			}

		/* swap lines i and maj */
		if (maj != i) {
			for (j = i;j <= n;j++) {
				r = *(ptra + n * maj + j - n - 1) ;
				*(ptra + n *maj + j - n -1) = *(ptra +n * i + j - n - 1) ;
				*(ptra + n * i + j - n - 1) = r ;
			}
			for(l=0 ; l<n ; l++) {
				r = *(ptrb + l * n + maj - 1) ;
				*(ptrb + l * n + maj - 1) = *(ptrb + l * n + i - 1) ;
				*(ptrb + l * n + i - 1) = r ;
			}
		}

		/* Subtract line by line */
		for (j=i+1 ; j<=n ; j++) {
			t = (*(ptra+(n+1)*i-n-1)) ;
			if (dtiny(t)) return 0 ;
			r = (*(ptra+n*j+i-n-1)) / t ;
			for (l=0 ; l<n ; l++) *(ptrb+l*n+j-1) -= r * (*(ptrb+l*n+i-1)) ;
			for (k=i ; k<=n ; k++) *(ptra+n*j+k-n-1) -= r * (*(ptra+n*i+k-n-1));
		}
	}

	/* Triangular system resolution	*/
	for(l=0 ; l<n ; l++)
		for (i=n ; i>=1 ; i--) {
			t = (*(ptra+(n+1)*i-n-1)) ;
			if (dtiny(t)) return 0 ;
			*(ptrc+l+(i-1)*n) = (*(ptrb+l*n+i-1)) / t ;
			if (i>1)
				for (j=i-1 ; j>0 ; j--)
					*(ptrb+l*n+j-1)-=(*(ptra+n*j+i-n-1))*(*(ptrc+l+(i-1)*n)) ;
		}
	free(ptrb) ;
	return 1 ;
}


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
		matrix	*	a,
		matrix	*	b)
{
	matrix	*	m1,
			*	m2,
			*	m3,
			*	m4,
			*	m5 ;

	m1 = matrix_transpose(a) ;
	m2 = matrix_mul(a, m1) ;
	m3 = matrix_invert(m2) ;
	if (m3 == NULL) return NULL ;
	m4 = matrix_mul(b, m1) ;
	m5 = matrix_mul(m4, m3) ;
	matrix_del(m1) ;
	matrix_del(m2) ;
	matrix_del(m3) ;
	matrix_del(m4) ;
	return m5 ;
}


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
		matrix	*	m,
		char 	*	name)
{
	int	i, j ;

	fprintf(stdout, "# matrix %s is [%d x %d]\n", name, m->nr, m->nc) ;
	for (j=0 ; j<m->nr ; j++) {
		for (i=0 ; i<m->nc ; i++) {
			fprintf(stdout, "%g\t", m->m[i+j*m->nc]) ;
		}
		fprintf(stdout, "\n") ;
	}
	fprintf(stdout, "\n") ;
}


/* Checked additions deliberately follow the legacy definitions: xmemory
 * macros below affect only these additions, preserving old allocation paths. */
#include <stdint.h>
#include <float.h>
#include "xmemory.h"

void matrix_qr_result_del(matrix_qr_result *result)
{
    if (!result) return;
    if (result->solution) {
        if (result->solution->m) free(result->solution->m);
        free(result->solution);
    }
    if (result->r) {
        if (result->r->m) free(result->r->m);
        free(result->r);
    }
    if (result->pivots) free(result->pivots);
    free(result);
}

/* Do not use unchecked legacy matrix_new in an error-atomic interface. */
static matrix *matrix_qr_new(int nr, int nc)
{
    matrix *m = calloc(1, sizeof(*m));
    if (!m) return NULL;
    m->nr = nr; m->nc = nc;
    m->m = calloc((size_t)nr * (size_t)nc, sizeof(double));
    if (!m->m) { free(m); return NULL; }
    return m;
}

int matrix_leastsq_qr_checked(const matrix *design, const matrix *rhs,
    const double *scales, double tolerance, matrix_qr_result **out)
{
    matrix_qr_result *res = NULL;
    double *a = NULL, *b = NULL, *v = NULL, *z = NULL;
    double reference = 0, norm, best, alpha, tau, dot, q, rn = 0, an = 0, invn = 0;
    size_t m, n, i, j, k, pivot, h, count;
    if (!design || !rhs || !scales || !out || *out ||
        !design->m || !rhs->m || design->nr < 1 || design->nc < 1 ||
        design->nr < design->nc || rhs->nr != design->nr || rhs->nc != 1 ||
        !isfinite(tolerance) || tolerance <= 0 || tolerance >= 1) return -1;
    m = (size_t)design->nr; n = (size_t)design->nc;
    if (m > SIZE_MAX/n || m*n > SIZE_MAX/sizeof(double) ||
        n > SIZE_MAX/sizeof(int)) return -1;
    count = m*n;
    for (j=0; j<n; ++j) if (!isfinite(scales[j]) || scales[j]<=0) return -1;
    for (i=0; i<count; ++i) if (!isfinite(design->m[i])) return -1;
    for (i=0; i<m; ++i) if (!isfinite(rhs->m[i])) return -1;
    res = calloc(1, sizeof(*res));
    if (!res) goto fail;
    res->columns = (int)n;
    res->r = matrix_qr_new((int)n, (int)n);
    res->pivots = malloc(n*sizeof(int));
    a = malloc(count*sizeof(double)); b = malloc(m*sizeof(double));
    v = malloc(m*sizeof(double)); z = malloc(n*sizeof(double));
    if (!res->r || !res->pivots || !a || !b || !v || !z) goto fail;
    for (i=0; i<m; ++i) b[i]=rhs->m[i];
    for (j=0; j<n; ++j) {
        res->pivots[j]=(int)j; norm=0;
        for (i=0; i<m; ++i) {
            a[i*n+j]=design->m[i*n+j]*scales[j];
            if (!isfinite(a[i*n+j])) goto fail;
            norm=hypot(norm,a[i*n+j]);
        }
        if (!isfinite(norm)) goto fail;
        if (norm>reference) reference=norm;
    }
    for (k=0; k<n; ++k) {
        best=0; pivot=k;
        for (j=k; j<n; ++j) {
            norm=0;
            for (i=k; i<m; ++i) norm=hypot(norm,a[i*n+j]);
            if (!isfinite(norm)) goto fail;
            if (norm>best) { best=norm; pivot=j; }
        }
        /* Compare by ratio, avoiding underflow in tolerance*reference. */
        if (reference==0 || best/reference<=tolerance) break;
        if (pivot!=k) {
            int ip=res->pivots[k]; res->pivots[k]=res->pivots[pivot];
            res->pivots[pivot]=ip;
            for (i=0; i<m; ++i) { q=a[i*n+k];a[i*n+k]=a[i*n+pivot];a[i*n+pivot]=q; }
        }
        /* Unit-scaled reflector avoids squaring large values. */
        alpha=-copysign(best,a[k*n+k]);
        for (i=k; i<m; ++i) v[i]=a[i*n+k]/best;
        v[k]-=alpha/best;
        dot=0; for (i=k; i<m; ++i) dot+=v[i]*v[i];
        tau=2/dot;
        if (!isfinite(tau)) goto fail;
        for (j=k+1; j<n; ++j) {
            dot=0; for (i=k; i<m; ++i) dot+=v[i]*a[i*n+j];
            dot*=tau; if (!isfinite(dot)) goto fail;
            for (i=k; i<m; ++i) { a[i*n+j]-=v[i]*dot; if(!isfinite(a[i*n+j])) goto fail; }
        }
        dot=0; for (i=k; i<m; ++i) dot+=v[i]*b[i];
        dot*=tau; if (!isfinite(dot)) goto fail;
        for (i=k; i<m; ++i) { b[i]-=v[i]*dot; if(!isfinite(b[i])) goto fail; }
        a[k*n+k]=alpha;
        for (i=k+1; i<m; ++i) a[i*n+k]=0;
        res->rank=(int)(k+1);
    }
    for (i=0; i<n; ++i) for(j=i; j<n; ++j) res->r->m[i*n+j]=a[i*n+j];
    /* Trailing rows are the residual after projection onto accepted columns. */
    for (i=(size_t)res->rank; i<m; ++i) rn=hypot(rn,b[i]);
    if (!isfinite(rn)) goto fail;
    res->residual_norm=rn;
    if ((size_t)res->rank==n) {
        res->solution=matrix_qr_new((int)n,1);
        if (!res->solution) goto fail;
        for (i=n; i-- >0;) {
            q=b[i]; for (j=i+1; j<n; ++j) q-=a[i*n+j]*z[j];
            z[i]=q/a[i*n+i]; if(!isfinite(z[i])) goto fail;
            h=(size_t)res->pivots[i];
            res->solution->m[h]=z[i]*scales[h];
            if(!isfinite(res->solution->m[h])) goto fail;
        }
        for (j=0; j<n; ++j) {
            q=0; for(i=0; i<=j; ++i) q+=fabs(a[i*n+j]);
            if(q>an) an=q;
            /* Column j of inverse(R), computed without storing an inverse. */
            for(i=n; i-- >0;) {
                q=(i==j)?1:0;
                for(h=i+1; h<n; ++h) q-=a[i*n+h]*z[h];
                z[i]=q/a[i*n+i]; if(!isfinite(z[i])) goto fail;
            }
            q=0;for(i=0;i<n;++i) q+=fabs(z[i]);
            if(q>invn) invn=q;
        }
        res->scaled_condition_1=an*invn;
        if(!isfinite(res->scaled_condition_1)) goto fail;
        res->condition_available=1;
    }
    free(a);free(b);free(v);free(z);*out=res;return 0;
fail:
    if (a) free(a);
    if (b) free(b);
    if (v) free(v);
    if (z) free(z);
    matrix_qr_result_del(res);return -1;
}
