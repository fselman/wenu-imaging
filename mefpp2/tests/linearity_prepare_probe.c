#include "mef_linearity_prepare.h"
#include "mefp_lib.h"
#include <assert.h>
#include <math.h>
typedef struct {size_t calls,fail,live;} fault;
static void *alloc(void *u,size_t n){fault *f=u;if(++f->calls>=f->fail&&f->fail)return NULL;void *p=(malloc)(n);if(p)++f->live;return p;}
static void drop(void *u,void *p){fault *f=u;assert(p&&f->live);--f->live;(free)(p);}
static void check(int n)
{
    int w=n+4,h=5,aw=2,ah=3;double ramp[]={30,10,70,0,20};
    mef_bias_settings g;memset(&g,0,sizeof g);g.use_overscan=1;
    g.overscan[0]=1;g.overscan[1]=n;g.prescan[0]=g.prescan[1]=w;
    g.trim[0]=n+2;g.trim[1]=n+3;g.trim[2]=2;g.trim[3]=4;
    g.rejection[0]=g.rejection[1]=10;g.minimum_frames=3;g.kappa=2;
    image_t *raw[4],*master=image_new(aw,ah);assert(master);
    for(int k=0;k<aw*ah;++k)master->data[k]=3;
    for(int f=0;f<4;++f){raw[f]=image_new(w,h);assert(raw[f]);
        for(int y=0;y<h;++y){
            for(int x=0;x<n;++x)raw[f]->data[y*w+x]=(pixelvalue)(ramp[y]+7*f+(x*7)%n);
            for(int x=n;x<w;++x)raw[f]->data[y*w+x]=(pixelvalue)(ramp[y]+7*f+(n-1)/2.0+3);
        }
        if(f<2)for(int y=0;y<ah;++y)for(int x=0;x<aw;++x){int k=y*aw+x;
            size_t at=(size_t)(y+g.trim[2]-1)*w+x+g.trim[0]-1;
            raw[f]->data[at]+=(pixelvalue)(f?102+2*k:100+k);}
    }
    pixelvalue *saved=(malloc)((size_t)w*h*4*sizeof(pixelvalue));assert(saved);
    for(int f=0;f<4;++f)memcpy(saved+(size_t)f*w*h,raw[f]->data,(size_t)w*h*sizeof(pixelvalue));
    mef_linearity_prepare_frame_input in={raw[0],master,g,MEF_PREPARE_FLAT,100000};
    mef_linearity_prepare_frame_result *r=NULL;
    assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_OK&&r&&r->rows==(size_t)h);
    for(int y=0;y<h;++y)assert(r->row_correction[y]==(pixelvalue)(ramp[y]+(n-1)/2.0));
    for(int k=0;k<aw*ah;++k)assert(r->active->data[k]==100+k);
    /* Native stages must match the pre-existing singleton correction exactly. */
    mef_bb bb;mef_ccd c;memset(&bb,0,sizeof bb);memset(&c,0,sizeof c);
    memcpy(c.overscan_x,g.overscan,sizeof g.overscan);memcpy(c.prescan_x,g.prescan,sizeof g.prescan);
    memcpy(c.trimreg,g.trim,sizeof g.trim);bb.ccd=&c;bb.xtnum=bb.nxts=1;
    bb.use_overscan=1;memcpy(bb.scanrej,g.rejection,sizeof g.rejection);
    image_t *copy=image_copy(raw[0]),*old=mef_overscan_correction(copy,&bb,0,"linearity");
    assert(old&&!image_sub_local(old,master));
    assert(!memcmp(old->data,r->active->data,(size_t)aw*ah*sizeof(pixelvalue)));
    image_del(old);image_del(copy);mef_linearity_prepare_frame_destroy(r);r=NULL;
    fault state={0,0,0};mef_allocator a={&state,alloc,drop};
    assert(mef_linearity_prepare_frame(&in,&a,&r)==MEF_OK);size_t calls=state.calls;
    mef_linearity_prepare_frame_destroy(r);r=NULL;assert(!state.live);
    for(size_t i=1;i<=calls;++i){state.calls=0;state.fail=i;
        assert(mef_linearity_prepare_frame(&in,&a,&r)==MEF_ERR_MEMORY&&!r&&!state.live);}
    state.fail=0;in.max_working_pixels=1;assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_ERR_INPUT&&!r);
    in.max_working_pixels=100000;raw[0]->data[0]=NAN;
    assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_ERR_INPUT&&!r);raw[0]->data[0]=saved[0];
    in.settings.rejection[1]=n;assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_ERR_CONFIG&&!r);in.settings=g;
    in.role=MEF_PREPARE_BIAS;assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_ERR_INPUT&&!r);
    in.master=NULL;assert(mef_linearity_prepare_frame(&in,NULL,&r)==MEF_OK);
    for(int k=0;k<aw*ah;++k)assert(r->active->data[k]==103+k);
    mef_linearity_prepare_frame_destroy(r);r=NULL;
    for(int f=0;f<4;++f)assert(!memcmp(saved+(size_t)f*w*h,raw[f]->data,(size_t)w*h*sizeof(pixelvalue)));
    /* Exact common population: saturation, BPM and nonfinite raw bias each remove
     * one different pixel. The remaining k=3,4,5 have analytical sample moments. */
    raw[0]->data[(size_t)(g.trim[2]-1)*w+g.trim[0]-1]=65534;
    raw[2]->data[(size_t)g.trim[2]*w+g.trim[0]-1]=NAN;
    unsigned char flags[6]={0,1,0,0,0,0};
    mef_config *cfg=NULL;mef_bb snapshot;memset(&snapshot,0,sizeof snapshot);
