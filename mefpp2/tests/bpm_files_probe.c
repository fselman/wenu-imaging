/* Synthetic bound-FITS acquisition adapter; no product writing. */
#include "mef_bpm_files.h"
#include "mefp_lib.h"
#include <assert.h>
#ifdef BPM_PUBLICATION_CONTRACT
#include "mef_bpm_publish.h"
#include <unistd.h>
#include <sys/stat.h>
static void integer_outputs(const char *directory) {
    qfits_header *h=qfits_header_default();
    int values[256],i;
    FILE *f;
    char path[4096];
    assert(h);
    qfits_header_add(h,"BITPIX","16",NULL,NULL); qfits_header_add(h,"NAXIS","2",NULL,NULL);
    qfits_header_add(h,"NAXIS1","4",NULL,NULL); qfits_header_add(h,"NAXIS2","1",NULL,NULL);
    values[0]=-32768; values[1]=-1; values[2]=0; values[3]=32767;
    snprintf(path,sizeof(path),"%s/integer-boundaries.fits",directory);
    f=fopen(path,"wbx"); assert(f);
    assert(intimage_write_hdu_checked(f,values,3,1,16,h)==-1 && ftell(f)==0);
    assert(intimage_write_hdu_checked(f,values,4,1,16,h)==0);
    assert(intimage_write_hdu_checked(f,values,4,1,16,h)==-1 && ftell(f)==5760);
    assert(fclose(f)==0);
    qfits_header_mod(h,"BITPIX","8",NULL); qfits_header_mod(h,"NAXIS1","256",NULL);
    for(i=0;i<256;++i) values[i]=i;
    snprintf(path,sizeof(path),"%s/integer-bytes.fits",directory);
    f=fopen(path,"wbx"); assert(f);
    values[0]=-1; assert(intimage_write_hdu_checked(f,values,256,1,8,h)==-1 && ftell(f)==0);
    values[0]=256; assert(intimage_write_hdu_checked(f,values,256,1,8,h)==-1 && ftell(f)==0);
    values[0]=0; assert(intimage_write_hdu_checked(f,values,256,1,8,h)==0); assert(fclose(f)==0);
#ifdef __linux__
    f=fopen("/dev/full","wb"); if(f) { assert(intimage_write_hdu_checked(f,values,256,1,8,h)==-1); fclose(f); }
#endif
    qfits_header_destroy(h);
}
static void publish_outputs(const mef_bpm_files_result *result,const char *directory,const char *raw,int kind) {
    mef_bpm_publish_options o;
    mef_error *error=NULL;
    char path[4096],other[4096];
    FILE *f;
    o.mode=MEF_BPM_PUBLISH_COMBINED;
    o.created_at="2026-11-02T19:00:00Z";
    o.source_revision=getenv("MEFPP_TEST_REVISION");
    if(!o.source_revision) o.source_revision="0000000000000000000000000000000000000000"; /* Synthetic identity only. */
    snprintf(path,sizeof(path),"%s/product.fits",directory);
    o.created_at="2026-02-30T19:00:00Z";
    assert(mef_bpm_publish(result,path,&o,&error)==MEF_ERR_INPUT && access(path,F_OK)!=0);
    mef_error_destroy(error); error=NULL; o.created_at="2026-11-02T19:00:00Z";
    if(kind>=3) {
        assert(mef_bpm_publish(result,path,&o,&error)==MEF_ERR_UNSUPPORTED && access(path,F_OK)!=0);
        mef_error_destroy(error); error=NULL; o.mode=MEF_BPM_PUBLISH_NEW;
    }
    assert(mef_bpm_publish(result,path,&o,&error)==MEF_OK && !error);
    assert(mef_bpm_publish(result,path,&o,&error)==MEF_ERR_IO);
    mef_error_destroy(error); error=NULL;
    snprintf(other,sizeof(other),"%s/protected-link.fits",directory); assert(symlink(raw,other)==0);
    assert(mef_bpm_publish(result,other,&o,&error)==MEF_ERR_IO); mef_error_destroy(error); error=NULL;
    snprintf(other,sizeof(other),"%s/protected-directory.fits",directory); assert(mkdir(other,0700)==0);
    assert(mef_bpm_publish(result,other,&o,&error)==MEF_ERR_IO); mef_error_destroy(error); error=NULL;
    snprintf(other,sizeof(other),"%s/missing-directory/product.fits",directory);
    assert(mef_bpm_publish(result,other,&o,&error)==MEF_ERR_IO); mef_error_destroy(error); error=NULL;
    snprintf(other,sizeof(other),"%s/handoff.json",directory); f=fopen(other,"wx"); assert(f);
    assert(mef_bpm_write_handoff(f,result,path,&o,NULL)==MEF_OK); assert(fclose(f)==0);
    snprintf(other,sizeof(other),"%s/configuration.json",directory); f=fopen(other,"wx"); assert(f);
    assert(mef_config_dump(mef_bpm_result_configuration(mef_bpm_files_result_service(result)),f)==MEF_OK);
    assert(fclose(f)==0); integer_outputs(directory);
}
#endif
static mef_layout_map *bind_file(const char *path,int hdu,int active,int mask,int wrong_readout) {
    mef_layout_options o;
    mef_detector_binding b;
    mef_layout *layout=NULL;
    mef_layout_map *map=NULL;
    memset(&o,0,sizeof(o)); o.max_hdus=4096; o.max_header_bytes=16*1024*1024;
    o.identity_key="DETID"; o.bin_x_key="XBINNING"; o.bin_y_key="YBINNING";
    memset(&b,0,sizeof(b)); b.detector_id="D"; b.expected_header_id="D";
    b.hdu_index=hdu; b.unit=mask?"mask":"ADU"; b.readout_id=wrong_readout?"other":"readout:test";
    b.bin_x=b.bin_y=1; b.configuration_detector=2;
    b.active_x=active?1:3; b.active_y=active?1:2; b.active_width=6; b.active_height=4;
    b.health=MEF_HEALTH_UNKNOWN; b.selection=MEF_OUTPUT_SELECTED;
    assert(mef_layout_read(path,&o,NULL,&layout,NULL)==MEF_OK);
    assert(mef_layout_bind(layout,&b,1,NULL,&map,NULL)==MEF_OK);
    mef_layout_destroy(layout); return map;
}
int main(int argc,char **argv) {
    mef_bb *bb;
    mef_layout_map *maps[12],*bias,*prior=NULL;
    mef_image_ref refs[12],cal[2];
    mef_calibration_role roles[2]={MEF_CAL_BIAS,MEF_CAL_BPM};
    mef_bpm_selection selection;
    mef_resolved_request_spec spec;
    mef_bpm_files_options o;
    mef_bpm_files_result *result=NULL;
    mef_context *context=NULL;
    mef_request *request=NULL;
    mef_config *config=NULL;
    mef_error *error=NULL;
    const char *detail=NULL;
    const mef_bpm_files_qc *qc;
    const mef_bpm_result *service;
    const detector_response_result *response;
    mef_status status;
    size_t pairs[12];
    char paths[12][4096],bias_path[4096],prior_path[4096];
    int rois[2][4]={{1,4,1,4},{3,6,1,4}};
    int i,count,kind,expected,mode;
    assert(argc==8); count=atoi(argv[3]); kind=atoi(argv[4]); expected=atoi(argv[5]); mode=atoi(argv[6]);
    assert(count>=2 && count<=12 && kind>=0 && kind<=4);
    bb=mef_bb_new_from_paf(argv[1]); assert(bb && bb->nchips>2);
    bb->bpm_proportional_flag=mode; bb->bpm_gainthr_lo=.5; bb->bpm_gainthr_hi=1.5;
    bb->use_prescan=bb->use_overscan=1; bb->scanrej[0]=bb->scanrej[1]=0;
    bb->ccd[2].prescan_x[0]=1; bb->ccd[2].prescan_x[1]=2;
    bb->ccd[2].overscan_x[0]=9; bb->ccd[2].overscan_x[1]=10;
    bb->ccd[2].trimreg[0]=3; bb->ccd[2].trimreg[1]=8;
    bb->ccd[2].trimreg[2]=2; bb->ccd[2].trimreg[3]=5;
    assert(mef_config_from_legacy(bb,NULL,&config,&detail)==MEF_OK); mef_bb_del(bb);
    memset(refs,0,sizeof(refs)); memset(cal,0,sizeof(cal)); memset(&spec,0,sizeof(spec));
    for(i=0;i<count;++i) {
        snprintf(paths[i],sizeof(paths[i]),"%s/flat-%d.fits",argv[2],i);
        maps[i]=bind_file(paths[i],i%2?2:0,0,0,0);
        refs[i].asset_record_id=paths[i]; refs[i].resolved_path=paths[i]; refs[i].detector_id="D";
        refs[i].hdu_index=i%2?2:0;
        pairs[i]=(size_t)i/2;
    }
    snprintf(bias_path,sizeof(bias_path),"%s/bias.fits",argv[2]);
    bias=bind_file(bias_path,0,1,0,!strcmp(argv[7],"readout"));
    cal[0].asset_record_id=bias_path; cal[0].resolved_path=bias_path; cal[0].detector_id="D";
    if(kind) {
        snprintf(prior_path,sizeof(prior_path),"%s/prior.fits",argv[2]);
        prior=bind_file(prior_path,0,kind==1 || kind==3,1,0);
        cal[1].asset_record_id=prior_path; cal[1].resolved_path=prior_path; cal[1].detector_id="D";
    }
    selection.detector_id="D"; selection.state=kind?MEF_BPM_SELECTED:MEF_BPM_OMITTED;
    spec.request.operation=MEF_OP_CAL_BPM; spec.request.operation_version=1;
    spec.request.inputs=refs; spec.request.input_count=(size_t)count;
    spec.request.calibrations=cal; spec.request.calibration_count=kind?2:1;
    spec.request.work_dir=argv[2]; spec.request.output_dir=argv[2]; spec.request.log_path="/synthetic/native.log";
    spec.calibration_roles=roles; spec.calibration_role_count=kind?2:1;
    spec.bpm_selections=&selection; spec.bpm_selection_count=1;
    assert(mef_request_create_resolved(&spec,NULL,&request,NULL)==MEF_OK);
    assert(mef_context_create(config,request,NULL,&context,NULL)==MEF_OK);
    mef_request_destroy(request); mef_config_destroy(config);
    memset(&o,0,sizeof(o)); o.mode=count==2?MEF_BPM_PROVISIONAL:MEF_BPM_QUICK;
    o.pair_ids=pairs; o.exposure_key="EXPTIME"; o.exposure_hdu=0;
    o.saturation_raw=1000; o.upper_fraction=.85; o.minimum_span_fraction=.15; o.maximum_pair_difference=.02;
    o.mask_encoding=!kind?MEF_BPM_MASK_OMITTED:kind<=2?MEF_BPM_MASK_FLAGS8:MEF_BPM_MASK_BINARY;
    o.prior_active_only=kind==1 || kind==3; o.binary_good_value=kind==4?1:0;
    o.mask_registry="WENU_BPM_V1"; o.reject_bits=255; o.with_mad=1;
    o.rois=(const int (*)[4])rois; o.roi_count=2;
    if(!strcmp(argv[7],"pair_ids")) pairs[0]=11;
    status=mef_bpm_from_files(context,(const mef_layout_map *const *)maps,(size_t)count,"D",bias,prior,&o,&result,&error);
    if(expected) {
        if(status!=MEF_OK) fprintf(stderr,"status=%d message=%s\n",status,error?mef_error_message(error):"none");
        assert(status==MEF_OK && result && !error);
        qc=mef_bpm_files_result_qc(result); service=mef_bpm_files_result_service(result);
        response=mef_bpm_result_response(service);
        assert(qc->span_fraction>=.15 && qc->input_count==(size_t)count);
        assert(qc->distinct_levels>=(size_t)(count==2?2:5));
        assert(count==2 || (qc->usable_pairs==5 && qc->distinct_times==5));
        assert(response->reasons[0]==4 && response->reasons[23]==8);
        if(count>=10) {
            assert(mef_bpm_result_qc(service)->frames[4].saturated==1);
            assert(mef_bpm_result_qc(service)->frames[8].margin_excluded==1);
            assert(response->sample_count[23]==6);
        }
        if(kind==1 || kind==2) assert(mef_bpm_result_combined_flags(service)[0]==5 && mef_bpm_result_combined_flags(service)[23]==136);
        if(kind>=3) assert(!mef_bpm_result_combined_flags(service));
        if(count==12) {
            assert(response->plane_count==10 && !mef_bpm_result_qc(service)->frames[10].included_in_fit);
            /* The deliberately low-response pixel remains unsaturated but is
             * excluded by the prior: all reference samples are unavailable. */
            assert(mef_bpm_result_qc(service)->frames[10].saturated==23);
            assert(mef_bpm_result_qc(service)->frames[10].reference_samples==0);
        }
    } else assert(status!=MEF_OK && !result && error && mef_error_status(error)==status);
    mef_error_destroy(error); mef_context_destroy(context);
    for(i=0;i<count;++i) mef_layout_map_destroy(maps[i]);
    mef_layout_map_destroy(bias); mef_layout_map_destroy(prior);
    memset(pairs,0,sizeof(pairs)); memset(rois,0,sizeof(rois));
#ifdef BPM_PUBLICATION_CONTRACT
    if(result) publish_outputs(result,argv[2],paths[0],kind);
#endif
    if(result) { assert(mef_bpm_files_result_qc(result)->rois[0][0]==1); mef_bpm_files_result_destroy(result); }
    puts("PASS: bound file acquisition, signal coverage, priors and detached ownership");
    return 0;
}
