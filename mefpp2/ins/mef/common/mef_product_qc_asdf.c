#define _POSIX_C_SOURCE 200809L
#include "mef_product_qc.h"
#include "mef_bpm_assembly_qc.h"
#include <asdf/config.h>
#ifdef MEF_ASDF_OMIT_FLOAT16
#undef ASDF_HAVE_FLOAT16
#endif
#include <asdf/file.h>
#include <asdf/value.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* Construct detached mappings directly, then transfer once. Never insert a
 * second nested sibling through a path: validated libasdf0.3 workaround #219.
 * Container wrappers transfer only on success; failed insertions destroy them. */
static int map(asdf_mapping_t *parent,const char *key,asdf_mapping_t *child)
{
    if(child==NULL) return 0;
    if(asdf_mapping_set_mapping(parent,key,child)==ASDF_VALUE_OK) return 1;
    asdf_mapping_destroy(child); return 0;
}
static int seq(asdf_mapping_t *parent,const char *key,asdf_sequence_t *child)
{
    if(child==NULL) return 0;
    if(asdf_mapping_set_sequence(parent,key,child)==ASDF_VALUE_OK) return 1;
    asdf_sequence_destroy(child); return 0;
}
static int append(asdf_sequence_t *parent,asdf_mapping_t *child)
{
    if(child==NULL) return 0;
    if(asdf_sequence_append_mapping(parent,child)==ASDF_VALUE_OK) return 1;
    asdf_mapping_destroy(child); return 0;
}
static int string(asdf_mapping_t *m,const char *key,const char *value)
{ return asdf_mapping_set_string0(m,key,value)==ASDF_VALUE_OK; }
static int nullable(asdf_mapping_t *m,const char *key,const char *value)
{ return value?string(m,key,value):asdf_mapping_set_null(m,key)==ASDF_VALUE_OK; }
static int count(asdf_mapping_t *m,const char *key,uint64_t value)
{ return asdf_mapping_set_uint64(m,key,value)==ASDF_VALUE_OK; }
static const char *leaf(const char *path)
{ const char *p=strrchr(path,'/'); return p?p+1:path; }
static asdf_mapping_t *file_record(asdf_file_t *f,const char *id,const char *path,const char *hash,const char *kind)
{
    asdf_mapping_t *m=asdf_mapping_create(f);
    if(m==NULL) return NULL;
    if(!string(m,"id",id)||!string(m,"filename",leaf(path))||!string(m,"location",path)||
       !string(m,"kind",kind)||!nullable(m,"sha256",hash)||
       !string(m,"integrity",hash?"caller_supplied_digest":"not_content_verified")) {
        asdf_mapping_destroy(m);return NULL;
    }
    return m;
}
static asdf_mapping_t *measurement(asdf_file_t *f,const mef_qc_measurement *q)
{
    asdf_mapping_t *m=asdf_mapping_create(f),*definition=NULL,*region=NULL;
    asdf_sequence_t *sources=NULL,*bounds=NULL,*values=NULL;
    size_t i;int okay;
    if(m==NULL) return NULL;
    okay=string(m,"name",q->name)&&string(m,"unit",q->unit)&&
        string(m,"status",q->state==MEF_QC_MEASURED?"measured":q->state==MEF_QC_UNAVAILABLE?"unavailable":"invalid")&&
        nullable(m,"reason",q->reason);
    if(okay && q->state!=MEF_QC_MEASURED) okay=asdf_mapping_set_null(m,"value")==ASDF_VALUE_OK;
    else if(okay && !q->vector) okay=!strcmp(q->unit,"count")?
        count(m,"value",(uint64_t)q->values[0]):asdf_mapping_set_double(m,"value",q->values[0])==ASDF_VALUE_OK;
    else if(okay) {
        values=asdf_sequence_create(f);okay=values!=NULL;
        for(i=0;okay && i<q->value_count;++i) okay=(!strcmp(q->unit,"count")?
            asdf_sequence_append_uint64(values,(uint64_t)q->values[i]):
            asdf_sequence_append_double(values,q->values[i]))==ASDF_VALUE_OK;
        if(okay){okay=seq(m,"value",values);values=NULL;}
    }
    definition=asdf_mapping_create(f);region=asdf_mapping_create(f);
    bounds=asdf_sequence_create(f);sources=asdf_sequence_create(f);
    okay=okay && definition!=NULL && region!=NULL && bounds!=NULL && sources!=NULL;
    for(i=0;okay && i<4;++i) okay=asdf_sequence_append_int32(bounds,q->bounds[i])==ASDF_VALUE_OK;
    if(okay) { okay=seq(region,"bounds",bounds);bounds=NULL; }
    if(okay) okay=string(region,"coordinates",q->coordinates)&&
        string(region,"detector_bpm",q->mask_policy)&&nullable(region,"mask_record_id",q->mask_id)&&
        string(region,"clipping",q->clipping)&&string(region,"nonfinite",q->nonfinite_policy);
    if(okay) { okay=map(definition,"region",region);region=NULL; }
    if(okay) okay=string(definition,"stage",q->stage)&&nullable(definition,"method",q->method)&&
        count(definition,"sample_count",q->sample_count);
    if(okay) { okay=map(m,"definition",definition);definition=NULL; }
    for(i=0;okay && i<q->source_count;++i) okay=asdf_sequence_append_string0(sources,q->source_ids[i])==ASDF_VALUE_OK;
    if(okay){okay=seq(m,"sources",sources);sources=NULL;}
    asdf_mapping_destroy(definition);asdf_mapping_destroy(region);
    asdf_sequence_destroy(values);asdf_sequence_destroy(bounds);asdf_sequence_destroy(sources);
    if(!okay){asdf_mapping_destroy(m);return NULL;}
    return m;
}
static asdf_sequence_t *measurements(asdf_file_t *f,const mef_qc_measurement *q,size_t n)
{
    asdf_sequence_t *s=asdf_sequence_create(f);size_t i;
    if(s==NULL)return NULL;
    for(i=0;i<n;++i) if(!append(s,measurement(f,q+i))){asdf_sequence_destroy(s);return NULL;}
    return s;
}
static asdf_mapping_t *detector(asdf_file_t *f,const mef_qc_detector_record *d,int table)
{
    asdf_mapping_t *m=asdf_mapping_create(f);
    if(m==NULL)return NULL;
    if(!string(m,"detector_id",d->id)||!string(m,"amplifier",d->amplifier)||!string(m,"readout_id",d->readout_id)||
        !count(m,"configuration_detector",d->configuration_detector)||
        (!table && !count(m,"output_hdu",(uint64_t)d->output_hdu))||
        !count(m,"bin_x",(uint64_t)d->bin_x)||!count(m,"bin_y",(uint64_t)d->bin_y)||
        !seq(m,"measurements",measurements(f,d->measurements,d->measurement_count))) {
        asdf_mapping_destroy(m);return NULL;
    }
    if (d->median_even_handling && !string(m,"median_even_handling",d->median_even_handling)) {
        asdf_mapping_destroy(m);return NULL;
    }
    return m;
}
static asdf_mapping_t *input_record(asdf_file_t *f,const mef_product_qc *p,size_t index)
{
    const mef_qc_input_record *input=p->inputs+index;
    asdf_mapping_t *m=asdf_mapping_create(f),*d=NULL;
    asdf_sequence_t *detectors=asdf_sequence_create(f);
    size_t i;int okay=m!=NULL && detectors!=NULL;
    if(okay)okay=string(m,"record_id",input->id)&&count(m,"original_index",input->original_index)&&
        map(m,"file",file_record(f,input->id,input->path,input->sha256,"raw"));
    for(i=0;okay && i<p->detector_count;++i) {
        const mef_qc_detector_record *source=p->detectors+i;
        const mef_qc_input_binding *b=source->inputs+index;
        d=asdf_mapping_create(f);okay=d!=NULL;
        if(okay)okay=string(d,"detector_id",source->id)&&count(d,"source_hdu",(uint64_t)b->source_hdu)&&
            count(d,"configuration_detector",source->configuration_detector)&&
            seq(d,"measurements",measurements(f,b->measurements,b->measurement_count));
        if(okay){okay=append(detectors,d);d=NULL;}
    }
    if(okay){okay=seq(m,"detectors",detectors);detectors=NULL;}
    asdf_mapping_destroy(d);asdf_sequence_destroy(detectors);
    if(!okay){asdf_mapping_destroy(m);return NULL;}
    return m;
}
static asdf_mapping_t *input_membership(asdf_file_t *f,const mef_product_qc *p,size_t index)
{
    asdf_mapping_t *m=asdf_mapping_create(f),*d=NULL;
    asdf_sequence_t *decisions=asdf_sequence_create(f);
    size_t i;int okay=m!=NULL && decisions!=NULL;
    if(okay)okay=count(m,"index",(uint64_t)index)&&count(m,"original_index",p->inputs[index].original_index)&&
        string(m,"file_id",p->inputs[index].id)&&string(m,"record_id",p->inputs[index].id);
    for(i=0;okay && i<p->detector_count;++i) {
        const mef_qc_input_binding *b=p->detectors[i].inputs+index;
        d=asdf_mapping_create(f);okay=d!=NULL;
        if(okay)okay=string(d,"detector_id",p->detectors[i].id)&&
            string(d,"status",b->accepted?"used":"rejected")&&nullable(d,"reason",b->rejection_reason);
        if(okay){okay=append(decisions,d);d=NULL;}
    }
    if(okay){okay=seq(m,"participation_by_detector",decisions);decisions=NULL;}
    asdf_mapping_destroy(d);asdf_sequence_destroy(decisions);
    if(!okay){asdf_mapping_destroy(m);return NULL;}
    return m;
}
static asdf_mapping_t *calibration_record(asdf_file_t *f,const mef_qc_calibration_record *c)
{
    asdf_mapping_t *m=asdf_mapping_create(f),*d=NULL;
    asdf_sequence_t *bindings=asdf_sequence_create(f);size_t i;int okay=m!=NULL && bindings!=NULL;
    if(okay)okay=string(m,"record_id",c->id)&&string(m,"role",c->role)&&nullable(m,"qc_location",c->qc_path)&&
        map(m,"file",file_record(f,c->id,c->path,c->sha256,"product"));
    for(i=0;okay && i<c->binding_count;++i){
        d=asdf_mapping_create(f);okay=d!=NULL;
        if(okay)okay=string(d,"detector_id",c->bindings[i].detector_id)&&
            count(d,"source_hdu",(uint64_t)c->bindings[i].source_hdu);
        if(okay){okay=append(bindings,d);d=NULL;}
    }
    if(okay){okay=seq(m,"detector_bindings",bindings);bindings=NULL;}
    asdf_mapping_destroy(d);asdf_sequence_destroy(bindings);
    if(!okay){asdf_mapping_destroy(m);return NULL;}return m;
}
static asdf_mapping_t *header_card(asdf_file_t *f,const mef_qc_fits_card *c,const char *source)
{
    asdf_mapping_t *m=asdf_mapping_create(f);
    int okay=m!=NULL;
    if(okay)okay=string(m,"source_file",source)&&string(m,"keyword",c->keyword)&&
        string(m,"role",c->detector_id?"detector":"primary")&&
        count(m,"hdu",(uint64_t)c->hdu)&&nullable(m,"detector_id",c->detector_id)&&
        string(m,"status",c->present?"present":"missing")&&string(m,"value_type",c->type)&&
        nullable(m,"fits_value",c->present?c->fits_value:NULL)&&
        nullable(m,"comment",c->present?c->comment:NULL)&&
        nullable(m,"card",c->present?c->card:NULL);
    if(okay) {
        if(!strcmp(c->type,"missing")||!strcmp(c->type,"undefined"))
            okay=asdf_mapping_set_null(m,"value")==ASDF_VALUE_OK;
        else if(!strcmp(c->type,"integer"))okay=asdf_mapping_set_int64(m,"value",c->integer)==ASDF_VALUE_OK;
        else if(!strcmp(c->type,"real"))okay=asdf_mapping_set_double(m,"value",c->real)==ASDF_VALUE_OK;
        else if(!strcmp(c->type,"boolean"))okay=asdf_mapping_set_bool(m,"value",c->boolean!=0)==ASDF_VALUE_OK;
        else okay=string(m,"value",c->value);
    }
    if(!okay){asdf_mapping_destroy(m);return NULL;}return m;
}
static int header_provenance(asdf_file_t *f,asdf_mapping_t *provenance,const mef_product_qc *p)
{
    asdf_mapping_t *config=NULL;asdf_sequence_t *cards=NULL;size_t i;int okay=1;
    if(p->recipe_config_path) {
        config=asdf_mapping_create(f);
        okay=config&&string(config,"path",p->recipe_config_path)&&
            string(config,"format","bias-recipe-toml/1")&&string(config,"snapshot",p->recipe_config_snapshot);
        if(okay){okay=map(provenance,"recipe_configuration",config);config=NULL;}
    }
    if(okay&&p->header_card_count) {
        cards=asdf_sequence_create(f);okay=cards!=NULL;
        for(i=0;okay&&i<p->header_card_count;++i)okay=append(cards,header_card(f,p->header_cards+i,p->fits_path));
        if(okay){okay=seq(provenance,"fits_headers",cards);cards=NULL;}
    }
    asdf_mapping_destroy(config);asdf_sequence_destroy(cards);return okay;
}
static asdf_mapping_t *container(asdf_file_t *f,const mef_product_qc *p)
{
    asdf_mapping_t *root=asdf_mapping_create(f),*record=NULL,*provenance=NULL,*producer=NULL,*configuration=NULL,*characterization=NULL,*extensions=NULL;
    asdf_sequence_t *detectors=NULL,*inputs=NULL,*embedded=NULL,*calibrations=NULL;
    size_t i;int okay=root!=NULL;
    if(okay)okay=map(root,"file",file_record(f,p->id,p->fits_path,p->sha256,"product"));
    record=asdf_mapping_create(f);producer=asdf_mapping_create(f);provenance=asdf_mapping_create(f);
    configuration=asdf_mapping_create(f);characterization=asdf_mapping_create(f);extensions=asdf_mapping_create(f);
    detectors=asdf_sequence_create(f);inputs=asdf_sequence_create(f);embedded=asdf_sequence_create(f);calibrations=asdf_sequence_create(f);
    okay=okay && record!=NULL && producer!=NULL && provenance!=NULL && configuration!=NULL &&
        characterization!=NULL && extensions!=NULL && detectors!=NULL && inputs!=NULL && embedded!=NULL && calibrations!=NULL;
    if(okay)okay=string(record,"schema_version",MEF_PRODUCT_QC_SCHEMA)&&string(record,"assessment_id",p->assessment_id)&&
        string(record,"created_at",p->recipe_start);
    if(okay){okay=map(root,"record",record);record=NULL;}
    if(okay)okay=string(producer,"name",p->producer_name)&&string(producer,"version",p->producer_version)&&
        string(producer,"source_revision",p->source_revision);
    if(okay){okay=map(provenance,"producer",producer);producer=NULL;}
    if(okay)okay=string(configuration,"id",p->configuration_id)&&
        string(configuration,"format","mef_config_dump_typed_bits_json")&&string(configuration,"snapshot",p->configuration_snapshot);
    if(okay){okay=map(provenance,"configuration",configuration);configuration=NULL;}
    if(okay)okay=string(provenance,"operation",p->recipe_name)&&count(provenance,"operation_version",p->recipe_version)&&
        string(provenance,"recipe_start",p->recipe_start)&&count(provenance,"product_sequence",p->product_sequence)&&
        string(provenance,"log_path",p->log_path);
    if(okay&&p->qc_profile)okay=string(provenance,"qc_profile",p->qc_profile);
    if(okay)okay=header_provenance(f,provenance,p);
    if(okay){okay=map(root,"provenance",provenance);provenance=NULL;}
    for(i=0;okay && i<p->detector_count;++i)okay=append(detectors,detector(f,p->detectors+i,p->table_name!=NULL));
    if(okay){okay=seq(characterization,"detectors",detectors);detectors=NULL;}
    if(okay){okay=map(root,"characterization",characterization);characterization=NULL;}
    for(i=0;okay && i<p->input_count;++i)okay=append(inputs,input_membership(f,p,i))&&append(embedded,input_record(f,p,i));
    if(okay){okay=seq(root,"inputs",inputs);inputs=NULL;}
    if(okay){okay=seq(root,"embedded_input_records",embedded);embedded=NULL;}
    for(i=0;okay && i<p->calibration_count;++i)okay=append(calibrations,calibration_record(f,p->calibrations+i));
    if(okay){okay=seq(root,"calibrations",calibrations);calibrations=NULL;}
    if(okay)okay=string(extensions,"record_scope",p->table_name?"one_final_table_product":p->primary_image?"one_final_primary_image_product":"one_final_MEF_product")&&
        string(extensions,"input_reference_policy","embedded_record_id")&&
        string(extensions,"measurement_policy","caller_supplied_values_only");
    if(okay && p->table_name) okay=string(extensions,"table_name",p->table_name);
    if(okay && p->evidence_count) {
        asdf_sequence_t *evidence=asdf_sequence_create(f);
        okay=evidence!=NULL;
        for(i=0;okay && i<p->evidence_count;++i) {
            const mef_qc_text_evidence *e=p->evidence+i;
            asdf_mapping_t *item=asdf_mapping_create(f);
            okay=item && string(item,"name",e->name) && string(item,"format",e->format) && string(item,"text",e->text);
            if(okay) {okay=append(evidence,item);item=NULL;}
            asdf_mapping_destroy(item);
        }
        if(okay) {okay=seq(extensions,"native_evidence",evidence);evidence=NULL;}
        asdf_sequence_destroy(evidence);
    }
    if(okay && p->bpm_registry) okay=string(extensions,"bpm_registry",p->bpm_registry);
    if(okay && p->operation_context_format) {
        asdf_mapping_t *context=asdf_mapping_create(f);
        okay=context && string(context,"format",p->operation_context_format) &&
            string(context,"snapshot",p->operation_context_snapshot);
        if(okay) {okay=map(extensions,"operation_context",context);context=NULL;}
        asdf_mapping_destroy(context);
    }
    if(okay){okay=map(root,"extensions",extensions);extensions=NULL;}
    asdf_mapping_destroy(record);asdf_mapping_destroy(provenance);asdf_mapping_destroy(producer);
    asdf_mapping_destroy(configuration);asdf_mapping_destroy(characterization);asdf_mapping_destroy(extensions);
    asdf_sequence_destroy(detectors);asdf_sequence_destroy(inputs);asdf_sequence_destroy(embedded);asdf_sequence_destroy(calibrations);
    if(!okay){asdf_mapping_destroy(root);return NULL;}
    return root;
}
int mef_product_qc_write(const char *path,const mef_product_qc *p,char *message,size_t size)
{
    asdf_file_t *f=NULL,*saved=NULL;
    asdf_mapping_t *root=NULL;
    asdf_sequence_t *detectors=NULL,*inputs=NULL;
    char *temporary=NULL,expected[4096],first[128],second[128];
    void *readback=NULL;
    const char *value=NULL;
    struct stat st;FILE *header=NULL;
    size_t n,readback_size;int fd=-1,code=-1,temporary_owned=0;
    const char *detail="Cannot construct native ASDF QC";
    if(mef_product_qc_validate(p,message,size)!=0)return -1;
    n=strlen(p->fits_path);
    if(path==NULL || snprintf(expected,sizeof(expected),"%.*s.asdf",(int)(n-(p->table_name?4:5)),p->fits_path)>=(int)sizeof(expected)||
        strcmp(path,expected)) {detail="ASDF must inherit the final product basename and directory";goto done;}
    if(stat(p->fits_path,&st)!=0||!S_ISREG(st.st_mode)||st.st_size==0){detail="Final product is missing or empty";goto done;}
    if(lstat(path,&st)==0||errno!=ENOENT){detail="ASDF destination exists or is inaccessible";goto done;}
    f=asdf_open_mem_ex(NULL,0,NULL);if(f==NULL)goto done;
    root=container(f,p);if(root==NULL)goto done;
    if(asdf_set_mapping(f,"qc",root)!=ASDF_VALUE_OK)goto done;
    root=NULL;
    temporary=malloc(strlen(path)+32);if(temporary==NULL)goto done;
    snprintf(temporary,strlen(path)+32,"%s.tmp-XXXXXX",path);
    fd=mkstemp(temporary);if(fd<0)goto done;temporary_owned=1;
    if(close(fd)!=0){fd=-1;goto done;}fd=-1;
    detail="Native ASDF write or readback failed";
    if(asdf_write_to_file(f,temporary)!=0)goto done;
    asdf_close(f);f=NULL;
    header=fopen(temporary,"rb");if(header==NULL)goto done;
    if(fgets(first,sizeof(first),header)==NULL||fgets(second,sizeof(second),header)==NULL)goto done;
    if(strncmp(first,"#ASDF ",6)||strcmp(second,"#ASDF_STANDARD 1.6.0\n")){
        detail="Native library did not emit the qualified ASDF1.6 standard";goto done;
    }
    /* libasdf0.3 file-backed tree parsing hangs on a target-confirmed valid
     * sidecar (#267). Read these exact staged bytes through its qualified
     * memory interface instead. This buffer contains QC metadata, not images;
     * keep it alive until the native reader and all its views are closed. */
    if(fstat(fileno(header),&st)!=0 || !S_ISREG(st.st_mode) || st.st_size<=0 ||
        (uintmax_t)st.st_size>(uintmax_t)SIZE_MAX || fseek(header,0,SEEK_SET)!=0)goto done;
    readback_size=(size_t)st.st_size;
    readback=malloc(readback_size);if(readback==NULL)goto done;
    if(fread(readback,1,readback_size,header)!=readback_size ||
        fgetc(header)!=EOF || ferror(header))goto done;
    if(fclose(header)!=0){header=NULL;goto done;}header=NULL;
    saved=asdf_open_mem_ex(readback,readback_size,NULL);if(saved==NULL)goto done;
    if(asdf_get_string0(saved,"qc/record/schema_version",&value)!=ASDF_VALUE_OK||strcmp(value,MEF_PRODUCT_QC_SCHEMA)||
        asdf_get_string0(saved,"qc/file/id",&value)!=ASDF_VALUE_OK||strcmp(value,p->id)||
        asdf_get_sequence(saved,"qc/characterization/detectors",&detectors)!=ASDF_VALUE_OK||
        asdf_sequence_size(detectors)!=(int)p->detector_count||
        asdf_get_sequence(saved,"qc/embedded_input_records",&inputs)!=ASDF_VALUE_OK||
        asdf_sequence_size(inputs)!=(int)p->input_count)goto done;
    asdf_sequence_destroy(detectors);detectors=NULL;asdf_sequence_destroy(inputs);inputs=NULL;
    asdf_close(saved);saved=NULL;
    free(readback);readback=NULL;
    detail="Cannot exclusively publish ASDF product";
    if(link(temporary,path)!=0)goto done;
    code=0;
done:
    if(fd>=0)close(fd);
    if(header!=NULL)fclose(header);
    asdf_sequence_destroy(detectors);asdf_sequence_destroy(inputs);
    asdf_mapping_destroy(root);if(saved!=NULL)asdf_close(saved);if(f!=NULL)asdf_close(f);
    free(readback);
    if(temporary!=NULL){
        if(temporary_owned && unlink(temporary)!=0 && code==0){
            /* Final ASDF already exists and is complete; report retained staging. */
            if(message!=NULL && size)snprintf(message,size,"ASDF complete; staging retained: %s",temporary);
            free(temporary);return 0;
        }
        free(temporary);
    }
    if(message!=NULL && size)snprintf(message,size,"%s",code==0?"":detail);
    return code;
}

