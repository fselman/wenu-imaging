
#include "detector_joint_fixture.h"
#define PG 5
#define PN (JP-1)
#define PB (JP*PN)
typedef struct {
    fixture f;
    detector_joint_profile_request request;
    double grid[PG],simplex[PG*2*PB];
} profile_fixture;
static void profile_fill(profile_fixture *pf,double delta,int dense)
{
    int point,start,row,j;memset(pf,0,sizeof(*pf));fill(&pf->f,delta,dense);
    for(point=0;point<PG;++point)pf->grid[point]=delta+(point-2)*.001;
    for(point=0;point<PG;++point)for(start=0;start<2;++start)
        for(row=0;row<JP;++row)for(j=0;j<PN;++j)
            pf->simplex[(point*2+start)*PB+row*PN+j]=pf->f.truth[1+j]+
                pf->f.scales[1+j]*(start?-.0002:.0001)+
                ((row==j+1)?pf->f.scales[1+j]*.0003:0);
    pf->request.points=PG;pf->request.starts=2;pf->request.delta=pf->grid;
    pf->request.initial_simplexes=pf->simplex;pf->request.optimizer=pf->f.o.optimizer;
    pf->request.delta_chi2=1;pf->request.cost_tolerance=1e-5;pf->request.boundary_tolerance=1e-6;
}
static detector_joint_profile_result *profile_run(profile_fixture *pf)
{
    detector_joint_profile_result *out=NULL;int i;
    assert(detector_joint_shutter_profile_checked(&pf->f.p,&pf->f.o,&pf->request,&out)==0&&out);
    if(out->status!=DETECTOR_JOINT_PROFILE_BRACKETED) {
        fprintf(stderr,"profile status %d base %d\n",out->status,out->base->status);
        for(i=0;i<out->points;++i) {
            int start,j;
            fprintf(stderr,"point %d delta %g status %d cost %g ref %g\n",i,out->delta[i],out->point_status[i],out->cost[i],out->reference_cost[i]);
            for(start=0;start<out->starts;++start)if(out->fit[i*out->starts+start]) {
                optimization_result *f=out->fit[i*out->starts+start];
                fprintf(stderr,"  start %d status %d cost %.12g parameters",start,f->status,f->cost);
                for(j=0;j<PN;++j)fprintf(stderr," %.12g",f->parameters[j]);
                fprintf(stderr,"\n");
            }
        }
    }
    return out;
}
int main(void)
{
    profile_fixture pf,saved;detector_joint_profile_result *out=NULL,*occupied;
    int i,j,k,improved;double offsets[]={-.15,0,.2};
    for(k=0;k<3;++k) {
        profile_fill(&pf,offsets[k],k==2);saved=pf;out=profile_run(&pf);
        assert(out->status==DETECTOR_JOINT_PROFILE_BRACKETED);
        assert(!memcmp(&pf,&saved,sizeof pf));
        assert(fabs(out->minimum_delta-offsets[k])<1e-5&&out->cost[2]<1e-6);
        assert(out->left_outside>=0&&out->right_outside>=0&&!out->flat_on_grid);
        assert(out->delta[out->left_outside]<out->minimum_delta);
        assert(out->delta[out->right_outside]>out->minimum_delta);
        assert(out->delta_cost[out->left_outside]>=1&&out->delta_cost[out->right_outside]>=1);
        assert(out->base->status==DETECTOR_JOINT_CANDIDATE);covariance_identity(&pf.f,out->base);
        improved=0;
        for(i=0;i<PG;++i) {
            assert(out->point_status[i]==DETECTOR_JOINT_PROFILE_POINT_OK);
            if(out->reference_cost[i]-out->cost[i]>1)improved=1;
            for(j=0;j<2;++j)assert(out->fit[i*2+j]->dimensions==PN);
        }
        assert(improved&&out->preflight_calls>0&&out->evaluations>0);
        assert(out->delta!=pf.grid&&out->initial_simplexes!=pf.simplex);
        occupied=out;assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==-1&&out==occupied);
        detector_joint_profile_result_del(out);out=NULL;
    }
    profile_fill(&pf,.2,0);for(i=0;i<JM;++i)pf.f.h[i]*=1e8;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_FLAT_ON_GRID&&out->flat_on_grid);
    assert(out->left_outside==-1&&out->right_outside==-1);detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);for(i=0;i<JM;++i)pf.f.h[i]*=1e8;
    pf.f.lo[0]=.198;pf.f.hi[0]=.202;
    for(i=0;i<2*(JP+1);++i)for(j=0;j<JP;++j)
        pf.f.simplex[i*JP+j]=pf.f.truth[j]+pf.f.scales[j]*
            ((i/(JP+1))?-.0002:.0001)+((i%(JP+1)==j+1)?pf.f.scales[j]*.0003:0);
    pf.grid[0]=pf.f.lo[0];pf.grid[PG-1]=pf.f.hi[0];
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_BOUNDARY_LIMITED&&out->flat_on_grid);
    detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);pf.request.delta_chi2=1e20;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_GRID_UNBRACKETED&&!out->flat_on_grid);
    detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);pf.request.optimizer.max_evaluations=JP;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_INCOMPLETE);
    for(i=0;i<PG;++i)assert(isnan(out->cost[i]));
    detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);pf.f.o.minimum_signal_span=100000;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_BASE_UNAVAILABLE&&isnan(out->minimum_delta));
    for(i=0;i<PG;++i)assert(out->point_status[i]==DETECTOR_JOINT_PROFILE_NOT_RUN&&isnan(out->cost[i]));
    detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);pf.f.lo[3]=-.001;pf.f.hi[4]=1;
    for(i=0;i<JP;++i) {
        pf.simplex[i*PN+2]=-.0001+((i==3)?1e-8:0);
        pf.simplex[i*PN+3]=2e-9+((i==4)?1e-12:0);
    }
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_INCOMPLETE&&
        out->point_status[0]==DETECTOR_JOINT_PROFILE_POINT_INADMISSIBLE&&isnan(out->cost[0]));
    detector_joint_profile_result_del(out);out=NULL;
    profile_fill(&pf,.2,0);pf.grid[1]=pf.grid[0];
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==-1&&!out);
    profile_fill(&pf,.2,0);pf.request.delta_chi2=0;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==-1&&!out);
    /* Loose free-fit tolerance gives a deliberately inferior free minimum;
     * accurate fixed-delta refits must expose it, never certify an interval. */
    profile_fill(&pf,.2,0);pf.f.p.starts=1;pf.f.o.optimizer.parameter_tolerance=1;
    pf.f.o.optimizer.objective_tolerance=3;pf.request.starts=1;
    assert(detector_joint_shutter_profile_checked(&pf.f.p,&pf.f.o,&pf.request,&out)==0);
    assert(out->status==DETECTOR_JOINT_PROFILE_INCONSISTENT_MINIMUM);
    detector_joint_profile_result_del(out);out=NULL;
    detector_joint_profile_result_del(NULL);
    puts("PASS: refitted signed shutter profiles, conditional improvement, covariance, flat/grid/boundary/limit states and owners");
    return 0;
}
