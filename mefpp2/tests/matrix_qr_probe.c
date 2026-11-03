
#include <assert.h>
#include <float.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "matrix.h"
static void close_to(double a,double b,double tol) { assert(fabs(a-b)<=tol*fmax(1,fabs(b))); }
static matrix_qr_result *solve(double *a,int m,int n,double *b,double *s,double t)
{
    matrix am={a,m,n},bm={b,m,1};matrix_qr_result *out=NULL;
    assert(matrix_leastsq_qr_checked(&am,&bm,s,t,&out)==0);assert(out);return out;
}
int main(void)
{
    double a[]={1,0,1,1,1,2},b[]={1,2,2},s[]={1,1};
    double ac[6],bc[3];matrix_qr_result *out=NULL,*sentinel;
    matrix am={a,3,2},bm={b,3,1};int i,j,k;
    memcpy(ac,a,sizeof a);memcpy(bc,b,sizeof b);
    out=solve(a,3,2,b,s,1e-12);assert(out->rank==2&&out->condition_available);
    close_to(out->solution->m[0],7.0/6,1e-13);close_to(out->solution->m[1],.5,1e-13);
    close_to(out->residual_norm,sqrt(1.0/6),1e-13);
    assert(out->pivots[0]==1);assert(out->scaled_condition_1>=1);
    /* Independent factor reconstruction via column inner products. */
    for(i=0;i<2;++i)for(j=0;j<2;++j){double lhs=0,rhs=0;
        for(k=0;k<3;++k) lhs+=a[k*2+out->pivots[i]]*a[k*2+out->pivots[j]];
        for(k=0;k<2;++k) rhs+=out->r->m[k*2+i]*out->r->m[k*2+j];
        close_to(lhs,rhs,1e-13);
    }
    sentinel=out;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&out==sentinel);
    matrix_qr_result_del(out);out=NULL;
    s[0]=1e-7;s[1]=1e7;out=solve(a,3,2,b,s,1e-16);
    close_to(out->solution->m[0],7.0/6,1e-12);close_to(out->solution->m[1],.5,1e-12);
    matrix_qr_result_del(out);out=NULL;s[0]=s[1]=1;
    {double aa[]={1,2,2,4,3,6};out=solve(aa,3,2,b,s,1e-12);
     assert(out->rank==1&&!out->solution&&!out->condition_available);matrix_qr_result_del(out);}
    {double aa[]={0,0,0,0,0,0};out=solve(aa,3,2,b,s,1e-12);
     assert(out->rank==0&&!out->solution);close_to(out->residual_norm,3,1e-14);matrix_qr_result_del(out);}
    {double aa[]={1,1,1,1+1e-10,1,1-1e-10},bb[]={1,1-1e-10,1+1e-10};
     out=solve(aa,3,2,bb,s,1e-8);assert(out->rank==1);matrix_qr_result_del(out);
     out=solve(aa,3,2,bb,s,1e-14);assert(out->rank==2);
     close_to(out->solution->m[0],2,1e-5);close_to(out->solution->m[1],-1,1e-5);matrix_qr_result_del(out);}
    {double aa[]={2},bb[]={6},ss[]={.5};out=solve(aa,1,1,bb,ss,1e-12);
     close_to(out->solution->m[0],3,1e-14);close_to(out->scaled_condition_1,1,1e-14);matrix_qr_result_del(out);}
    {double aa[15],bb[5],ss[]={1,.01,100};
     double noise[]={.1,-.4,.6,-.4,.1};
     for(i=0;i<5;++i){double t=i-2;aa[3*i]=1;aa[3*i+1]=t;aa[3*i+2]=t*t;
         bb[i]=2-3*t+.5*t*t+noise[i];}
     out=solve(aa,5,3,bb,ss,1e-12);assert(out->rank==3);
     close_to(out->solution->m[0],2,1e-12);close_to(out->solution->m[1],-3,1e-12);
     close_to(out->solution->m[2],.5,1e-12);close_to(out->residual_norm,sqrt(.7),1e-12);
     matrix_qr_result_del(out);}
    {double aa[]={2,0,0,1},bb[]={6,4},ss[]={1,1};out=solve(aa,2,2,bb,ss,1e-12);
     close_to(out->scaled_condition_1,2,1e-14);matrix_qr_result_del(out);}
    out=NULL;
    am.nr=1;bm.nr=1;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&!out);
    am.nr=bm.nr=3;
    assert(matrix_leastsq_qr_checked(&am,&bm,s,0,&out)==-1&&!out);
    s[0]=0;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&!out);s[0]=1;
    a[0]=NAN;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&!out);a[0]=1;
    bm.nc=2;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&!out);bm.nc=1;
    a[0]=DBL_MAX;s[0]=2;assert(matrix_leastsq_qr_checked(&am,&bm,s,1e-12,&out)==-1&&!out);a[0]=1;s[0]=1;
    assert(!memcmp(ac,a,sizeof a)&&!memcmp(bc,b,sizeof b));
    /* Legacy XA=B known answer, exercising unchanged allocator/API. */
    {double aa[]={1,2,3},bb[]={2,4,6};matrix x={aa,1,3},y={bb,1,3};
     matrix *p=matrix_leastsq(&x,&y);assert(p);close_to(p->m[0],2,1e-14);matrix_del(p);}
    matrix_qr_result_del(NULL);
    puts("PASS: QR known answers, pivot reconstruction, scaling, rank, limits and legacy fit");return 0;
}
