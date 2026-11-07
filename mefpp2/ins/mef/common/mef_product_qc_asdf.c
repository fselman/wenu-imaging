#define _POSIX_C_SOURCE 200809L
#include "mef_product_qc.h"
#include <asdf/config.h>
#ifdef MEF_ASDF_OMIT_FLOAT16
#undef ASDF_HAVE_FLOAT16
#endif
#include <asdf/file.h>
#include <asdf/value.h>
#include <errno.h>
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
static asdf_mapping_t *detector(asdf_file_t *f,const mef_qc_detector_record *d)
{
    asdf_mapping_t *m=asdf_mapping_create(f);
    if(m==NULL)return NULL;
    if(!string(m,"detector_id",d->id)||!string(m,"amplifier",d->amplifier)||!string(m,"readout_id",d->readout_id)||
        !count(m,"configuration_detector",d->configuration_detector)||!count(m,"output_hdu",(uint64_t)d->output_hdu)||
        !count(m,"bin_x",(uint64_t)d->bin_x)||!count(m,"bin_y",(uint64_t)d->bin_y)||
        !seq(m,"measurements",measurements(f,d->measurements,d->measurement_count))) {
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
    if(okay){okay=map(root,"provenance",provenance);provenance=NULL;}
    for(i=0;okay && i<p->detector_count;++i)okay=append(detectors,detector(f,p->detectors+i));
    if(okay){okay=seq(characterization,"detectors",detectors);detectors=NULL;}
    if(okay){okay=map(root,"characterization",characterization);characterization=NULL;}
    for(i=0;okay && i<p->input_count;++i)okay=append(inputs,input_membership(f,p,i))&&append(embedded,input_record(f,p,i));
    if(okay){okay=seq(root,"inputs",inputs);inputs=NULL;}
    if(okay){okay=seq(root,"embedded_input_records",embedded);embedded=NULL;}
    for(i=0;okay && i<p->calibration_count;++i)okay=append(calibrations,calibration_record(f,p->calibrations+i));
    if(okay){okay=seq(root,"calibrations",calibrations);calibrations=NULL;}
    if(okay)okay=string(extensions,"record_scope","one_final_MEF_product")&&
        string(extensions,"input_reference_policy","embedded_record_id")&&
        string(extensions,"measurement_policy","caller_supplied_values_only");
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
    if(path==NULL || snprintf(expected,sizeof(expected),"%.*s.asdf",(int)(n-5),p->fits_path)>=(int)sizeof(expected)||
        strcmp(path,expected)) {detail="ASDF must inherit the final FITS basename and directory";goto done;}
    if(stat(p->fits_path,&st)!=0||!S_ISREG(st.st_mode)||st.st_size==0){detail="Final FITS product is missing or empty";goto done;}
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
