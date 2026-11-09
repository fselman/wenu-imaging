#define _POSIX_C_SOURCE 200809L
#include "mef_linearity_archive.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* Metadata and memory-stream buffers use libc, never the image allocator. */
#undef malloc
#undef calloc
#undef free
#undef strdup

#define EVIDENCE_LIMIT (256u*1024u*1024u)
#define STAGE "scan_corrected_master_bias_subtracted"
typedef struct {
    size_t frame, roi;
    char roi_id[65], pair[65];
    double seconds, mean, variance;
    size_t valid;
    int mean_available, variance_available, bounds[4];
} exposure;
struct mef_linearity_archive {
    mef_linearity_archive_options options;
    mef_product_qc product;
    mef_qc_detector_record detector;
    mef_qc_calibration_record calibration[2];
    mef_qc_calibration_binding calibration_binding[2];
    mef_qc_input_record *input;
    mef_qc_input_binding *binding;
    mef_qc_measurement *input_metric, *metric;
    double *input_index;
    exposure *row;
    size_t rows, evidence_bytes;
    mef_qc_text_evidence evidence[256];
    char *configuration, *source_table;
    const char **sources;
    char (*names)[80];
};
static mef_qc_measurement metric(const char *name,const char *unit,const double *value,
    int available,size_t count,const char *const *sources,size_t n)
{
    mef_qc_measurement q={0};
    q.name=name;q.unit=unit;q.stage=STAGE;
    q.state=available?MEF_QC_MEASURED:MEF_QC_UNAVAILABLE;
    q.reason=available?NULL:"native_population_insufficient";
    q.method="native_corrected_common_population";
    q.values=available?value:NULL;q.value_count=available?1:0;
    q.sample_count=count;q.coordinates="FITS-1-based-inclusive";
    q.mask_policy="not_applicable";q.clipping="none";
    q.nonfinite_policy="native_four_plane_common_population";
    q.source_ids=sources;q.source_count=n;
    return q;
}
mef_linearity_archive *mef_linearity_archive_new(const mef_linearity_archive_options *o)
{
    if(!o || !o->input || !o->flat_count || o->flat_count>64 || o->input_count>128 || o->flat_count>=o->input_count ||
        !o->max_roi_rows || o->max_roi_rows>24999 || !o->master || !o->configuration)
        return NULL;
    mef_linearity_archive *a=calloc(1,sizeof(*a));
    if(!a) return NULL;
    a->options=*o;
    a->row=calloc(2*o->max_roi_rows,sizeof(*a->row));
    a->input=calloc(o->input_count,sizeof(*a->input));
    a->binding=calloc(o->input_count,sizeof(*a->binding));
    a->input_metric=calloc(o->input_count,sizeof(*a->input_metric));
    a->input_index=calloc(o->input_count,sizeof(*a->input_index));
    a->sources=calloc(o->input_count,sizeof(*a->sources));
    if(!a->row || !a->input || !a->binding || !a->input_metric || !a->input_index || !a->sources)
        goto fail;
    size_t length=0;
    FILE *stream=open_memstream(&a->configuration,&length);
    if(!stream) goto fail;
    int okay=mef_config_dump(o->configuration,stream)==MEF_OK;
    if(fclose(stream) || !okay) goto fail;
    stream=open_memstream(&a->source_table,&length);
    if(!stream) goto fail;
    fputs("global_index\trole\tinput_index\thdu\tasset\tmaster_accepted\n",stream);
    for(size_t i=0;i<o->input_count;++i) {
        const mef_linearity_archive_source *s=o->input+i;
        if(!s->path || !s->asset || !s->role || s->index<0 || s->hdu<0 ||
            strpbrk(s->asset,"\t\r\n") || strpbrk(s->role,"\t\r\n")) {
            fclose(stream);goto fail;
        }
        a->sources[i]=s->asset;a->input_index[i]=s->index;
        a->input[i]=(mef_qc_input_record){s->asset,s->path,NULL,(uint64_t)s->index};
        a->input_metric[i]=metric("source.input_index","count",a->input_index+i,1,1,a->sources+i,1);
        a->input_metric[i].stage="input_identity";
        a->input_metric[i].method="caller_supplied_original_index";
        a->binding[i]=(mef_qc_input_binding){s->asset,s->hdu,1,NULL,a->input_metric+i,1};
        fprintf(stream,"%zu\t%s\t%d\t%d\t%s\t%d\n",i,s->role,s->index,s->hdu,s->asset,s->master_accepted);
    }
    okay=!ferror(stream);
    if(fclose(stream) || !okay) goto fail;
    a->evidence[0]=(mef_qc_text_evidence){strdup("source-bindings.tsv"),strdup("linearity-preparation-sources/1"),strdup(a->source_table)};
    a->product.evidence_count=1;
    if(!a->evidence[0].name || !a->evidence[0].format || !a->evidence[0].text) goto fail;
    a->evidence_bytes=strlen(a->source_table);
    a->detector=(mef_qc_detector_record){.id=o->detector,.amplifier=o->amplifier,.readout_id=o->readout,
        .configuration_detector=o->configuration_detector,.output_hdu=0,.bin_x=o->bin_x,.bin_y=o->bin_y,
        .inputs=a->binding,.input_count=o->input_count};
    const mef_image_ref *references[]={o->master,o->bpm};
    const char *roles[]={"master_bias","bpm"};
    for(size_t i=0;i<(o->bpm?2u:1u);++i) {
        a->calibration_binding[i]=(mef_qc_calibration_binding){o->detector,references[i]->hdu_index};
        a->calibration[i]=(mef_qc_calibration_record){.id=references[i]->asset_record_id,.path=references[i]->resolved_path,
            .role=roles[i],.bindings=a->calibration_binding+i,.binding_count=1};
    }
    a->product=(mef_product_qc){.id=o->table_path,.fits_path=o->table_path,.log_path=o->log_path,
        .assessment_id=o->table_path,.recipe_name="linearity.prepare",.recipe_start=o->created_at,
        .recipe_version=1,.product_sequence=1,.producer_name="mefpp_linearity_prepare_command",
        .producer_version="1",.source_revision=o->source_revision,.configuration_id="embedded_native_configuration",
        .configuration_snapshot=a->configuration,.inputs=a->input,.input_count=o->input_count,
        .detectors=&a->detector,.detector_count=1,.calibrations=a->calibration,.calibration_count=o->bpm?2:1,
        .table_name="linearity_preparation",.evidence=a->evidence,.evidence_count=1,
        .operation_context_format="linearity-preparation/1",
        .operation_context_snapshot="measurement_stage=scan_corrected_master_bias_subtracted; noise_state=unavailable; covariance=unavailable; fit_state=not_performed; scientific_acceptance=false; input_order=flats_then_biases; master_accepted_applies_only_to_master_construction"};
    return a;
fail:
    mef_linearity_archive_destroy(a);return NULL;
}
int mef_linearity_archive_add_pair(mef_linearity_archive *a,const mef_linearity_files_result *r)
{
    if(!a || !r || !r->prepared || a->metric) return 0;
    const mef_linearity_prepared_result *p=r->prepared;
    if(p->raw->rows>a->options.max_roi_rows-a->rows/2) return 0;
    for(size_t i=0;i<p->raw->rows;++i) for(int member=0;member<2;++member) {
        const mef_linearity_pair_row *raw=p->raw->row+i;
        const mef_linearity_frame *f=p->raw->frame+(member?raw->second:raw->first);
        const image_sample_stats *v=member?&p->row[i].second:&p->row[i].first;
        size_t frame=0;
        while(frame<a->options.flat_count && strcmp(a->options.input[frame].asset,f->asset_id)) ++frame;
        if(frame==a->options.flat_count || a->options.input[frame].hdu!=f->hdu ||
            a->options.input[frame].index!=f->input_index) return 0;
        exposure *e=a->row+a->rows++;
        e->frame=frame;e->roi=(size_t)raw->roi;
        const detector_roi *roi=&p->raw->bias[raw->roi].roi;
        if(strlen(roi->roi_id)>=sizeof(e->roi_id) || strlen(f->pair_id)>=sizeof(e->pair)) return 0;
        strcpy(e->roi_id,roi->roi_id);strcpy(e->pair,f->pair_id);
        e->seconds=f->seconds;e->mean=v->mean;e->variance=v->stdev*v->stdev;
        e->valid=v->valid_pixels;e->mean_available=v->level_available;e->variance_available=v->stdev_available;
        e->bounds[0]=roi->xmin;e->bounds[1]=roi->xmax;e->bounds[2]=roi->ymin;e->bounds[3]=roi->ymax;
    }
    return 1;
}
int mef_linearity_archive_add_evidence(mef_linearity_archive *a,const char *name,const char *format,const char *path)
{
    if(!a || !name || !format || a->product.evidence_count>=256) return 0;
    FILE *f=fopen(path,"rb");struct stat st;
    if(!f) return 0;
    char *data=NULL;int okay=0;
    if(fstat(fileno(f),&st) || !S_ISREG(st.st_mode) || st.st_size<=0 ||
        st.st_size>64*1024*1024 || (size_t)st.st_size>EVIDENCE_LIMIT-a->evidence_bytes) goto done;
    data=malloc((size_t)st.st_size+1);
    if(!data || fread(data,1,(size_t)st.st_size,f)!=(size_t)st.st_size || fgetc(f)!=EOF || ferror(f) ||
        memchr(data,0,(size_t)st.st_size)) goto done;
    data[st.st_size]=0;
    mef_qc_text_evidence *e=a->evidence+a->product.evidence_count++;
    *e=(mef_qc_text_evidence){strdup(name),strdup(format),data};data=NULL;
    okay=e->name && e->format;
    a->evidence_bytes+=(size_t)st.st_size;
done:
    free(data);if(fclose(f)) okay=0;return okay;
}
static int exposure_order(const void *left,const void *right)
{
    const exposure *a=left,*b=right;
    if(a->frame!=b->frame) return a->frame<b->frame?-1:1;
    return a->roi<b->roi?-1:a->roi>b->roi;
}
int mef_linearity_archive_table(mef_linearity_archive *a)
{
    if(!a || !a->rows || a->metric) return 0;
    qsort(a->row,a->rows,sizeof(*a->row),exposure_order);
    a->metric=calloc(2*a->rows+1,sizeof(*a->metric));
    a->names=calloc(2*a->rows,sizeof(*a->names));
    if(!a->metric || !a->names) return 0;
    for(size_t i=0;i<a->rows;++i) {
        exposure *e=a->row+i;
        if(i && e->frame==a->row[i-1].frame && e->roi==a->row[i-1].roi) return 0;
        for(size_t j=0;j<2;++j) {
            size_t k=2*i+j;
            snprintf(a->names[k],sizeof(*a->names),"exposure.%zu.%s",i,j?"spatial_variance_adu2":"signal_adu");
            a->metric[k]=metric(a->names[k],j?"ADU2":"ADU",j?&e->variance:&e->mean,
                j?e->variance_available:e->mean_available,e->valid,a->sources+e->frame,1);
            memcpy(a->metric[k].bounds,e->bounds,sizeof(e->bounds));
            a->metric[k].mask_policy=a->options.bpm?"applied":"omitted";
            a->metric[k].mask_id=a->options.bpm?a->options.bpm->asset_record_id:NULL;
        }
    }
    a->metric[2*a->rows]=metric("absolute_noise_covariance","ADU2",NULL,0,0,a->sources,1);
    a->metric[2*a->rows].reason="reviewed_absolute_noise_covariance_model_unavailable";
    a->detector.measurements=a->metric;a->detector.measurement_count=2*a->rows+1;
    char diagnostic[256];
    if(mef_product_qc_validate(&a->product,diagnostic,sizeof diagnostic)) {
        fprintf(stderr,"Preparation metadata: %s\n",diagnostic);return 0;
    }
    int fd=open(a->options.table_path,O_WRONLY|O_CREAT|O_EXCL,0600);
    if(fd<0) return 0;
    FILE *f=fdopen(fd,"wb");
    if(!f) {close(fd);return 0;}
    fputs("detector\troi\tinput_index\tasset\thdu\tpair_id\texposure_seconds\tsignal_adu\tspatial_variance_adu2\tvalid_pixels\n",f);
    for(size_t i=0;i<a->rows;++i) {
        const exposure *e=a->row+i;
        const mef_linearity_archive_source *s=a->options.input+e->frame;
        fprintf(f,"%s\t%s\t%d\t%s\t%d\t%s\t%.17g\t",a->options.detector,e->roi_id,s->index,s->asset,s->hdu,e->pair,e->seconds);
        if(e->mean_available) fprintf(f,"%.17g",e->mean);
        fputc('\t',f);
        if(e->variance_available) fprintf(f,"%.17g",e->variance);
        fprintf(f,"\t%zu\n",e->valid);
    }
    int okay=!ferror(f);if(fclose(f)) okay=0;
    return okay && mef_linearity_archive_add_evidence(a,"exposure-table.tsv","linearity-preparation-exposures/1",a->options.table_path);
}
const mef_product_qc *mef_linearity_archive_view(const mef_linearity_archive *a)
{return a?&a->product:NULL;}
void mef_linearity_archive_destroy(mef_linearity_archive *a)
{
    if(!a) return;
    for(size_t i=0;i<a->product.evidence_count;++i) {
        free((void *)a->evidence[i].name);free((void *)a->evidence[i].format);free((void *)a->evidence[i].text);
    }
    free(a->configuration);free(a->source_table);free(a->sources);free(a->input);
    free(a->binding);free(a->input_metric);free(a->input_index);free(a->row);free(a->metric);free(a->names);free(a);
}
