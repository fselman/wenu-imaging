#include "mef_bpm_files.h"
#include "mef_bpm_settings.h"
#include "mef_operation_template.h"
#include "pixelmap_flags8.h"
#include "mefp_lib.h"
#include <ctype.h>
#include <float.h>
#include <errno.h>

struct mef_bpm_files_result {
    mef_allocator allocator;
    mef_bpm_result *service;
    mef_bpm_files_qc qc;
};
typedef struct {
    mef_context *context;
    const mef_layout_map *const *maps;
    size_t count, config_slot;
    const char *detector;
    const mef_layout_map *bias_map,*prior_map;
    const mef_bpm_files_options *options;
    mef_bpm_settings settings;
    mef_bpm_files_result *pending;
    image_t **frames, *bias;
    const image_t **borrowed;
    pixelmap *binary;
    unsigned char *flags;
} file_state;
static void release(const mef_allocator *a,const void *p) { if(p) a->release(a->user,(void *)p); }
void mef_bpm_files_result_destroy(mef_bpm_files_result *r) {
    mef_allocator a;
    if(!r) return;
    a=r->allocator; mef_bpm_result_destroy(r->service);
    release(&a,r->qc.integration_seconds); release(&a,r->qc.pair_ids); release(&a,r->qc.rois); release(&a,r);
}
const mef_bpm_result *mef_bpm_files_result_service(const mef_bpm_files_result *r) { return r?r->service:NULL; }
const mef_bpm_files_qc *mef_bpm_files_result_qc(const mef_bpm_files_result *r) { return r?&r->qc:NULL; }
#include "mef_file_metadata_internal.h"
static mef_status validate(void *opaque,mef_error **error) {
    file_state *s=opaque;
    const mef_bpm_files_options *o=s->options;
    const mef_resolved_request_spec *resolved;
    const mef_request_spec *rq;
    const mef_bound_detector *first,*d;
    const mef_layout_map *cal;
    const mef_allocator *a;
    mef_bpm_files_result *r;
    double *times;
    size_t *pairs,i,j,n,groups=0,levels=0;
    int found_bias=0,found_prior=0;
    (void)error;
    if(!s->context || !s->maps || !s->detector || !*s->detector || !s->bias_map || !o ||
        s->count<2 || s->count>MAX_IMAGE_NUMBER ||
        (o->mode!=MEF_BPM_PROVISIONAL && o->mode!=MEF_BPM_QUICK) ||
        !o->exposure_key || !*o->exposure_key || strlen(o->exposure_key)>80 || o->exposure_hdu<0 ||
        !finite_number(o->saturation_raw) || o->saturation_raw<=0 ||
        !finite_number(o->upper_fraction) || o->upper_fraction<=0 || o->upper_fraction>1 ||
        !finite_number(o->minimum_span_fraction) || o->minimum_span_fraction<0 || o->minimum_span_fraction>1 ||
        !finite_number(o->maximum_pair_difference) || o->maximum_pair_difference<0 ||
        o->reject_bits>255 || (o->with_mad!=0 && o->with_mad!=1) ||
        ((o->roi_count!=0)!=(o->rois!=NULL)) || o->roi_count>(size_t)-1/sizeof(*o->rois) ||
        (o->mode==MEF_BPM_QUICK && (!o->pair_ids || s->count<10)) ||
        (o->mask_encoding!=MEF_BPM_MASK_OMITTED && o->mask_encoding!=MEF_BPM_MASK_FLAGS8 && o->mask_encoding!=MEF_BPM_MASK_BINARY) ||
        (o->mask_encoding==MEF_BPM_MASK_OMITTED)!=(s->prior_map==NULL) ||
        (o->prior_active_only!=0 && o->prior_active_only!=1) ||
        (o->mask_encoding==MEF_BPM_MASK_BINARY && o->binary_good_value!=0 && o->binary_good_value!=1) ||
        (o->mask_encoding==MEF_BPM_MASK_FLAGS8 && (!o->mask_registry || !*o->mask_registry || strlen(o->mask_registry)>32))) return MEF_ERR_INPUT;
    if (s->prior_map && !mef_bpm_policy_matches(&mef_config_processing(mef_context_config(s->context))->bpm,
        o->mask_encoding == MEF_BPM_MASK_BINARY ? MEF_BPM_BINARY : MEF_BPM_REASON8,
        o->binary_good_value,o->reject_bits,o->mask_registry)) return MEF_ERR_CONFIG;
    resolved=mef_request_resolved_view(mef_context_request(s->context));
    if(!resolved || resolved->request.operation!=MEF_OP_CAL_BPM || resolved->request.operation_version!=1 ||
        resolved->request.input_count!=s->count || resolved->bpm_selection_count!=1) return MEF_ERR_INPUT;
    rq=&resolved->request; first=mef_layout_find(s->maps[0],s->detector);
    if(!first) return MEF_ERR_INPUT;
    s->config_slot=first->configuration_detector;
    if(mef_config_bpm_settings(mef_context_config(s->context),s->config_slot,&s->settings)!=MEF_OK) return MEF_ERR_CONFIG;
    for(i=0;i<o->roi_count;++i) {
        const int *z=o->rois[i];
        if(z[0]<1 || z[1]<z[0] || z[1]>first->active_width ||
            z[2]<1 || z[3]<z[2] || z[3]>first->active_height) return MEF_ERR_INPUT;
    }
    for(i=0;i<s->count;++i) {
        d=mef_layout_find(s->maps[i],s->detector);
        if(!binding_matches(s->maps[i],s->detector,rq->inputs+i,"ADU",s->config_slot) ||
            mef_layout_compatible(s->maps[0],s->maps[i],"ADU","ADU",NULL,NULL)!=MEF_OK ||
            d->active_x!=s->settings.scan.trim[0] || d->active_y!=s->settings.scan.trim[2] ||
            d->active_width!=s->settings.scan.trim[1]-s->settings.scan.trim[0]+1 ||
            d->active_height!=s->settings.scan.trim[3]-s->settings.scan.trim[2]+1) return MEF_ERR_INPUT;
        for(j=0;j<i;++j) if(!strcmp(rq->inputs[i].resolved_path,rq->inputs[j].resolved_path) &&
            rq->inputs[i].hdu_index==rq->inputs[j].hdu_index) return MEF_ERR_INPUT;
    }
    for(i=0;i<rq->calibration_count;++i) {
        if(resolved->calibration_roles[i]==MEF_CAL_BIAS) { cal=s->bias_map; ++found_bias; }
        else if(resolved->calibration_roles[i]==MEF_CAL_BPM) { cal=s->prior_map; ++found_prior; }
        else return MEF_ERR_UNSUPPORTED;
        if(!binding_matches(cal,s->detector,rq->calibrations+i,resolved->calibration_roles[i]==MEF_CAL_BIAS?"ADU":"mask",s->config_slot) ||
            mef_layout_compatible(s->maps[0],cal,"ADU",resolved->calibration_roles[i]==MEF_CAL_BIAS?"ADU":"mask",NULL,NULL)!=MEF_OK)
            return MEF_ERR_INPUT;
        d=mef_layout_find(cal,s->detector);
        if(resolved->calibration_roles[i]==MEF_CAL_BPM) {
            if(o->mask_encoding==MEF_BPM_MASK_FLAGS8) {
                qfits_header *h;
                char *v;
                int match=0;
                if(d->image.bitpix!=8 || d->image.bscale!=1 || d->image.bzero!=0) return MEF_ERR_INPUT;
                h=qfits_header_readext((char *)mef_layout_map_path(cal),d->image.hdu_index);
                if(!h) return MEF_ERR_INPUT;
                v=qfits_header_getstr(h,"MASKENC");
                if(v && !strcmp(qfits_pretty_string(v),"REASON8")) {
                    v=qfits_header_getstr(h,"MASKREG");
                    match=v && !strcmp(qfits_pretty_string(v),o->mask_registry);
                }
                qfits_header_destroy(h); if(!match) return MEF_ERR_INPUT;
            } else if(d->image.bitpix!=8 && d->image.bitpix!=16 && d->image.bitpix!=32) return MEF_ERR_INPUT;
        }
        if(resolved->calibration_roles[i]==MEF_CAL_BIAS || o->prior_active_only) {
            if(d->active_x!=1 || d->active_y!=1 || d->image.axes[0]!=(size_t)first->active_width ||
                d->image.axes[1]!=(size_t)first->active_height) return MEF_ERR_INPUT;
        } else if(d->active_x!=first->active_x || d->active_y!=first->active_y ||
            d->image.axes[0]!=first->image.axes[0] || d->image.axes[1]!=first->image.axes[1]) return MEF_ERR_INPUT;
    }
    if(found_bias!=1 || found_prior!=(s->prior_map?1:0)) return MEF_ERR_INPUT;
    a=mef_context_allocator(s->context);
    r=a->allocate(a->user,sizeof(*r)); if(!r) return MEF_ERR_MEMORY;
    memset(r,0,sizeof(*r)); r->allocator=*a; s->pending=r;
    times=a->allocate(a->user,s->count*sizeof(*times)); r->qc.integration_seconds=times;
    pairs=a->allocate(a->user,s->count*sizeof(*pairs)); r->qc.pair_ids=pairs;
    if(!times || !pairs) return MEF_ERR_MEMORY;
    r->qc.mode=o->mode; r->qc.input_count=s->count;
    r->qc.configuration_detector=s->config_slot;
    strcpy(r->qc.readout_id,first->readout_id); r->qc.bin_x=first->bin_x; r->qc.bin_y=first->bin_y;
    r->qc.mask_encoding=o->mask_encoding; r->qc.prior_active_only=o->prior_active_only;
    r->qc.binary_good_value=o->binary_good_value; r->qc.reject_bits=o->reject_bits;
    if(o->mask_encoding==MEF_BPM_MASK_FLAGS8) strcpy(r->qc.mask_registry,o->mask_registry);
    r->qc.saturation_raw=o->saturation_raw; r->qc.upper_fraction=o->upper_fraction;
    r->qc.minimum_span_fraction=o->minimum_span_fraction; r->qc.maximum_pair_difference=o->maximum_pair_difference;
    r->qc.exposure_hdu=o->exposure_hdu; strcpy(r->qc.exposure_key,o->exposure_key);
    r->qc.roi_count=o->roi_count;
    if(o->roi_count) {
        r->qc.rois=a->allocate(a->user,o->roi_count*sizeof(*o->rois));
        if(!r->qc.rois) return MEF_ERR_MEMORY;
        memcpy((void *)r->qc.rois,o->rois,o->roi_count*sizeof(*o->rois));
    }
    for(i=0;i<s->count;++i) {
        if(!exposure(rq->inputs[i].resolved_path,o->exposure_hdu,o->exposure_key,times+i)) return MEF_ERR_INPUT;
        pairs[i]=o->pair_ids?o->pair_ids[i]:i;
        if(pairs[i]>=s->count) return MEF_ERR_INPUT;
    }
    if(o->mode==MEF_BPM_QUICK) for(i=0;i<s->count;++i) {
        for(j=0;j<i;++j) if(pairs[j]==pairs[i]) break;
        if(j<i) continue;
        n=0; for(j=0;j<s->count;++j) if(pairs[j]==pairs[i]) { ++n; if(times[j]!=times[i]) return MEF_ERR_INPUT; }
        if(n!=2) return MEF_ERR_INPUT;
        ++groups;
        for(j=0;j<i;++j) if(times[j]==times[i]) break;
        if(j==i) ++levels;
    }
    return o->mode==MEF_BPM_QUICK && (groups<5 || levels<5)?MEF_ERR_INPUT:MEF_OK;
}
static mef_status load(void *opaque,mef_error **error) {
    file_state *s=opaque;
    const mef_bpm_files_options *o=s->options;
    const mef_bound_detector *d;
    const mef_bias_settings *g=&s->settings.scan;
    unsigned char *all=NULL;
    pixelmap *full=NULL;
    size_t i;
    int width,height,x,y;
    mef_status status;
    s->frames=calloc(s->count,sizeof(*s->frames)); s->borrowed=calloc(s->count,sizeof(*s->borrowed));
    if(!s->frames || !s->borrowed) return MEF_ERR_MEMORY;
    for(i=0;i<s->count;++i) {
        status=mef_layout_load(s->maps[i],s->detector,s->frames+i,error);
        if(status!=MEF_OK) return status;
        s->borrowed[i]=s->frames[i];
    }
    status=mef_layout_load(s->bias_map,s->detector,&s->bias,error);
    if(status!=MEF_OK) return status;
    if(o->mask_encoding==MEF_BPM_MASK_BINARY) {
        status=mef_layout_load_bpm(s->prior_map,s->detector,o->binary_good_value,&full,error);
        if(status!=MEF_OK) return status;
        if(o->prior_active_only) s->binary=full;
        else { s->binary=pixelmap_getvig(full,g->trim[0],g->trim[2],g->trim[1],g->trim[3]); pixelmap_del(full); }
        if(!s->binary) return MEF_ERR_COMPUTATION;
    } else if(o->mask_encoding==MEF_BPM_MASK_FLAGS8) {
        d=mef_layout_find(s->prior_map,s->detector);
        if(pixelmap_flags8_load_checked(mef_layout_map_path(s->prior_map),d->image.hdu_index,o->mask_registry,
            &all,&width,&height)!=0) return MEF_ERR_INPUT;
        if(width!=(int)d->image.axes[0] || height!=(int)d->image.axes[1]) { free(all); return MEF_ERR_INPUT; }
        if(o->prior_active_only) s->flags=all;
        else {
            s->flags=malloc((size_t)s->bias->lx*(size_t)s->bias->ly);
            if(!s->flags) { free(all); return MEF_ERR_MEMORY; }
            for(y=0;y<s->bias->ly;++y) for(x=0;x<s->bias->lx;++x)
                s->flags[y*s->bias->lx+x]=all[(y+g->trim[2]-1)*width+x+g->trim[0]-1];
            free(all);
        }
    }
    return MEF_OK;
}
static mef_status calculate(void *opaque,mef_error **error) {
    file_state *s=opaque;
    mef_bpm_input in;
    mef_bpm_options o;
    mef_bpm_files_qc *q=&s->pending->qc;
    const mef_bpm_qc *service;
    const detector_response_result *response;
    const size_t *indices;
    size_t i,j,k,distinct=0,pairs=0,distinct_times=0,paired_levels=0;
    double *pair_times=NULL;
    double *pair_levels=NULL;
    double lo=DBL_MAX,hi=-DBL_MAX;
    mef_status status;
    memset(&o,0,sizeof(o));
    in.frames=s->borrowed; in.count=s->count; in.configuration_detector=s->config_slot; in.master_bias=s->bias;
    o.prior_binary=s->binary; o.prior_flags=s->flags;
    o.prior_count=s->flags?(size_t)s->bias->lx*(size_t)s->bias->ly:0;
    o.reject_bits=s->options->reject_bits; o.with_mad=s->options->with_mad;
    o.rois=q->rois; o.roi_count=q->roi_count;
    o.saturation_set=1; o.saturation_raw=s->options->saturation_raw; o.upper_fraction=s->options->upper_fraction;
    status=mef_cal_bpm(s->context,&in,&o,&s->pending->service,error);
    if(status!=MEF_OK) return status;
    service=mef_bpm_result_qc(s->pending->service); response=mef_bpm_result_response(s->pending->service);
    indices=mef_bpm_result_fit_indices(s->pending->service);
    if(q->mode==MEF_BPM_QUICK) {
        pair_times=malloc(2*(size_t)response->plane_count*sizeof(*pair_times));
        if(!pair_times) return MEF_ERR_MEMORY;
        pair_levels=pair_times+response->plane_count;
    }
    for(i=0;i<(size_t)response->plane_count;++i) {
        double level=response->reference_levels[i];
        double fraction=service->frames[indices[i]].reference_fraction_median;
        if(!finite_number(level) || level<=0 || !finite_number(fraction)) goto bad;
        if(q->mode!=MEF_BPM_QUICK) {
            if(fraction<lo) lo=fraction;
            if(fraction>hi) hi=fraction;
        }
        for(j=0;j<i;++j) if(response->reference_levels[j]==level) break;
        if(j==i) ++distinct;
        if(q->mode!=MEF_BPM_QUICK) continue;
        for(j=0;j<i;++j) if(q->pair_ids[indices[j]]==q->pair_ids[indices[i]]) break;
        if(j<i) continue;
        for(j=i+1;j<(size_t)response->plane_count;++j) if(q->pair_ids[indices[j]]==q->pair_ids[indices[i]]) break;
        if(j==(size_t)response->plane_count) continue;
        if(!finite_number(response->reference_levels[j]) || response->reference_levels[j]<=0) goto bad;
        if(fabs(level-response->reference_levels[j])/((level+response->reference_levels[j])/2)>
            q->maximum_pair_difference) goto bad;
        fraction=(fraction+service->frames[indices[j]].reference_fraction_median)/2;
        if(fraction<lo) lo=fraction;
        if(fraction>hi) hi=fraction;
        /* Count distinct usable exposure times, not merely differently named pairs. */
        for(k=0;k<distinct_times;++k) if(pair_times[k]==q->integration_seconds[indices[i]]) break;
        if(k==distinct_times) pair_times[distinct_times++]=q->integration_seconds[indices[i]];
        for(k=0;k<paired_levels;++k) if(pair_levels[k]==(level+response->reference_levels[j])/2) break;
        if(k==paired_levels) pair_levels[paired_levels++]=(level+response->reference_levels[j])/2;
        ++pairs;
    }
    if(lo==DBL_MAX || hi==-DBL_MAX) goto bad;
    q->minimum_reference_fraction=lo; q->maximum_reference_fraction=hi; q->span_fraction=hi-lo;
    q->distinct_levels=distinct; q->usable_pairs=pairs; q->distinct_times=distinct_times; q->paired_levels=paired_levels;
    free(pair_times);
    if(hi-lo<q->minimum_span_fraction || distinct<(q->mode==MEF_BPM_QUICK?5:2) ||
        (q->mode==MEF_BPM_QUICK && (pairs<5 || distinct_times<5 || paired_levels<5))) return MEF_ERR_COMPUTATION;
    return MEF_OK;
bad:
    free(pair_times); return MEF_ERR_COMPUTATION;
}
static void cleanup(void *opaque) {
    file_state *s=opaque;
    size_t i;
    if(s->frames) for(i=0;i<s->count;++i) image_del(s->frames[i]);
    free(s->frames); free(s->borrowed); image_del(s->bias); free(s->flags); pixelmap_del(s->binary);
}
mef_status mef_bpm_from_files(mef_context *context,const mef_layout_map *const *maps,size_t count,
    const char *detector,const mef_layout_map *bias,const mef_layout_map *prior,
    const mef_bpm_files_options *options,mef_bpm_files_result **out,mef_error **error) {
    file_state s;
    mef_status status;
    static const mef_operation_steps steps={validate,load,calculate,NULL,cleanup};
    if(!out || *out || (error && *error)) return MEF_ERR_INPUT;
    memset(&s,0,sizeof(s)); s.context=context; s.maps=maps; s.count=count; s.detector=detector;
    s.bias_map=bias; s.prior_map=prior; s.options=options;
    status=mef_operation_run(&steps,&s,error);
    if(status==MEF_OK) { *out=s.pending; return MEF_OK; }
    mef_bpm_files_result_destroy(s.pending);
    if(error && !*error) (void)mef_error_create(status,"BPM file input: incompatible binding, acquisition or signal coverage",NULL,error);
    return status;
}
