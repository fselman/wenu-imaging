#include "detector_linearity_fit.h"
#include <stdint.h>
#include <string.h>
static int provenance_id(const char *s)
{
    if(!s||!s[0])return 0;
    for(int i=0;i<128;++i)if(!s[i])return 1;
    return 0;
}
void detector_linearity_fit_result_del(detector_linearity_fit_result *r)
{
    if(!r)return;
    detector_joint_profile_result_del(r->profile);
    detector_noise_result_del(r->noise);
    if(r->curve)free(r->curve);
    free(r);
}
int detector_linearity_fit_checked(const detector_linearity_fit_problem *p,detector_linearity_fit_result **out)
{
    detector_linearity_fit_result *r=NULL;
    detector_measurements view;
    detector_joint_problem joint;
    if(!p||!out||*out||!p->profile||p->starts<1||!p->scales||!p->lower||!p->upper||!p->initial_simplexes||
       !provenance_id(p->sample_set_id)||!provenance_id(p->noise_model_id)||!provenance_id(p->correction_pipeline_id))return -1;
    r=calloc(1,sizeof *r);if(!r)return -1;
    r->common_delta_seconds=NAN;
    strcpy(r->sample_set_id,p->sample_set_id);strcpy(r->noise_model_id,p->noise_model_id);
    strcpy(r->correction_pipeline_id,p->correction_pipeline_id);
    if(detector_noise_assemble_checked(&p->noise,&r->noise))goto fail;
    r->status=DETECTOR_LINEARITY_NOISE_UNAVAILABLE;
    if(r->noise->status!=DETECTOR_NOISE_READY)goto publish;
    memset(&view,0,sizeof view);
    if(detector_noise_measurements(r->noise,&view))goto fail;
    memset(&joint,0,sizeof joint);
    joint.amplifiers=view.amplifiers;joint.sites=view.sites;joint.observations=view.observations;
    joint.amplifier=view.amplifier;joint.site=view.site;joint.observation=view.observation;
    joint.noise_factor=view.noise_factor;joint.starts=p->starts;
    joint.scales=p->scales;joint.lower=p->lower;joint.upper=p->upper;joint.initial_simplexes=p->initial_simplexes;
    if(detector_joint_shutter_profile_checked(&joint,&p->fit,p->profile,&r->profile))goto fail;
    r->status=DETECTOR_LINEARITY_FIT_UNAVAILABLE;
    if(r->profile->base->status!=DETECTOR_JOINT_CANDIDATE)goto publish;
    r->status=DETECTOR_LINEARITY_PROFILE_UNAVAILABLE;
    if(r->profile->status!=DETECTOR_JOINT_PROFILE_BRACKETED)goto publish;
    detector_joint_result *base=r->profile->base;
    const double *best=base->start[base->best_start]->parameters;
    if(!base->covariance||(size_t)view.amplifiers>SIZE_MAX/sizeof *r->curve)goto fail;
    r->curve=calloc((size_t)view.amplifiers,sizeof *r->curve);if(!r->curve)goto fail;
    for(int a=0;a<view.amplifiers;++a){
        detector_linearity_curve *curve=r->curve+a;
        strcpy(curve->detector_id,view.amplifier[a].detector_id);
        strcpy(curve->amplifier_id,view.amplifier[a].amplifier_id);
        int c2=1+view.sites+2*a,c3=c2+1,indices[3]={0,c2,c3};
        curve->c2=best[c2];curve->c3=best[c3];
        curve->declared_signal_min=view.amplifier[a].signal_min;curve->declared_signal_max=view.amplifier[a].signal_max;
        curve->observed_signal_min=INFINITY;curve->observed_signal_max=-INFINITY;
        for(int i=0;i<view.observations;++i)if(view.site[view.observation[i].site].amplifier==a){
            curve->observed_signal_min=fmin(curve->observed_signal_min,view.observation[i].signal);
            curve->observed_signal_max=fmax(curve->observed_signal_max,view.observation[i].signal);
        }
        if(!isfinite(curve->observed_signal_min)||!isfinite(curve->observed_signal_max))goto fail;
        for(int i=0;i<3;++i)for(int j=0;j<3;++j)
            curve->covariance[i*3+j]=base->covariance->m[indices[i]*base->parameters+indices[j]];
    }
    r->curves=view.amplifiers;r->common_delta_seconds=best[0];r->status=DETECTOR_LINEARITY_CURVE_CANDIDATE;
publish:
    *out=r;return 0;
fail:
    detector_linearity_fit_result_del(r);return -1;
}