/* Recovery is explicitly caller-verified metadata reuse, not recipe replay.
 * The caller independently checks FITS values/pixels and the complete new tree
 * before exclusively publishing the staged bytes. No source file is modified. */
static int recovery_count(asdf_file_t *f,const char *path)
{
    asdf_sequence_t *s=NULL; int n=-1;
    if(asdf_get_sequence(f,path,&s)==ASDF_VALUE_OK) n=asdf_sequence_size(s);
    asdf_sequence_destroy(s); return n;
}
static asdf_mapping_t *recovery_mapping(asdf_file_t *f,const char *path)
{
    asdf_mapping_t *m=NULL;
    if(asdf_get_mapping(f,path,&m)!=ASDF_VALUE_OK) return NULL;
    return m;
}
static int recovery_set(asdf_file_t *f,const char *path,const char *key,const char *value)
{
    asdf_mapping_t *m=recovery_mapping(f,path);
    int okay=m!=NULL && asdf_mapping_set_string0(m,key,value)==ASDF_VALUE_OK;
    asdf_mapping_destroy(m); return okay;
}
static int recovery_copy(asdf_file_t *f,asdf_mapping_t *parent,const char *key,const char *path)
{
    asdf_mapping_t *m=recovery_mapping(f,path),*copy=NULL; int okay;
    if(m) copy=asdf_mapping_copy(m);
    asdf_mapping_destroy(m); okay=map(parent,key,copy); return okay;
}
static int recovery_read(const char *path,void **out,size_t *length)
{
    FILE *stream=fopen(path,"rb"); struct stat st; void *buffer=NULL; int okay=0;
    if(!stream) return 0;
    if(fstat(fileno(stream),&st) || !S_ISREG(st.st_mode) || st.st_size<=0 ||
       (uintmax_t)st.st_size>64u*1024u*1024u) goto done;
    buffer=malloc((size_t)st.st_size); if(!buffer) goto done;
    if(fread(buffer,1,(size_t)st.st_size,stream)!=(size_t)st.st_size ||
       fgetc(stream)!=EOF || ferror(stream)) goto done;
    *out=buffer; *length=(size_t)st.st_size; buffer=NULL; okay=1;
done:
    free(buffer); if(fclose(stream)) okay=0; return okay;
}
int mef_product_qc_recover_verified(const mef_qc_recovery *r,char *message,size_t size)
{
    asdf_file_t *f=NULL,*saved=NULL; asdf_mapping_t *recovery=NULL;
    asdf_sequence_t *sources=NULL; asdf_mapping_t *measurement=NULL;
    void *buffer=NULL,*readback=NULL; size_t length=0,readback_length=0;
    const char *value=NULL,*basename; char *old_id=NULL;
    char path[256],source_path[288]; int nd,nm,ns,d,m,j,fd=-1,code=-1;
    FILE *stream=NULL; struct stat st; int owned=0;
    const char *detail="Invalid recovery request";
    if(!r || !r->reference_asdf || !r->fits_path || !r->staging_path ||
       !r->failed_log || !r->assembly_log || !r->created_at || !r->recipe_start || !r->source_revision ||
       r->reference_asdf[0]!='/' || r->fits_path[0]!='/' || r->staging_path[0]!='/' ||
       strlen(r->source_revision)!=40 || strspn(r->source_revision,"0123456789abcdef")!=40 ||
       strlen(r->created_at)!=24 || strlen(r->recipe_start)!=24) goto done;
    if(stat(r->fits_path,&st) || !S_ISREG(st.st_mode) ||
       stat(r->failed_log,&st) || !S_ISREG(st.st_mode) ||
       stat(r->assembly_log,&st) || !S_ISREG(st.st_mode)) goto done;
    detail="Cannot read reference QC through native memory interface";
    if(!recovery_read(r->reference_asdf,&buffer,&length) ||
       (f=asdf_open_mem_ex(buffer,length,NULL))==NULL) goto done;
    if(asdf_get_string0(f,"qc/record/schema_version",&value)!=ASDF_VALUE_OK || strcmp(value,"2.0.0") ||
       asdf_get_string0(f,"qc/file/id",&value)!=ASDF_VALUE_OK || !(old_id=strdup(value))) goto done;
    if(asdf_get_string0(f,"qc/file/location",&value)!=ASDF_VALUE_OK || strcmp(value,old_id)) goto done;
    nd=recovery_count(f,"qc/characterization/detectors");
    if(nd<1 || nd>4096 || recovery_count(f,"qc/embedded_input_records")<1) goto done;
    detail="Cannot preserve reference recovery provenance";
    recovery=asdf_mapping_create(f);
    if(!recovery || !string(recovery,"method","verified_reference_qc_reuse") ||
       !string(recovery,"status","recovered_product_qc") ||
       !string(recovery,"original_recipe_status","incomplete_after_assembly_failure") ||
       !string(recovery,"reference_asdf",r->reference_asdf) ||
       !string(recovery,"failed_recipe_log",r->failed_log) ||
       !string(recovery,"assembly_recovery_log",r->assembly_log) ||
       !string(recovery,"recovered_at",r->created_at) ||
       !string(recovery,"recovery_tool_source_revision",r->source_revision) ||
       !string(recovery,"measurement_policy","reference_values_definitions_arrays_and_inputs_preserved") ||
       !string(recovery,"verification_basis","caller_verified_FITS_scalar_context_and_prior_pixel_comparison") ||
       !recovery_copy(f,recovery,"reference_product","qc/file") ||
       !recovery_copy(f,recovery,"reference_record","qc/record") ||
       !recovery_copy(f,recovery,"reference_provenance","qc/provenance")) goto done;
    detail="Cannot update recovered product identity";
    basename=strrchr(r->fits_path,'/'); basename=basename?basename+1:r->fits_path;
    if(!recovery_set(f,"qc/file","id",r->fits_path) ||
       !recovery_set(f,"qc/file","location",r->fits_path) ||
       !recovery_set(f,"qc/file","filename",basename) ||
       !recovery_set(f,"qc/record","assessment_id",r->fits_path) ||
       !recovery_set(f,"qc/record","created_at",r->created_at) ||
       !recovery_set(f,"qc/provenance/producer","name","mefpp_product_qc_recover_verified") ||
       !recovery_set(f,"qc/provenance/producer","version","1") ||
       !recovery_set(f,"qc/provenance/producer","source_revision",r->source_revision) ||
       !recovery_set(f,"qc/provenance","recipe_start",r->recipe_start) ||
       !recovery_set(f,"qc/provenance","log_path",r->failed_log)) goto done;
    detail="Cannot remap product measurement source identities";
    for(d=0;d<nd;++d) {
        snprintf(path,sizeof(path),"qc/characterization/detectors/%d/measurements",d);
        nm=recovery_count(f,path); if(nm<1 || nm>100000) goto done;
        for(m=0;m<nm;++m) {
            snprintf(path,sizeof(path),"qc/characterization/detectors/%d/measurements/%d",d,m);
            snprintf(source_path,sizeof(source_path),"%s/sources",path);
            ns=recovery_count(f,source_path); if(ns<1 || ns>100000) goto done;
            measurement=recovery_mapping(f,path); sources=asdf_sequence_create(f);
            if(!measurement || !sources) goto done;
            for(j=0;j<ns;++j) {
                snprintf(source_path,sizeof(source_path),"%s/sources/%d",path,j);
                if(asdf_get_string0(f,source_path,&value)!=ASDF_VALUE_OK ||
                   asdf_sequence_append_string0(sources,!strcmp(value,old_id)?r->fits_path:value)!=ASDF_VALUE_OK) goto done;
            }
            if(asdf_mapping_set_sequence(measurement,"sources",sources)!=ASDF_VALUE_OK) goto done;
            sources=NULL; asdf_mapping_destroy(measurement); measurement=NULL;
        }
    }
    /* Only a root sibling is inserted by path; nested siblings were changed
     * through direct mapping views, preserving the qualified #219 boundary. */
    if(asdf_set_mapping(f,"recovery",recovery)!=ASDF_VALUE_OK) goto done;
    recovery=NULL;
    detail="Cannot exclusively create native recovery staging";
    fd=open(r->staging_path,O_WRONLY|O_CREAT|O_EXCL,0600); if(fd<0) goto done;
    owned=1; stream=fdopen(fd,"wb"); if(!stream) goto done; fd=-1;
    detail="Cannot write native recovery staging";
    if(asdf_write_to_fp(f,stream) || fflush(stream) || ferror(stream)) goto done;
    if(fclose(stream)) { stream=NULL; goto done; } stream=NULL;
    asdf_close(f); f=NULL;
    detail="Native recovery staging readback failed";
    if(!recovery_read(r->staging_path,&readback,&readback_length) ||
       (saved=asdf_open_mem_ex(readback,readback_length,NULL))==NULL ||
       asdf_get_string0(saved,"qc/file/id",&value)!=ASDF_VALUE_OK || strcmp(value,r->fits_path) ||
       recovery_count(saved,"qc/characterization/detectors")!=nd ||
       asdf_get_string0(saved,"recovery/method",&value)!=ASDF_VALUE_OK || strcmp(value,"verified_reference_qc_reuse")) goto done;
    code=0;
done:
    asdf_sequence_destroy(sources); asdf_mapping_destroy(measurement); asdf_mapping_destroy(recovery);
    if(stream) fclose(stream);
    if(fd>=0) close(fd);
    if(saved) asdf_close(saved);
    if(f) asdf_close(f);
    free(old_id); free(buffer); free(readback);
    if(message && size) snprintf(message,size,"%s%s",code?detail:"Native recovery staging written; independent verification/publication required",
        code && owned?"; staging retained":"");
    return code;
}

