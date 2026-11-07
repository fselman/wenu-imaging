#include <assert.h>
#include <math.h>
#include <float.h>
#include <stdio.h>
#include <string.h>
#include "detector_noise.h"
#include "detector_roi.h"
typedef struct {
    detector_joint_amplifier amp;
    detector_joint_site site[2];detector_joint_observation obs[4];
    detector_noise_scan_group group[2];
    double independent[4],master[4],scan[4];matrix mf,sf;
    detector_noise_problem p;
} noise_fixture;
static void close_to(double a,double b){assert(fabs(a-b)<1e-10*fmax(1,fabs(b)));}
static void noise_fill(noise_fixture *f)
{
    memset(f,0,sizeof *f);strcpy(f->amp.detector_id,"D8");strcpy(f->amp.amplifier_id,"OUT1");f->amp.signal_max=10000;
    for(int i=0;i<2;++i){f->site[i].x=i+1;f->site[i].y=1;f->group[i].input_index=i?3:8;f->group[i].y=1;}
    for(int i=0;i<4;++i){f->obs[i].site=i%2;f->obs[i].input_index=i<2?8:3;
        f->obs[i].seconds=i<2?2:5;f->obs[i].signal=10+i;f->independent[i]=4;}
    f->master[0]=1;f->master[3]=2;f->scan[0]=3;f->scan[3]=4;
    f->mf.m=f->master;f->mf.nr=f->mf.nc=2;f->sf.m=f->scan;f->sf.nr=f->sf.nc=2;
    f->p.data.amplifiers=1;f->p.data.sites=2;f->p.data.observations=4;
    f->p.data.amplifier=&f->amp;f->p.data.site=f->site;f->p.data.observation=f->obs;
    f->p.independent_variance=f->independent;f->p.master_factor=&f->mf;f->p.scan_applied=1;
    f->p.scan_groups=2;f->p.scan_group=f->group;f->p.scan_factor=&f->sf;f->p.independent_components=1;
    f->p.rank_tolerance=1e-12;f->p.max_factor_condition=1e8;f->p.max_dense_elements=10000;
}
static void check_factor(const detector_noise_result *r)
{
    int n=r->observations;
    for(int i=0;i<n;++i){assert(r->noise_factor->m[i*n+i]>0);
        assert(!memcmp(r->ordered_observation+i,r->observation+r->factor_to_observation[i],sizeof(*r->observation)));
        for(int j=0;j<n;++j){double v=0;for(int k=0;k<n;++k)v+=r->noise_factor->m[i*n+k]*r->noise_factor->m[j*n+k];
            close_to(v,r->covariance->m[r->factor_to_observation[i]*n+r->factor_to_observation[j]]);}}
}
int main(void)
{
    noise_fixture f,saved;noise_fill(&f);saved=f;detector_noise_result *r=NULL,*occupied;
    double expected[]={14,9,1,0,9,17,0,4,1,0,21,16,0,4,16,24};
    assert(detector_noise_assemble_checked(&f.p,&r)==0&&r->status==DETECTOR_NOISE_READY);
    assert(!memcmp(&f,&saved,sizeof f));for(int i=0;i<16;++i)close_to(r->covariance->m[i],expected[i]);
    assert(r->factor_to_observation[0]==3);check_factor(r);
    detector_measurements view;memset(&view,0,sizeof view);
    assert(detector_noise_measurements(r,&view)==0&&view.noise_factor==r->noise_factor);
    /* Integration: exact ROI operator consumes SAME ordered observations/factor. */
    detector_roi regions[2];memset(regions,0,sizeof regions);
    for(int i=0;i<2;++i){snprintf(regions[i].roi_id,64,"R%d",i);regions[i].xmin=regions[i].ymin=regions[i].ymax=1;regions[i].xmax=i?1:2;}
    int dim[1][2]={{2,1}};detector_roi_problem rp;memset(&rp,0,sizeof rp);rp.data=view;rp.rois=2;rp.roi=regions;
    rp.dimensions=(const int (*)[2])dim;rp.covariance_rank_tolerance=1e-12;rp.max_factor_condition=1e8;rp.max_dense_elements=10000;
    detector_roi_result *ro=NULL;assert(detector_roi_aggregate_checked(&rp,&ro)==0&&ro->status==DETECTOR_ROI_READY);
    int first=-1,second=-1,pixel=-1;
    for(int i=0;i<ro->active_rows;++i){detector_roi_row row=ro->row[ro->active_to_row[i]];
        if(row.roi==0&&row.input_index==8)first=i;
        if(row.roi==0&&row.input_index==3)second=i;
        if(row.roi==1&&row.input_index==8)pixel=i;}
    assert(first>=0&&second>=0&&pixel>=0);
    close_to(ro->covariance->m[first*4+first],12.25);close_to(ro->covariance->m[second*4+second],19.25);
    close_to(ro->covariance->m[first*4+second],1.25);close_to(ro->covariance->m[first*4+pixel],11.5);
    detector_roi_result_del(ro);
    occupied=r;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&r==occupied);
    detector_noise_result_del(r);r=NULL;
    /* Cross-site master and cross-exposure scan covariance are retained. */
    f.master[2]=.5;f.master[3]=sqrt(3.75);f.scan[2]=1;f.scan[3]=sqrt(15.);
    assert(detector_noise_assemble_checked(&f.p,&r)==0&&r->status==DETECTOR_NOISE_READY);
    close_to(r->covariance->m[1],9.5);close_to(r->covariance->m[2],4);
    close_to(r->covariance->m[3],3.5);close_to(r->covariance->m[7],7);check_factor(r);
    detector_noise_result_del(r);r=NULL;
    noise_fill(&f);f.p.scan_applied=0;f.p.scan_groups=0;f.p.scan_group=NULL;f.p.scan_factor=NULL;
    assert(detector_noise_assemble_checked(&f.p,&r)==0&&r->status==DETECTOR_NOISE_READY);
    close_to(r->covariance->m[0],5);close_to(r->covariance->m[1],0);close_to(r->covariance->m[2],1);check_factor(r);
    detector_noise_result_del(r);r=NULL;
    noise_fill(&f);memset(f.independent,0,sizeof f.independent);memset(f.master,0,sizeof f.master);
    assert(detector_noise_assemble_checked(&f.p,&r)==0&&r->status==DETECTOR_NOISE_RANK_UNAVAILABLE&&!r->noise_factor);
    detector_measurements sentinel;memset(&sentinel,0x5a,sizeof sentinel);view=sentinel;
    assert(detector_noise_measurements(r,&view)==-1&&!memcmp(&view,&sentinel,sizeof view));detector_noise_result_del(r);r=NULL;
    noise_fill(&f);f.p.max_factor_condition=1;
    assert(detector_noise_assemble_checked(&f.p,&r)==0&&r->status==DETECTOR_NOISE_CONDITION_UNAVAILABLE&&!r->noise_factor);
    detector_noise_result_del(r);r=NULL;
    noise_fill(&f);f.p.master_factor=NULL;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.independent[0]=-1;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.scan[0]=NAN;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.group[1]=f.group[0];assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.group[1].y=9;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.obs[1].seconds=3;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.p.independent_components=0;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.p.scan_applied=0;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.master[0]=DBL_MAX;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.p.data.noise_factor=&f.mf;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);f.p.max_dense_elements=10;assert(detector_noise_assemble_checked(&f.p,&r)==-1&&!r);
    noise_fill(&f);assert(detector_noise_assemble_checked(&f.p,&r)==0);memset(&f,0,sizeof f);
    close_to(r->covariance->m[0],14);assert(!strcmp(r->amplifier[0].detector_id,"D8"));check_factor(r);detector_noise_result_del(r);
    puts("PASS: explicit noise covariance, shared pixel/row identities, QR order, ROI integration and ownership");return 0;
}
