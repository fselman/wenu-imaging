/* Recipe configuration only: reuse qfits PAF queries and bundled tomlc17. */
#include "mef_roi_config.h"
#include "mef_toml_bridge.h"
#include "qfits.h"
#include "tomlc17.h"
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>
#define ROI_LIMIT 4096
#define TEXT_LIMIT (1024*1024)
typedef struct {
    char id[64], detector[64], amplifier[64];
    int xmin,xmax,ymin,ymax;
} roi_entry;
struct mef_roi_config {
    mef_allocator allocator;
    size_t count;
    roi_entry *entry;
    char *source;
};
static void detail(char *d,size_t n,const char *s){if(d&&n)snprintf(d,n,"%s",s);}
static void *alloc_default(void *u,size_t n){(void)u;return (malloc)(n);}
static void free_default(void *u,void *p){(void)u;(free)(p);}
void mef_roi_config_destroy(mef_roi_config *c)
{
    if(!c)return;
    mef_allocator a=c->allocator;
    if(c->source)a.release(a.user,c->source);
    if(c->entry)a.release(a.user,c->entry);
    a.release(a.user,c);
}
size_t mef_roi_config_count(const mef_roi_config *c){return c?c->count:0;}
const char *mef_roi_config_source(const mef_roi_config *c){return c?c->source:NULL;}
static int id_valid(const char *s)
{
    size_t n=0;
    if(!s||!s[0])return 0;
    for(;s[n];++n)if(n>=63||!((s[n]>='a'&&s[n]<='z')||
        (s[n]>='A'&&s[n]<='Z')||(s[n]>='0'&&s[n]<='9')||strchr("._:-",s[n])))return 0;
    return 1;
}
static const char *fields[]={"id","detector","amplifier","xmin","xmax","ymin","ymax"};
static const char *paf_fields[]={"ID","DETECTOR","AMPLIFIER","X.MIN","X.MAX","Y.MIN","Y.MAX"};
static int integer_text(const char *s,int *v)
{
    char *end;long q;
    if(!s||!s[0])return 0;
    errno=0;q=strtol(s,&end,10);
    if(errno||*end||q<INT_MIN||q>INT_MAX)return 0;
    *v=(int)q;return 1;
}
/* PAF queries return static storage: copy each value immediately. The inventory
 * rejects repeated/unknown body keys before those queries (first-wins is unsafe).
 * This supplement deliberately uses one canonical, unindented key per line. */
