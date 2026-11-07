#include "linearity_fit_fixture.h"
static void candidate_check(const linearity_fixture *v,const detector_linearity_fit_result *r)
{
    assert(r->status==DETECTOR_LINEARITY_CURVE_CANDIDATE&&r->curves==2&&r->curve);
    assert(r->noise->factor_to_observation[0]!=0); /* Deliberately nonidentity QR order. */
    const detector_joint_result *base=r->profile->base;
    assert(fabs(r->common_delta_seconds-v->f.truth[0])<1e-5);
    assert(!memcmp(base->noise_factor->m,r->noise->noise_factor->m,JM*JM*sizeof(double)));
    for(int i=0;i<JM;++i){
        int original=r->noise->factor_to_observation[i];
        assert(!memcmp(base->observation+i,v->f.obs+original,sizeof *v->f.obs));
    }
    for(int a=0;a<2;++a){
        const detector_linearity_curve *c=r->curve+a;
        assert(!strcmp(c->detector_id,v->f.amp[a].detector_id)&&!strcmp(c->amplifier_id,v->f.amp[a].amplifier_id));
        assert(fabs(c->c2-v->f.truth[3+2*a])<v->f.scales[3+2*a]*2e-5);
        assert(fabs(c->c3-v->f.truth[4+2*a])<v->f.scales[4+2*a]*2e-5);
        assert(c->observed_signal_min>c->declared_signal_min&&c->observed_signal_max<c->declared_signal_max);
        int indices[3]={0,3+2*a,4+2*a};
        for(int i=0;i<3;++i)for(int j=0;j<3;++j)
            assert(c->covariance[i*3+j]==base->covariance->m[indices[i]*JP+indices[j]]);
        for(int i=0;i<10;++i){
            double signal=v->f.obs[a*10+i].signal;
            double linear=signal+c->c2*signal*signal+c->c3*signal*signal*signal;
            double expected=v->f.truth[1+a]*(v->f.obs[a*10+i].seconds+r->common_delta_seconds);
            assert(fabs(linear-expected)<.002);
        }
    }
}
int main(void)
{
    (void)covariance_identity;
    linearity_fixture f,saved;detector_linearity_fit_result *r=NULL,*occupied;
    double offsets[]={-.15,0,.2};
    for(int i=0;i<3;++i){
        linearity_fill(&f,offsets[i]);saved=f;
        assert(detector_linearity_fit_checked(&f.problem,&r)==0&&r);
        assert(!memcmp(&f,&saved,sizeof f));candidate_check(&f,r);
        occupied=r;assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&r==occupied);
        memset(&f,0,sizeof f);assert(!strcmp(r->curve[0].detector_id,"DET1"));
        assert(!strcmp(r->noise_model_id,"synthetic:explicit-independent-shared-master-and-scans"));
        detector_linearity_fit_result_del(r);r=NULL;
    }
    linearity_fill(&f,.2);memset(f.independent,0,sizeof f.independent);memset(f.master,0,sizeof f.master);memset(f.scan,0,sizeof f.scan);
    assert(detector_linearity_fit_checked(&f.problem,&r)==0&&r->status==DETECTOR_LINEARITY_NOISE_UNAVAILABLE);
    assert(!r->profile&&!r->curve&&!r->curves&&isnan(r->common_delta_seconds));detector_linearity_fit_result_del(r);r=NULL;
    linearity_fill(&f,.2);f.problem.noise.max_factor_condition=1;
    assert(detector_linearity_fit_checked(&f.problem,&r)==0&&r->status==DETECTOR_LINEARITY_NOISE_UNAVAILABLE);
    assert(!r->curve);detector_linearity_fit_result_del(r);r=NULL;
    linearity_fill(&f,.2);f.problem.fit.minimum_signal_span=100000;
    assert(detector_linearity_fit_checked(&f.problem,&r)==0&&r->status==DETECTOR_LINEARITY_FIT_UNAVAILABLE);
    assert(!r->curve&&!r->curves&&isnan(r->common_delta_seconds));detector_linearity_fit_result_del(r);r=NULL;
    linearity_fill(&f,.2);f.profile.delta_chi2=1e20;
    assert(detector_linearity_fit_checked(&f.problem,&r)==0&&r->status==DETECTOR_LINEARITY_PROFILE_UNAVAILABLE);
    assert(!r->curve&&!r->curves&&isnan(r->common_delta_seconds));detector_linearity_fit_result_del(r);r=NULL;
    linearity_fill(&f,.2);f.problem.noise.master_factor=NULL;
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    linearity_fill(&f,.2);f.problem.noise.independent_components=0;
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    linearity_fill(&f,.2);f.problem.noise_model_id=NULL;
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    linearity_fill(&f,.2);char long_id[128];memset(long_id,'x',sizeof long_id);f.problem.sample_set_id=long_id;
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    linearity_fill(&f,.2);f.problem.profile=NULL;
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    linearity_fill(&f,.2);f.delta[1]=f.delta[0];
    assert(detector_linearity_fit_checked(&f.problem,&r)==-1&&!r);
    detector_linearity_fit_result_del(NULL);
    puts("PASS: supplied correlated covariance -> QR-ordered direct pixels -> shared shutter profile -> owned amplifier correction candidates; explicit unavailable/atomic failure states");return 0;
}
