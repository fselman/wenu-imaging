/* Actual in-memory bias operation and QC copying; no ASDF writer substituted. */
#include "mef_bias_product_qc.h"
#include "mefp_lib.h"
#include <assert.h>
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
    assert(bb!=NULL); bb->bias_minframe=3; bb->bias_kappa1=10;
    bb->use_prescan=0; bb->use_overscan=1; bb->scanrej[0]=bb->scanrej[1]=0;
    for(i=0;i<2;++i) {
        bb->ccd[i].prescan_x[0]=bb->ccd[i].prescan_x[1]=1;
        bb->ccd[i].overscan_x[0]=4; bb->ccd[i].overscan_x[1]=6;
        bb->ccd[i].trimreg[0]=1; bb->ccd[i].trimreg[1]=3;
        bb->ccd[i].trimreg[2]=1; bb->ccd[i].trimreg[3]=4;
    }
    assert(mef_config_from_legacy(bb,NULL,&config,&diagnostic)==MEF_OK);
    memset(&output,0,sizeof(output)); strcpy(output.fits,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.fits");
    strcpy(output.asdf,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.asdf");
    strcpy(output.log,"/synthetic/products/CMDP.2026-11-06T16:00:00.123Z.001.log");
    archive=mef_bias_product_qc_new(config,&output,"2026-11-06T16:00:00.123Z",MEFPP_CANDIDATE_REVISION,paths,4,2);
    assert(archive!=NULL);
    for(d=0;d<2;++d) {
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
        assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_OK);
        assert(mef_config_bias_settings(config,d,&settings)==MEF_OK);
        m=mef_bias_result_measurements(result); legacy=mef_bias_result_qc(result);
        expected_master[d]=m->master.mean;
        assert(mef_bias_product_qc_add(archive,d,ids[d],"explicit-amplifier","synthetic-readout",d,1,1,
            result,&options,&settings,4,masked?"/synthetic/bpm.fits":NULL,(int)d+1,1));
        view=mef_bias_product_qc_view(archive);
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
    for(d=0;d<2;++d) {
        const mef_qc_detector_record *q=mef_bias_product_qc_view(archive)->detectors+d;
        assert(*find(q->measurements,q->measurement_count,"master.mean")->values==expected_master[d]);
        for(i=0;i<4;++i) assert(*find(q->inputs[i].measurements,q->inputs[i].measurement_count,"raw_active.mean")->values==expected_raw[d][i]);
    }
    assert(mef_bias_product_qc_view(archive)->calibration_count==(size_t)(masked?1:0));
    if(masked) assert(mef_bias_product_qc_view(archive)->calibrations[0].binding_count==2);
    mef_bias_product_qc_destroy(archive); mef_config_destroy(config); mef_bb_del(bb);
}
int main(int argc,char **argv)
{
    if(argc!=2) return 2;
    eclipse_init(); set_logfile(0);
    profile(argv[1],0,1,1); profile(argv[1],1,1,1); profile(argv[1],0,0,1); profile(argv[1],1,0,0);
    puts("PASS: four actual bias QC copying/lifetime profiles, explicit BPM/MAD/RON choices");
    return 0;
}
