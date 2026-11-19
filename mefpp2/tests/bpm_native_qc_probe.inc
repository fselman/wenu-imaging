/* Real service result -> existing shared product contract; no ASDF substitute. */
#include "mef_bpm_product_qc.h"
static const mef_qc_measurement *native_metric(const mef_qc_input_binding *binding,const char *name)
{
    size_t i;
    for(i=0;i<binding->measurement_count;++i)
        if(!strcmp(binding->measurements[i].name,name)) return binding->measurements+i;
    assert(0); return NULL;
}
static void native_product_qc(const mef_bpm_files_result *result,const char *path,
    const mef_bpm_publish_options *options)
{
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const mef_bpm_qc *measured=mef_bpm_result_qc(service);
    const mef_bpm_files_qc *files=mef_bpm_files_result_qc(result);
    mef_bpm_product_qc *archive;
    const mef_product_qc *product;
    mef_product_qc invalid;
    mef_qc_detector_record extension;
    size_t i;
    char message[512]="unreported failure";
    archive=mef_bpm_product_qc_new(result,path,options,message,sizeof(message));
    if(!archive) fprintf(stderr,"Native BPM QC: %s\n",message);
    assert(archive); product=mef_bpm_product_qc_view(archive);
    assert(mef_product_qc_validate(product,message,sizeof(message))==0);
    assert(product->primary_image && product->detector_count==1 && product->detectors[0].output_hdu==0);
    assert(product->input_count==files->input_count);
    assert(strstr(product->operation_context_snapshot,"\"reason_histogram\"")!=NULL);
    for(i=0;i<files->input_count;++i) {
        const mef_qc_input_binding *binding=product->detectors[0].inputs+i;
        const mef_qc_measurement *level=native_metric(binding,"corrected_active.mean");
        const mef_qc_measurement *mad=native_metric(binding,"corrected_active.scaled_mad");
        assert(binding->accepted==measured->frames[i].included_in_fit);
        assert(product->inputs[i].original_index==i && binding->source_hdu==(i%2?2:0));
        assert(native_metric(binding,"integration_seconds")->values[0]==files->integration_seconds[i]);
        assert(native_metric(binding,"reference_samples")->values[0]==(double)measured->frames[i].reference_samples);
        assert((level->state==MEF_QC_MEASURED)==measured->frames[i].active_corrected.level_available);
        if(level->state==MEF_QC_MEASURED) assert(level->values[0]==measured->frames[i].active_corrected.mean);
        assert((mad->state==MEF_QC_MEASURED)==measured->frames[i].active_corrected.mad_available);
    }
    invalid=*product; invalid.primary_image=0;
    assert(mef_product_qc_validate(&invalid,message,sizeof(message))!=0);
    extension=product->detectors[0]; extension.output_hdu=1;
    invalid=*product; invalid.primary_image=0; invalid.detectors=&extension;
    assert(mef_product_qc_validate(&invalid,message,sizeof(message))==0);
    invalid=*product; invalid.detector_count=2;
    assert(mef_product_qc_validate(&invalid,message,sizeof(message))!=0);
    invalid=*product; invalid.operation_context_snapshot=NULL;
    assert(mef_product_qc_validate(&invalid,message,sizeof(message))!=0);
#ifdef BPM_NATIVE_ASDF_CONTRACT
    {
        char asdf[4096]; size_t length=strlen(path);
        assert(length>5 && length<sizeof(asdf));
        strcpy(asdf,path); strcpy(asdf+length-5,".asdf");
        assert(mef_product_qc_write(asdf,product,message,sizeof(message))==0);
        assert(mef_product_qc_write(asdf,product,message,sizeof(message))!=0);
    }
#endif
    mef_bpm_product_qc_destroy(archive);
    puts("PASS: native BPM metadata preserves input binding, measured/unavailable QC and explicit primary layout");
}
