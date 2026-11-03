
/* Direct-pixel joint response candidate, reviewed PR #227; ownership #75.
 * Reuse checked Eclipse optimizer/QR, never the historical time-polynomial fit.
 */
#include <stdint.h>
#include <limits.h>
#include <string.h>
#include "detector_joint.h"

typedef struct {
    const detector_joint_problem *p;
    const detector_joint_options *o;
    double *residual, *white;
} joint_context;

void detector_joint_result_del(detector_joint_result *r)
{
    int k;
    if(!r) return;
    if(r->start) { for(k=0;k<r->starts;++k) optimization_result_del(r->start[k]);free(r->start); }
    matrix_qr_result_del(r->local);
    if(r->covariance) { if(r->covariance->m) free(r->covariance->m);free(r->covariance); }
    if(r->noise_factor) { if(r->noise_factor->m)free(r->noise_factor->m);free(r->noise_factor); }
    if(r->scales)free(r->scales);
    if(r->lower)free(r->lower);
    if(r->upper)free(r->upper);
    if(r->residuals) free(r->residuals);
    if(r->amplifier) free(r->amplifier);
    if(r->site) free(r->site);
    if(r->observation) free(r->observation);
    free(r);
}

/* Apply H^-1 without forming an inverse or discarding off-diagonal entries. */
static int joint_whiten(const matrix *h,const double *src,size_t stride,double *dst)
{
    size_t i,j,m=(size_t)h->nr;
    for(i=0;i<m;++i) {
        double q=src[i*stride];
        if(h->nc!=1) for(j=0;j<i;++j) q-=h->m[i*m+j]*dst[j];
        dst[i]=q/h->m[h->nc==1?i:i*m+i];
        if(!isfinite(dst[i])) return -1;
    }
    return 0;
}
static double joint_q(double u,double c2,double c3) { return u*(1+u*(c2+u*c3)); }
static double joint_d(double u,double c2,double c3) { return 1+u*(2*c2+3*u*c3); }

