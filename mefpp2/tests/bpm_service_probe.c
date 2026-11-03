/* Purpose: generated raw flats/master/prior mask, typed operation lifecycle,
 * exact legacy fitting and independent corrected-signal/reason answers.
 * No files reduced, no publication, no acquisition/scientific acceptance. */
#include "mef_cal_bpm.h"
#include "mefp_lib.h"
#include <assert.h>

typedef struct { size_t calls, fail, owners; } allocations;
static void *allocate(void *u,size_t n) {
    allocations *s=u;
    void *p;
    ++s->calls;
    if (s->fail && s->calls>=s->fail) return NULL;
    p=(malloc)(n); if (p) ++s->owners; return p;
}
static void release(void *u,void *p) {
    allocations *s=u;
    assert(p && s->owners); --s->owners; (free)(p);
}
static mef_context *context_for(mef_bb *bb, int prior, int wrong_operation,
    const mef_allocator *a) {
    mef_resolved_request_spec spec;
    mef_image_ref refs[5], cal[2];
    mef_calibration_role roles[2]={MEF_CAL_BIAS,MEF_CAL_BPM};
    mef_bpm_selection selection;
    mef_config *config=NULL;
    mef_request *request=NULL;
    mef_context *context=NULL;
    char paths[5][80], ids[5][40];
    const char *detail=NULL;
    int i;
    memset(&spec,0,sizeof(spec)); memset(refs,0,sizeof(refs));
    for (i=0;i<5;++i) {
        sprintf(paths[i],"/synthetic bpm/flat-%d.fits",i);
        sprintf(ids[i],"flat:%d",i);
        refs[i].resolved_path=paths[i]; refs[i].asset_record_id=ids[i];
        refs[i].detector_id="detector:explicit";
        refs[i].hdu_index=i%2?0:2;
    }
    cal[0]=refs[0]; cal[0].asset_record_id="bias:selected";
    cal[0].resolved_path="/synthetic bpm/master-bias.fits";
    cal[1]=cal[0]; cal[1].asset_record_id="bpm:selected";
    cal[1].resolved_path="/synthetic bpm/prior.fits";
    selection.detector_id="detector:explicit";
    selection.state=prior?MEF_BPM_SELECTED:MEF_BPM_OMITTED;
    spec.request.operation=wrong_operation?MEF_OP_CAL_BIAS:MEF_OP_CAL_BPM;
    spec.request.operation_version=1; spec.request.inputs=refs; spec.request.input_count=5;
    spec.request.calibrations=cal; spec.request.calibration_count=prior?2:1;
    spec.request.work_dir="/synthetic bpm/work"; spec.request.output_dir="/synthetic bpm/output";
    spec.request.log_path="/synthetic bpm/native.log";
    spec.calibration_roles=roles; spec.calibration_role_count=prior?2:1;
    spec.bpm_selections=&selection; spec.bpm_selection_count=1;
    assert(mef_config_from_legacy(bb,NULL,&config,&detail)==MEF_OK);
    assert(mef_request_create_resolved(&spec,NULL,&request,NULL)==MEF_OK);
    assert(mef_context_create(config,request,a,&context,NULL)==MEF_OK);
    mef_request_destroy(request); mef_config_destroy(config); return context;
}
static void controls(mef_bb *bb, int proportional, int scan_mode) {
    image_t *frames[5], *bias=image_new(6,4);
    const image_t *borrowed[5];
    pixelvalue saved[5][60], saved_bias[24];
    unsigned char prior[24], prior_saved[24];
    pixelmap *binary=pixelmap_new(6,4), *samples[5];
    mef_context *context;
    mef_bpm_input input;
    mef_bpm_options options;
    mef_bpm_result *r=NULL, *alias;
    const detector_response_result *response;
    const mef_bpm_qc *qc;
    mef_error *error=NULL;
    int rois[2][4]={{1,4,1,4},{3,6,1,4}};
    int i,x,y,p,mode,slot=2;
    allocations state;
    mef_allocator allocator;
    size_t base,calls,k;
    assert(bias && binary && bb->nchips>slot);
    bb->bpm_proportional_flag=proportional; bb->bpm_gainthr_lo=.5; bb->bpm_gainthr_hi=1.5;
    bb->use_prescan=scan_mode==0 || scan_mode==1;
    bb->use_overscan=scan_mode==0 || scan_mode==2;
    bb->scanrej[0]=bb->scanrej[1]=0;
    bb->ccd[slot].prescan_x[0]=1; bb->ccd[slot].prescan_x[1]=2;
    bb->ccd[slot].overscan_x[0]=9; bb->ccd[slot].overscan_x[1]=10;
    bb->ccd[slot].trimreg[0]=3; bb->ccd[slot].trimreg[1]=8;
    bb->ccd[slot].trimreg[2]=2; bb->ccd[slot].trimreg[3]=5;
    memset(prior,0,sizeof(prior)); prior[0]=1; prior[23]=128;
    memcpy(prior_saved,prior,sizeof(prior)); binary->data[0]=binary->data[23]=0;
    for (p=0;p<24;++p) bias->data[p]=(pixelvalue)(5+p*.5);
    memcpy(saved_bias,bias->data,sizeof(saved_bias));
    for (i=0;i<5;++i) {
        frames[i]=image_new(10,6); samples[i]=pixelmap_new(6,4);
        assert(frames[i] && samples[i]); borrowed[i]=frames[i];
        for (y=0;y<6;++y) for (x=0;x<10;++x) {
            double pedestal=scan_mode==3?0:100+y+3*i;
            frames[i]->data[10*y+x]=(pixelvalue)pedestal;
            if (x>=2 && x<=7 && y>=1 && y<=4) {
                p=(y-1)*6+x-2;
                frames[i]->data[10*y+x]+=(pixelvalue)(bias->data[p]+(i+1)*16*(p==0?.25:p==23?2:1));
            }
        }
        memcpy(saved[i],frames[i]->data,sizeof(saved[i]));
    }
    input.frames=borrowed; input.count=5; input.configuration_detector=(size_t)slot; input.master_bias=bias;
    memset(&options,0,sizeof(options)); options.reject_bits=255; options.with_mad=1;
    options.rois=(const int (*)[4])rois; options.roi_count=2;
    /* Both prior encodings filter reference only, not all-pixel defect fitting.
     * Bit priors preserve individual reasons; binary priors invent no reason. */
    for (mode=0;mode<3;++mode) {
        context=context_for(bb,mode!=0,0,NULL);
        options.prior_flags=mode==1?prior:NULL; options.prior_count=mode==1?24:0;
        options.prior_binary=mode==2?binary:NULL;
        bb->bpm_gainthr_lo=-99; bb->bpm_gainthr_hi=99; /* Snapshot remains authoritative. */
        assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_OK);
        bb->bpm_gainthr_lo=.5; bb->bpm_gainthr_hi=1.5;
        response=mef_bpm_result_response(r); qc=mef_bpm_result_qc(r);
        assert(qc->provisional_numerical_only && qc->bias_applied && qc->input_count==5);
        assert(qc->prior==(mode==0?MEF_BPM_PRIOR_OMITTED:mode==1?MEF_BPM_PRIOR_FLAGS8:MEF_BPM_PRIOR_BINARY));
        assert(response->reasons[0]==4 && response->reasons[23]==8);
        if (mode) { assert(response->normalized->data[0]==.25 && response->normalized->data[23]==2); }
        assert(response->sample_count[0]==5 && response->sample_count[23]==5);
        assert(!mef_bpm_result_selection(r)->data[0] && !mef_bpm_result_selection(r)->data[23]);
        if (mode==1) {
            assert(mef_bpm_result_combined_flags(r)[0]==5 && mef_bpm_result_combined_flags(r)[23]==136);
            assert(!memcmp(mef_bpm_result_prior_flags(r),prior,24));
        } else if (mode==2) assert(!mef_bpm_result_combined_flags(r) && !mef_bpm_result_prior_flags(r));
        for (i=0;i<5;++i) {
            assert(qc->frames[i].prescan.bpm_excluded==0 && qc->frames[i].overscan.bpm_excluded==0);
            assert(qc->frames[i].prescan.level_available==bb->use_prescan);
            assert(qc->frames[i].overscan.level_available==bb->use_overscan);
            assert(qc->frames[i].active_corrected.valid_pixels==(mode?22:24));
        }
        alias=r; assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && r==alias);
        mef_context_destroy(context);
        assert(mef_request_view(mef_bpm_result_request(r))->operation==MEF_OP_CAL_BPM);
        assert(response->reasons[23]==8); mef_bpm_result_destroy(r); r=NULL;
    }
    /* Samples with no usable fit never become selected, even with reject_bits=0. */
    context=context_for(bb,1,0,NULL);
    options.prior_binary=NULL; options.prior_flags=prior; options.prior_count=24;
    options.reject_bits=0; options.samples=(const pixelmap *const *)samples;
    for (i=0;i<5;++i) samples[i]->data[3]=0;
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_OK);
    assert(!mef_bpm_result_selection(r)->data[3]);
    assert(mef_bpm_result_selection(r)->data[0] && mef_bpm_result_combined_flags(r)[0]==5);
    mef_bpm_result_destroy(r); r=NULL;
    options.samples=NULL; options.reject_bits=255;
    /* Preflight mismatch, malformed geometry/mask and wrong operation fail with
     * no pending result and without modifying caller pixels. */
    options.prior_count=23;
    assert(mef_cal_bpm(context,&input,&options,&r,&error)==MEF_ERR_INPUT && !r);
    assert(mef_error_status(error)==MEF_ERR_INPUT); mef_error_destroy(error); error=NULL; options.prior_count=24;
    options.prior_flags=NULL; options.prior_count=0;
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && !r);
    options.prior_flags=prior; options.prior_count=24;
    memset(prior,255,sizeof(prior));
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_COMPUTATION && !r);
    memcpy(prior,prior_saved,sizeof(prior));
    options.samples=(const pixelmap *const *)samples;
    memset(samples[0]->data,0,24);
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_OK);
    assert(!mef_bpm_result_qc(r)->frames[0].included_in_fit);
    assert(mef_bpm_result_response(r)->plane_count==4 && mef_bpm_result_fit_indices(r)[0]==1);
    mef_bpm_result_destroy(r); r=NULL;
    memset(samples[0]->data,1,24); options.samples=NULL;
    input.configuration_detector=(size_t)bb->nchips;
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_CONFIG && !r);
    input.configuration_detector=(size_t)slot;
    bias->lx=5; assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && !r); bias->lx=6;
    rois[0][0]=0; assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && !r); rois[0][0]=1;
    if (bb->use_prescan || bb->use_overscan) {
        p=bb->use_prescan?0:8; frames[0]->data[p]=NAN;
        assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && !r);
        frames[0]->data[p]=saved[0][p];
    }
    mef_context_destroy(context); context=context_for(bb,1,1,NULL);
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_ERR_INPUT && !r); mef_context_destroy(context);
    /* Persistent service-allocator failures at every observed allocation must
     * release pending request/QC/flags owners; dependency allocator not injected. */
    memset(&state,0,sizeof(state)); allocator.user=&state; allocator.allocate=allocate; allocator.release=release;
    context=context_for(bb,1,0,&allocator); base=state.owners; state.calls=0;
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_OK);
    calls=state.calls; mef_bpm_result_destroy(r); r=NULL; assert(state.owners==base);
    for (k=1;k<=calls;++k) {
        state.calls=0; state.fail=k;
        assert(mef_cal_bpm(context,&input,&options,&r,&error)==MEF_ERR_MEMORY && !r && !error);
        assert(state.owners==base);
    }
    state.fail=0; mef_context_destroy(context); assert(state.owners==0);
    /* Returned data survive destruction of every input/calibration/context. */
    context=context_for(bb,1,0,NULL);
    assert(mef_cal_bpm(context,&input,&options,&r,NULL)==MEF_OK);
    mef_context_destroy(context);
    for (i=0;i<5;++i) {
        assert(!memcmp(saved[i],frames[i]->data,sizeof(saved[i]))); image_del(frames[i]); pixelmap_del(samples[i]);
    }
    assert(!memcmp(saved_bias,bias->data,sizeof(saved_bias)) && !memcmp(prior_saved,prior,24));
    image_del(bias); pixelmap_del(binary);
    memset(prior,0,sizeof(prior));
    assert(mef_bpm_result_response(r)->normalized->data[23]==2);
    assert(mef_bpm_result_prior_flags(r)[23]==128 && mef_bpm_result_combined_flags(r)[0]==5);
    assert(mef_bpm_result_qc(r)->frames[0].active_corrected.valid_pixels==22);
    mef_bpm_result_destroy(r);
    printf("PASS: typed BPM mode=%d scans=%d, known response/flags, coverage, ownership and failures\n",proportional,scan_mode);
}
int main(int argc,char **argv) {
    mef_bb *bb;
    int mode,scans;
    assert(argc==2); bb=mef_bb_new_from_paf(argv[1]); assert(bb);
    for (mode=0;mode<2;++mode) for (scans=0;scans<4;++scans) controls(bb,mode,scans);
    assert(mef_cal_bpm(NULL,NULL,NULL,NULL,NULL)==MEF_ERR_INPUT);
    mef_bb_del(bb); return 0;
}
