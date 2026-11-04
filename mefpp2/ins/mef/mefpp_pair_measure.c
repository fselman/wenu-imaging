/* Expert raw-pair command: explicit bounded plan, one detector, no fit. */
#include "mef_linearity_raw_files.h"
#include "mef_linearity_pairs_export.h"
#include "mef_roi_config.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
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
static int write_table(const char *dir,const char *name,const mef_linearity_pairs_result *r,int bias)
{
    FILE *f=new_output(dir,name);if(!f)return 0;
    mef_status status=bias?mef_linearity_bias_write_tsv(f,r):mef_linearity_pairs_write_tsv(f,r);
    int closed=fclose(f);return status==MEF_OK&&!closed;
}
int main(int argc,char **argv)
{
    if(argc!=5){fprintf(stderr,"Usage: %s NATIVE.paf SELECTED-ROIS.toml PLAN.tsv EMPTY-OUTPUT-DIRECTORY\n",argv[0]);return 2;}
    int code=1;plan p;memset(&p,0,sizeof p);mef_config *config=NULL;mef_roi_config *roi_config=NULL;
    detector_roi *rois=NULL;mef_linearity_files_result *result=NULL;mef_bb *bb=NULL;
    if(!read_plan(argv[3],&p)||!empty_directory(argv[4])){fputs("Invalid explicit plan or nonempty output directory\n",stderr);goto done;}
    size_t slot,budget,rows;int bx,by,good,reject,exphdu,mad,rw,rh;
    double saturation,tolerance;
    if(strlen(p.value[0])>63||strlen(p.value[1])>63||
       !unsigned_number(p.value[2],4095,&slot)||!int_number(p.value[8],64,&bx)||!bx||
       !int_number(p.value[9],64,&by)||!by||!int_number(p.value[11],1,&good)||
       !int_number(p.value[13],255,&reject)||!real_number(p.value[14],&saturation)||saturation<=0||
       !real_number(p.value[15],&tolerance)||tolerance<0||!unsigned_number(p.value[16],SIZE_MAX,&budget)||!budget||
       !unsigned_number(p.value[17],SIZE_MAX,&rows)||!rows||!int_number(p.value[19],127,&exphdu)||
       !int_number(p.value[20],1,&mad)||!int_number(p.value[23],MAX_COLUMN_NUMBER,&rw)||!rw||
       !int_number(p.value[24],MAX_LINE_NUMBER,&rh)||!rh){fputs("Invalid numeric choice\n",stderr);goto done;}
    mef_linearity_mask_encoding mask;
    if(!strcmp(p.value[10],"omitted"))mask=MEF_LINEARITY_MASK_OMITTED;
    else if(!strcmp(p.value[10],"binary"))mask=MEF_LINEARITY_MASK_BINARY;
    else if(!strcmp(p.value[10],"reason8"))mask=MEF_LINEARITY_MASK_REASON8;
    else{fputs("Unknown mask encoding\n",stderr);goto done;}
    if((mask!=MEF_LINEARITY_MASK_OMITTED)!=p.has_bpm){fputs("Mask declaration/source conflict\n",stderr);goto done;}
    bb=mef_bb_new_from_paf(argv[1]);if(!bb||mef_config_from_legacy(bb,NULL,&config,NULL)!=MEF_OK)goto done;
    mef_bb_del(bb);bb=NULL;mef_bias_settings g;
    if(mef_config_bias_settings(config,slot,&g)!=MEF_OK)goto done;
    if(g.trim[0]<1||g.trim[2]<1||g.trim[1]<g.trim[0]||g.trim[3]<g.trim[2]||
       g.trim[1]>rw||g.trim[3]>rh)goto done;
    char *crop=p.value[22];
    for(int j=0;j<4;++j){char *next=strchr(crop,',');if(next)*next=0;int value;
        if(!int_number(crop,INT_MAX,&value)||value!=g.trim[j]||(j<3?!next:next!=NULL)){
            fputs("Processing TOML crop does not match native configuration\n",stderr);goto done;}
        crop=next?next+1:NULL;}
    mef_config_toml_initialize();char diagnostic[256];
    if(mef_roi_config_read(argv[2],"toml",NULL,&roi_config,diagnostic,sizeof diagnostic)!=MEF_OK){fprintf(stderr,"ROI: %s\n",diagnostic);goto done;}
    size_t n=mef_roi_config_count(roi_config);if(!n||n>4096)goto done;
    rois=(malloc)(n*sizeof *rois);if(!rois)goto done;
    detector_joint_amplifier identity;memset(&identity,0,sizeof identity);
    strcpy(identity.detector_id,p.value[0]);strcpy(identity.amplifier_id,p.value[1]);
    int dim[1][2]={{g.trim[1]-g.trim[0]+1,g.trim[3]-g.trim[2]+1}};size_t bound=0;
    if(mef_roi_config_bind(roi_config,1,&identity,(const int (*)[2])dim,rois,n,&bound,diagnostic,sizeof diagnostic)!=MEF_OK){fprintf(stderr,"ROI binding: %s\n",diagnostic);goto done;}
    mef_linearity_file_frame frames[FLATS];memset(frames,0,sizeof frames);mef_image_ref bias[2],bpm;
    for(int i=0;i<p.flats;++i){if(!bind_source(&p.flat[i],&p,&g,slot,bx,by,0,rw,rh)){fprintf(stderr,"Flat binding failed: %s [HDU %d]\n",p.flat[i].path,p.flat[i].hdu);goto done;}
        frames[i].map=p.flat[i].map;frames[i].reference=reference(&p.flat[i],p.value[0]);
        frames[i].pair_id=p.flat[i].pair;frames[i].input_index=p.flat[i].index;}
    for(int j=0;j<2;++j){if(!bind_source(&p.bias[j],&p,&g,slot,bx,by,0,rw,rh)){fprintf(stderr,"Raw bias binding failed: %s [HDU %d]\n",p.bias[j].path,p.bias[j].hdu);goto done;}bias[j]=reference(&p.bias[j],p.value[0]);}
    if(p.has_bpm){if(!bind_source(&p.bpm,&p,&g,slot,bx,by,1,rw,rh)){fprintf(stderr,"BPM binding failed: %s [HDU %d]\n",p.bpm.path,p.bpm.hdu);goto done;}bpm=reference(&p.bpm,p.value[0]);}
    mef_linearity_raw_files_input in;memset(&in,0,sizeof in);in.pairs.configuration=config;
    in.pairs.configuration_detector=slot;in.pairs.identity=identity;in.pairs.frames=p.flats;
    in.pairs.rois=(int)bound;in.pairs.roi=rois;in.pairs.with_mad=mad;in.pairs.reject_bits=(unsigned int)reject;
    in.pairs.saturation_raw=saturation;in.pairs.pair_time_tolerance=tolerance;in.pairs.max_rows=rows;
    in.input=frames;for(int j=0;j<2;++j){in.raw_bias_map[j]=p.bias[j].map;in.raw_bias_reference[j]=&bias[j];}
    in.mask_encoding=mask;in.binary_good_value=good;in.mask_registry=p.value[12];in.max_loaded_pixels=budget;
    in.exposure_key=p.value[18];in.exposure_hdu=exphdu;
    if(p.has_bpm){in.bpm_map=p.bpm.map;in.bpm_reference=&bpm;}
    mef_status status=mef_linearity_raw_from_files(&in,NULL,&result);
    if(status!=MEF_OK){fprintf(stderr,"Raw measurement failed, status %d\n",status);goto done;}
    if(!write_table(argv[4],"pairs.tsv",result->pairs,0)||!write_table(argv[4],"bias-ron.tsv",result->pairs,1))goto done;
    FILE *f=new_output(argv[4],"configuration.json");if(!f)goto done;
    status=mef_config_dump(config,f);int closed=fclose(f);if(status!=MEF_OK||closed)goto done;
    f=new_output(argv[4],"command.complete");if(!f)goto done;
    int wrote=fputs("raw_pair_tables_complete\n",f);closed=fclose(f);if(wrote<0||closed)goto done;
    printf("RAW_PAIR_TABLES_COMPLETE %s\n",p.value[0]);code=0;
done:
    if(code)fputs("Raw pair command failed; no completed measurement run is asserted. Retain partial files/log.\n",stderr);
    mef_linearity_files_destroy(result);mef_config_destroy(config);if(bb)mef_bb_del(bb);
    mef_roi_config_destroy(roi_config);(free)(rois);
    for(int i=0;i<p.flats;++i)mef_layout_map_destroy(p.flat[i].map);
    for(int j=0;j<p.biases;++j)mef_layout_map_destroy(p.bias[j].map);
    mef_layout_map_destroy(p.bpm.map);(free)(p.text);return code;
}