/* All source documents stay alive until publication: detached copies can refer
 * to their document storage. Only product identity/HDU/source IDs are remapped;
 * numeric values, definitions, populations and input HDUs are copied verbatim. */
typedef struct {
    asdf_file_t *file;
    void *bytes;
    size_t length;
} assembly_document;

static int equal_text(asdf_file_t *a, asdf_file_t *b, const char *path)
{
    const char *x, *y;
    return asdf_get_string0(a,path,&x)==ASDF_VALUE_OK &&
        asdf_get_string0(b,path,&y)==ASDF_VALUE_OK && !strcmp(x,y);
}
static asdf_mapping_t *mapping_copy_at(asdf_file_t *f,const char *path)
{
    asdf_mapping_t *view=recovery_mapping(f,path),*copy=NULL;
    if(view) copy=asdf_mapping_copy(view);
    asdf_mapping_destroy(view);
    return copy;
}
static int append_copy_at(asdf_sequence_t *sequence,asdf_file_t *f,const char *path)
{ return append(sequence,mapping_copy_at(f,path)); }
static int replace_sequence(asdf_file_t *f,const char *path,const char *key,asdf_sequence_t *values)
{
    asdf_mapping_t *parent=recovery_mapping(f,path);
    int okay=parent && values && asdf_mapping_set_sequence(parent,key,values)==ASDF_VALUE_OK;
    if(!okay) asdf_sequence_destroy(values);
    asdf_mapping_destroy(parent);
    return okay;
}
static int remap_product_sources(asdf_file_t *f,asdf_mapping_t *detector,const char *old_id,const char *id)
{
    asdf_sequence_t *metrics=NULL;
    asdf_value_t *value=asdf_mapping_get(detector,"measurements");
    int i,j,okay=value && asdf_value_as_sequence(value,&metrics)==ASDF_VALUE_OK;
    /* The typed containers are aliases, not separately owned handles. */
    for(i=0;okay && i<asdf_sequence_size(metrics);++i) {
        asdf_value_t *item=asdf_sequence_get(metrics,i),*old_sources=NULL;
        asdf_mapping_t *metric=NULL;
        asdf_sequence_t *old=NULL,*sources=asdf_sequence_create(f);
        okay=item && sources && asdf_value_as_mapping(item,&metric)==ASDF_VALUE_OK;
        if(okay) old_sources=asdf_mapping_get(metric,"sources");
        okay=okay && old_sources && asdf_value_as_sequence(old_sources,&old)==ASDF_VALUE_OK;
        for(j=0;okay && j<asdf_sequence_size(old);++j) {
            asdf_value_t *v=asdf_sequence_get(old,j);
            const char *text=NULL;
            okay=v && asdf_value_as_string0(v,&text)==ASDF_VALUE_OK &&
                asdf_sequence_append_string0(sources,!strcmp(text,old_id)?id:text)==ASDF_VALUE_OK;
            asdf_value_destroy(v);
        }
        /* Release the view while its node is still attached, before replacement. */
        asdf_value_destroy(old_sources);
        if(okay) {
            okay=asdf_mapping_set_sequence(metric,"sources",sources)==ASDF_VALUE_OK;
            if(okay) sources=NULL;
        }
        asdf_sequence_destroy(sources);
        asdf_value_destroy(item);
    }
    asdf_value_destroy(value);
    return okay;
}

