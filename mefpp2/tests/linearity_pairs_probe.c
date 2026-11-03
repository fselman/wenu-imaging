#include "mef_linearity_pairs.h"
#include "mefp_lib.h"
#include <assert.h>
#include <float.h>
typedef struct {size_t calls,fail,live;} fault;
static void *alloc(void *u,size_t n){fault *f=u;if(++f->calls>=f->fail&&f->fail)return NULL;void *p=(malloc)(n);if(p)++f->live;return p;}
static void drop(void *u,void *p){fault *f=u;assert(p&&f->live);--f->live;(free)(p);}
static void near(double a,double b){assert(fabs(a-b)<1e-9*(1+fabs(b)));}
int main(int argc,char **argv)
{
    assert(argc==2);mef_bb *bb=mef_bb_new_from_paf(argv[1]);assert(bb);
    int trim[]={2,5,2,2};memcpy(bb->ccd[0].trimreg,trim,sizeof trim);
    mef_config *config=NULL;assert(mef_config_from_legacy(bb,NULL,&config,NULL)==MEF_OK);mef_bb_del(bb);
    image_t *im[4],*b[2];const image_t *raw[4];pixelvalue saved[6][18];
    for(int i=0;i<4;++i){im[i]=image_new(6,3);assert(im[i]);raw[i]=im[i];
        for(int j=0;j<18;++j)im[i]->data[j]=900+100*i;}
    for(int i=0;i<2;++i){b[i]=image_new(6,3);assert(b[i]);for(int j=0;j<18;++j)b[i]->data[j]=1000*i;}
    for(int x=0;x<4;++x){int pattern=x==0?1:x==1?-1:0;
        im[0]->data[7+x]=100+pattern;im[3]->data[7+x]=100-pattern;
        im[1]->data[7+x]=200+2*pattern;im[2]->data[7+x]=200-2*pattern;
        b[0]->data[7+x]=10+pattern;b[1]->data[7+x]=10;}
    for(int i=0;i<6;++i)memcpy(saved[i],i<4?im[i]->data:b[i-4]->data,sizeof saved[i]);
    mef_linearity_frame frame[4];memset(frame,0,sizeof frame);
    const char *ids[]={"P0","P1","P1","P0"};int index[]={8,3,11,4};
    for(int i=0;i<4;++i){snprintf(frame[i].asset_id,128,"F%d",i);strcpy(frame[i].pair_id,ids[i]);
        frame[i].input_index=index[i];frame[i].hdu=i%2?2:0;frame[i].seconds=i==0||i==3?2:5;}
    detector_roi roi[2];memset(roi,0,sizeof roi);
    for(int i=0;i<2;++i){snprintf(roi[i].roi_id,64,"R%d",i);roi[i].amplifier=3;
        roi[i].xmin=roi[i].ymin=roi[i].ymax=1;roi[i].xmax=i?2:4;}
    mef_linearity_pairs_input p;memset(&p,0,sizeof p);p.configuration=config;p.frames=4;p.raw=raw;p.frame=frame;
    p.raw_bias[0]=b[0];p.raw_bias[1]=b[1];p.raw_bias_asset[0]="B1";p.raw_bias_asset[1]="B2";
    p.raw_bias_hdu[1]=2;p.rois=2;p.roi=roi;p.amplifier_index=3;p.with_mad=1;p.reject_bits=255;p.saturation_raw=1000;p.max_rows=4;
    strcpy(p.identity.detector_id,"D");strcpy(p.identity.amplifier_id,"OUT1");
    mef_linearity_pairs_result *r=NULL,*occupied;fault f={0,0,0};mef_allocator a={&f,alloc,drop};
    assert(mef_linearity_measure_pairs(&p,&a,&r)==MEF_OK);size_t calls=f.calls;
    assert(r->pairs==2&&r->rows==4&&r->row[0].first==0&&r->row[0].second==3&&r->row[2].first==1&&r->row[2].second==2);
    near(r->row[0].mean_signal,90);near(r->row[0].single_flat_variance,4./3);near(r->row[0].single_bias_variance,1./3);
    near(r->row[0].measurement.gain_e_per_adu,90);near(r->row[1].measurement.gain_e_per_adu,30);
    near(r->row[2].mean_signal,190);near(r->row[2].single_flat_variance,16./3);near(r->row[2].measurement.gain_e_per_adu,38);
    near(r->bias[0].ron_adu,sqrt(1./3));assert(r->bias[0].raw_zone[0]==2&&r->bias[0].raw_zone[2]==2);
    near(r->bias[0].difference.mean,0);assert(r->row[0].measurement.valid_pixels==4);
    occupied=r;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&r==occupied);
    mef_linearity_pairs_destroy(r);r=NULL;assert(!f.live);
    for(size_t i=1;i<=calls;++i){f.calls=0;f.fail=i;assert(mef_linearity_measure_pairs(&p,&a,&r)==MEF_ERR_MEMORY&&!r&&!f.live);}
    unsigned char flags[4]={1,0,0,0};p.bpm_flags=flags;p.bpm_count=4;im[0]->data[10]=NAN;im[3]->data[9]=1000;
    assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_OK);
    assert(r->bias[0].difference.valid_pixels==3&&r->bias[0].ron_available);
    assert(r->row[0].measurement.valid_pixels==1&&!r->row[0].variance_available&&r->row[0].saturated==1&&r->row[0].bpm_excluded==1);
    assert(r->row[0].measurement.nonfinite_excluded==1&&r->row[0].measurement.bpm_excluded==2);
    assert(r->row[2].measurement.valid_pixels==3&&r->row[2].variance_available);
    mef_linearity_pairs_destroy(r);r=NULL;
    pixelmap *binary=pixelmap_new(4,1);assert(binary);for(int k=0;k<4;++k)binary->data[k]=(k!=0);
    p.bpm_binary=binary;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&!r);
    p.bpm_flags=NULL;p.bpm_count=0;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_OK&&r->bpm_binary_supplied);
    assert(r->row[0].measurement.valid_pixels==1);mef_linearity_pairs_destroy(r);r=NULL;pixelmap_del(binary);p.bpm_binary=NULL;
    for(int i=0;i<4;++i)memcpy(im[i]->data,saved[i],sizeof saved[i]);
    p.max_rows=3;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&!r);p.max_rows=4;
    frame[3].seconds=2.01;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&!r);
    p.pair_time_tolerance=.02;assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_OK&&r->frame[3].seconds==2.01);
    mef_linearity_pairs_destroy(r);r=NULL;frame[3].seconds=2;p.pair_time_tolerance=0;
    strcpy(frame[3].pair_id,"missing");assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&!r);strcpy(frame[3].pair_id,"P0");
    p.raw_bias_asset[1]="B1";assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_INPUT&&!r);p.raw_bias_asset[1]="B2";
    b[0]->data[7]=FLT_MAX;b[1]->data[7]=-FLT_MAX;p.saturation_raw=DBL_MAX;
    assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_ERR_COMPUTATION&&!r);
    memcpy(b[0]->data,saved[4],sizeof saved[4]);memcpy(b[1]->data,saved[5],sizeof saved[5]);p.saturation_raw=1000;
    assert(mef_linearity_measure_pairs(&p,NULL,&r)==MEF_OK);
    for(int i=0;i<6;++i)assert(!memcmp(saved[i],i<4?im[i]->data:b[i-4]->data,sizeof saved[i]));
    for(int i=0;i<4;++i)image_del(im[i]);
    for(int i=0;i<2;++i)image_del(b[i]);
    mef_config_destroy(config);memset(frame,0,sizeof frame);memset(roi,0,sizeof roi);
    assert(r->row[0].measurement.valid_pixels==4&&!strcmp(r->frame[3].pair_id,"P0"));mef_linearity_pairs_destroy(r);
    printf("PASS: raw pair/ROI known answers and %zu persistent service/snapshot allocation failures\n",calls);return 0;
}