#define MEF_STRING(member,key) snapshot.member="";
#define MEF_INT(member,key)
#define MEF_FLOAT(member,key)
#define MEF_DOUBLE(member,key)
#include "mef_config_fields.def"
#undef MEF_STRING
#undef MEF_INT
#undef MEF_FLOAT
#undef MEF_DOUBLE
    snapshot.nchips=1;snapshot.ccd=&c;snapshot.use_overscan=1;
    snapshot.scanrej[0]=snapshot.scanrej[1]=10;
    assert(mef_config_from_legacy(&snapshot,NULL,&cfg,NULL)==MEF_OK);
    const image_t *flats[]={raw[0],raw[1]};mef_linearity_frame frames[2];memset(frames,0,sizeof frames);
    for(int f=0;f<2;++f){snprintf(frames[f].asset_id,128,"F%d",f);strcpy(frames[f].pair_id,"pair");
        frames[f].input_index=f;frames[f].hdu=3-f;frames[f].seconds=2;}
    detector_roi roi;memset(&roi,0,sizeof roi);strcpy(roi.roi_id,"all");roi.xmin=roi.ymin=1;roi.xmax=aw;roi.ymax=ah;
    mef_linearity_pairs_input p;memset(&p,0,sizeof p);p.configuration=cfg;p.frames=2;p.rois=1;p.roi=&roi;
    p.raw=flats;p.frame=frames;p.raw_bias[0]=raw[2];p.raw_bias[1]=raw[3];p.raw_bias_asset[0]="B0";p.raw_bias_asset[1]="B1";
    p.raw_bias_hdu[0]=2;p.raw_bias_hdu[1]=0;p.bpm_flags=flags;p.bpm_count=6;p.reject_bits=255;
    strcpy(p.identity.detector_id,"D");strcpy(p.identity.amplifier_id,"A");p.saturation_raw=65534;p.max_rows=1;p.with_mad=1;
    mef_linearity_prepared_result *q=NULL,*occupied;state.calls=0;
    assert(mef_linearity_prepare_pairs(&p,master,100000,&a,&q)==MEF_OK);
    calls=state.calls;assert(q->raw->row[0].measurement.valid_pixels==3);
    assert(q->row[0].first.mean==104&&q->row[0].second.mean==110&&q->row[0].difference.mean==-6);
    assert(q->row[0].first.stdev==1&&q->row[0].second.stdev==2&&q->row[0].difference.stdev==1);
    assert(q->trace_rows==5&&q->row_correction[0]==(pixelvalue)(30+(n-1)/2.0));
    occupied=q;assert(mef_linearity_prepare_pairs(&p,master,100000,NULL,&q)==MEF_ERR_INPUT&&q==occupied);
    mef_linearity_prepared_destroy(q);q=NULL;assert(!state.live);
    for(size_t i=1;i<=calls;++i){state.calls=0;state.fail=i;
        assert(mef_linearity_prepare_pairs(&p,master,100000,&a,&q)==MEF_ERR_MEMORY&&!q&&!state.live);}
    state.fail=0;assert(mef_linearity_prepare_pairs(&p,master,1,NULL,&q)==MEF_ERR_INPUT&&!q);
    master->data[0]=NAN;assert(mef_linearity_prepare_pairs(&p,master,100000,NULL,&q)==MEF_ERR_INPUT&&!q);
    master->data[0]=3;memset(flags,1,sizeof flags);
    assert(mef_linearity_prepare_pairs(&p,master,100000,NULL,&q)==MEF_OK);
    assert(q->row[0].first.valid_pixels==0&&!q->row[0].first.level_available&&!q->row[0].first.stdev_available);
    mef_linearity_prepared_destroy(q);q=NULL;flags[3]=0;
    assert(mef_linearity_prepare_pairs(&p,master,100000,NULL,&q)==MEF_OK);
    assert(q->row[0].first.valid_pixels==1&&q->row[0].first.level_available&&!q->row[0].first.stdev_available);
    assert(q->row[0].first.mean==103&&q->row[0].difference.mean==-5);
    mef_config_destroy(cfg);image_del(master);for(int f=0;f<4;++f)image_del(raw[f]);(free)(saved);
    memset(frames,0,sizeof frames);memset(&roi,0,sizeof roi);
    assert(q->raw->frame[0].hdu==3&&!strcmp(q->raw->frame[0].asset_id,"F0")&&q->row[0].first.mean==103);
    mef_linearity_prepared_destroy(q);
    printf("PASS: %d-read ramp/edges, staged arithmetic, raw population, moments and %zu persistent allocation failures\n",n,calls);
}
int main(void){check(43);check(44);return 0;}