/* Return 1 for inadmissible physics, -1 for failed inversion, 0 for prediction. */
static int joint_predict(const joint_context *c,const double *theta,int index,double *u)
{
    const detector_joint_problem *p=c->p;
    const detector_joint_observation *ob=p->observation+index;
    int a=p->site[ob->site].amplifier,k,off=1+p->sites+2*a;
    double lo=p->amplifier[a].signal_min,hi=p->amplifier[a].signal_max;
    double c2=theta[off],c3=theta[off+1],rate=theta[1+ob->site];
    double duration=ob->seconds+theta[0],target,left,right,d,mid,q;
    if(!isfinite(duration)||duration<=0||!isfinite(rate)||rate<=0) return 1;
    d=joint_d(lo,c2,c3);if(!isfinite(d)||d<=0) return 1;
    d=joint_d(hi,c2,c3);if(!isfinite(d)||d<=0) return 1;
    if(c3!=0) { double vertex=-(c2/c3)/3;
        if(vertex>lo&&vertex<hi) {d=joint_d(vertex,c2,c3);if(!isfinite(d)||d<=0)return 1;}
    }
    target=rate*duration;left=joint_q(lo,c2,c3);right=joint_q(hi,c2,c3);
    if(!isfinite(target)||!isfinite(left)||!isfinite(right)||target<left||target>right) return 1;
    if(target==left) {*u=lo;return 0;}
    if(target==right) {*u=hi;return 0;}
    for(k=0;k<c->o->inversion_iterations;++k) {
        mid=.5*lo+.5*hi;
        if(hi-lo<=c->o->inversion_tolerance) {*u=mid;return 0;}
        if(mid==lo||mid==hi) return -1;
        q=joint_q(mid,c2,c3);if(!isfinite(q))return -1;
        if(q==target) {*u=mid;return 0;}
        if(q<target)lo=mid;else hi=mid;
    }
    return -1;
}
static optimization_evaluation joint_cost(const double *theta,int dim,void *data,double *value)
{
    joint_context *c=data;int i,rc;double u,cost=0;
    (void)dim;
    for(i=0;i<c->p->observations;++i) {
        rc=joint_predict(c,theta,i,&u);
        if(rc) return rc>0?OPTIMIZATION_EVAL_INADMISSIBLE:OPTIMIZATION_EVAL_ERROR;
        c->residual[i]=c->p->observation[i].signal-u;
    }
    if(joint_whiten(c->p->noise_factor,c->residual,1,c->white))return OPTIMIZATION_EVAL_ERROR;
    for(i=0;i<c->p->observations;++i) cost+=c->white[i]*c->white[i];
    if(!isfinite(cost))return OPTIMIZATION_EVAL_ERROR;
    *value=cost;return OPTIMIZATION_EVAL_VALID;
}
static int joint_valid(const detector_joint_problem *p,const detector_joint_options *o,
    detector_joint_result **out)
{
    size_t m,n,a,j;int i;
    if(!p||!o||!out||*out||p->amplifiers<1||p->sites<1||p->observations<1||p->starts<1||
       !p->amplifier||!p->site||!p->observation||!p->scales||!p->lower||!p->upper||
       !p->initial_simplexes||!p->noise_factor||!p->noise_factor->m) return 0;
    m=(size_t)p->observations;
    n=1+(size_t)p->sites+2*(size_t)p->amplifiers;
    if(n>=INT_MAX||m>SIZE_MAX/n||m*n>SIZE_MAX/sizeof(double)||
       n>SIZE_MAX/n||n*n>SIZE_MAX/sizeof(double)||(n+1)>SIZE_MAX/n||
       (n+1)*n>SIZE_MAX/(size_t)p->starts||
       (n+1)*n*(size_t)p->starts>SIZE_MAX/sizeof(double))return 0;
    if(p->noise_factor->nr!=p->observations ||
       (p->noise_factor->nc!=1&&p->noise_factor->nc!=p->observations))return 0;
    if(p->noise_factor->nc!=1 && (m>SIZE_MAX/m||m*m>SIZE_MAX/sizeof(double)))return 0;
    if(o->inversion_iterations<1||!isfinite(o->inversion_tolerance)||o->inversion_tolerance<=0||
       !isfinite(o->rank_tolerance)||o->rank_tolerance<=0||o->rank_tolerance>=1||
       !isfinite(o->max_scaled_condition)||o->max_scaled_condition<1||
       !isfinite(o->start_parameter_tolerance)||o->start_parameter_tolerance<=0||
       !isfinite(o->start_cost_tolerance)||o->start_cost_tolerance<=0||
       !isfinite(o->minimum_signal_span)||o->minimum_signal_span<0)return 0;
    if(!isfinite(o->optimizer.parameter_tolerance)||o->optimizer.parameter_tolerance<=0||
       !isfinite(o->optimizer.objective_tolerance)||o->optimizer.objective_tolerance<=0||
       !isfinite(o->optimizer.initial_rank_tolerance)||o->optimizer.initial_rank_tolerance<=0||
       o->optimizer.initial_rank_tolerance>=1||o->optimizer.max_evaluations<n+1)return 0;
    for(j=0;j<n;++j)if(!isfinite(p->scales[j])||p->scales[j]<=0||
        !isfinite(p->lower[j])||!isfinite(p->upper[j])||p->lower[j]>=p->upper[j])return 0;
    for(j=0;j<(n+1)*n*(size_t)p->starts;++j)if(!isfinite(p->initial_simplexes[j])||
        p->initial_simplexes[j]<p->lower[j%n]||p->initial_simplexes[j]>p->upper[j%n])return 0;
    for(a=0;a<(size_t)p->amplifiers;++a) {
        const detector_joint_amplifier *amp=p->amplifier+a;
        if(!memchr(amp->detector_id,0,64)||!memchr(amp->amplifier_id,0,64)||
           !amp->detector_id[0]||!amp->amplifier_id[0]||
           !isfinite(amp->signal_min)||!isfinite(amp->signal_max)||
           amp->signal_min<0||amp->signal_min>=amp->signal_max)return 0;
        for(j=0;j<a;++j) if(!strcmp(amp->detector_id,p->amplifier[j].detector_id)&&
            !strcmp(amp->amplifier_id,p->amplifier[j].amplifier_id))return 0;
    }
    for(i=0;i<p->sites;++i) {
        const detector_joint_site *s=p->site+i;
        if(s->amplifier<0||s->amplifier>=p->amplifiers||s->x<1||s->y<1)return 0;
        for(j=0;j<(size_t)i;++j)if(s->amplifier==p->site[j].amplifier&&
            s->x==p->site[j].x&&s->y==p->site[j].y)return 0;
    }
    for(i=0;i<p->observations;++i) {
        const detector_joint_observation *ob=p->observation+i;
        if(ob->site<0||ob->site>=p->sites||ob->input_index<0||!isfinite(ob->seconds)||
           ob->seconds<=0||!isfinite(ob->signal))return 0;
        a=(size_t)p->site[ob->site].amplifier;
        if(ob->signal<p->amplifier[a].signal_min||ob->signal>p->amplifier[a].signal_max)return 0;
        for(j=0;j<(size_t)i;++j)if(ob->input_index==p->observation[j].input_index) {
            if(ob->site==p->observation[j].site||ob->seconds!=p->observation[j].seconds)return 0;
        }
    }
    for(a=0;a<m;++a) {
        if(p->noise_factor->nc==1) {
            if(!isfinite(p->noise_factor->m[a])||p->noise_factor->m[a]<=0)return 0;
        }else for(j=0;j<m;++j) {
            double v=p->noise_factor->m[a*m+j];
            if(!isfinite(v)||(a==j&&v<=0)||(j>a&&v!=0))return 0;
        }
    }
    /* Full parameter/initial-simplex feasibility is delegated to minimize_checked. */
    return 1;
}

