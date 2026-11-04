#include "detector_joint_fixture.h"
#include "detector_linearity_fit.h"
#define LF_POINTS 5
#define LF_NUISANCE (JP-1)
#define LF_BLOCK (JP*LF_NUISANCE)
typedef struct {
    fixture f;
    detector_linearity_fit_problem problem;
    detector_joint_profile_request profile;
    double delta[LF_POINTS],simplex[LF_POINTS*2*LF_BLOCK];
    double independent[JM],master[4],scan[JM*JM];
    detector_noise_scan_group groups[JM];
    matrix mf,sf;
} linearity_fixture;
static void linearity_fill(linearity_fixture *v,double offset)
{
    memset(v,0,sizeof *v);fill(&v->f,offset,0);
    for(int point=0;point<LF_POINTS;++point)v->delta[point]=offset+(point-2)*.003;
    for(int point=0;point<LF_POINTS;++point)for(int start=0;start<2;++start)
        for(int row=0;row<JP;++row)for(int j=0;j<LF_NUISANCE;++j)
            v->simplex[(point*2+start)*LF_BLOCK+row*LF_NUISANCE+j]=v->f.truth[j+1]+
                v->f.scales[j+1]*(start?-.0002:.0001)+(row==j+1?v->f.scales[j+1]*.0003:0);
    v->profile.points=LF_POINTS;v->profile.starts=2;v->profile.delta=v->delta;
    v->profile.initial_simplexes=v->simplex;v->profile.optimizer=v->f.o.optimizer;
    v->profile.delta_chi2=1;v->profile.cost_tolerance=1e-5;v->profile.boundary_tolerance=1e-6;
    for(int i=0;i<JM;++i){
        int a=v->f.site[v->f.obs[i].site].amplifier;
        v->independent[i]=.25+.002*i;
        v->groups[i].input_index=v->f.obs[i].input_index;v->groups[i].amplifier=a;v->groups[i].y=200;
        v->scan[i*JM+i]=.015;
        if(i)v->scan[i*JM+i-1]=.005;
    }
    v->master[0]=.05;v->master[2]=.02;v->master[3]=.08;
    v->mf.m=v->master;v->mf.nr=v->mf.nc=2;v->sf.m=v->scan;v->sf.nr=v->sf.nc=JM;
    detector_noise_problem *noise=&v->problem.noise;
    noise->data.amplifiers=2;noise->data.sites=2;noise->data.observations=JM;
    noise->data.amplifier=v->f.amp;noise->data.site=v->f.site;noise->data.observation=v->f.obs;
    noise->independent_variance=v->independent;noise->master_factor=&v->mf;
    noise->scan_applied=1;noise->scan_groups=JM;noise->scan_group=v->groups;noise->scan_factor=&v->sf;
    noise->independent_components=1;noise->rank_tolerance=1e-12;noise->max_factor_condition=1e8;noise->max_dense_elements=10000;
    v->problem.starts=2;v->problem.scales=v->f.scales;v->problem.lower=v->f.lo;v->problem.upper=v->f.hi;
    v->problem.initial_simplexes=v->f.simplex;v->problem.fit=v->f.o;v->problem.profile=&v->profile;
    v->problem.sample_set_id="synthetic:corrected-direct-pixels";
    v->problem.noise_model_id="synthetic:explicit-independent-shared-master-and-scans";
    v->problem.correction_pipeline_id="synthetic:fixed-population-no-free-bias";
}
