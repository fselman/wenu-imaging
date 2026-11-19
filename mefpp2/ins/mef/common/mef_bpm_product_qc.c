/* Map qualified BPM results to the shared typed product container.
 * Existing FITS diagnostic arrays and native operation context remain intact.
 * No ASDF serializer, image load, pixel correction or response fit lives here. */
#define _POSIX_C_SOURCE 200809L
#include "mef_bpm_product_qc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#undef malloc
#undef calloc
#undef free
#define METRICS 40
#define CONTEXT_LIMIT (1024u * 1024u)

typedef struct {
    mef_qc_measurement records[METRICS];
    double values[METRICS];
    char names[METRICS][80];
    const char *source;
    size_t count;
} measurements;

struct mef_bpm_product_qc {
    mef_product_qc product;
    mef_qc_detector_record detector;
    mef_qc_input_record *inputs;
    mef_qc_input_binding *bindings;
    measurements *input_metrics, product_metrics;
    mef_qc_calibration_record calibrations[2];
    mef_qc_calibration_binding calibration_bindings[2];
    double reasons[256], coverage[3];
    char *configuration, *context;
    char start[25];
};

static int snapshots(mef_bpm_product_qc *archive, const mef_bpm_files_result *result,
    const char *path, const mef_bpm_publish_options *options)
{
    size_t length=0;
    FILE *stream=open_memstream(&archive->configuration,&length);
    int okay;
    if (!stream) return 0;
    okay=mef_config_dump(mef_bpm_result_configuration(mef_bpm_files_result_service(result)),stream)==MEF_OK;
    if (fclose(stream) || !okay || !length || length>CONTEXT_LIMIT) return 0;
    stream=open_memstream(&archive->context,&length);
    if (!stream) return 0;
    okay=mef_bpm_write_handoff(stream,result,path,options,NULL)==MEF_OK;
    return fclose(stream)==0 && okay && length>0 && length<=CONTEXT_LIMIT;
}

static int scalar(measurements *storage, const char *name, const char *unit,
    const char *stage, double value, int available)
{
    size_t index=storage->count;
    mef_qc_measurement *record;
    if (index==METRICS || strlen(name)>=sizeof(storage->names[index])) return 0;
    record=storage->records+index;
    strcpy(storage->names[index],name);
    storage->values[index]=value;
    record->name=storage->names[index]; record->unit=unit; record->stage=stage;
    record->method="native_BPM_service";
    record->state=available?MEF_QC_MEASURED:MEF_QC_UNAVAILABLE;
    record->reason=available?NULL:"native_measurement_unavailable";
    record->values=available?storage->values+index:NULL;
    record->value_count=available?1:0; record->sample_count=1;
    record->coordinates="not_applicable"; record->mask_policy="not_applicable";
    record->clipping="none"; record->nonfinite_policy="native_selection";
    record->source_ids=&storage->source; record->source_count=1;
    ++storage->count;
    return 1;
}

static int statistics(measurements *storage, const char *name,
    const image_sample_stats *stats, const char *mask)
{
    const char *suffix[]={"mean","median","stdev","scaled_mad",
                          "region_pixels","bpm_excluded","nonfinite_excluded","valid_pixels"};
    double values[]={stats->mean,stats->median,stats->stdev,1.4826*stats->mad,
        (double)stats->region_pixels,(double)stats->bpm_excluded,
        (double)stats->nonfinite_excluded,(double)stats->valid_pixels};
    int available[]={stats->level_available,stats->level_available,
                     stats->stdev_available,stats->mad_available,1,1,1,1};
    size_t i;
    char key[80];
    for (i=0;i<8;++i) {
        mef_qc_measurement *record;
        if (snprintf(key,sizeof(key),"%s.%s",name,suffix[i]) >= (int)sizeof(key) ||
            !scalar(storage,key,i<4?"ADU":"count",name,values[i],available[i])) return 0;
        record=storage->records+storage->count-1;
        record->sample_count=i<4?stats->valid_pixels:1;
        if (stats->region_pixels) {
            memcpy(record->bounds,stats->zone,sizeof(record->bounds));
            record->coordinates="FITS-1-based-inclusive";
        }
        record->mask_policy=mask?"applied":"omitted";
        record->mask_id=mask;
    }
    return 1;
}