static int assembly_detectors(asdf_file_t *out,const mef_bpm_assembly_qc *r,assembly_document *docs)
{
    asdf_sequence_t *joined=asdf_sequence_create(out);
    size_t i;
    int okay=joined!=NULL;
    for(i=0;okay && i<r->detector_count;++i) {
        asdf_mapping_t *detector=mapping_copy_at(docs[i].file,"qc/characterization/detectors/0");
        okay=detector && count(detector,"output_hdu",i+1) &&
            remap_product_sources(out,detector,r->detectors[i].path,r->fits_path);
        if(okay){okay=append(joined,detector);detector=NULL;}
        asdf_mapping_destroy(detector);
    }
    if(okay){okay=replace_sequence(out,"qc/characterization","detectors",joined);joined=NULL;}
    asdf_sequence_destroy(joined);
    return okay;
}

static int assembly_inputs(asdf_file_t *out,const mef_bpm_assembly_qc *r,assembly_document *docs,int inputs)
{
    asdf_sequence_t *members=asdf_sequence_create(out),*embedded=asdf_sequence_create(out);
    char path[256],base[160];
    int i,okay=members && embedded;
    size_t d;
    for(i=0;okay && i<inputs;++i) {
        asdf_mapping_t *membership=NULL,*record=NULL;
        asdf_sequence_t *decisions=asdf_sequence_create(out),*detectors=asdf_sequence_create(out);
        snprintf(base,sizeof(base),"qc/inputs/%d",i);
        membership=mapping_copy_at(docs[0].file,base);
        snprintf(base,sizeof(base),"qc/embedded_input_records/%d",i);
        record=mapping_copy_at(docs[0].file,base);
        okay=membership && record && decisions && detectors;
        for(d=0;okay && d<r->detector_count;++d) {
            snprintf(path,sizeof(path),"qc/inputs/%d/participation_by_detector/0",i);
            okay=append_copy_at(decisions,docs[d].file,path);
            snprintf(path,sizeof(path),"qc/embedded_input_records/%d/detectors/0",i);
            okay=okay && append_copy_at(detectors,docs[d].file,path);
        }
        if(okay){okay=seq(membership,"participation_by_detector",decisions);decisions=NULL;}
        if(okay){okay=seq(record,"detectors",detectors);detectors=NULL;}
        if(okay){okay=append(members,membership);membership=NULL;}
        if(okay){okay=append(embedded,record);record=NULL;}
        asdf_mapping_destroy(membership);asdf_mapping_destroy(record);
        asdf_sequence_destroy(decisions);asdf_sequence_destroy(detectors);
    }
    if(okay){okay=replace_sequence(out,"qc","inputs",members);members=NULL;}
    if(okay){okay=replace_sequence(out,"qc","embedded_input_records",embedded);embedded=NULL;}
    asdf_sequence_destroy(members);asdf_sequence_destroy(embedded);
    return okay;
}

