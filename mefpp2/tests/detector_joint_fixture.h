/* Reused qualified synthetic generator and finite-difference covariance oracle. */

#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "detector_joint.h"
#define JP 7
#define JM 20
#define JB ((JP+1)*JP)
typedef struct {
    detector_joint_amplifier amp[2];detector_joint_site site[2];
    detector_joint_observation obs[JM];double h[JM*JM],truth[JP];
    double scales[JP],lo[JP],hi[JP],simplex[2*JB];
    matrix factor;detector_joint_problem p;detector_joint_options o;
} fixture;
/* Independent forward-data generator: Newton solve, not production bisection. */
static double forward(double t,double delta,double rate,double c2,double c3)
{
    double u=rate*(t+delta);int k;
    for(k=0;k<80;++k) {
        double q=u+c2*u*u+c3*u*u*u-rate*(t+delta);
        double step=q/(1+2*c2*u+3*c3*u*u);u-=step;
        if(fabs(step)<1e-10)break;
    }
    return u;
}
static void fill(fixture *f,double delta,int dense)
{
    int a,i,j,k;double times[]={2,70,40,5,10,30,20,50,60,7};
    memset(f,0,sizeof(*f));
    f->truth[0]=delta;f->truth[1]=800;f->truth[2]=500;
    f->truth[3]=2e-6;f->truth[4]=1e-11;f->truth[5]=.5e-6;f->truth[6]=3e-12;
    f->scales[0]=.2;f->lo[0]=-.8;f->hi[0]=.8;
    for(i=1;i<3;++i){f->scales[i]=1000;f->lo[i]=100;f->hi[i]=1500;}
    for(i=3;i<7;++i){f->scales[i]=(i%2)?1e-5:1e-10;
        f->lo[i]=(i%2)?-3e-6:-5e-12;f->hi[i]=(i%2)?8e-6:8e-11;}
    for(a=0;a<2;++a) {
        snprintf(f->amp[a].detector_id,64,"DET%d",a+1);snprintf(f->amp[a].amplifier_id,64,"AMP%d",a+1);
        f->amp[a].signal_min=0;f->amp[a].signal_max=100000;
        f->site[a].amplifier=a;f->site[a].x=100;f->site[a].y=200;
        for(i=0;i<10;++i) {
            k=10*a+i;f->obs[k].site=a;f->obs[k].input_index=i;
            f->obs[k].seconds=times[i];
            f->obs[k].signal=forward(times[i],delta,f->truth[1+a],f->truth[3+2*a],f->truth[4+2*a]);
        }
    }
    if(dense)for(i=0;i<JM;++i)for(j=0;j<=i;++j)f->h[i*JM+j]=(i==j)?.5:.03;
    else for(i=0;i<JM;++i)f->h[i]=.5;
    f->factor.m=f->h;f->factor.nr=JM;f->factor.nc=dense?JM:1;
    for(k=0;k<2;++k)for(i=0;i<=JP;++i)for(j=0;j<JP;++j)
        f->simplex[k*JB+i*JP+j]=f->truth[j]+f->scales[j]*(k?-.008:.01)+
            (i==j+1?f->scales[j]*.015:0);
    f->p.amplifiers=2;f->p.sites=2;f->p.observations=JM;f->p.starts=2;
    f->p.amplifier=f->amp;f->p.site=f->site;f->p.observation=f->obs;
    f->p.scales=f->scales;f->p.lower=f->lo;f->p.upper=f->hi;f->p.initial_simplexes=f->simplex;
    f->p.noise_factor=&f->factor;
    f->o.optimizer.max_evaluations=30000;f->o.optimizer.parameter_tolerance=1e-7;
    f->o.optimizer.objective_tolerance=1e-12;f->o.optimizer.initial_rank_tolerance=1e-12;
    f->o.inversion_iterations=80;f->o.inversion_tolerance=1e-8;
    f->o.rank_tolerance=1e-10;f->o.max_scaled_condition=1e8;
    f->o.start_parameter_tolerance=2e-5;f->o.start_cost_tolerance=1e-6;
    f->o.minimum_signal_span=1000;
}
/* Finite differences of independently generated data verify the implemented
 * analytic derivatives, whitening, scales and covariance permutation jointly.
 * Normal-equation products appear only in this independent test identity. */
static void covariance_identity(fixture *f,detector_joint_result *out)
{
    double jac[JM*JP],w[JM*JP],gram[JP*JP],eps,theta[JP];int i,j,k;
    const double *best=out->start[out->best_start]->parameters;
    for(j=0;j<JP;++j) {
        eps=f->scales[j]*1e-5;memcpy(theta,best,sizeof theta);
        for(i=0;i<JM;++i) {
            int a=f->obs[i].site;double plus,minus,q;
            theta[j]=best[j]+eps;plus=forward(f->obs[i].seconds,theta[0],theta[1+a],theta[3+2*a],theta[4+2*a]);
            theta[j]=best[j]-eps;minus=forward(f->obs[i].seconds,theta[0],theta[1+a],theta[3+2*a],theta[4+2*a]);
            jac[i*JP+j]=-(plus-minus)/(2*eps)*f->scales[j];
            q=jac[i*JP+j];
            if(f->factor.nc!=1)for(k=0;k<i;++k)q-=f->h[i*JM+k]*w[k*JP+j];
            w[i*JP+j]=q/.5;
        }
    }
    for(i=0;i<JP;++i)for(j=0;j<JP;++j) {
        double q=0;for(k=0;k<JM;++k)q+=w[k*JP+i]*w[k*JP+j];gram[i*JP+j]=q;
    }
    for(i=0;i<JP;++i)for(j=0;j<JP;++j) {
        double q=0;
        for(k=0;k<JP;++k)q+=gram[i*JP+k]*out->covariance->m[k*JP+j]/f->scales[k]/f->scales[j];
        assert(fabs(q-(i==j))<.002);
    }
}
