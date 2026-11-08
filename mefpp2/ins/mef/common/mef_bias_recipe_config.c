#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias_recipe_config.h"
#include "tomlc17.h"
#include <ctype.h>
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

struct mef_bias_recipe_config {
    toml_result_t parsed;
    char *path, *source, **argv;
    int argc, capacity;
    const char *primary[16], *detector[16];
    size_t primary_count, detector_count;
    const char *median_even_handling;
};
static int fail(char *m,size_t n,const char *s)
{ if(m&&n)snprintf(m,n,"%s",s);return 0; }
void mef_bias_recipe_config_destroy(mef_bias_recipe_config *p)
{
    if(!p)return;
    for(int i=0;i<p->argc;++i)free(p->argv[i]);
    free(p->argv);toml_free(p->parsed);free(p->source);free(p->path);free(p);
}
const char *mef_bias_recipe_source(const mef_bias_recipe_config *p){return p?p->source:NULL;}
const char *mef_bias_recipe_path(const mef_bias_recipe_config *p){return p?p->path:NULL;}
const char *const *mef_bias_recipe_primary_keys(const mef_bias_recipe_config *p,size_t *n)
{ *n=p?p->primary_count:0;return p?p->primary:NULL; }
const char *const *mef_bias_recipe_detector_keys(const mef_bias_recipe_config *p,size_t *n)
{ *n=p?p->detector_count:0;return p?p->detector:NULL; }
static const char *text(toml_datum_t v)
{ return v.type==TOML_STRING && v.u.str.len>0 && strlen(v.u.s)==(size_t)v.u.str.len?v.u.s:NULL; }
static int table(toml_datum_t t,const char *const *names,size_t n)
{
    if(t.type!=TOML_TABLE)return 0;
    for(int i=0;i<t.u.tab.size;++i) {
        size_t j;
        if(strlen(t.u.tab.key[i])!=(size_t)t.u.tab.len[i])return 0;
        for(j=0;j<n;++j)if(!strcmp(t.u.tab.key[i],names[j]))break;
        if(j==n)return 0;
    }
    return 1;
}
#define TABLE(t,names) table(t,names,sizeof(names)/sizeof(*(names)))
static int add(mef_bias_recipe_config *p,const char *s)
{
    if(p->argc>=1000000||!s||!*s)return 0;
    if(p->argc+1>=p->capacity) {
        int capacity=p->capacity?p->capacity*2:64;
        char **a=realloc(p->argv,(size_t)capacity*sizeof(*a));
        if(!a)return 0;
        p->argv=a;p->capacity=capacity;
    }
    p->argv[p->argc]=strdup(s);if(!p->argv[p->argc])return 0;
    p->argv[++p->argc]=NULL;return 1;
}
static int pair(mef_bias_recipe_config *p,const char *key,const char *value)
{ return add(p,key)&&add(p,value); }
static int integer(toml_datum_t v,int *n)
{
    if(v.type!=TOML_INT64||v.u.int64<0||v.u.int64>INT_MAX)return 0;
    *n=(int)v.u.int64;return 1;
}
static int int_arg(mef_bias_recipe_config *p,const char *key,toml_datum_t v)
{ char s[32];int n;if(!integer(v,&n))return 0;snprintf(s,sizeof(s),"%d",n);return pair(p,key,s); }
static char *relative(const mef_bias_recipe_config *p,const char *s)
{
    char *name,*resolved;size_t length;
    if(!s)return NULL;
    if(s[0]=='/')return realpath(s,NULL);
    length=(size_t)(strrchr(p->path,'/')-p->path)+1;
    name=malloc(length+strlen(s)+1);if(!name)return NULL;
    memcpy(name,p->path,length);strcpy(name+length,s);
    resolved=realpath(name,NULL);free(name);return resolved;
}
static toml_datum_t inherited(toml_datum_t entry,toml_datum_t bias,const char *key)
{ toml_datum_t v=toml_get(entry,key);return v.type==TOML_UNKNOWN?toml_get(bias,key):v; }
static int keys(toml_datum_t v,const char **out,size_t *count)
{
    if(v.type==TOML_UNKNOWN)return 1;
    if(v.type!=TOML_ARRAY||v.u.arr.size>16)return 0;
    for(int i=0;i<v.u.arr.size;++i) {
        const char *s=text(v.u.arr.elem[i]),*canonical=s;
        if(!s||strlen(s)>79)return 0;
        if(!strncmp(s,"HIERARCH ",9))canonical=s+9;
        if(!*canonical||!strcmp(canonical,"COMMENT")||!strcmp(canonical,"HISTORY")||
            !strcmp(canonical,"END")||!strcmp(canonical,"CONTINUE"))return 0;
        for(const char *c=canonical;*c;++c)
            if(!isupper((unsigned char)*c)&&!isdigit((unsigned char)*c)&&
                !strchr(" _-.",*c))return 0;
        for(size_t j=0;j<*count;++j)if(!strcmp(out[j],canonical))return 0;
        out[(*count)++]=canonical;
    }
    return 1;
}
static int id_valid(const char *s)
{
    if(!s||!*s||strlen(s)>68)return 0;
    for(;*s;++s)if((unsigned char)*s<=32||(unsigned char)*s>126||*s==','||*s=='\'')return 0;
    return 1;
}
int mef_bias_recipe_expand(int argc,char **argv,int *outc,char ***outv,
    mef_bias_recipe_config **owner,char *message,size_t size)
{
    static const char *root_keys[]={"bias_recipe_schema_version","settings","bias","detector","provenance"};
    static const char *bias_keys[]={"detectors","reference_detector","mad","ron_pair","high_sigma",
        "readout_id","bin_x","bin_y","input_bpm","bpm_hdu","bpm_good_value","bpm_coordinates","bpm_expected_extname","amplifier_id","median_even_handling"};
    static const char *det_keys[]={"id","configuration_detector","hdus","expected_extname",
        "readout_id","bin_x","bin_y","input_bpm","bpm_hdu","bpm_good_value","bpm_coordinates",
        "bpm_expected_extname","amplifier_id"};
    static const char *prov_keys[]={"primary","detector"};
    static const char *field_keys[]={"readout_id","bin_x","bin_y","input_bpm",
        "bpm_hdu","bpm_good_value","bpm_coordinates","bpm_expected_extname","amplifier_id"};
    static const char *field_args[]={"--readout-id","--bin-x","--bin-y","--input-bpm",
        "--bpm-hdu","--bpm-good-value","--bpm-coordinates","--bpm-expected-extname","--amplifier-id"};
    const char *path=NULL,*override=NULL,*reason="Invalid bias recipe TOML envelope";
    mef_bias_recipe_config *p=NULL;FILE *f=NULL;struct stat st;long length;
    toml_datum_t root,bias,entries,selection,provenance;char *settings=NULL,*csv=NULL;
    const char *ids[4096],*requested[4096],*reference=NULL;int slots[4096],selected[4096]={0};
    size_t requested_count=0,count=0;
    *outc=argc;*outv=argv;*owner=NULL;
    for(int i=3;i+1<argc;i+=2) {
        if(!strcmp(argv[i],"--config")) {if(path)return fail(message,size,"Duplicate --config");path=argv[i+1];}
        if(!strcmp(argv[i],"--detectors")) {if(override)return fail(message,size,"Duplicate --detectors");override=argv[i+1];}
    }
    if(!path)return override?fail(message,size,"--detectors requires recipe TOML"):1;
    p=calloc(1,sizeof(*p));if(!p)goto done;
    p->path=realpath(path,NULL);if(!p->path)goto done;
    f=fopen(p->path,"rb");
    if(!f||fstat(fileno(f),&st)||!S_ISREG(st.st_mode)||fseek(f,0,SEEK_END)||
        (length=ftell(f))<0||length>4*1024*1024||fseek(f,0,SEEK_SET))goto done;
    p->source=malloc((size_t)length+1);if(!p->source)goto done;
    if(fread(p->source,1,(size_t)length,f)!=(size_t)length)goto done;
    p->source[length]=0;if(memchr(p->source,0,(size_t)length))goto done;
    fclose(f);f=NULL;p->parsed=toml_parse(p->source,(int)length);
    if(!p->parsed.ok){reason=p->parsed.errmsg;goto done;}
    root=p->parsed.toptab;
    if(toml_get(root,"bias_recipe_schema_version").type==TOML_UNKNOWN) {
        if(override){reason="--detectors requires bias_recipe_schema_version=1";goto done;}
        mef_bias_recipe_config_destroy(p);return 1;
    }
    if(length>1024*1024||!TABLE(root,root_keys))goto done;
    toml_datum_t version=toml_get(root,"bias_recipe_schema_version");
    if(version.type!=TOML_INT64||version.u.int64!=1)goto done;
    bias=toml_get(root,"bias");entries=toml_get(root,"detector");provenance=toml_get(root,"provenance");
    if(!TABLE(bias,bias_keys)||entries.type!=TOML_ARRAY||entries.u.arr.size<1||
        entries.u.arr.size>4096)goto done;
    if(provenance.type!=TOML_UNKNOWN && (!TABLE(provenance,prov_keys)||
        !keys(toml_get(provenance,"primary"),p->primary,&p->primary_count)||
        !keys(toml_get(provenance,"detector"),p->detector,&p->detector_count)))goto done;
    {
        toml_datum_t handling=toml_get(bias,"median_even_handling");
        if (handling.type != TOML_UNKNOWN) {
            p->median_even_handling=text(handling);
            if (!p->median_even_handling || (strcmp(p->median_even_handling,"average") && strcmp(p->median_even_handling,"lower"))) {
                reason="median_even_handling must be average or lower";goto done;
            }
        }
    }
    count=(size_t)entries.u.arr.size;
    for(size_t i=0;i<count;++i) {
        toml_datum_t e=entries.u.arr.elem[i];ids[i]=text(toml_get(e,"id"));
        if(!TABLE(e,det_keys)||!id_valid(ids[i])||
            !integer(toml_get(e,"configuration_detector"),slots+i))goto done;
        for(size_t j=0;j<i;++j)if(!strcmp(ids[i],ids[j])||slots[i]==slots[j]) {
            reason="Duplicate detector ID or configuration index";goto done;
        }
    }
    selection=toml_get(bias,"detectors");
    if(override) {
        if(!strcmp(override,"all"))for(size_t i=0;i<count;++i)selected[i]=1;
        else {
            csv=strdup(override);if(!csv)goto done;
            char *start=csv;
            while(start) {
                char *comma=strchr(start,',');if(comma)*comma=0;
                if(!id_valid(start)||requested_count==4096)goto done;
                requested[requested_count++]=start;start=comma?comma+1:NULL;
            }
        }
    } else if(selection.type==TOML_UNKNOWN||
        (text(selection)&&!strcmp(text(selection),"all"))) {
        for(size_t i=0;i<count;++i)selected[i]=1;
    } else {
        if(selection.type!=TOML_ARRAY||selection.u.arr.size<1||selection.u.arr.size>4096)goto done;
        for(int i=0;i<selection.u.arr.size;++i) {
            const char *id=text(selection.u.arr.elem[i]);if(!id_valid(id))goto done;
            requested[requested_count++]=id;
        }
    }
    for(size_t j=0;j<requested_count;++j) {
        size_t i;
        for(i=0;i<count;++i)if(!strcmp(ids[i],requested[j]))break;
        if(i==count||selected[i]){reason="Unknown or duplicate selected detector ID";goto done;}
        selected[i]=1;
    }
    reference=text(toml_get(bias,"reference_detector"));
    if(toml_get(bias,"reference_detector").type!=TOML_UNKNOWN&&!reference)goto done;
    int reference_selected=0;
    for(size_t i=0;i<count;++i)if(selected[i]) {
        if(!reference)reference=ids[i];
        if(!strcmp(reference,ids[i]))reference_selected=1;
    }
    if(!reference_selected){reason="Reference detector is outside the selected set";goto done;}
    settings=relative(p,text(toml_get(root,"settings")));if(!settings)goto done;
    if(!add(p,argv[0])||!add(p,"cal")||!add(p,"bias")||!pair(p,"--config",settings)||
        !pair(p,"--reference-detector",reference))goto done;
    for(int i=3;i<argc;i+=2) {
        if(i+1>=argc)goto done;
        if(!strcmp(argv[i],"--config")||!strcmp(argv[i],"--detectors"))continue;
        if(strcmp(argv[i],"--bias")&&strcmp(argv[i],"--output")&&strcmp(argv[i],"--output-dir")) {
            reason="Recipe TOML owns detector/measurement choices; do not mix legacy CLI fields";goto done;
        }
        if(!pair(p,argv[i],argv[i+1]))goto done;
    }
    toml_datum_t mad=toml_get(bias,"mad"),ron=toml_get(bias,"ron_pair"),sigma=toml_get(bias,"high_sigma");
    if(mad.type!=TOML_BOOLEAN||!pair(p,"--mad",mad.u.boolean?"yes":"no"))goto done;
    if(ron.type!=TOML_UNKNOWN && (ron.type!=TOML_ARRAY||ron.u.arr.size!=2||
        !int_arg(p,"--ron-first",ron.u.arr.elem[0])||!int_arg(p,"--ron-second",ron.u.arr.elem[1])))goto done;
    if(sigma.type!=TOML_UNKNOWN) {
        double value=sigma.type==TOML_FP64?sigma.u.fp64:sigma.type==TOML_INT64?(double)sigma.u.int64:NAN;
        char s[64];if(!isfinite(value)||value<=0)goto done;
        snprintf(s,sizeof(s),"%.17g",value);if(!pair(p,"--high-sigma",s))goto done;
    }
    for(size_t i=0;i<count;++i)if(selected[i]) {
        toml_datum_t e=entries.u.arr.elem[i],hdus=toml_get(e,"hdus");
        if(!pair(p,"--detector-id",ids[i])||!int_arg(p,"--config-detector",toml_get(e,"configuration_detector"))||
            hdus.type!=TOML_ARRAY||hdus.u.arr.size<1||hdus.u.arr.size>100000)goto done;
        for(int j=0;j<hdus.u.arr.size;++j)if(!int_arg(p,"--hdu",hdus.u.arr.elem[j]))goto done;
        toml_datum_t extname=toml_get(e,"expected_extname");
        if(extname.type!=TOML_UNKNOWN&&!text(extname))goto done;
        if(!pair(p,"--raw-expected-extname",text(extname)?text(extname):"omitted"))goto done;
        const char *mask=text(inherited(e,bias,"input_bpm"));
        if(!mask)goto done;
        for(size_t j=0;j<sizeof(field_keys)/sizeof(*field_keys);++j) {
            toml_datum_t v=inherited(e,bias,field_keys[j]);
            if(j>=4&&j<=7&&!strcmp(mask,"omitted")) {
                if(v.type!=TOML_UNKNOWN){reason="BPM omitted but BPM fields supplied";goto done;}
                continue;
            }
            if((j==5||j==7)&&v.type==TOML_UNKNOWN)continue;
            if(j==1||j==2||j==4||j==5) {if(!int_arg(p,field_args[j],v))goto done;}
            else {
                const char *s=text(v);char *absolute=NULL;
                if(j==3&&strcmp(mask,"omitted"))s=absolute=relative(p,mask);
                int okay=s&&pair(p,field_args[j],s);free(absolute);if(!okay)goto done;
            }
        }
    }
    free(settings);free(csv);*outc=p->argc;*outv=p->argv;*owner=p;return 1;
done:
    if(f)fclose(f);
    fail(message,size,reason);free(settings);free(csv);mef_bias_recipe_config_destroy(p);return 0;
}

const char *mef_bias_recipe_median_even_handling(const mef_bias_recipe_config *p)
{ return p ? p->median_even_handling : NULL; }