static int input_records(mef_bpm_product_qc *archive, const mef_bpm_files_result *result)
{
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const mef_request_spec *request=mef_request_view(mef_bpm_result_request(service));
    const mef_bpm_files_qc *files=mef_bpm_files_result_qc(result);
    const mef_bpm_qc *native=mef_bpm_result_qc(service);
    const detector_response_result *response=mef_bpm_result_response(service);
    const size_t *indices=mef_bpm_result_fit_indices(service);
    size_t i,j;
    const char *mask=NULL;
    for (i=0;i<archive->product.calibration_count;++i)
        if (!strcmp(archive->calibrations[i].role,"bpm")) mask=archive->calibrations[i].id;
    archive->inputs=calloc(request->input_count,sizeof(*archive->inputs));
    archive->bindings=calloc(request->input_count,sizeof(*archive->bindings));
    archive->input_metrics=calloc(request->input_count,sizeof(*archive->input_metrics));
    if (!archive->inputs || !archive->bindings || !archive->input_metrics) return 0;
    for (i=0;i<request->input_count;++i) {
        const mef_image_ref *input=request->inputs+i;
        const mef_bpm_frame_qc *frame=native->frames+i;
        measurements *storage=archive->input_metrics+i;
        mef_qc_input_binding *binding=archive->bindings+i;
        storage->source=input->asset_record_id;
        archive->inputs[i]=(mef_qc_input_record){input->asset_record_id,input->resolved_path,NULL,i};
        binding->input_id=input->asset_record_id; binding->source_hdu=input->hdu_index;
        binding->accepted=frame->included_in_fit;
        binding->rejection_reason=frame->included_in_fit?NULL:"native_reference_population_unavailable";
        if (!statistics(storage,"corrected_active",&frame->active_corrected,mask) ||
            !statistics(storage,"prescan",&frame->prescan,NULL) ||
            !statistics(storage,"overscan",&frame->overscan,NULL)) return 0;
#define VALUE(name,unit,value,available) \
        if (!scalar(storage,name,unit,"frame_admission",(double)(value),available)) return 0
        VALUE("integration_seconds","s",files->integration_seconds[i],1);
        VALUE("pair_id","count",files->pair_ids[i],1);
        VALUE("included_in_fit","count",frame->included_in_fit,1);
        VALUE("saturated","count",frame->saturated,1);
        VALUE("margin_excluded","count",frame->margin_excluded,1);
        VALUE("sample_excluded","count",frame->sample_excluded,1);
        VALUE("nonfinite","count",frame->nonfinite,1);
        VALUE("reference_samples","count",frame->reference_samples,1);
        VALUE("reference_fraction","1",frame->reference_fraction_median,frame->included_in_fit);
        for (j=0;j<(size_t)response->plane_count && indices[j]!=i;++j) {}
        VALUE("reference_level","ADU",j<(size_t)response->plane_count?response->reference_levels[j]:0,
              j<(size_t)response->plane_count);
#undef VALUE
        binding->measurements=storage->records; binding->measurement_count=storage->count;
    }
    archive->product.inputs=archive->inputs; archive->product.input_count=request->input_count;
    archive->detector.inputs=archive->bindings; archive->detector.input_count=request->input_count;
    return 1;
}

