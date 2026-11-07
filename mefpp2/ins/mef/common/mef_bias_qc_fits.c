#include "mef_bias_qc_fits.h"
#include "qfits.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#undef malloc
#undef free

#define G(s,a,f) {s,a,f},
#define M(a,f)
#define Q(s,a,f)
#define C(k,a,f)
static const struct group { int scope; const char *asdf, *fits; } groups[]={
#include "mef_bias_qc_fits.def"
};
#undef G
#undef M
#define G(s,a,f)
#define M(a,f) {a,f},
static const struct metric { const char *asdf, *fits; } metrics[]={
#include "mef_bias_qc_fits.def"
};
#undef M
#undef Q
#define M(a,f)
#define Q(s,a,f) {s,a,f},
static const struct scalar { int scope; const char *asdf, *fits; } scalars[]={
#include "mef_bias_qc_fits.def"
};
#undef Q
#undef C
#define Q(s,a,f)
#define C(k,a,f) {k,a,f},
static const struct code { const char *kind, *text, *value; } codes[]={
#include "mef_bias_qc_fits.def"
};
#undef G
#undef M
#undef Q
#undef C
#define LENGTH(a) (sizeof(a)/sizeof((a)[0]))
static const char *code(const char *kind,const char *text)
{
    size_t i;
    if(text==NULL) return NULL;
    for(i=0;i<LENGTH(codes);++i)
        if(!strcmp(kind,codes[i].kind) && !strcmp(text,codes[i].text)) return codes[i].value;
    return NULL;
}
static const mef_qc_measurement *find(const mef_qc_measurement *q,size_t n,const char *name)
{
    size_t i; const mef_qc_measurement *found=NULL;
    if(!q || !name) return NULL;
    for(i=0;i<n;++i) if(q[i].name && !strcmp(q[i].name,name)) { if(found) return NULL; found=q+i; }
    return found;
}
/* Preflight the exact 80-byte HIERARCH layout. No supplied comments or CONTINUE cards.
 * qfits must never silently truncate a keyword, value or quoted string. */
