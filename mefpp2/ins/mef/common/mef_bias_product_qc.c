#define _POSIX_C_SOURCE 200809L
#include "mef_bias_product_qc.h"
#include "mef_product_qc.h"
#include <stdlib.h>
#include <string.h>
/* Eclipse's public image headers expose allocator macros. These metadata owners
 * use libc; numerical image owners still use their library destructors. */
#undef malloc
#undef calloc
#undef realloc
#undef free

#define QC_CAPACITY 64
typedef struct {
    mef_qc_measurement *q;
    double *values;
    char (*names)[80];
    const char *source[1];
    size_t count;
} bucket;
typedef struct {
    bucket product, *inputs;
    const char *pair[2];
    double *hot_x, *hot_y;
} detector_storage;
struct mef_bias_product_qc {
    mef_product_qc product;
    const mef_product_paths *paths;
    char *snapshot;
    mef_qc_input_record *inputs;
    char (*input_ids)[40], (*calibration_ids)[40];
    mef_qc_detector_record *detectors;
    mef_qc_calibration_record *calibrations;
    detector_storage *storage;
};
static int bucket_new(bucket *b, const char *source)
{
    b->q = calloc(QC_CAPACITY, sizeof(*b->q));
    b->values = calloc(QC_CAPACITY, sizeof(*b->values));
    b->names = calloc(QC_CAPACITY, sizeof(*b->names));
    b->source[0] = source;
    return b->q != NULL && b->values != NULL && b->names != NULL;
}
static void bucket_destroy(bucket *b)
{ free(b->q); free(b->values); free(b->names); }
static mef_qc_measurement *scalar(bucket *b, const char *name, double value,
    const char *unit, const char *stage, const char *method, int available,
    const char *reason, size_t samples, const int *bounds, const char *mask,
    const char *mask_id, const char *const *sources, size_t source_count)
{
    size_t i = b->count;
    mef_qc_measurement *q;
    if (i == QC_CAPACITY || strlen(name) >= sizeof(b->names[i])) return NULL;
    strcpy(b->names[i], name); b->values[i] = value; q = b->q + i;
    q->name = b->names[i]; q->unit = unit; q->stage = stage; q->method = method;
    q->state = available ? MEF_QC_MEASURED : MEF_QC_UNAVAILABLE;
    q->reason = available ? NULL : reason;
    q->values = available ? b->values + i : NULL; q->value_count = available ? 1 : 0;
    q->sample_count = samples; q->coordinates = "FITS-1-based-inclusive";
    q->mask_policy = mask; q->mask_id = mask_id;
    q->clipping = "none"; q->nonfinite_policy = "excluded";
    if (bounds != NULL) memcpy(q->bounds, bounds, sizeof(q->bounds));
    q->source_ids = sources ? sources : b->source;
    q->source_count = sources ? source_count : 1;
    ++b->count; return q;
}
static int sample(bucket *b, const char *name, const char *stage,
    const image_sample_stats *s, int scan, const char *mask_id,
    const char *const *sources, size_t source_count)
{
    static const char *suffix[] = {"mean", "median", "stdev", "scaled_mad",
        "region_pixels", "bpm_excluded", "nonfinite_excluded", "valid_pixels"};
    static const char *method[] = {"arithmetic_mean", "median_averaged_central_pair",
        "sample_standard_deviation_n_minus_1", "1.4826_times_median_absolute_deviation"};
    double v[8]; int available[8]; size_t i; char key[80];
    const char *mask = scan ? "not_applicable" : s->bpm_supplied ? "applied" :
        mask_id ? "unmasked_diagnostic" : "omitted";
    const char *record = !scan && s->bpm_supplied ? mask_id : NULL;
    v[0]=s->mean; v[1]=s->median; v[2]=s->stdev; v[3]=1.4826*s->mad;
    v[4]=(double)s->region_pixels; v[5]=(double)s->bpm_excluded;
    v[6]=(double)s->nonfinite_excluded; v[7]=(double)s->valid_pixels;
    available[0]=available[1]=s->level_available;
    available[2]=s->stdev_available; available[3]=s->mad_available;
    for(i=4;i<8;++i) available[i]=s->region_pixels != 0;
    for(i=0;i<8;++i) {
        snprintf(key,sizeof(key),"%s.%s",name,suffix[i]);
        if(scalar(b,key,v[i],i<4?"ADU":"count",stage,i<4?method[i]:"explicit_sample_partition",
            available[i],i<4?"not_requested_or_insufficient_samples":"region_not_configured",i<4?s->valid_pixels:s->region_pixels,
            s->zone,mask,record,sources,source_count)==NULL) return 0;
    }
    return 1;
}
mef_bias_product_qc *mef_bias_product_qc_new(const mef_config *config,
    const mef_product_paths *paths, const char *start, const char *revision,
    const char *const *inputs, size_t count, size_t detectors)
{
    mef_bias_product_qc *a; FILE *stream; size_t length=0, i; int okay;
    if(config==NULL || paths==NULL || start==NULL || revision==NULL || inputs==NULL ||
        count==0 || count>100000 || detectors==0 || detectors>4096) return NULL;
    a=calloc(1,sizeof(*a)); if(a==NULL) return NULL;
    a->product.input_count=count; a->product.detector_count=detectors; a->paths=paths;
    a->inputs=calloc(count,sizeof(*a->inputs)); a->input_ids=calloc(count,sizeof(*a->input_ids));
    a->detectors=calloc(detectors,sizeof(*a->detectors)); a->storage=calloc(detectors,sizeof(*a->storage));
    a->calibrations=calloc(detectors,sizeof(*a->calibrations));
    a->calibration_ids=calloc(detectors,sizeof(*a->calibration_ids));
    if(!a->inputs || !a->input_ids || !a->detectors || !a->storage || !a->calibrations || !a->calibration_ids) goto failed;
    stream=open_memstream(&a->snapshot,&length); if(stream==NULL) goto failed;
    okay=mef_config_dump(config,stream)==MEF_OK;
    if(fclose(stream)!=0 || !okay) goto failed;
    for(i=0;i<count;++i) {
        snprintf(a->input_ids[i],sizeof(a->input_ids[i]),"raw-%06lu",(unsigned long)i);
        a->inputs[i].id=a->input_ids[i]; a->inputs[i].path=inputs[i]; a->inputs[i].original_index=i;
    }
    a->product.id=paths->fits; a->product.fits_path=paths->fits; a->product.log_path=paths->log;
    a->product.assessment_id=paths->fits; a->product.recipe_name="cal.bias";
    a->product.recipe_start=start; a->product.recipe_version=1; a->product.product_sequence=1;
    a->product.producer_name="mefpp_bias_recipe"; a->product.producer_version="1";
    a->product.source_revision=revision; a->product.configuration_id="effective-native-settings";
    a->product.configuration_snapshot=a->snapshot; a->product.inputs=a->inputs;
    a->product.detectors=a->detectors; a->product.calibrations=a->calibrations;
    return a;
failed:
    mef_bias_product_qc_destroy(a); return NULL;
}
static const char *calibration(mef_bias_product_qc *a, const char *path,
    const char *id, int hdu)
{
    size_t i, n=a->product.calibration_count;
    mef_qc_calibration_binding *bindings;
    for(i=0;i<n;++i) if(!strcmp(path,a->calibrations[i].path)) break;
    if(i==n) {
        snprintf(a->calibration_ids[i],sizeof(a->calibration_ids[i]),"bpm-%06lu",(unsigned long)i);
        a->calibrations[i].id=a->calibration_ids[i]; a->calibrations[i].path=path;
        a->calibrations[i].role="bpm";
        a->calibrations[i].bindings=calloc(a->product.detector_count,sizeof(*bindings));
        if(a->calibrations[i].bindings==NULL) return NULL;
        ++a->product.calibration_count;
    }
    bindings=(mef_qc_calibration_binding *)a->calibrations[i].bindings;
    n=a->calibrations[i].binding_count;
    bindings[n].detector_id=id; bindings[n].source_hdu=hdu;
    ++a->calibrations[i].binding_count; return a->calibrations[i].id;
}
int mef_bias_product_qc_add(mef_bias_product_qc *a, size_t index,
    const char *id, const char *amplifier, const char *readout, size_t configured,
    int bin_x, int bin_y, const mef_bias_result *result,
    const mef_bias_measurement_options *options, const mef_bias_settings *settings,
    int rows, const char *bpm_path, int bpm_hdu, int good)
{
    detector_storage *store; mef_qc_detector_record *d; mef_qc_input_binding *bindings;
    const mef_bias_measurements *m=mef_bias_result_measurements(result);
    const mef_bias_qc *legacy=mef_bias_result_qc(result);
    const mef_request_spec *request=mef_request_view(mef_bias_result_request(result));
    const char *mask=NULL; bucket *b; size_t i,n; int bounds[4]={1,1,1,rows};
    const char *const *pair=NULL; size_t pair_count=0;
    if(a==NULL || index>=a->product.detector_count || m==NULL || legacy==NULL || request==NULL ||
        options==NULL || settings==NULL || m->count!=a->product.input_count ||
        request->input_count!=a->product.input_count || a->detectors[index].id!=NULL) return 0;
    store=a->storage+index; d=a->detectors+index;
    if(bpm_path!=NULL) { mask=calibration(a,bpm_path,id,bpm_hdu); if(mask==NULL) return 0; }
    store->inputs=calloc(m->count,sizeof(*store->inputs));
    bindings=calloc(m->count,sizeof(*bindings)); d->inputs=bindings;
    if(store->inputs==NULL || bindings==NULL || !bucket_new(&store->product,a->product.id)) return 0;
    d->id=id; d->amplifier=amplifier; d->readout_id=readout; d->configuration_detector=configured;
    d->output_hdu=(int)index+1; d->bin_x=bin_x; d->bin_y=bin_y; d->input_count=m->count;
    for(i=0;i<m->count;++i) {
        const mef_bias_frame_measurements *f=m->frames+i;
        if(strcmp(request->inputs[i].resolved_path,a->inputs[i].path)) return 0;
        b=store->inputs+i; if(!bucket_new(b,a->inputs[i].id)) return 0;
        if(!sample(b,"raw_active","raw_before_correction",&f->active_raw,0,mask,NULL,0) ||
            !sample(b,"corrected_active","overscan_corrected_trimmed",&f->active_corrected,0,mask,NULL,0) ||
            !sample(b,"prescan","raw_prescan_empty_reads",&f->prescan,1,mask,NULL,0) ||
            !sample(b,"overscan","raw_overscan_empty_reads",&f->overscan,1,mask,NULL,0)) return 0;
#define SCAN(name,value,unit,method) if(scalar(b,name,(double)(value),unit,"scan_correction_profile",method,1,NULL,rows,bounds,"not_applicable",NULL,NULL,0)==NULL) return 0
        SCAN("scan_correction.median",legacy->scan_median[i],"ADU","legacy_median_of_row_corrections");
        SCAN("scan_correction.stdev",legacy->scan_stdev[i],"ADU","legacy_sample_stdev_of_row_corrections");
        SCAN("scan_correction.prescan_used",settings->use_prescan!=0,"count","explicit_native_setting");
        SCAN("scan_correction.overscan_used",settings->use_overscan!=0,"count","explicit_native_setting");
        SCAN("scan_correction.rejected_low",settings->rejection[0],"count","explicit_native_setting");
        SCAN("scan_correction.rejected_high",settings->rejection[1],"count","explicit_native_setting");
#undef SCAN
        bindings[i].input_id=a->inputs[i].id; bindings[i].source_hdu=request->inputs[i].hdu_index;
        bindings[i].accepted=legacy->accepted[i];
        bindings[i].rejection_reason=legacy->accepted[i]?NULL:"native_frame_mean_rejection";
        bindings[i].measurements=b->q; bindings[i].measurement_count=b->count;
    }
    b=&store->product;
    if(!sample(b,"master","median_stacked_master",&m->master,0,mask,NULL,0) ||
        !sample(b,"master_unmasked","median_stacked_master_unmasked",&m->master_unmasked,0,mask,NULL,0)) return 0;
    if(options->ron_pair_set) {
        if(m->ron_first>=m->count || m->ron_second>=m->count) return 0;
        store->pair[0]=a->inputs[m->ron_first].id; store->pair[1]=a->inputs[m->ron_second].id;
        pair=store->pair; pair_count=2;
    }
    if(!sample(b,"raw_difference","raw_pair_difference_before_any_correction",&m->raw_difference,0,mask,pair,pair_count)) return 0;
#define PRODUCT(name,value,unit,stage,method,available,reason,samples,zone,sources,source_count) \
    if(scalar(b,name,(double)(value),unit,stage,method,available,reason,samples,zone,"not_applicable",NULL,sources,source_count)==NULL) return 0
    PRODUCT("read_noise",m->ron_stdev_adu,"ADU","raw_pair_difference_before_any_correction","sample_stdev_raw_difference_div_sqrt2",m->ron_stdev_available,"pair_not_requested_or_insufficient_samples",m->raw_difference.valid_pixels,m->raw_difference.zone,pair,pair_count);
    PRODUCT("read_noise.mad",m->ron_mad_adu,"ADU","raw_pair_difference_before_any_correction","1.4826_MAD_raw_difference_div_sqrt2",m->ron_mad_available,"pair_not_requested_or_insufficient_samples",m->raw_difference.valid_pixels,m->raw_difference.zone,pair,pair_count);
    /* These two RON quantities use exactly the same mask as the raw difference. */
    if(mask!=NULL && options->ron_pair_set) for(i=b->count-2;i<b->count;++i) { b->q[i].mask_policy="applied"; b->q[i].mask_id=mask; }
    PRODUCT("pixels.hot",m->high_offset_count,"count","median_stacked_master","all_master_pixels_above_masked_median_plus_k_scaled_MAD",m->high_offset_available,"MAD_not_requested",m->master.region_pixels,m->master.zone,NULL,0);
    PRODUCT("pixels.hot.threshold",m->high_offset_threshold,"ADU","median_stacked_master","all_master_pixels_above_masked_median_plus_k_scaled_MAD",m->high_offset_available,"MAD_not_requested",m->master.region_pixels,m->master.zone,NULL,0);
    b->q[b->count-2].mask_policy=mask?"unmasked_diagnostic":"omitted";
    b->q[b->count-2].mask_id=mask;
    b->q[b->count-1].mask_policy=mask?"applied":"omitted";
    b->q[b->count-1].mask_id=mask;
    PRODUCT("pixels.hot.sigma",options->high_sigma,"dimensionless","recipe_parameters","explicit_native_setting",1,NULL,1,NULL,NULL,0);
    PRODUCT("recipe.mad_requested",options->with_mad,"count","recipe_parameters","explicit_native_setting",1,NULL,1,NULL,NULL,0);
    PRODUCT("recipe.ron_pair_requested",options->ron_pair_set,"count","recipe_parameters","explicit_native_setting",1,NULL,1,NULL,NULL,0);
    PRODUCT("pixels.hot.threshold_degenerate",m->high_offset_degenerate,"count","median_stacked_master","explicit_native_flag",m->high_offset_available,"MAD_not_requested",m->master.region_pixels,m->master.zone,NULL,0);
    if(mask!=NULL) {
        PRODUCT("bpm.good_value",good,"count","recipe_parameters","explicit_native_setting",1,NULL,1,NULL,NULL,0);
        PRODUCT("bpm.active_coordinates",options->bpm_active_only,"count","recipe_parameters","explicit_native_setting",1,NULL,1,NULL,NULL,0);
    }
    PRODUCT("legacy.frame_mean_average",legacy->frame_mean_average,"ADU","frame_mean_rejection","legacy_frame_mean_average",1,NULL,m->count,NULL,NULL,0);
    PRODUCT("legacy.frame_mean_sigma",legacy->frame_mean_sigma,"ADU","frame_mean_rejection","legacy_frame_mean_sigma",1,NULL,m->count,NULL,NULL,0);
    PRODUCT("legacy.rejection_low",legacy->rejection_low,"ADU","frame_mean_rejection","legacy_rejection_boundary",1,NULL,m->count,NULL,NULL,0);
    PRODUCT("legacy.rejection_high",legacy->rejection_high,"ADU","frame_mean_rejection","legacy_rejection_boundary",1,NULL,m->count,NULL,NULL,0);
    PRODUCT("legacy.product_median",legacy->product_median,"ADU","median_stacked_master","legacy_image_median",1,NULL,m->master.region_pixels,m->master.zone,NULL,0);
    PRODUCT("legacy.product_stdev",legacy->product_stdev,"ADU","median_stacked_master","legacy_image_stdev",1,NULL,m->master.region_pixels,m->master.zone,NULL,0);
    PRODUCT("variance",0,"ADU2","median_stacked_master",NULL,0,"legacy_variance_unavailable",0,NULL,NULL,0);
#undef PRODUCT
    n=m->high_offset_count;
    if(n) {
        const pixelmap *flags=m->high_offset_flags; size_t k=0; int x,y;
        if(flags==NULL || n>SIZE_MAX/sizeof(double)) return 0;
        store->hot_x=malloc(n*sizeof(double)); store->hot_y=malloc(n*sizeof(double));
        if(!store->hot_x || !store->hot_y) return 0;
        for(y=0;y<flags->ly;++y) for(x=0;x<flags->lx;++x) if(flags->data[y*flags->lx+x]) {
            if(k==n) return 0;
            store->hot_x[k]=x+1; store->hot_y[k]=y+1; ++k;
        }
        if(k!=n) return 0;
    }
    for(i=0;i<2;++i) {
        mef_qc_measurement *q=scalar(b,i?"pixels.hot.y":"pixels.hot.x",0,"pixel","median_stacked_master",
            "stored_high_offset_flag_locations",n!=0,n?NULL:m->high_offset_available?"empty_location_set_zero_flagged_pixels":"MAD_not_requested",
            m->master.region_pixels,m->master.zone,"unmasked_diagnostic",mask,NULL,0);
        if(q==NULL) return 0;
        q->coordinates="FITS-1-based-active";
        if(n) { q->vector=1; q->value_count=n; q->values=i?store->hot_y:store->hot_x; }
    }
    d->measurements=b->q; d->measurement_count=b->count;
    return 1;
}
int mef_bias_product_qc_check(mef_bias_product_qc *a,char *message,size_t size)
{ return a==NULL?-1:mef_product_qc_validate(&a->product,message,size); }
const mef_product_qc *mef_bias_product_qc_view(const mef_bias_product_qc *a)
{ return a==NULL?NULL:&a->product; }
int mef_bias_product_qc_write(mef_bias_product_qc *a,char *message,size_t size)
{ return a==NULL?-1:mef_product_qc_write(a->paths->asdf,&a->product,message,size); }
void mef_bias_product_qc_destroy(mef_bias_product_qc *a)
{
    size_t i,j;
    if(a==NULL) return;
    if(a->storage) for(i=0;i<a->product.detector_count;++i) {
        bucket_destroy(&a->storage[i].product);
        if(a->storage[i].inputs) for(j=0;j<a->product.input_count;++j) bucket_destroy(a->storage[i].inputs+j);
        free(a->storage[i].inputs); free(a->storage[i].hot_x); free(a->storage[i].hot_y);
        if(a->detectors) free((void *)a->detectors[i].inputs);
    }
    if(a->calibrations) for(i=0;i<a->product.calibration_count;++i) free((void *)a->calibrations[i].bindings);
    free(a->snapshot); free(a->inputs); free(a->input_ids); free(a->detectors);
    free(a->storage); free(a->calibrations); free(a->calibration_ids); free(a);
}
