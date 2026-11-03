#include "mef_linearity_samples.h"
#include "mefp_lib.h"
#include <assert.h>
#include <math.h>
typedef struct {size_t calls,fail,live;} fault;
static void *alloc(void *u,size_t n){fault *f=u;if(++f->calls>=f->fail&&f->fail)return NULL;void *p=(malloc)(n);if(p)++f->live;return p;}
static void drop(void *u,void *p){fault *f=u;assert(p&&f->live);--f->live;(free)(p);}
int main(int argc,char **argv)
{
    assert(argc==2);mef_bb *bb=mef_bb_new_from_paf(argv[1]);assert(bb);
    bb->use_prescan=bb->use_overscan=1;bb->scanrej[0]=bb->scanrej[1]=0;
    bb->ccd[0].prescan_x[0]=bb->ccd[0].prescan_x[1]=1;
    bb->ccd[0].overscan_x[0]=bb->ccd[0].overscan_x[1]=6;
    int trim[]={2,5,2,3};memcpy(bb->ccd[0].trimreg,trim,sizeof trim);
    mef_config *config=NULL,*no_scan=NULL;
    assert(mef_config_from_legacy(bb,NULL,&config,NULL)==MEF_OK);
    bb->use_prescan=bb->use_overscan=0;
    assert(mef_config_from_legacy(bb,NULL,&no_scan,NULL)==MEF_OK);mef_bb_del(bb);
    image_t *raw[2]={image_new(6,4),image_new(6,4)},*bias=image_new(4,2);
    const image_t *planes[2]={raw[0],raw[1]};pixelmap *sample=pixelmap_new(4,2);
    const pixelmap *maps[]={sample,NULL};unsigned char flags[8]={1,0,0,0,0,0,0,0};
    for(int k=0;k<8;++k){bias->data[k]=3;sample->data[k]=1;}sample->data[1]=0;
    for(int f=0;f<2;++f)for(int y=0;y<4;++y){
        raw[f]->data[y*6]=10+y*10;raw[f]->data[y*6+5]=14+y*10;
        for(int x=1;x<=4;++x)raw[f]->data[y*6+x]=12+y*10+3+100+f*10+(y-1)*4+x-1;
    }
    raw[0]->data[6+3]=NAN;raw[1]->data[12+2]=500;
    pixelvalue saved[2][24];memcpy(saved[0],raw[0]->data,sizeof saved[0]);memcpy(saved[1],raw[1]->data,sizeof saved[1]);
    mef_linearity_frame frames[2];memset(frames,0,sizeof frames);
    for(int f=0;f<2;++f){snprintf(frames[f].asset_id,128,"flat:%d",f);snprintf(frames[f].pair_id,64,"pair:%d",f);
        frames[f].input_index=f?3:8;frames[f].hdu=9;frames[f].seconds=f?5:2;}
    detector_roi rois[3];memset(rois,0,sizeof rois);
    for(int i=0;i<3;++i){snprintf(rois[i].roi_id,64,"R%d",i);rois[i].amplifier=i==2?9:4;
        rois[i].xmin=i==1?2:1;rois[i].xmax=i==1?3:2;rois[i].ymin=1;rois[i].ymax=2;}
    mef_linearity_sample_input in;memset(&in,0,sizeof in);in.configuration=config;in.frames=2;in.raw=planes;
    in.frame=frames;in.master_bias=bias;in.bpm_flags=flags;in.bpm_count=8;in.reject_bits=1;in.samples=maps;
    in.rois=3;in.roi=rois;in.amplifier_index=4;in.saturation_raw=500;in.max_sites=8;in.max_observations=16;
    strcpy(in.identity.detector_id,"CHIP8");strcpy(in.identity.amplifier_id,"OUT1");in.identity.signal_max=10000;
    mef_linearity_sample_result *r=NULL,*occupied;fault f={0,0,0};mef_allocator a={&f,alloc,drop};
    assert(mef_linearity_samples(&in,&a,&r)==MEF_OK&&r);
    size_t allocations=f.calls;
    assert(r->sites==5&&r->observations==7&&r->rois==2&&r->roi[0].amplifier==0);
    assert(r->noise_state==MEF_LINEARITY_NOISE_UNAVAILABLE&&r->width==4&&r->height==2);
    assert(r->frame[0].input_index==8&&r->frame[1].input_index==3&&r->frame[1].seconds==5&&r->frame[0].hdu==9);
    assert(r->population[0].outside_roi==2&&r->population[0].bpm_excluded==1&&r->population[0].sample_excluded==1&&r->population[0].nonfinite==1&&r->population[0].admitted==3);
    assert(r->population[1].outside_roi==2&&r->population[1].bpm_excluded==1&&r->population[1].saturated==1&&r->population[1].admitted==4);
    int expected_site[]={2,3,4,0,1,2,4};double expected_signal[]={104,105,106,111,112,114,116};
    for(int i=0;i<7;++i){assert(r->observation[i].site==expected_site[i]);assert(r->observation[i].signal==expected_signal[i]);
        assert(r->observation[i].input_index==(i<3?8:3));}
    occupied=r;assert(mef_linearity_samples(&in,NULL,&r)!=MEF_OK&&r==occupied);
    mef_linearity_samples_destroy(r);r=NULL;assert(!f.live);
    /* Every service/config-snapshot allocation fails persistently and releases. */
    for(size_t i=1;i<=allocations;++i){f.calls=0;f.fail=i;assert(mef_linearity_samples(&in,&a,&r)==MEF_ERR_MEMORY&&!r&&!f.live);}
    in.max_observations=6;assert(mef_linearity_samples(&in,NULL,&r)==MEF_ERR_INPUT&&!r);in.max_observations=16;
    in.max_sites=4;assert(mef_linearity_samples(&in,NULL,&r)==MEF_ERR_INPUT&&!r);in.max_sites=8;
    frames[1].input_index=8;assert(mef_linearity_samples(&in,NULL,&r)==MEF_ERR_INPUT&&!r);frames[1].input_index=3;
    raw[0]->data[0]=NAN;assert(mef_linearity_samples(&in,NULL,&r)==MEF_ERR_INPUT&&!r);raw[0]->data[0]=saved[0][0];
    flags[0]=0;in.reject_bits=0;in.saturation_raw=1;
    assert(mef_linearity_samples(&in,NULL,&r)==MEF_OK&&r->sites==0&&r->observations==0);
    mef_linearity_samples_destroy(r);r=NULL;
    for(int j=0;j<2;++j)assert(!memcmp(saved[j],raw[j]->data,sizeof saved[j]));
    /* Explicit no-scan branch still crops/subtracts; it is not a real-data policy. */
    flags[0]=1;in.reject_bits=1;in.saturation_raw=500;in.configuration=no_scan;
    assert(mef_linearity_samples(&in,NULL,&r)==MEF_OK&&r->observations==7);
    assert(r->observation[0].signal==136&&r->observation[3].signal==133);
    mef_linearity_samples_destroy(r);r=NULL;in.configuration=config;
    mef_config_destroy(no_scan);
    for(int k=0;k<8;++k)assert(bias->data[k]==3);
    /* Result owns source metadata/configuration; no borrowing after return. */
    flags[0]=1;in.reject_bits=1;in.saturation_raw=500;
    assert(mef_linearity_samples(&in,NULL,&r)==MEF_OK);memset(frames,0,sizeof frames);memset(rois,0,sizeof rois);
    image_del(raw[0]);image_del(raw[1]);image_del(bias);pixelmap_del(sample);mef_config_destroy(config);
    assert(r->observations==7&&r->frame[0].seconds==2&&!strcmp(r->roi[0].roi_id,"R0"));
    mef_linearity_samples_destroy(r);
    printf("Known row scan/bias samples, ROI union, populations, ownership, %zu allocation failures passed\n",allocations);
    return 0;
}
