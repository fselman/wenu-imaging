
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include "detector_roi.h"
typedef struct {
    detector_joint_amplifier amp;
    detector_joint_site site[4];detector_joint_observation obs[8];
    detector_roi roi[5];int dimensions[1][2];
    double h[64],vectors[16];matrix factor,vec;
    detector_roi_problem p;
} roi_fixture;
static void near(double a,double b){assert(fabs(a-b)<1e-10*fmax(1,fabs(b)));}
static void roi_fill(roi_fixture *f,int correlated)
{
    int i;memset(f,0,sizeof(*f));
    strcpy(f->amp.detector_id,"DET1");strcpy(f->amp.amplifier_id,"AMP1");
    f->amp.signal_max=100000;f->dimensions[0][0]=5;f->dimensions[0][1]=1;
    for(i=0;i<4;++i){f->site[i].amplifier=0;f->site[i].x=i+1;f->site[i].y=1;}
    for(i=0;i<8;++i) {
        double value=10*(i%4+1)+(i>=4?2:0);
        f->obs[i].site=i%4;f->obs[i].input_index=i<4?8:3;
        f->obs[i].seconds=i<4?2:5;f->obs[i].signal=value;
        /* Nonlinear toy response and a derivative-like vector column. */
        f->vectors[2*i]=value+.01*value*value;f->vectors[2*i+1]=i%4+1;
    }
    for(i=0;i<5;++i){snprintf(f->roi[i].roi_id,64,"ROI%d",i);f->roi[i].amplifier=0;
        f->roi[i].ymin=f->roi[i].ymax=1;}
    f->roi[0].xmin=1;f->roi[0].xmax=2;
    f->roi[1].xmin=2;f->roi[1].xmax=3;
    f->roi[2].xmin=f->roi[2].xmax=4;
    f->roi[3].xmin=f->roi[3].xmax=5;
    f->roi[4].xmin=f->roi[4].xmax=1;
    f->factor.m=f->h;f->factor.nr=8;f->factor.nc=correlated?8:1;
    if(correlated)for(i=0;i<4;++i) {
        f->h[i*8+i]=2;
        f->h[(i+4)*8+i]=.5;
        f->h[(i+4)*8+i+4]=sqrt(3.75);
    }else for(i=0;i<8;++i)f->h[i]=2;
    f->vec.m=f->vectors;f->vec.nr=8;f->vec.nc=2;
    f->p.data.amplifiers=1;f->p.data.sites=4;f->p.data.observations=8;
    f->p.data.amplifier=&f->amp;f->p.data.site=f->site;f->p.data.observation=f->obs;
    f->p.data.noise_factor=&f->factor;f->p.rois=3;f->p.roi=f->roi;
    f->p.dimensions=(const int (*)[2])f->dimensions;f->p.pixel_vectors=&f->vec;
    f->p.covariance_rank_tolerance=1e-12;f->p.max_factor_condition=1e8;
    f->p.max_dense_elements=10000;
}
static void factor_identity(detector_roi_result *out)
{
    int i,j,k,n=out->active_rows;
    assert(out->noise_factor&&out->factor_to_active);
    for(i=0;i<n;++i) {
        assert(out->noise_factor->m[i*n+i]>0);
        for(j=0;j<n;++j) {
            double q=0;
            for(k=0;k<n;++k)q+=out->noise_factor->m[i*n+k]*out->noise_factor->m[j*n+k];
            near(q,out->covariance->m[out->factor_to_active[i]*n+out->factor_to_active[j]]);
        }
    }
}
int main(void)
{
    roi_fixture f,saved;detector_roi_result *out=NULL,*occupied;int correlated,i,j;
    double means[]={15,17,25,27,40,42};
    for(correlated=0;correlated<=1;++correlated) {
        roi_fill(&f,correlated);saved=f;
        assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_READY);
        assert(!memcmp(&f,&saved,sizeof f));
        assert(out->rows==6&&out->active_rows==6&&out->frames==2);
        assert(out->geometric_overlap_pairs==1&&out->shared_observations==2);
        assert(out->union_observations==8&&out->union_sites==4&&out->offset[6]==10);
        for(i=0;i<6;++i) {
            assert(out->row[i].input_index==(i%2?3:8));near(out->row[i].mean,means[i]);
            near(out->covariance->m[i*6+i],i<4?2:4);
        }
        /* Independent C=independent variance 3 + shared same-pixel bias variance 1.
         * Diagonal-only case has variance 4 and no cross-frame contribution. */
        for(i=0;i<6;++i)for(j=0;j<6;++j) {
            size_t a,b;double expected=0;
            for(a=out->offset[i];a<out->offset[i+1];++a)for(b=out->offset[j];b<out->offset[j+1];++b) {
                int x=out->member[a],y=out->member[b];
                if(x==y)expected+=4;
                else if(correlated&&f.obs[x].site==f.obs[y].site)expected+=1;
            }
            expected/=(double)(out->row[i].count*out->row[j].count);
            near(out->covariance->m[i*6+j],expected);
        }
        near(out->covariance->m[2],1);near(out->covariance->m[1],correlated?.5:0);
        near(out->projected->m[0],17.5);near(out->projected->m[1],1.5);
        assert(fabs(out->projected->m[0]-(15+.01*15*15))>.2); /* predict/transform first */
        factor_identity(out);assert(out->factor_to_active[0]==4);assert(out->factor_qr_transposed&&out->factor_qr->rank==6);
        for(i=0;i<8;++i)assert(out->union_index[i]==i);
        occupied=out;assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&out==occupied);
        assert(out->roi!=f.roi&&out->observation!=f.obs&&out->source_noise_factor->m!=f.h);
        detector_roi_result_del(out);out=NULL;
    }
    roi_fill(&f,0);f.p.rois=4;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_READY);
    assert(out->rows==8&&out->active_rows==6&&out->row[6].count==0&&isnan(out->row[6].mean));
    assert(out->row[7].count==0&&out->active_to_row[5]==5);detector_roi_result_del(out);out=NULL;
    /* A saturated/rejected pixel in one exposure is absent from admitted data. */
    roi_fill(&f,0);f.p.data.observations=7;f.factor.nr=f.vec.nr=7;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_READY);
    assert(out->active_rows==5&&out->row[5].count==0&&isnan(out->row[5].mean));
    assert(out->union_observations==7);factor_identity(out);detector_roi_result_del(out);out=NULL;
    /* A partially masked overlap changes the exact per-exposure population. */
    roi_fill(&f,0);f.obs[5]=f.obs[6];f.obs[6]=f.obs[7];
    for(j=0;j<2;++j){f.vectors[10+j]=f.vectors[12+j];f.vectors[12+j]=f.vectors[14+j];}
    f.p.data.observations=7;f.factor.nr=f.vec.nr=7;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_READY);
    assert(out->row[1].count==1&&out->row[3].count==1&&out->shared_observations==1);
    near(out->row[1].mean,12);near(out->row[3].mean,32);near(out->covariance->m[1*6+3],0);
    near(out->covariance->m[1*6+1],4);factor_identity(out);detector_roi_result_del(out);out=NULL;
    /* Equal coordinates on distinct amplifier/detector identities stay separate. */
    {detector_joint_amplifier amps[2];int dims[2][2]={{5,1},{5,1}};
     roi_fill(&f,0);amps[0]=f.amp;amps[1]=f.amp;
     strcpy(amps[1].detector_id,"DET2");strcpy(amps[1].amplifier_id,"AMP2");
     f.site[2].amplifier=f.site[3].amplifier=1;f.site[2].x=1;f.site[3].x=2;
     f.p.data.amplifiers=2;f.p.data.amplifier=amps;f.p.dimensions=(const int (*)[2])dims;
     f.p.rois=2;f.roi[1].amplifier=1;f.roi[1].xmin=1;f.roi[1].xmax=2;
     assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_READY);
     assert(out->geometric_overlap_pairs==0&&out->shared_observations==0&&out->union_observations==8);
     near(out->row[0].mean,15);near(out->row[2].mean,35);near(out->covariance->m[2],0);
     factor_identity(out);assert(!strcmp(out->amplifier[1].detector_id,"DET2"));
     detector_roi_result_del(out);out=NULL;}
    roi_fill(&f,0);f.p.rois=1;f.roi[0].xmin=f.roi[0].xmax=5;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_EMPTY);
    assert(!out->noise_factor&&!out->covariance&&!out->projected&&out->union_observations==0);
    detector_roi_result_del(out);out=NULL;
    roi_fill(&f,0);f.roi[1].xmin=1;f.roi[1].xmax=2;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_COVARIANCE_RANK_UNAVAILABLE);
    assert(out->factor_qr->rank==4&&!out->noise_factor);near(out->covariance->m[2],2);
    detector_roi_result_del(out);out=NULL;
    /* More aggregate rows than source samples: use QR(B) for rank, no factor. */
    roi_fill(&f,0);f.p.rois=5;
    for(i=0;i<5;++i){f.roi[i].xmin=1;f.roi[i].xmax=2;}
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_COVARIANCE_RANK_UNAVAILABLE);
    assert(out->active_rows==10&&!out->factor_qr_transposed&&out->factor_qr->rank==2&&!out->noise_factor);
    detector_roi_result_del(out);out=NULL;
    roi_fill(&f,0);f.p.max_factor_condition=1;
    assert(detector_roi_aggregate_checked(&f.p,&out)==0&&out->status==DETECTOR_ROI_COVARIANCE_CONDITION_UNAVAILABLE);
    assert(!out->noise_factor);detector_roi_result_del(out);out=NULL;
    roi_fill(&f,0);f.roi[0].xmax=6;assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&!out);
    roi_fill(&f,0);f.obs[1]=f.obs[0];assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&!out);
    roi_fill(&f,1);f.h[1]=1;assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&!out);
    roi_fill(&f,0);f.vectors[0]=NAN;assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&!out);
    roi_fill(&f,0);f.p.max_dense_elements=1;assert(detector_roi_aggregate_checked(&f.p,&out)==-1&&!out);
    detector_roi_result_del(NULL);
    puts("PASS: exact ROI means/operators, overlap/shared-bias covariance, pivoted factors, empty/singular states and inputs");
    return 0;
}