static int paf_inventory(const char *text,size_t count)
{
    unsigned char seen[2+7*ROI_LIMIT]={0};size_t keys=0;
    const char *p=text;
    while(*p){
        const char *end=strchr(p,'\n');size_t len=end?(size_t)(end-p):strlen(p);
        char line[512],key[96],expected[96];int slot=-1;
        if(len>=sizeof line)return 0;
        memcpy(line,p,len);line[len]=0;
        if(line[0]&&line[0]!='#'&&line[0]!='\r') {
            if(isspace((unsigned char)line[0])||sscanf(line,"%95s",key)!=1)return 0;
            if(!strncmp(key,"PAF.HDR.",8)) {
                size_t kn=strlen(key);if(kn&&key[kn-1]==';')key[kn-1]=0; /* standard qfits header only */
                const char *names[]={"START","END","TYPE","ID","NAME","DESC","CRTE.NAME","CRTE.DAYTIM","LCHG.NAME","LCHG.DAYTIM","CHECKSUM"};
                int ok=0;for(size_t k=0;k<sizeof names/sizeof names[0];++k)if(!strcmp(key+8,names[k]))ok=1;
                if(!ok)return 0;
            } else {
                if(!strcmp(key,"MEF.ROI.VERSION"))slot=0;
                if(!strcmp(key,"MEF.ROI.COUNT"))slot=1;
                /* Resolve a canonical ordinal without a count-squared scan. */
                if(slot<0&&!strncmp(key,"MEF.ROI.",8)){
                    char *tail;errno=0;long ordinal=strtol(key+8,&tail,10);
                    if(!errno&&ordinal>=1&&(size_t)ordinal<=count&&*tail=='.')
                        for(int j=0;j<7;++j){
                            snprintf(expected,sizeof expected,"MEF.ROI.%ld.%s",ordinal,paf_fields[j]);
                            if(!strcmp(key,expected)){slot=2+7*((int)ordinal-1)+j;break;}
                        }
                }
                if(slot<0||seen[slot]++)return 0;
                ++keys;
                const char *semi=strchr(line,';');
                if(!semi)return 0;
                for(++semi;*semi;++semi){if(*semi=='#')break;if(!isspace((unsigned char)*semi))return 0;}
            }
        }
        p+=len;if(*p=='\n')++p;
    }
    return keys==2+7*count;
}
mef_status mef_roi_config_read(const char *path,const char *format,
    const mef_allocator *allocator,mef_roi_config **out,char *diagnostic,size_t capacity)
{
    mef_roi_config *c=NULL;mef_status status=MEF_ERR_CONFIG;
    mef_allocator a={NULL,alloc_default,free_default};
    FILE *fp=NULL;long length;int paf,version=0,count=0;
    toml_result_t parsed={0};toml_datum_t root={0},array={0};
    const char *error="Invalid ROI configuration arguments";
    if(!path||!format||!out||*out||(allocator&&(!allocator->allocate||!allocator->release)))goto done;
    paf=!strcmp(format,"paf");
    if(!paf&&strcmp(format,"toml"))goto done;
    if(!paf&&!mef_toml_is_initialized()){error="Initialize existing TOML parser first";goto done;}
    if(allocator)a=*allocator;
    fp=fopen(path,"rb");if(!fp){status=MEF_ERR_IO;error="Cannot open ROI configuration";goto done;}
    if(fseek(fp,0,SEEK_END)||(length=ftell(fp))<1||length>TEXT_LIMIT||fseek(fp,0,SEEK_SET)){
        status=MEF_ERR_IO;error="ROI text size/seek limit";goto done;}
    c=a.allocate(a.user,sizeof *c);if(!c){status=MEF_ERR_MEMORY;goto done;}
    c->allocator=a;c->count=0;c->entry=NULL;c->source=NULL;
    c->source=a.allocate(a.user,(size_t)length+1);if(!c->source){status=MEF_ERR_MEMORY;goto done;}
    if(fread(c->source,1,(size_t)length,fp)!=(size_t)length||ferror(fp)||fgetc(fp)!=EOF){
        status=MEF_ERR_IO;error="ROI read failed or file changed";goto done;}
    c->source[length]=0;
    if(fclose(fp)){fp=NULL;status=MEF_ERR_IO;goto done;}fp=NULL;
    if(memchr(c->source,0,(size_t)length)){error="Embedded NUL in ROI source";goto done;}
    if(paf){
        char *v=qfits_paf_query((char *)path,"MEF.ROI.VERSION");
        if(!integer_text(v,&version))goto invalid;
        v=qfits_paf_query((char *)path,"MEF.ROI.COUNT");if(!integer_text(v,&count))goto invalid;
        if(count<1||count>ROI_LIMIT||!paf_inventory(c->source,(size_t)count))goto invalid;
    }else{
        parsed=toml_parse_named(c->source,(int)length,path);if(!parsed.ok)goto invalid;
        root=parsed.toptab;
        if(root.u.tab.size!=2)goto invalid;
        toml_datum_t v=toml_get(root,"roi_schema_version");array=toml_get(root,"roi");
        if(v.type!=TOML_INT64||v.u.int64!=1||array.type!=TOML_ARRAY)goto invalid;
        version=1;count=array.u.arr.size;if(count<1||count>ROI_LIMIT)goto invalid;
    }
    if(version!=1)goto invalid;
    c->count=(size_t)count;c->entry=a.allocate(a.user,c->count*sizeof *c->entry);
    if(!c->entry){status=MEF_ERR_MEMORY;goto done;}
    for(int i=0;i<count;++i){
        roi_entry *e=c->entry+i;char *dest[]={e->id,e->detector,e->amplifier};
        int *bounds[]={&e->xmin,&e->xmax,&e->ymin,&e->ymax};
        toml_datum_t table={0};
        if(!paf){table=array.u.arr.elem[i];if(table.type!=TOML_TABLE||table.u.tab.size!=7)goto invalid;}
        for(int j=0;j<7;++j){
            if(paf){char key[96];snprintf(key,sizeof key,"MEF.ROI.%d.%s",i+1,paf_fields[j]);
                char *v=qfits_paf_query((char *)path,key);
                if(j<3){if(!id_valid(v))goto invalid;strcpy(dest[j],v);}
                else if(!integer_text(v,bounds[j-3]))goto invalid;
            }else{
                toml_datum_t v=toml_get(table,fields[j]);
                if(j<3){if(v.type!=TOML_STRING||strlen(v.u.str.ptr)!=(size_t)v.u.str.len||!id_valid(v.u.str.ptr))goto invalid;strcpy(dest[j],v.u.str.ptr);}
                else{if(v.type!=TOML_INT64||v.u.int64<1||v.u.int64>INT_MAX)goto invalid;*bounds[j-3]=(int)v.u.int64;}
            }
        }
        if(e->xmin<1||e->ymin<1||e->xmax<e->xmin||e->ymax<e->ymin)goto invalid;
        for(int j=0;j<i;++j)if(!strcmp(e->id,c->entry[j].id))goto invalid;
    }
    /* qfits reopened PAF for each query: refuse a final source-byte mismatch. */
    if(paf){fp=fopen(path,"rb");if(!fp){status=MEF_ERR_IO;goto done;}
        for(long i=0;i<length;++i)if(fgetc(fp)!=(unsigned char)c->source[i]){status=MEF_ERR_IO;goto done;}
        if(fgetc(fp)!=EOF||ferror(fp)){status=MEF_ERR_IO;goto done;}
        if(fclose(fp)){fp=NULL;status=MEF_ERR_IO;goto done;}fp=NULL;}
    *out=c;c=NULL;status=MEF_OK;error="";goto done;
invalid:error="Invalid ROI schema, type, identity, bounds, duplicate or unknown key";
done:
    if(fp)fclose(fp);
    if(parsed.ok)toml_free(parsed);
    mef_roi_config_destroy(c);
    if(status==MEF_ERR_MEMORY)error="Cannot allocate ROI snapshot";
    detail(diagnostic,capacity,error);return status;
}
mef_status mef_roi_config_bind(const mef_roi_config *c,int n,
    const detector_joint_amplifier *amp,const int (*dim)[2],detector_roi *out,
    size_t capacity,size_t *count,char *diagnostic,size_t dcap)
{
    const char *error="Invalid ROI binding arguments/capacity";
    if(!c||n<1||!amp||!dim||!out||!count||capacity<c->count)goto fail;
    for(int i=0;i<n;++i){
        if(!memchr(amp[i].detector_id,0,64)||!memchr(amp[i].amplifier_id,0,64)||
           !id_valid(amp[i].detector_id)||!id_valid(amp[i].amplifier_id)||dim[i][0]<1||dim[i][1]<1)goto fail;
        for(int j=0;j<i;++j)if(!strcmp(amp[i].detector_id,amp[j].detector_id)&&
            !strcmp(amp[i].amplifier_id,amp[j].amplifier_id)){error="Duplicate amplifier identity";goto fail;}
    }
    /* Validate all entries first; no partially bound output on failure. */
    for(size_t i=0;i<c->count;++i){
        const roi_entry *e=c->entry+i;int match=-1;
        for(int j=0;j<n;++j)if(!strcmp(e->detector,amp[j].detector_id)&&!strcmp(e->amplifier,amp[j].amplifier_id))match=j;
        if(match<0){error="ROI detector/amplifier identity not found";goto fail;}
        if(e->xmax>dim[match][0]||e->ymax>dim[match][1]){error="ROI outside active amplifier bounds";goto fail;}
    }
    for(size_t i=0;i<c->count;++i){
        const roi_entry *e=c->entry+i;detector_roi *r=out+i;
        strcpy(r->roi_id,e->id);r->xmin=e->xmin;r->xmax=e->xmax;r->ymin=e->ymin;r->ymax=e->ymax;
        for(int j=0;j<n;++j)if(!strcmp(e->detector,amp[j].detector_id)&&!strcmp(e->amplifier,amp[j].amplifier_id))r->amplifier=j;
    }
    *count=c->count;detail(diagnostic,dcap,"");return MEF_OK;
fail:detail(diagnostic,dcap,error);return MEF_ERR_CONFIG;
}
