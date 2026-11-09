/* Actual in-memory bias operation and QC copying; no ASDF writer substituted. */
#include "mef_bias_product_qc.h"
#include "mef_bias_qc_fits.h"
#include <math.h>
#include <float.h>
#include "optional_cleanup_probe.c"
#include "mefp_lib.h"
#include <assert.h>
#include <unistd.h>
#include "bias_header_provenance_probe.inc"
#include "bias_clipping_probe.inc"
#include "bias_median_even_probe.inc"
static const char *dump_directory;
static int clipping_profile, reason_profile, average_profile;
static const mef_qc_measurement *find(const mef_qc_measurement *q,size_t n,const char *name)
{
    size_t i; for(i=0;i<n;++i) if(!strcmp(q[i].name,name)) return q+i;
    assert(0); return NULL;
}
static void profile(const char *paf,int masked,int mad,int pair)
{
    const char *paths[4]={"/synthetic/raw0.fits","/synthetic/raw1.fits","/synthetic/raw2.fits","/synthetic/raw3.fits"};
    const char *ids[2]={"CCD-A","CCD-B"}, *diagnostic=NULL;
    mef_product_paths output; mef_bb *bb=mef_bb_new_from_paf((char *)paf);
    mef_config *config=NULL; mef_bias_product_qc *archive;
    mef_bias_settings settings; size_t d,i; int x,y;
    double expected_master[2],expected_raw[2][4]; char message[512];
    assert(bb!=NULL); bb->bias_median_even_handling=average_profile?MEDIAN_EVEN_AVERAGE:MEDIAN_EVEN_LOWER; bb->bias_minframe=3; bb->bias_kappa1=10;
    bb->use_prescan=0; bb->use_overscan=1; bb->scanrej[0]=bb->scanrej[1]=0;
    for(i=0;i<2;++i) {
        bb->ccd[i].prescan_x[0]=bb->ccd[i].prescan_x[1]=1;
        bb->ccd[i].overscan_x[0]=4; bb->ccd[i].overscan_x[1]=6;
        bb->ccd[i].trimreg[0]=1; bb->ccd[i].trimreg[1]=3;
        bb->ccd[i].trimreg[2]=1; bb->ccd[i].trimreg[3]=4;
    }
    assert(mef_config_from_legacy(bb,NULL,&config,&diagnostic)==MEF_OK);
    if (reason_profile) {
        mef_processing_policy policy;
        policy=*mef_config_processing(config);policy.bpm.supplied=1;
        policy.bpm.encoding=MEF_BPM_REASON8;policy.bpm.bad_when_nonzero=1;policy.bpm.reject_bits=255;
        strcpy(policy.bpm.registry,"WENU_BPM_V1");mef_config_initialize_processing(config,&policy);
    }
    memset(&output,0,sizeof(output)); strcpy(output.fits,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.fits");
    strcpy(output.asdf,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.asdf");
    strcpy(output.log,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.log");
    if(metadata_directory) {
        snprintf(output.fits,sizeof(output.fits),"%s/headers-%lu.fits",metadata_directory,(unsigned long)profile_detector_count);
        snprintf(output.asdf,sizeof(output.asdf),"%s/headers-%lu.asdf",metadata_directory,(unsigned long)profile_detector_count);
        snprintf(output.log,sizeof(output.log),"%s/headers-%lu.log",metadata_directory,(unsigned long)profile_detector_count);
    }
    archive=mef_bias_product_qc_new(config,&output,"2026-11-06T16:00:00.123Z",MEFPP_CANDIDATE_REVISION,paths,4,profile_detector_count);
    assert(archive!=NULL);
    for(d=0;d<profile_detector_count;++d) {
        image_t *frames[4]; const image_t *borrowed[4]; pixelvalue saved[4][24];
        mef_image_ref refs[4],calibration; mef_bpm_selection bpm;
        mef_calibration_role role=MEF_CAL_BPM; mef_resolved_request_spec spec;
        mef_request *request=NULL; mef_context *context=NULL; mef_bias_result *result=NULL;
        mef_bias_input input; mef_bias_measurement_options options;
        const mef_bias_measurements *m; const mef_bias_qc *legacy;
        const mef_product_qc *view; pixelmap *mask=NULL;
        memset(&spec,0,sizeof(spec)); memset(refs,0,sizeof(refs)); memset(&calibration,0,sizeof(calibration));
        memset(&options,0,sizeof(options));
        for(i=0;i<4;++i) {
            frames[i]=image_new(6,4); assert(frames[i]!=NULL); borrowed[i]=frames[i];
            for(y=0;y<4;++y) for(x=0;x<6;++x)
                frames[i]->data[y*6+x]=(pixelvalue)(100+y+i+(x<3?10+3*d+x*(i+1):0));
            memcpy(saved[i],frames[i]->data,sizeof(saved[i]));
            refs[i].asset_record_id=paths[i]; refs[i].resolved_path=paths[i];
            refs[i].detector_id=ids[d]; refs[i].hdu_index=(int)d+1;
        }
        spec.request.operation=MEF_OP_CAL_BIAS; spec.request.operation_version=1;
        spec.request.inputs=refs; spec.request.input_count=4;
        spec.request.work_dir="/synthetic/work"; spec.request.output_dir="/synthetic/products";
        spec.request.log_path=output.log; bpm.detector_id=ids[d];
        bpm.state=masked?MEF_BPM_SELECTED:MEF_BPM_OMITTED;
        spec.bpm_selections=&bpm; spec.bpm_selection_count=1;
        if(masked) {
            mask=pixelmap_new(6,4); assert(mask!=NULL);
            for(i=0;i<24;++i) mask->data[i]=1;
            mask->data[0]=0; pixelmap_updatecount(mask);
            calibration.asset_record_id="bpm"; calibration.resolved_path="/synthetic/bpm.fits";
            calibration.detector_id=ids[d]; calibration.hdu_index=(int)d+1;
            spec.request.calibrations=&calibration; spec.request.calibration_count=1;
            spec.calibration_roles=&role; spec.calibration_role_count=1;
        }
        assert(mef_request_create_resolved(&spec,NULL,&request,NULL)==MEF_OK);
        assert(mef_context_create(config,request,NULL,&context,NULL)==MEF_OK);
        input.frames=borrowed; input.count=4; input.configuration_detector=d;
        options.bpm=mask; options.with_mad=mad; options.high_sigma=5;
        options.ron_pair_set=pair; options.ron_first=0; options.ron_second=3;
        if (clipping_profile) {
            options.ron_clip_enabled=1;options.ron_clip.sigma_low=5;options.ron_clip.sigma_high=5;
            options.ron_clip.max_iterations=clipping_profile==2?1:10;
            if(clipping_profile==2)options.ron_clip.sigma_low=options.ron_clip.sigma_high=1;
        }
        assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_OK);
        assert(mef_config_bias_settings(config,d,&settings)==MEF_OK);
        m=mef_bias_result_measurements(result); legacy=mef_bias_result_qc(result);
        if (d == 0) {
            mef_bias_measurement_options minimal_options = options;
            mef_bias_result *minimal = NULL;
            mef_bias_product_qc *minimal_archive;
            const mef_product_qc *minimal_view;
            const mef_qc_measurement *measurement;
            qfits_header *minimal_header = NULL;
            minimal_options.legacy_qc = 1;
            minimal_options.with_mad = 0;
            minimal_options.ron_pair_set = 0;
            minimal_options.ron_clip_enabled = 0;
            assert(mef_cal_bias_measurements(context, &input, &minimal_options,
                &minimal, NULL) == MEF_OK);
            minimal_archive = mef_bias_product_qc_new(config, &output,
                "2026-11-06T16:00:00.123Z", MEFPP_CANDIDATE_REVISION, paths, 4, 1);
            assert(minimal_archive != NULL);
            assert(mef_bias_product_qc_add(minimal_archive, 0, ids[d], "L",
                "synthetic", d, 1, 1, minimal, &minimal_options, &settings, 4,
                masked ? "/synthetic/bpm.fits" : NULL, (int)d+1, 1));
            assert(!mef_bias_product_qc_check(minimal_archive, message, sizeof(message)));
            minimal_view = mef_bias_product_qc_view(minimal_archive);
            assert(!strcmp(minimal_view->qc_profile, "legacy"));
            measurement = find(minimal_view->detectors[0].measurements,
                minimal_view->detectors[0].measurement_count, "master.mean");
            assert(measurement->state == MEF_QC_UNAVAILABLE);
            assert(!strcmp(measurement->reason, "disabled_by_legacy_qc"));
            measurement = find(minimal_view->detectors[0].measurements,
                minimal_view->detectors[0].measurement_count, "legacy.product_median");
            assert(measurement->state == MEF_QC_MEASURED);
            assert(measurement->values[0] == legacy->product_median);
            assert(!mef_bias_qc_fits_header(minimal_view, 0, &minimal_header,
                message, sizeof(message)));
            assert(qfits_header_getstr(minimal_header, "HIERARCH ESO MPP QC PROFILE") != NULL);
            qfits_header_destroy(minimal_header);
            mef_bias_product_qc_destroy(minimal_archive);
            mef_bias_result_destroy(minimal);
        }
        {
            const image_t *signal=mef_bias_result_signal(result);
            for(int row=0;row<4;++row)for(int col=0;col<3;++col)
                assert(signal->data[row*3+col]==(pixelvalue)(10+3*d+col*(average_profile?2.5:2.0)));
            assert(legacy->median_even_handling==(average_profile?MEDIAN_EVEN_AVERAGE:MEDIAN_EVEN_LOWER));
        }
        if(clipping_profile) {
            if(clipping_profile==2)assert(!m->clipped_difference.converged && !m->ron_clipped_available);
            else assert(m->clipped_difference.converged && m->ron_clipped_available);
            assert(m->ron_clipped_adu==m->clipped_difference.sample.stdev/sqrt(2.0));
        }
        expected_master[d]=m->master.mean;
        assert(mef_bias_product_qc_add(archive,d,ids[d],"explicit-amplifier","synthetic-readout",d,1,1,
            result,&options,&settings,4,masked?"/synthetic/bpm.fits":NULL,(int)d+1,1));
        view=mef_bias_product_qc_view(archive);
        {
            qfits_header *header=NULL;
            int code=mef_bias_qc_fits_header(view,d,&header,message,sizeof(message));
            if(code) fprintf(stderr,"%s\n",message);
            assert(code==0 && header!=NULL);
            assert(atof(qfits_header_getstr(header,"HIERARCH ESO MPP QC MAST MEAN"))==m->master.mean);
            if(mad) assert(atof(qfits_header_getstr(header,"HIERARCH ESO MPP QC HOT N"))==m->high_offset_count);
            assert((qfits_header_getstr(header,"HIERARCH ESO MPP QC RON STD")!=NULL)==(m->ron_stdev_available!=0));
            if(dump_directory) {
                char path[4096]; FILE *stream;
                snprintf(path,sizeof(path),"%s/profile-%d%d%d-%lu.hdr",dump_directory,masked,mad,pair,(unsigned long)d);
                stream=fopen(path,"wx"); assert(stream);
                qfits_header_append(header,"END",NULL,NULL,NULL);
                assert(qfits_header_dump(header,stream)==0); assert(fclose(stream)==0);
            }
            qfits_header_destroy(header); header=NULL;
            /* Long/quoted identifiers must fail safely instead of truncating. */
            mef_qc_detector_record copy=view->detectors[d];
            mef_product_qc changed=*view;
            char long_id[128]; memset(long_id,'X',sizeof(long_id)-1); long_id[sizeof(long_id)-1]=0;
            copy.readout_id=long_id; changed.detectors=&copy; changed.detector_count=1;
            assert(mef_bias_qc_fits_header(&changed,0,&header,message,sizeof(message))!=0 && header==NULL);
            /* Metadata must not accept a measured NaN or invent availability. */
            size_t count=copy.measurement_count;
            mef_qc_measurement *bad=malloc(count*sizeof(*bad)); assert(bad);
            memcpy(bad,copy.measurements,count*sizeof(*bad)); copy.measurements=bad;
            copy.readout_id="synthetic-readout";
            double invalid=NAN; bad[0].values=&invalid;
            assert(mef_bias_qc_fits_header(&changed,0,&header,message,sizeof(message))!=0 && header==NULL);
            /* Finite extremes and signed zero must round-trip without a
             * lowercase exponent or accidental integer conversion. */
            const double values[]={DBL_MIN,DBL_MAX,-0.0,0x1.0000000000001p0};
            for(size_t k=0;k<sizeof(values)/sizeof(values[0]);++k) {
                bad[0].values=values+k;
                assert(mef_bias_qc_fits_header(&changed,0,&header,message,sizeof(message))==0);
                const char *number=qfits_header_getstr(header,"HIERARCH ESO MPP QC MAST MEAN");
                double actual=strtod(number,NULL);
                assert(actual==values[k] && !strchr(number,'e'));
                if(values[k]==0) assert(signbit(actual)==signbit(values[k]));
                qfits_header_destroy(header); header=NULL;
            }
            free(bad);
        }
        if(pair) assert(*find(view->detectors[d].measurements,view->detectors[d].measurement_count,"read_noise")->values==m->ron_stdev_adu);
        else assert(find(view->detectors[d].measurements,view->detectors[d].measurement_count,"read_noise")->values==NULL);
        for(i=0;i<4;++i) {
            const mef_qc_input_binding *b=view->detectors[d].inputs+i;
            expected_raw[d][i]=m->frames[i].active_raw.mean;
            assert(b->accepted==legacy->accepted[i] && b->source_hdu==(int)d+1);
            assert(*find(b->measurements,b->measurement_count,"scan_correction.median")->values==legacy->scan_median[i]);
            assert(memcmp(saved[i],frames[i]->data,sizeof(saved[i]))==0);
        }
        mef_bias_result_destroy(result); mef_context_destroy(context); mef_request_destroy(request);
        for(i=0;i<4;++i) image_del(frames[i]);
        pixelmap_del(mask);
    }
    assert(mef_bias_product_qc_check(archive,message,sizeof(message))==0);
    for(d=0;d<profile_detector_count;++d) {
        const mef_qc_detector_record *q=mef_bias_product_qc_view(archive)->detectors+d;
        assert(*find(q->measurements,q->measurement_count,"master.mean")->values==expected_master[d]);
        for(i=0;i<4;++i) assert(*find(q->inputs[i].measurements,q->inputs[i].measurement_count,"raw_active.mean")->values==expected_raw[d][i]);
    }
    assert(mef_bias_product_qc_view(archive)->calibration_count==(size_t)(masked?1:0));
    if(masked) assert(mef_bias_product_qc_view(archive)->calibrations[0].binding_count==profile_detector_count);
    if(metadata_directory)selected_header_contract(archive,&output);
    mef_bias_product_qc_destroy(archive); mef_config_destroy(config); mef_bb_del(bb);
}
int main(int argc,char **argv)
{
    if(argc==2 && !strcmp(argv[1],"median-even")) {
        eclipse_init();set_logfile(0);median_even_contract();median_even_benchmark();return 0;
    }
    if(argc==4 && !strcmp(argv[1],"median-average-profile")) {
        eclipse_init();set_logfile(0);average_profile=1;dump_directory=argv[3];
        profile(argv[2],1,1,1);puts("PASS: actual average-mode bias pixels and typed FITS mode provenance");return 0;
    }
    if(argc==3 && !strcmp(argv[1],"mask-policy")) {
        eclipse_init();set_logfile(0);mask_policy_contract(argv[2]);return 0;
    }
    if(argc==4 && (!strcmp(argv[1],"clipped-profile") || !strcmp(argv[1],"reason-profile") || !strcmp(argv[1],"clipped-limit"))) {
        reason_profile=!strcmp(argv[1],"reason-profile");
        eclipse_init();set_logfile(0);clipping_profile=!strcmp(argv[1],"clipped-limit")?2:1;dump_directory=argv[3];
        profile(argv[2],1,1,1);puts("PASS: actual bias kernel and additive clipped FITS mapping");return 0;
    }
    if(argc==2 && !strcmp(argv[1],"clipping")) {
        eclipse_init();set_logfile(0);clipping_contract();clipping_benchmark();return 0;
    }
    if(argc==4 && !strcmp(argv[1],"headers")) {
        metadata_directory=argv[3];eclipse_init();set_logfile(0);
        profile_detector_count=1;profile(argv[2],0,1,1);
        profile_detector_count=2;profile(argv[2],1,1,1);
        puts("PASS: actual one/two-detector QC and selected final FITS provenance");return 0;
    }
    if(argc==3 && !strcmp(argv[1],"cleanup")) { optional_cleanup_contract(argv[2]); return 0; }
#ifndef MEF_QC_IN_MEMORY_ONLY
    if(argc==10 && !strcmp(argv[1],"recover-verified")) {
        mef_qc_recovery r={argv[2],argv[3],argv[4],argv[5],argv[6],argv[7],argv[8],argv[9]};
        char message[512]; int code=mef_product_qc_recover_verified(&r,message,sizeof(message));
        puts(message); return code?1:0;
    }
#endif
    if(argc!=2 && argc!=3) return 2;
    if(argc==3) dump_directory=argv[2];
    eclipse_init(); set_logfile(0);
    profile(argv[1],0,1,1); profile(argv[1],1,1,1); profile(argv[1],0,0,1); profile(argv[1],1,0,0);
    puts("PASS: four actual bias QC copying/lifetime profiles, explicit BPM/MAD/RON choices");
    return 0;
}
