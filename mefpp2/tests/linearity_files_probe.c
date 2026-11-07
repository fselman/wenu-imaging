#include "mef_linearity_files.h"
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
    mef_bb *bb=mef_bb_new_from_paf(argv[1]);assert(bb);bb->use_prescan=bb->use_overscan=1;bb->scanrej[0]=bb->scanrej[1]=0;
    bb->ccd[0].prescan_x[0]=bb->ccd[0].prescan_x[1]=1;bb->ccd[0].overscan_x[0]=bb->ccd[0].overscan_x[1]=6;
    int trim[]={2,5,2,3};memcpy(bb->ccd[0].trimreg,trim,sizeof trim);
    mef_config *config=NULL;assert(mef_config_from_legacy(bb,NULL,&config,NULL)==MEF_OK);mef_bb_del(bb);
    char paths[4][4096],bias_path[4096],bpm_path[4096],assets[4][16];
    mef_linearity_file_frame frames[4];memset(frames,0,sizeof frames);int indices[]={8,3,11,4};
    const char *pair_ids[]={"P0","P1","P1","P0"};
    for(int i=0;i<4;++i){snprintf(paths[i],4096,"%s/flat-%d.fits",argv[2],i);snprintf(assets[i],16,"raw:%d",i);
        frames[i].map=bind_file(paths[i],i%2?2:0,0,0,0);frames[i].reference.asset_record_id=assets[i];
        frames[i].reference.resolved_path=paths[i];frames[i].reference.detector_id="D";frames[i].reference.hdu_index=i%2?2:0;
        frames[i].input_index=indices[i];frames[i].pair_id=pair_ids[i];}
    snprintf(bias_path,4096,"%s/bias.fits",argv[2]);snprintf(bpm_path,4096,"%s/bpm.fits",argv[2]);
    mef_layout_map *bias=bind_file(bias_path,0,1,0,!strcmp(mode,"readout"));
    mef_layout_map *bpm=kind?bind_file(bpm_path,0,1,1,0):NULL;
    mef_image_ref bias_ref={"bias:selected","D",bias_path,0,NULL,0};
    mef_image_ref bpm_ref={"bpm:selected","D",bpm_path,0,NULL,0};
    detector_roi rois[2];memset(rois,0,sizeof rois);for(int i=0;i<2;++i){snprintf(rois[i].roi_id,64,"R%d",i);
        rois[i].amplifier=4;rois[i].xmin=i?2:1;rois[i].xmax=i?3:2;rois[i].ymin=1;rois[i].ymax=2;}
    char rbpath[2][4096];mef_layout_map *rbmap[2]={NULL,NULL};mef_image_ref rbref[2];memset(rbref,0,sizeof rbref);
    int measuring=!strncmp(mode,"measure",7);
    if(measuring)for(int j=0;j<2;++j){snprintf(rbpath[j],4096,"%s/raw-bias-%d.fits",argv[2],j);
        rbmap[j]=bind_file(rbpath[j],0,0,0,!strcmp(mode,"measure_readout")&&j==1);
        rbref[j].asset_record_id=j?"raw-bias:1":"raw-bias:0";rbref[j].detector_id="D";
        rbref[j].resolved_path=rbpath[j];}
    mef_linearity_files_input in;memset(&in,0,sizeof in);in.sample.configuration=config;in.sample.frames=4;
    strcpy(in.sample.identity.detector_id,"D");strcpy(in.sample.identity.amplifier_id,"OUT1");in.sample.identity.signal_max=2000;
    in.sample.amplifier_index=4;in.sample.rois=2;in.sample.roi=rois;in.sample.saturation_raw=1000;
    in.sample.reject_bits=255;in.sample.max_sites=8;in.sample.max_observations=24;
    in.input=frames;in.bias_map=bias;in.bias_reference=&bias_ref;in.bpm_map=bpm;in.bpm_reference=kind?&bpm_ref:NULL;
    in.mask_encoding=!kind?MEF_LINEARITY_MASK_OMITTED:kind==1?MEF_LINEARITY_MASK_REASON8:MEF_LINEARITY_MASK_BINARY;
    in.binary_good_value=kind==3?1:0;in.mask_registry="WENU_BPM_V1";in.exposure_key="EXPTIME";in.max_loaded_pixels=1000;
    if(measuring){in.measure_pairs=1;in.pair_with_mad=1;in.max_pair_rows=4;
        for(int j=0;j<2;++j){in.raw_bias_map[j]=rbmap[j];in.raw_bias_reference[j]=rbref+j;}}
    int preparing=!strncmp(mode,"measure_prepare",15);detector_roi full[2];memcpy(full,rois,sizeof full);
    if(preparing){in.prepare_pairs=1;in.preparation_roi=full;in.preparation_rois=2;in.max_working_pixels=1000;}
    if(!strcmp(mode,"measure_prepare_limit"))in.max_working_pixels=1;
    if(!strcmp(mode,"measure_prepare_roi"))full[0].xmax=5;
    if(!strcmp(mode,"measure_limit"))in.max_loaded_pixels=120;
    if(!strcmp(mode,"measure_rows"))in.max_pair_rows=3;
    if(!strcmp(mode,"measure_alias"))rbref[1].asset_record_id=rbref[0].asset_record_id;
    if(!strcmp(mode,"hdu"))frames[0].reference.hdu_index=1;
    if(!strcmp(mode,"pair_id"))frames[0].pair_id="missing";
    if(!strcmp(mode,"registry"))in.mask_registry="OTHER";
    if(!strcmp(mode,"limit"))in.max_loaded_pixels=10;
    if(!strcmp(mode,"tolerant"))in.pair_time_tolerance=.02;
    mef_linearity_files_result *r=NULL,*occupied;fault f={0,0,0};mef_allocator a={&f,alloc,drop};
    mef_status status=mef_linearity_from_files(&in,&a,&r);
    if(strcmp(mode,"normal")&&strcmp(mode,"tolerant")&&strcmp(mode,"measure")&&strcmp(mode,"measure_prepare")){assert(status!=MEF_OK&&!r&&!f.live);goto cleanup;}
    assert(status==MEF_OK&&r);size_t allocations=f.calls;printf("Adapter/sample snapshot allocations: %zu\n",allocations);
    if(preparing){assert(r->prepared&&!r->pairs&&r->prepared->raw->rows==4);
        if(kind==1)assert(fabs(r->prepared->row[0].first.mean-610./3)<1e-12);
        /* Temporarily borrow the nested RAW view for unchanged RAW assertions. */
        r->pairs=r->prepared->raw;}
    if(measuring){assert(r->pairs&&r->pairs->rows==4&&r->pairs->rois==2&&r->pairs->pairs==2);
        assert(!strcmp(r->pairs->raw_bias_asset[0],"raw-bias:0")&&r->pairs->row[0].first==0&&r->pairs->row[0].second==3);
        assert(r->pairs->row[0].measurement.valid_pixels==(kind?3:4));
        assert(r->pairs->bias[0].ron_available&&r->pairs->bias[0].ron_adu>0);
        assert(fabs(r->pairs->bias[0].ron_adu-sqrt(2./3))<1e-9);
        /* Scan values are deliberately different between the two raw biases. */
        assert(fabs(r->pairs->bias[0].difference.mean-(kind?-1./3:0))<1e-9&&r->pairs->bias[0].raw_zone[0]==2);
        assert(strstr(r->raw_bias_path[0],"raw-bias-0.fits"));
    }else assert(!r->pairs);
    assert(r->samples->observations==(kind?14:22)&&r->samples->sites==(kind?4:6));
    assert(r->samples->frame[0].input_index==8&&r->samples->frame[1].input_index==3&&r->samples->frame[3].hdu==2);
    assert(!strcmp(r->samples->frame[2].pair_id,"P1")&&r->samples->frame[0].seconds==2);
    assert(r->samples->population[1].nonfinite==1&&r->samples->population[2].saturated==1);
    for(int i=0;i<r->samples->observations;++i){detector_joint_observation ob=r->samples->observation[i];
        detector_joint_site site=r->samples->site[ob.site];double expected=100*ob.seconds+(site.y-1)*4+site.x-1;
        /* Tolerant fixture changes time metadata only, not its synthetic payload. */
        if(!strcmp(mode,"tolerant")&&ob.input_index==3)expected-=1;
        assert(fabs(ob.signal-expected)<1e-4);}
    assert(r->samples->bpm_binary_supplied==(kind>=2)&&r->samples->noise_state==MEF_LINEARITY_NOISE_UNAVAILABLE);
    occupied=r;assert(mef_linearity_from_files(&in,NULL,&r)!=MEF_OK&&r==occupied);
    if(preparing)r->pairs=NULL;
    mef_linearity_files_destroy(r);r=NULL;assert(!f.live);
    if(kind==1&&(!strcmp(mode,"normal")||!strcmp(mode,"measure")||!strcmp(mode,"measure_prepare")))for(size_t i=1;i<=allocations;++i){f.calls=0;f.fail=i;
        assert(mef_linearity_from_files(&in,&a,&r)==MEF_ERR_MEMORY&&!r&&!f.live);}
    f.fail=0;assert(mef_linearity_from_files(&in,NULL,&r)==MEF_OK);
cleanup:
    for(int i=0;i<4;++i)mef_layout_map_destroy((mef_layout_map *)frames[i].map);
    for(int j=0;j<2;++j)mef_layout_map_destroy(rbmap[j]);
    mef_layout_map_destroy(bias);mef_layout_map_destroy(bpm);mef_config_destroy(config);memset(frames,0,sizeof frames);memset(rois,0,sizeof rois);
    if(r&&measuring)assert((preparing?r->prepared->raw:r->pairs)->row[0].measurement.valid_pixels==(kind?3:4)&&strstr(r->raw_bias_path[1],"raw-bias-1.fits"));
    if(r){assert(r->samples->frame[0].seconds==2&&strstr(r->input_paths[0],"flat-0.fits"));mef_linearity_files_destroy(r);}
    assert(!f.live);puts("PASS: explicit FITS admission, times/pairs, mask polarity, source ownership and atomic failures");return 0;
}