static int card(qfits_header *h,const char *name,const char *value,int string)
{
    char key[81],quoted[81]; size_t i,n=0,limit;
    if(name==NULL || value==NULL || strlen(name)+9>=sizeof(key)) return 0;
    snprintf(key,sizeof(key),"HIERARCH %s",name);
    if(qfits_header_getstr(h,key)!=NULL) return 0;
    limit=(strlen(key)<29?29:strlen(key))+2;
    if(string) {
        quoted[n++]='\'';
        for(i=0;value[i];++i) {
            unsigned char c=(unsigned char)value[i];
            if(c<32 || c>126 || n+3>=sizeof(quoted)) return 0;
            quoted[n++]=(char)c;
            if(c=='\'') quoted[n++]='\'';
        }
        quoted[n++]='\''; quoted[n]='\0'; value=quoted;
    }
    if(limit+strlen(value)>80) return 0;
    qfits_header_append(h,key,value,NULL,NULL);
    return qfits_header_getstr(h,key)!=NULL;
}
static int field(qfits_header *h,const char *base,const char *suffix,const char *value,int string)
{
    char key[128]; int n=snprintf(key,sizeof(key),"ESO MPP QC %s%s%s",base,*suffix?" ":"",suffix);
    return n>0 && (size_t)n<sizeof(key) && card(h,key,value,string);
}
static int integer(qfits_header *h,const char *base,const char *suffix,uint64_t value)
{
    char number[32]; snprintf(number,sizeof(number),"%llu",(unsigned long long)value);
    return field(h,base,suffix,number,0);
}
static int context(qfits_header *h,const char *key,const mef_qc_measurement *q)
{
    static const char *bounds[]={"X1","X2","Y1","Y2"};
    size_t i;
    if(!field(h,key,"STG",code("stage",q->stage),1) ||
       !field(h,key,"MASK",code("mask",q->mask_policy),1) ||
       !field(h,key,"COORD",code("coord",q->coordinates),1) ||
       !q->clipping || strcmp(q->clipping,"none") ||
       !q->nonfinite_policy || strcmp(q->nonfinite_policy,"excluded")) return 0;
    if(q->mask_id && !field(h,key,"BPMID",q->mask_id,1)) return 0;
    for(i=0;i<4;++i) {
        if(q->bounds[i]<0 || !integer(h,key,bounds[i],(uint64_t)q->bounds[i])) return 0;
    }
    for(i=0;i<q->source_count;++i) {
        char suffix[32]; snprintf(suffix,sizeof(suffix),"SRC%lu",(unsigned long)i+1);
        /* Product identities are absolute paths in ASDF. FITS uses basename. */
        if(!q->source_ids || !q->source_ids[i]) return 0;
        const char *s=strrchr(q->source_ids[i],'/'); s=s?s+1:q->source_ids[i];
        if(!field(h,key,suffix,s,1)) return 0;
    }
    return 1;
}
static int measurement(qfits_header *h,const char *key,const mef_qc_measurement *q,int own_context)
{
    char number[64]; const char *method;
    if(!q || q->vector || !q->unit || !integer(h,key,"NSAMP",q->sample_count)) return 0;
    if(own_context && !context(h,key,q)) return 0;
    if(q->method) {
        method=code("method",q->method);
        if(!field(h,key,"METHOD",method,1)) return 0;
    }
    if(!field(h,key,"UNIT",q->unit,1)) return 0;
    if(q->state==MEF_QC_MEASURED) {
        if(!q->method || !q->values || q->value_count!=1 || !isfinite(q->values[0]) || q->reason) return 0;
        if(!strcmp(q->unit,"count")) {
            if(q->values[0]<0 || floor(q->values[0])!=q->values[0]) return 0;
            snprintf(number,sizeof(number),"%.0f",q->values[0]);
        } else {
            char *p;
            snprintf(number,sizeof(number),"%.17g",q->values[0]);
            for(p=number;*p;++p) if(*p=='e') *p='E';
            /* A float-looking card preserves type for integral-valued ADU. */
            if(!strchr(number,'.') && !strchr(number,'E')) strcat(number,".0");
        }
        return field(h,key,"S","measured",1) && field(h,key,"",number,0);
    }
    return q->state==MEF_QC_UNAVAILABLE && !q->values && !q->value_count &&
        field(h,key,"S","unavailable",1) && field(h,key,"R",code("reason",q->reason),1);
}
static int samples(qfits_header *h,int scope,const char *prefix,const mef_qc_measurement *q,size_t n)
{
    size_t i,j; char key[96],name[96],group[80];
    for(i=0;i<LENGTH(groups);++i) if(groups[i].scope==scope) {
        snprintf(group,sizeof(group),"%s%s%s",prefix,*prefix?" ":"",groups[i].fits);
        snprintf(name,sizeof(name),"%s.mean",groups[i].asdf);
        const mef_qc_measurement *first=find(q,n,name);
        if(!first || !context(h,group,first)) return 0;
        for(j=0;j<LENGTH(metrics);++j) {
            snprintf(name,sizeof(name),"%s.%s",groups[i].asdf,metrics[j].asdf);
            snprintf(key,sizeof(key),"%s %s",group,metrics[j].fits);
            const mef_qc_measurement *m=find(q,n,name);
            /* The registry groups only definitions whose context is identical. */
            if(!m || !m->stage || !m->mask_policy || !m->coordinates ||
                !m->clipping || !m->nonfinite_policy || strcmp(m->clipping,"none") ||
                strcmp(m->nonfinite_policy,"excluded") || strcmp(first->stage,m->stage) || strcmp(first->mask_policy,m->mask_policy) ||
                strcmp(first->coordinates,m->coordinates) || memcmp(first->bounds,m->bounds,sizeof(m->bounds)) ||
                first->source_count!=m->source_count ||
                ((first->mask_id==NULL)!=(m->mask_id==NULL)) ||
                (first->mask_id && strcmp(first->mask_id,m->mask_id))) return 0;
            for(size_t k=0;k<m->source_count;++k) if(strcmp(first->source_ids[k],m->source_ids[k])) return 0;
            if(!measurement(h,key,m,0)) return 0;
        }
    }
    for(i=0;i<LENGTH(scalars);++i) if(scalars[i].scope==scope) {
        const mef_qc_measurement *m=find(q,n,scalars[i].asdf);
        /* BPM parameter measurements exist only when a BPM was supplied. */
        if(!m && !strncmp(scalars[i].asdf,"bpm.",4)) continue;
        snprintf(key,sizeof(key),"%s%s%s",prefix,*prefix?" ":"",scalars[i].fits);
        if(!measurement(h,key,m,1)) return 0;
    }
    return 1;
}
int mef_bias_qc_fits_header(const mef_product_qc *p,size_t index,qfits_header **out,char *message,size_t size)
{
    qfits_header *h=NULL; const mef_qc_detector_record *d; size_t i;
    if(!p || !p->detectors || !p->inputs || !out || *out || index>=p->detector_count || !p->fits_path) goto failed;
    /* Numeric formatting is locale sensitive. Refuse rather than mutate global
     * locale or emit a decimal comma in scientific metadata. */
    if(strcmp(localeconv()->decimal_point,".")) goto failed;
    d=p->detectors+index; if(!d->id || !d->inputs || d->bin_x<1 || d->bin_y<1 || d->input_count!=p->input_count) goto failed;
    h=qfits_header_new(); if(!h) goto failed;
    const char *fits=strrchr(p->fits_path,'/'); fits=fits?fits+1:p->fits_path;
    char asdf[128]; size_t length=strlen(fits);
    if(length<5 || length+1>=sizeof(asdf) || strcmp(fits+length-5,".fits")) goto failed;
    memcpy(asdf,fits,length-5); strcpy(asdf+length-5,".asdf");
    if(!field(h,"MAPVER","","bias-scalar/1",1) || !field(h,"ASDF","",asdf,1) ||
       !field(h,"PROD","",fits,1) || !integer(h,"CONFIG","",d->configuration_detector) ||
       !integer(h,"BINX","",(uint64_t)d->bin_x) || !integer(h,"BINY","",(uint64_t)d->bin_y) ||
       !field(h,"READID","",d->readout_id,1) || !field(h,"AMP","",d->amplifier,1) ||
       !samples(h,0,"",d->measurements,d->measurement_count)) goto failed;
    const mef_qc_measurement *pair=find(d->measurements,d->measurement_count,"read_noise");
    if(!pair) goto failed;
    for(i=0;i<pair->source_count;++i) {
        size_t j; char key[32];
        /* Unrequested RON uses the product as its source, not a raw pair. */
        if(!strncmp(pair->source_ids[i],"raw-",4)) {
            for(j=0;j<p->input_count;++j) if(!strcmp(pair->source_ids[i],p->inputs[j].id)) break;
            if(j==p->input_count) goto failed;
            snprintf(key,sizeof(key),"RON I%lu",(unsigned long)i+1);
            if(!integer(h,key,"",p->inputs[j].original_index)) goto failed;
        }
    }
    for(i=0;i<d->input_count;++i) {
        char prefix[48]; const mef_qc_input_binding *b=d->inputs+i;
        if(!b->input_id || strcmp(b->input_id,p->inputs[i].id) || b->source_hdu<0 ||
           p->inputs[i].original_index>99999999) goto failed;
        snprintf(prefix,sizeof(prefix),"FRAME%03llu",(unsigned long long)p->inputs[i].original_index+1);
        if(!field(h,prefix,"ID",b->input_id,1) || !integer(h,prefix,"HDU",(uint64_t)b->source_hdu) ||
           !field(h,prefix,"USE",b->accepted?"used":"rejected",1) ||
           (!b->accepted && !field(h,prefix,"WHY",code("reason",b->rejection_reason),1)) ||
           !samples(h,1,prefix,b->measurements,b->measurement_count)) goto failed;
    }
    *out=h; return 0;
failed:
    qfits_header_destroy(h);
    if(message && size) snprintf(message,size,"bias-scalar/1 header refused: invalid metadata, unknown code, collision or 80-byte card limit");
    return -1;
}