static int assembly_calibrations(asdf_file_t *out,const mef_bpm_assembly_qc *r,assembly_document *docs,int count_cal)
{
    asdf_sequence_t *joined=asdf_sequence_create(out);
    char path[256];
    int c,okay=joined!=NULL;
    size_t d;
    for(c=0;okay && c<count_cal;++c) {
        asdf_mapping_t *record;
        asdf_sequence_t *bindings=asdf_sequence_create(out);
        snprintf(path,sizeof(path),"qc/calibrations/%d",c);
        record=mapping_copy_at(docs[0].file,path);
        okay=record && bindings;
        for(d=0;okay && d<r->detector_count;++d) {
            snprintf(path,sizeof(path),"qc/calibrations/%d/detector_bindings/0",c);
            okay=append_copy_at(bindings,docs[d].file,path);
        }
        if(okay){okay=seq(record,"detector_bindings",bindings);bindings=NULL;}
        if(okay){okay=append(joined,record);record=NULL;}
        asdf_sequence_destroy(bindings);asdf_mapping_destroy(record);
    }
    if(okay){okay=replace_sequence(out,"qc","calibrations",joined);joined=NULL;}
    asdf_sequence_destroy(joined);
    return okay;
}

static int assembly_admit(const mef_bpm_assembly_qc *r,assembly_document *docs,int *inputs,int *calibrations)
{
    size_t d,total=0;
    char path[256];
    const char *text;
    uint64_t slot,hdu;
    int i;
    for(d=0;d<r->detector_count;++d) {
        asdf_file_t *f;
        if(!recovery_read(r->sidecars[d],&docs[d].bytes,&docs[d].length) ||
            docs[d].length>256u*1024u*1024u-total ||
            memchr(docs[d].bytes,0,docs[d].length)) return 0;
        total+=docs[d].length;
        f=docs[d].file=asdf_open_mem_ex(docs[d].bytes,docs[d].length,NULL);
        if(!f || asdf_get_string0(f,"qc/record/schema_version",&text)!=ASDF_VALUE_OK || strcmp(text,"2.0.0") ||
            asdf_get_string0(f,"qc/file/id",&text)!=ASDF_VALUE_OK || strcmp(text,r->detectors[d].path) ||
            asdf_get_string0(f,"qc/file/location",&text)!=ASDF_VALUE_OK || strcmp(text,r->detectors[d].path) ||
            asdf_get_string0(f,"qc/provenance/operation",&text)!=ASDF_VALUE_OK || strcmp(text,"cal.bpm") ||
            asdf_get_string0(f,"qc/provenance/producer/source_revision",&text)!=ASDF_VALUE_OK || strcmp(text,r->detector_source_revision) ||
            asdf_get_string0(f,"qc/extensions/record_scope",&text)!=ASDF_VALUE_OK || strcmp(text,"one_final_primary_image_product") ||
            recovery_count(f,"qc/characterization/detectors")!=1 ||
            asdf_get_string0(f,"qc/characterization/detectors/0/detector_id",&text)!=ASDF_VALUE_OK || strcmp(text,r->detectors[d].detector_id) ||
            asdf_get_uint64(f,"qc/characterization/detectors/0/configuration_detector",&slot)!=ASDF_VALUE_OK || slot!=r->detectors[d].configuration_detector ||
            asdf_get_uint64(f,"qc/characterization/detectors/0/output_hdu",&hdu)!=ASDF_VALUE_OK || hdu!=0) return 0;
        if(d==0) {
            *inputs=recovery_count(f,"qc/embedded_input_records");
            *calibrations=recovery_count(f,"qc/calibrations");
            if(*inputs<1 || *inputs>100000 || *calibrations!=2) return 0;
        }
        if(recovery_count(f,"qc/embedded_input_records")!=*inputs || recovery_count(f,"qc/inputs")!=*inputs ||
            recovery_count(f,"qc/calibrations")!=*calibrations ||
            !equal_text(f,docs[0].file,"qc/provenance/configuration/snapshot") ||
            !equal_text(f,docs[0].file,"qc/extensions/bpm_registry")) return 0;
        for(i=0;i<*inputs;++i) {
            const char *fields[]={"record_id","file/id","file/location"};size_t j;
            for(j=0;j<3;++j) {
                snprintf(path,sizeof(path),"qc/embedded_input_records/%d/%s",i,fields[j]);
                if(!equal_text(f,docs[0].file,path)) return 0;
            }
            snprintf(path,sizeof(path),"qc/embedded_input_records/%d/detectors",i);
            if(recovery_count(f,path)!=1) return 0;
            snprintf(path,sizeof(path),"qc/inputs/%d/participation_by_detector",i);
            if(recovery_count(f,path)!=1) return 0;
        }
        for(i=0;i<*calibrations;++i) {
            snprintf(path,sizeof(path),"qc/calibrations/%d/file/id",i);
            if(!equal_text(f,docs[0].file,path)) return 0;
            snprintf(path,sizeof(path),"qc/calibrations/%d/role",i);
            if(!equal_text(f,docs[0].file,path)) return 0;
            snprintf(path,sizeof(path),"qc/calibrations/%d/detector_bindings",i);
            if(recovery_count(f,path)!=1) return 0;
        }
    }
    return 1;
}

