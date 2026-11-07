#include "mef_linearity_raw_files.h"
#include "mef_linearity_pairs_export.h"
#include "mefp_lib.h"
#include <assert.h>
typedef struct {size_t calls,fail,live;} fault;
static void *alloc(void *u,size_t n){fault *f=u;if(++f->calls>=f->fail&&f->fail)return NULL;void *p=(malloc)(n);if(p)++f->live;return p;}
static void drop(void *u,void *p){fault *f=u;assert(p&&f->live);--f->live;(free)(p);}
static mef_layout_map *bind_file(const char *path,int hdu,int active,int mask,int wrong_readout)
{
    mef_layout_options o;mef_detector_binding b;mef_layout *layout=NULL;mef_layout_map *map=NULL;
    memset(&o,0,sizeof o);o.max_hdus=10;o.max_header_bytes=100000;o.identity_key="DETID";o.amplifier_key="AMPID";
    o.bin_x_key="XBINNING";o.bin_y_key="YBINNING";
    memset(&b,0,sizeof b);b.detector_id="D";b.expected_header_id="D";b.hdu_index=hdu;b.unit=mask?"mask":"ADU";
    b.readout_id=wrong_readout?"wrong":"WFI:test";b.bin_x=b.bin_y=1;b.active_x=active?1:2;b.active_y=active?1:2;
    b.active_width=4;b.active_height=2;b.configuration_detector=0;b.health=MEF_HEALTH_UNKNOWN;b.selection=MEF_OUTPUT_SELECTED;
    assert(mef_layout_read(path,&o,NULL,&layout,NULL)==MEF_OK);
    assert(mef_layout_bind(layout,&b,1,NULL,&map,NULL)==MEF_OK);mef_layout_destroy(layout);return map;
}
int main(int argc,char **argv)
{
    assert(argc==5);int kind=atoi(argv[3]);const char *mode=argv[4];
    mef_bb *bb=mef_bb_new_from_paf(argv[1]);assert(bb);int trim[]={2,5,2,3};
    memcpy(bb->ccd[0].trimreg,trim,sizeof trim);
    mef_config *config=NULL;assert(mef_config_from_legacy(bb,NULL,&config,NULL)==MEF_OK);mef_bb_del(bb);
    mef_linearity_file_frame frames[4];memset(frames,0,sizeof frames);
    char paths[4][4096],assets[4][16];const char *pair[]={"P0","P1","P1","P0"};int indices[]={8,3,11,4};
    for(int i=0;i<4;++i){snprintf(paths[i],4096,"%s/flat-%d.fits",argv[2],i);snprintf(assets[i],16,"raw:%d",i);
        frames[i].map=bind_file(paths[i],i%2?2:0,0,0,0);frames[i].reference.asset_record_id=assets[i];
        frames[i].reference.resolved_path=paths[i];frames[i].reference.detector_id="D";frames[i].reference.hdu_index=i%2?2:0;
        frames[i].input_index=indices[i];frames[i].pair_id=pair[i];}
    char rbpath[2][4096],bpmpath[4096];mef_layout_map *rbmap[2];mef_image_ref rbref[2];memset(rbref,0,sizeof rbref);
    for(int j=0;j<2;++j){snprintf(rbpath[j],4096,"%s/raw-bias-%d.fits",argv[2],j);
        rbmap[j]=bind_file(rbpath[j],0,0,0,!strcmp(mode,"readout")&&j==1);
        rbref[j].asset_record_id=j?"raw-bias:1":"raw-bias:0";rbref[j].detector_id="D";rbref[j].resolved_path=rbpath[j];}
    snprintf(bpmpath,4096,"%s/bpm.fits",argv[2]);mef_layout_map *bpm=kind?bind_file(bpmpath,0,1,1,0):NULL;
    mef_image_ref bpmref={"bpm:selected","D",bpmpath,0,NULL,0};
    detector_roi roi[2];memset(roi,0,sizeof roi);
    for(int i=0;i<2;++i){snprintf(roi[i].roi_id,64,"R%d",i);roi[i].amplifier=4;
        roi[i].xmin=i?2:1;roi[i].xmax=i?3:2;roi[i].ymin=1;roi[i].ymax=2;}
    mef_linearity_raw_files_input in;memset(&in,0,sizeof in);in.pairs.configuration=config;
    in.pairs.frames=4;in.pairs.rois=2;in.pairs.roi=roi;in.pairs.amplifier_index=4;
    strcpy(in.pairs.identity.detector_id,"D");strcpy(in.pairs.identity.amplifier_id,"OUT1");
    in.pairs.saturation_raw=1000;in.pairs.reject_bits=255;in.pairs.with_mad=1;in.pairs.max_rows=4;
    in.input=frames;for(int j=0;j<2;++j){in.raw_bias_map[j]=rbmap[j];in.raw_bias_reference[j]=rbref+j;}
    in.bpm_map=bpm;in.bpm_reference=kind?&bpmref:NULL;in.exposure_key="EXPTIME";in.max_loaded_pixels=1000;
    in.mask_encoding=!kind?MEF_LINEARITY_MASK_OMITTED:kind==1?MEF_LINEARITY_MASK_REASON8:MEF_LINEARITY_MASK_BINARY;
    in.binary_good_value=kind==3?1:0;in.mask_registry="WENU_BPM_V1";
    if(!strcmp(mode,"limit"))in.max_loaded_pixels=143;
    if(!strcmp(mode,"rows"))in.pairs.max_rows=3;
    if(!strcmp(mode,"alias"))rbref[1].asset_record_id=rbref[0].asset_record_id;
    if(!strcmp(mode,"flat_alias"))rbref[1].asset_record_id=frames[0].reference.asset_record_id;
    if(!strcmp(mode,"hdu"))frames[0].reference.hdu_index=1;
    if(!strcmp(mode,"pair_id"))frames[0].pair_id="missing";
    if(!strcmp(mode,"registry"))in.mask_registry="OTHER";
    if(!strcmp(mode,"tolerant"))in.pairs.pair_time_tolerance=.02;
    if(!strcmp(mode,"roi"))roi[0].xmax=5;
    if(!strcmp(mode,"pointer"))in.pairs.raw_bias_hdu[0]=1;
    mef_linearity_files_result *r=NULL,*occupied;fault f={0,0,0};mef_allocator a={&f,alloc,drop};
    mef_status status=mef_linearity_raw_from_files(&in,&a,&r);
    if(strcmp(mode,"normal")&&strcmp(mode,"tolerant")){assert(status!=MEF_OK&&!r&&!f.live);goto cleanup;}
    assert(status==MEF_OK&&r&&!r->samples&&!r->bias_path&&r->pairs&&r->pairs->rows==4);
    assert(r->pairs->row[0].first==0&&r->pairs->row[0].second==3&&r->pairs->row[2].first==1);
    assert(r->pairs->row[0].measurement.valid_pixels==(kind?3:4));
    assert(r->pairs->bias[0].ron_available&&fabs(r->pairs->bias[0].ron_adu-sqrt(2./3))<1e-9);
    assert(r->pairs->frame[1].hdu==2&&r->pairs->frame[2].input_index==11);
    if(!strcmp(mode,"tolerant"))assert(r->pairs->frame[1].seconds==5.01);
    size_t calls=f.calls;occupied=r;
    assert(mef_linearity_raw_from_files(&in,NULL,&r)==MEF_ERR_INPUT&&r==occupied);
    mef_linearity_files_destroy(r);r=NULL;assert(!f.live);
    if(kind==1&&!strcmp(mode,"normal")){
        for(size_t i=1;i<=calls;++i){f.calls=0;f.fail=i;
            assert(mef_linearity_raw_from_files(&in,&a,&r)==MEF_ERR_MEMORY&&!r&&!f.live);}
        printf("PASS: %zu persistent raw-file/service owner allocation failures\n",calls);}
    assert(mef_linearity_raw_from_files(&in,NULL,&r)==MEF_OK);
cleanup:
    for(int i=0;i<4;++i)mef_layout_map_destroy((mef_layout_map *)frames[i].map);
    for(int j=0;j<2;++j)mef_layout_map_destroy(rbmap[j]);
    mef_layout_map_destroy(bpm);mef_config_destroy(config);memset(frames,0,sizeof frames);memset(roi,0,sizeof roi);
    if(r){assert(r->pairs->frame[0].input_index==8&&strstr(r->raw_bias_path[1],"raw-bias-1.fits"));
        char table[4096];snprintf(table,4096,"%s/pairs.tsv",argv[2]);FILE *stream=fopen(table,"w");assert(stream);
        assert(mef_linearity_pairs_write_tsv(stream,r->pairs)==MEF_OK);assert(!fclose(stream));mef_linearity_files_destroy(r);}
    assert(!f.live);puts("PASS: raw-only file admission, no master/corrected samples, detached ownership");return 0;
}