static int product_records(mef_bpm_product_qc *archive, const mef_bpm_files_result *result,
    const mef_bpm_publish_options *options)
{
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const detector_response_result *response=mef_bpm_result_response(service);
    const unsigned char *flags=options->mode==MEF_BPM_PUBLISH_NEW?response->reasons:
        mef_bpm_result_combined_flags(service);
    size_t i,count=(size_t)response->valid->lx*(size_t)response->valid->ly;
    measurements *storage=&archive->product_metrics;
    if (!flags || !count) return 0;
    for (i=0;i<count;++i) {
        if (response->fit_state[i]>2) return 0;
        ++archive->reasons[flags[i]]; ++archive->coverage[response->fit_state[i]];
    }
    storage->source=archive->product.id;
    if (!scalar(storage,"reason_histogram","count","response_characterization",0,1) ||
        !scalar(storage,"fit_histogram","count","response_characterization",0,1) ||
        !scalar(storage,"normalization","1","response_characterization",response->normalization,1)) return 0;
    for (i=0;i<2;++i) {
        mef_qc_measurement *record=storage->records+i;
        record->vector=1; record->values=i?archive->coverage:archive->reasons;
        record->value_count=i?3:256; record->sample_count=count;
    }
    archive->detector.measurements=storage->records;
    archive->detector.measurement_count=storage->count;
    return 1;
}

mef_bpm_product_qc *mef_bpm_product_qc_new(const mef_bpm_files_result *result,
    const char *path, const mef_bpm_publish_options *options, char *message, size_t size)
{
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const mef_bpm_files_qc *files=mef_bpm_files_result_qc(result);
    const mef_request *owner=mef_bpm_result_request(service);
    const mef_request_spec *request=mef_request_view(owner);
    const mef_resolved_request_spec *resolved=mef_request_resolved_view(owner);
    mef_bpm_product_qc *archive;
    size_t i;
    if (!service || !files || !request || !resolved || !path || !options ||
        !options->created_at || strlen(options->created_at)!=20 ||
        !request->input_count || request->calibration_count>2) return NULL;
    archive=calloc(1,sizeof(*archive));
    if (!archive) return NULL;
    memcpy(archive->start,options->created_at,19);
    strcpy(archive->start+19,".000Z");
    archive->product=(mef_product_qc){.id=path,.fits_path=path,.log_path=request->log_path,
        .assessment_id=path,.recipe_name="cal.bpm",.recipe_start=archive->start,
        .recipe_version=1,.product_sequence=1,.producer_name="mefpp.cal.bpm",
        .producer_version="1",.source_revision=options->source_revision,
        .configuration_id="effective-native-settings",.primary_image=1,
        .bpm_registry="WENU_BPM_V1",.operation_context_format="mef_bpm_handoff/1"};
    archive->detector=(mef_qc_detector_record){.id=request->inputs[0].detector_id,
        .amplifier="explicit-whole-detector",.readout_id=files->readout_id,
        .configuration_detector=files->configuration_detector,.output_hdu=0,
        .bin_x=files->bin_x,.bin_y=files->bin_y};
    archive->product.detectors=&archive->detector; archive->product.detector_count=1;
    for (i=0;i<request->calibration_count;++i) {
        const mef_image_ref *ref=request->calibrations+i;
        archive->calibration_bindings[i]=(mef_qc_calibration_binding){ref->detector_id,ref->hdu_index};
        archive->calibrations[i]=(mef_qc_calibration_record){.id=ref->asset_record_id,
            .path=ref->resolved_path,.role=resolved->calibration_roles[i]==MEF_CAL_BIAS?"bias":"bpm",
            .bindings=archive->calibration_bindings+i,.binding_count=1};
    }
    archive->product.calibrations=archive->calibrations;
    archive->product.calibration_count=request->calibration_count;
    if (!snapshots(archive,result,path,options) || !input_records(archive,result) ||
        !product_records(archive,result,options)) goto failed;
    archive->product.configuration_snapshot=archive->configuration;
    archive->product.operation_context_snapshot=archive->context;
    if (mef_product_qc_validate(&archive->product,message,size)) goto failed;
    return archive;
failed:
    mef_bpm_product_qc_destroy(archive);
    return NULL;
}

const mef_product_qc *mef_bpm_product_qc_view(const mef_bpm_product_qc *archive)
{ return archive?&archive->product:NULL; }

void mef_bpm_product_qc_destroy(mef_bpm_product_qc *archive)
{
    if (!archive) return;
    free(archive->inputs); free(archive->bindings); free(archive->input_metrics);
    free(archive->configuration); free(archive->context); free(archive);
}