int detector_joint_response_fit_checked(const detector_joint_problem *p,
    const detector_joint_options *o,detector_joint_result **out)
{
    detector_joint_result *r=NULL;joint_context c;optimization_problem op;
    double *jac=NULL,*white_jac=NULL,*inverse=NULL;
    matrix design,rhs;size_t m,n,i,j,k,block;int start,best=0,rc;
    double cost,u,d,rate,q,cond;
    if(!joint_valid(p,o,out))return -1;
    m=(size_t)p->observations;n=1+(size_t)p->sites+2*(size_t)p->amplifiers;block=(n+1)*n;
    memset(&c,0,sizeof(c));c.p=p;c.o=o;
    r=calloc(1,sizeof(*r));if(!r)goto fail;
    r->parameters=(int)n;r->amplifiers=p->amplifiers;r->sites=p->sites;
    r->observations=p->observations;r->starts=p->starts;r->best_start=-1;
    r->options=*o;
    r->noise_factor=calloc(1,sizeof(matrix));
    r->scales=malloc(n*sizeof(double));r->lower=malloc(n*sizeof(double));r->upper=malloc(n*sizeof(double));
    if(!r->noise_factor||!r->scales||!r->lower||!r->upper)goto fail;
    *r->noise_factor=*p->noise_factor;
    r->noise_factor->m=malloc(m*(size_t)p->noise_factor->nc*sizeof(double));
    if(!r->noise_factor->m)goto fail;
    memcpy(r->noise_factor->m,p->noise_factor->m,m*(size_t)p->noise_factor->nc*sizeof(double));
    memcpy(r->scales,p->scales,n*sizeof(double));memcpy(r->lower,p->lower,n*sizeof(double));
    memcpy(r->upper,p->upper,n*sizeof(double));
    r->amplifier=malloc((size_t)p->amplifiers*sizeof(*r->amplifier));
    r->site=malloc((size_t)p->sites*sizeof(*r->site));
    r->observation=malloc(m*sizeof(*r->observation));
    r->start=calloc((size_t)p->starts,sizeof(*r->start));
    c.residual=malloc(m*sizeof(double));c.white=malloc(m*sizeof(double));
    if(!r->amplifier||!r->site||!r->observation||!r->start||!c.residual||!c.white)goto fail;
    memcpy(r->amplifier,p->amplifier,(size_t)p->amplifiers*sizeof(*r->amplifier));
    memcpy(r->site,p->site,(size_t)p->sites*sizeof(*r->site));
    memcpy(r->observation,p->observation,m*sizeof(*r->observation));
    r->status=DETECTOR_JOINT_COVERAGE_UNAVAILABLE;
    if(m<=n)goto done;
    for(i=0;i<(size_t)p->amplifiers;++i) {
        int found=0;double low=0,high=0;
        for(j=0;j<m;++j) if((size_t)p->site[p->observation[j].site].amplifier==i) {
            q=p->observation[j].signal;
            if(!found)low=high=q;
            if(q<low)low=q;
            if(q>high)high=q;
            found=1;
        }
        if(!found||high-low<o->minimum_signal_span)goto done;
    }
    memset(&op,0,sizeof(op));op.dimensions=(int)n;op.scales=p->scales;
    op.lower=p->lower;op.upper=p->upper;op.cost=joint_cost;op.context=&c;
    for(start=0;start<p->starts;++start) {
        op.initial_simplex=p->initial_simplexes+(size_t)start*block;
        if(minimize_checked(&op,&o->optimizer,r->start+start))goto fail;
        if(r->start[start]->cost<r->start[best]->cost)best=start;
    }
    r->best_start=best;
    r->residuals=malloc(m*sizeof(double));if(!r->residuals)goto fail;
    if(joint_cost(r->start[best]->parameters,(int)n,&c,&cost)!=OPTIMIZATION_EVAL_VALID)goto fail;
    memcpy(r->residuals,c.residual,m*sizeof(double));
    r->status=DETECTOR_JOINT_UNCONVERGED;
    for(start=0;start<p->starts;++start) if(r->start[start]->status!=OPTIMIZATION_CONVERGED)goto done;
    r->status=DETECTOR_JOINT_STARTS_INCONSISTENT;
    for(start=0;start<p->starts;++start) {
        double scale=fmax(1,fmax(fabs(r->start[start]->cost),fabs(cost)));
        if(fabs(r->start[start]->cost/scale-cost/scale)>o->start_cost_tolerance)goto done;
        for(j=0;j<n;++j)if(fabs(r->start[start]->parameters[j]/p->scales[j]-
            r->start[best]->parameters[j]/p->scales[j])>o->start_parameter_tolerance)goto done;
    }
    jac=calloc(m*n,sizeof(double));white_jac=malloc(m*n*sizeof(double));
    if(!jac||!white_jac)goto fail;
    for(i=0;i<m;++i) {
        const detector_joint_observation *ob=p->observation+i;
        int a=p->site[ob->site].amplifier,off=1+p->sites+2*a;
        const double *theta=r->start[best]->parameters;
        rc=joint_predict(&c,theta,(int)i,&u);if(rc)goto fail;
        d=joint_d(u,theta[off],theta[off+1]);rate=theta[1+ob->site];
        jac[i*n]=-rate/d;jac[i*n+1+ob->site]=-(ob->seconds+theta[0])/d;
        jac[i*n+off]=u*u/d;jac[i*n+off+1]=u*u*u/d;
        for(j=0;j<n;++j)if(!isfinite(jac[i*n+j]))goto fail;
    }
    for(j=0;j<n;++j) {
        if(joint_whiten(p->noise_factor,jac+j,n,c.white))goto fail;
        for(i=0;i<m;++i)white_jac[i*n+j]=c.white[i];
    }
    /* Diagnostic linear step uses -residual; it is not applied to the fit. */
    if(joint_whiten(p->noise_factor,r->residuals,1,c.white))goto fail;
    for(i=0;i<m;++i)c.white[i]=-c.white[i];
    design.m=white_jac;design.nr=(int)m;design.nc=(int)n;
    rhs.m=c.white;rhs.nr=(int)m;rhs.nc=1;
    if(matrix_leastsq_qr_checked(&design,&rhs,p->scales,o->rank_tolerance,&r->local))goto fail;
    r->status=DETECTOR_JOINT_RANK_UNAVAILABLE;
    if(r->local->rank!=(int)n)goto done;
    r->status=DETECTOR_JOINT_CONDITION_UNAVAILABLE;
    cond=r->local->scaled_condition_1;
    if(!r->local->condition_available||cond>o->max_scaled_condition)goto done;
    inverse=calloc(n*n,sizeof(double));r->covariance=calloc(1,sizeof(matrix));
    if(!inverse||!r->covariance)goto fail;
    r->covariance->nr=r->covariance->nc=(int)n;r->covariance->m=calloc(n*n,sizeof(double));
    if(!r->covariance->m)goto fail;
    for(j=0;j<n;++j)for(i=n;i-- >0;) {
        q=(i==j)?1:0;
        for(k=i+1;k<n;++k)q-=r->local->r->m[i*n+k]*inverse[k*n+j];
        inverse[i*n+j]=q/r->local->r->m[i*n+i];
        if(!isfinite(inverse[i*n+j]))goto fail;
    }
    for(i=0;i<n;++i)for(j=0;j<n;++j) {
        size_t pi=(size_t)r->local->pivots[i],pj=(size_t)r->local->pivots[j];
        q=0;for(k=0;k<n;++k)q+=inverse[i*n+k]*inverse[j*n+k];
        q*=p->scales[pi];q*=p->scales[pj];if(!isfinite(q))goto fail;
        r->covariance->m[pi*n+pj]=q;
    }
    r->status=DETECTOR_JOINT_CANDIDATE;
done:
    if(c.residual)free(c.residual);
    if(c.white)free(c.white);
    if(jac)free(jac);
    if(white_jac)free(white_jac);
    if(inverse)free(inverse);
    *out=r;return 0;
fail:
    if(c.residual)free(c.residual);
    if(c.white)free(c.white);
    if(jac)free(jac);
    if(white_jac)free(white_jac);
    if(inverse)free(inverse);
    detector_joint_result_del(r);return -1;
}
