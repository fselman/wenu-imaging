/* Private raw-selection transport shared by the pair and sample commands.
 * Static helpers only; parser/selection semantics preserved from pair command. */
#ifndef MEF_MEASURE_PLAN_INTERNAL_H
#define MEF_MEASURE_PLAN_INTERNAL_H
#include <dirent.h>
#include <errno.h>
#include <math.h>
#include <stdint.h>
#define PLAN_BYTES 1048576
#define FLATS 64
#define KEYS 25
static const char *keys[KEYS]={"detector","amplifier","slot","readout","identity_key","amplifier_key",
    "bin_x_key","bin_y_key","bin_x","bin_y","mask_encoding","good_value","mask_registry","reject_bits",
    "saturation","tolerance","max_pixels","max_rows","exposure_key","exposure_hdu","with_mad","schema","crop","raw_width","raw_height"};
typedef struct {char *path,*asset,*pair;int hdu,index;mef_layout_map *map;} source;
typedef struct {char *text,*value[KEYS];source flat[FLATS],bias[2],bpm;int flats,biases,has_bpm;} plan;
static int unsigned_number(const char *s,size_t ceiling,size_t *out)
{
    if(!s||!*s||*s<'0'||*s>'9')return 0;
    errno=0;char *end;unsigned long long v=strtoull(s,&end,10);
    if(errno||*end||v>ceiling)return 0;
    *out=(size_t)v;return 1;
}
static int int_number(const char *s,int ceiling,int *out)
{size_t v;if(!unsigned_number(s,(size_t)ceiling,&v))return 0;*out=(int)v;return 1;}
static int real_number(const char *s,double *out)
{errno=0;char *end;double v=strtod(s,&end);if(end==s||errno||*end||!isfinite(v))return 0;*out=v;return 1;}
static int fields(char *line,char **field,int limit)
{
    int n=0;char *next=line;
    while(next){if(n==limit)return -1;field[n++]=next;char *tab=strchr(next,'\t');
        if(tab){*tab=0;next=tab+1;}else next=NULL;
        if(!*field[n-1])return -1;}
    return n;
}
static int read_plan(const char *path,plan *p)
{
    FILE *f=fopen(path,"rb");if(!f)return 0;
    p->text=(malloc)(PLAN_BYTES+1);if(!p->text){fclose(f);return 0;}
    size_t n=fread(p->text,1,PLAN_BYTES+1,f);int failed=ferror(f);fclose(f);
    if(failed||!n||n>PLAN_BYTES||memchr(p->text,0,n))return 0;
    p->text[n]=0;if(strstr(p->text,"\n\n"))return 0;char *line=p->text;
    while(line&&*line){char *next=strchr(line,'\n');if(next){*next=0;++next;}
        if(strchr(line,'\r'))return 0;
        char *v[7];int count=fields(line,v,7);if(count<0)return 0;
        if(!strcmp(v[0],"flat")||!strcmp(v[0],"bias")||!strcmp(v[0],"bpm")){
            int flat=!strcmp(v[0],"flat"),bias=!strcmp(v[0],"bias");
            if(count!=(flat?6:4)||(flat&&p->flats==FLATS)||(bias&&p->biases==2)||(!flat&&!bias&&p->has_bpm))return 0;
            source *s=flat?&p->flat[p->flats++]:bias?&p->bias[p->biases++]:&p->bpm;
            if(!flat&&!bias)p->has_bpm=1;
            s->path=v[1];s->asset=v[3];if(s->path[0]!='/'||strlen(s->asset)>127||!int_number(v[2],4095,&s->hdu))return 0;
            if(flat){if(!int_number(v[4],INT_MAX,&s->index))return 0;s->pair=v[5];if(strlen(s->pair)>63)return 0;}
        }else{
            if(count!=2)return 0;
            int k;for(k=0;k<KEYS;++k)if(!strcmp(v[0],keys[k]))break;
            if(k==KEYS||p->value[k])return 0;
            p->value[k]=v[1];
        }
        line=next;
    }
    for(int k=0;k<KEYS;++k)if(!p->value[k])return 0;
    return !strcmp(p->value[21],"raw-pair-plan-v1")&&p->flats>=2&&!(p->flats%2)&&p->biases==2;
}
static int empty_directory(const char *path)
{
    DIR *dir=opendir(path);if(!dir)return 0;struct dirent *e;int empty=1;
    while((e=readdir(dir)))if(strcmp(e->d_name,".")&&strcmp(e->d_name,"..")){empty=0;break;}
    closedir(dir);return empty;
}
static int bind_source(source *s,const plan *p,const mef_bias_settings *g,size_t slot,int bx,int by,int mask,int rw,int rh)
{
    mef_layout_options o;memset(&o,0,sizeof o);o.max_hdus=128;o.max_header_bytes=1048576;
    o.identity_key=p->value[4];o.amplifier_key=p->value[5];o.bin_x_key=p->value[6];o.bin_y_key=p->value[7];
    mef_layout *layout=NULL;mef_detector_binding b;memset(&b,0,sizeof b);
    b.detector_id=p->value[0];b.expected_header_id=p->value[0];b.hdu_index=s->hdu;b.unit=mask?"mask":"ADU";
    b.readout_id=p->value[3];b.bin_x=bx;b.bin_y=by;b.configuration_detector=slot;
    b.active_x=mask?1:g->trim[0];b.active_y=mask?1:g->trim[2];
    b.active_width=g->trim[1]-g->trim[0]+1;b.active_height=g->trim[3]-g->trim[2]+1;
    b.health=MEF_HEALTH_UNKNOWN;b.selection=MEF_OUTPUT_SELECTED;
    mef_error *error=NULL;
    mef_status status=mef_layout_read(s->path,&o,NULL,&layout,&error);
    if(status==MEF_OK)status=mef_layout_bind(layout,&b,1,NULL,&s->map,&error);
    if(status!=MEF_OK)fprintf(stderr,"Layout discovery/binding status %d: %s\n",status,
        error?mef_error_message(error):"No additional diagnostic");
    mef_error_destroy(error);
    mef_layout_destroy(layout);
    const mef_bound_detector *d=status==MEF_OK?mef_layout_find(s->map,p->value[0]):NULL;
    if(d&&!mask&&(d->image.axes[0]!=(size_t)rw||d->image.axes[1]!=(size_t)rh)){
        fputs("Bound raw dimensions differ from explicit detector profile\n",stderr);return 0;}
    return status==MEF_OK;
}
static mef_image_ref reference(source *s,const char *id)
{mef_image_ref r={s->asset,id,s->path,s->hdu,NULL,0};return r;}
static FILE *new_output(const char *dir,const char *name)
{char path[4096];if(snprintf(path,sizeof path,"%s/%s",dir,name)>=(int)sizeof path)return NULL;return fopen(path,"wx");}
#endif