int mef_bpm_assembly_qc_write(const mef_bpm_assembly_qc *r,char *message,size_t size)
{
    assembly_document *docs=NULL;
    asdf_file_t *out=NULL,*saved=NULL;
    asdf_mapping_t *root=NULL,*extensions=NULL,*item=NULL,*config=NULL;
    asdf_sequence_t *evidence=NULL;
    void *readback=NULL;size_t length=0,d;
    char *temporary=NULL,name[80],expected[4096];
    const char *text,*detail="Invalid BPM QC assembly request";
    FILE *stream=NULL;struct stat st;int fd=-1,owned=0,status=-1,inputs=0,calibrations=0;
    if(!r || !r->fits_path || !r->asdf_path || !r->detectors || !r->sidecars ||
        !r->created_at || strlen(r->created_at)!=24 || !r->log_path || !r->recipe_path ||
        !r->recipe_snapshot || !r->plane_map || !r->source_revision || !r->detector_source_revision ||
        !r->detector_count || r->detector_count>4095 ||
        strlen(r->source_revision)!=40 || strspn(r->source_revision,"0123456789abcdef")!=40 ||
        stat(r->fits_path,&st) || !S_ISREG(st.st_mode) || st.st_size<=0 ||
        lstat(r->asdf_path,&st)==0 || errno!=ENOENT) goto done;
    length=strlen(r->fits_path);
    if(length<6 || r->fits_path[0]!='/' || strcmp(r->fits_path+length-5,".fits") ||
        snprintf(expected,sizeof(expected),"%.*s.asdf",(int)(length-5),r->fits_path)>=(int)sizeof(expected) ||
        strcmp(expected,r->asdf_path)) goto done;
    docs=calloc(r->detector_count,sizeof(*docs));
    detail="Detector ASDF identities, configuration or common ordered inputs/calibrations differ";
    if(!docs || !assembly_admit(r,docs,&inputs,&calibrations)) goto done;
    detail="Cannot create assembled QC document";
    out=asdf_open_mem_ex(NULL,0,NULL);
    root=mapping_copy_at(docs[0].file,"qc");
    if(!out || !root || asdf_set_mapping(out,"qc",root)!=ASDF_VALUE_OK) goto done;
    root=NULL;
    root=recovery_mapping(out,"qc/file");
    if(!root || asdf_mapping_set_null(root,"sha256")!=ASDF_VALUE_OK ||
        !string(root,"integrity","not_content_verified")) goto done;
    asdf_mapping_destroy(root);root=NULL;
    detail="Cannot join detector/input QC and remap final product identity";
    if(!recovery_set(out,"qc/file","id",r->fits_path) || !recovery_set(out,"qc/file","location",r->fits_path) ||
        !recovery_set(out,"qc/file","filename",leaf(r->fits_path)) ||
        !recovery_set(out,"qc/record","assessment_id",r->fits_path) || !recovery_set(out,"qc/record","created_at",r->created_at) ||
        !recovery_set(out,"qc/provenance/producer","name","mefpp_bpm_assemble") ||
        !recovery_set(out,"qc/provenance/producer","source_revision",r->source_revision) ||
        !recovery_set(out,"qc/provenance","recipe_start",r->created_at) ||
        !recovery_set(out,"qc/provenance","log_path",r->log_path) ||
        !assembly_detectors(out,r,docs) || !assembly_inputs(out,r,docs,inputs) ||
        !assembly_calibrations(out,r,docs,calibrations)) goto done;
    detail="Cannot attach assembly recipe snapshot and original detector evidence";
    config=asdf_mapping_create(out);
    if(!config || !string(config,"path",r->recipe_path) || !string(config,"format","bpm-linearity-recipe-toml/1") ||
        !string(config,"snapshot",r->recipe_snapshot)) goto done;
    root=recovery_mapping(out,"qc/provenance");
    if(!root || !map(root,"recipe_configuration",config)) {config=NULL;goto done;} config=NULL;
    asdf_mapping_destroy(root);root=NULL;
    extensions=asdf_mapping_create(out);evidence=asdf_sequence_create(out);
    if(!extensions || !evidence || !string(extensions,"record_scope","one_final_MEF_product") ||
        !string(extensions,"input_reference_policy","embedded_record_id") ||
        !string(extensions,"measurement_policy","caller_supplied_values_only") ||
        !string(extensions,"bpm_registry","WENU_BPM_V1")) goto done;
    for(d=0;d<=r->detector_count;++d) {
        item=asdf_mapping_create(out);
        snprintf(name,sizeof(name),"detector-product-%04lu",(unsigned long)d);
        if(!item || !string(item,"name",d<r->detector_count?name:"image-plane-map") ||
            !string(item,"format",d<r->detector_count?"product-qc-asdf/2.0.0":"mef-bpm-plane-map/1") ||
            (d<r->detector_count ? asdf_mapping_set_string(item,"text",docs[d].bytes,docs[d].length)!=ASDF_VALUE_OK :
                !string(item,"text",r->plane_map))) goto done;
        if(!append(evidence,item)){item=NULL;goto done;} item=NULL;
    }
    if(!seq(extensions,"native_evidence",evidence)){evidence=NULL;goto done;}evidence=NULL;
    root=recovery_mapping(out,"qc");
    if(!root || !map(root,"extensions",extensions)){extensions=NULL;goto done;}extensions=NULL;
    asdf_mapping_destroy(root);root=NULL;
    temporary=malloc(strlen(r->asdf_path)+32);
    if(!temporary) goto done;
    snprintf(temporary,strlen(r->asdf_path)+32,"%s.tmp-XXXXXX",r->asdf_path);
    fd=mkstemp(temporary);if(fd<0)goto done;owned=1;
    stream=fdopen(fd,"wb");if(!stream)goto done;fd=-1;
    detail="Native assembled ASDF write/readback failed";
    if(asdf_write_to_fp(out,stream) || fflush(stream) || fsync(fileno(stream)) || ferror(stream))goto done;
    if(fclose(stream)){stream=NULL;goto done;}stream=NULL;
    if(!recovery_read(temporary,&readback,&length) || !(saved=asdf_open_mem_ex(readback,length,NULL)) ||
        asdf_get_string0(saved,"qc/file/id",&text)!=ASDF_VALUE_OK || strcmp(text,r->fits_path) ||
        recovery_count(saved,"qc/characterization/detectors")!=(int)r->detector_count ||
        recovery_count(saved,"qc/embedded_input_records")!=inputs) goto done;
    detail="Cannot exclusively publish assembled native ASDF";
    if(link(temporary,r->asdf_path))goto done;
    status=0;
done:
    if(status) fprintf(stderr,"BPM_QC_ASSEMBLY_FAILURE: %s\n",detail);
    if(stream)fclose(stream);
    if(fd>=0)close(fd);
    asdf_mapping_destroy(root);asdf_mapping_destroy(extensions);asdf_mapping_destroy(item);asdf_mapping_destroy(config);
    asdf_sequence_destroy(evidence);
    if(saved)asdf_close(saved);
    if(out)asdf_close(out);
    if(docs)for(d=0;d<r->detector_count;++d){if(docs[d].file)asdf_close(docs[d].file);free(docs[d].bytes);}
    if(owned)unlink(temporary);
    free(docs);free(temporary);free(readback);
    if(message && size)snprintf(message,size,"%s",status?detail:"");
    return status;
}
