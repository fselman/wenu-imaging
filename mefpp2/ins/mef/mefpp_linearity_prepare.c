/* Explicit TOML-led native preparation, pair streamed, no fit or ASDF backend. */
#include "mef_linearity_files.h"
#include "mef_linearity_pairs_export.h"
#include "mef_roi_config.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include "mef_measure_plan_internal.h"
#include "mef_linearity_command_internal.h"
#include "mef_file_metadata_internal.h"
#include <float.h>
#include <sys/stat.h>
typedef struct {source input;int accepted;} bias_source;
static int bias_list(const char *path,bias_source *items,int *count,char **owner)
{
    FILE *f=fopen(path,"rb");if(!f)return 0;
    char *data=(malloc)(PLAN_BYTES+1);if(!data){fclose(f);return 0;}*owner=data;
    size_t n=fread(data,1,PLAN_BYTES+1,f);int bad=ferror(f);fclose(f);
    if(bad||!n||n>PLAN_BYTES||memchr(data,0,n)||data[n-1]!='\n')return 0;
    data[n]=0;char *line=strchr(data,'\n');if(!line)return 0;*line++=0;
    if(strcmp(data,"input_index\thdu\tasset\tpath\taccepted"))return 0;
    while(*line){char *next=strchr(line,'\n');if(!next||*count>=FLATS)return 0;*next++=0;
        char *v[5];if(fields(line,v,5)!=5)return 0;
        bias_source *b=items+*count;
        if(!int_number(v[0],INT_MAX,&b->input.index)||!int_number(v[1],127,&b->input.hdu)||
           !int_number(v[4],1,&b->accepted)||strlen(v[2])>127||v[3][0]!='/')return 0;
        b->input.asset=v[2];b->input.path=v[3];
        for(int j=0;j<*count;++j)if(b->input.index==items[j].input.index||
            !strcmp(b->input.asset,items[j].input.asset)||
            (!strcmp(b->input.path,items[j].input.path)&&b->input.hdu==items[j].input.hdu))return 0;
        ++*count;line=next;
    }
    return *count>=3;
}
static int trace(FILE *f,const char *role,int index,int accepted,const pixelvalue *values,size_t rows)
{
    for(size_t y=0;y<rows;++y){if(!isfinite(values[y]))return 0;
        fprintf(f,"%s\t%d\t%d\t%zu\t%.17g\n",role,index,accepted,y+1,(double)values[y]);}
    return !ferror(f);
}
static void number(FILE *f,int available,double value)
{if(available)fprintf(f,"%.17g",value);}
static int corrected(const char *dir,const mef_linearity_prepared_result *r)
{
    FILE *f=new_output(dir,"corrected.tsv");if(!f)return 0;
    fputs("schema_version\tpair_row\tvalid_pixels\tfirst_mean_adu\tsecond_mean_adu\tfirst_spatial_variance_adu2\tsecond_spatial_variance_adu2\tdifference_mean_adu\tdifference_variance_adu2\thalf_difference_variance_adu2\n",f);
    for(size_t i=0;i<r->raw->rows;++i){const mef_linearity_prepared_roi *v=r->row+i;
        fprintf(f,"1\t%zu\t%zu\t",i,v->first.valid_pixels);
        number(f,v->first.level_available,v->first.mean);fputc('\t',f);
        number(f,v->second.level_available,v->second.mean);fputc('\t',f);
        number(f,v->first.stdev_available,v->first.stdev*v->first.stdev);fputc('\t',f);
        number(f,v->second.stdev_available,v->second.stdev*v->second.stdev);fputc('\t',f);
        number(f,v->difference.level_available,v->difference.mean);fputc('\t',f);
        number(f,v->difference.stdev_available,v->difference.stdev*v->difference.stdev);fputc('\t',f);
        number(f,v->difference.stdev_available,.5*v->difference.stdev*v->difference.stdev);fputc('\n',f);
    }
    int bad=ferror(f);return fclose(f)==0&&!bad;
}
static int raw_table(const char *dir,const char *name,const mef_linearity_pairs_result *r,int bias)
{
    FILE *f=new_output(dir,name);if(!f)return 0;
    mef_status s=bias?mef_linearity_bias_write_tsv(f,r):mef_linearity_pairs_write_tsv(f,r);
    int bad=ferror(f);return fclose(f)==0&&!bad&&s==MEF_OK;
}
static int same(const source *a,const source *b)
{return a->hdu==b->hdu&&!strcmp(a->path,b->path)&&!strcmp(a->asset,b->asset);}
int main(int argc,char **argv)
{
    if(argc!=10){fprintf(stderr,"Usage: %s CONFIG.toml ROIS.toml SITES.toml PLAN.tsv MASTER.fits MASTER-HDU MASTER-ASSET BIASES.tsv EMPTY-OUTPUT\n",argv[0]);return 2;}
    int code=1,nbias=0;plan p;source master;bias_source biases[FLATS];
    memset(&p,0,sizeof p);memset(&master,0,sizeof master);memset(biases,0,sizeof biases);
    char *bias_owner=NULL;mef_config *config=NULL;mef_roi_config *regions[2]={NULL,NULL};
    detector_roi *rois[2]={NULL,NULL};size_t bound[2]={0,0};FILE *f=NULL;
    mef_linearity_files_result *result=NULL;mef_linearity_prepare_frame_result *bias_result=NULL;image_t *bias_plane=NULL;
    if(!read_plan(argv[4],&p)||!empty_directory(argv[9])||!bias_list(argv[8],biases,&nbias,&bias_owner))goto done;
    size_t slot,budget,rows;int bx,by,good,reject,rw,rh,exphdu,mad;
    double saturation,tolerance;master.path=argv[5];master.asset=argv[7];
    if(strlen(p.value[0])>63||strlen(p.value[1])>63||master.path[0]!='/'||!master.asset[0]||strlen(master.asset)>127||
       !int_number(argv[6],127,&master.hdu)||!unsigned_number(p.value[2],4095,&slot)||
       !int_number(p.value[8],64,&bx)||!bx||!int_number(p.value[9],64,&by)||!by||
       !int_number(p.value[11],1,&good)||!int_number(p.value[13],255,&reject)||
       !real_number(p.value[14],&saturation)||saturation<=0||!real_number(p.value[15],&tolerance)||tolerance<0||
       !unsigned_number(p.value[16],SIZE_MAX,&budget)||!budget||!unsigned_number(p.value[17],SIZE_MAX,&rows)||!rows||
       !int_number(p.value[19],127,&exphdu)||!int_number(p.value[20],1,&mad)||
       !int_number(p.value[23],MAX_COLUMN_NUMBER,&rw)||!rw||!int_number(p.value[24],MAX_LINE_NUMBER,&rh)||!rh)goto done;
    mef_config_toml_initialize();char diagnostic[256];mef_bias_settings g;
    if(mef_config_from_toml(argv[1],NULL,&config,diagnostic,sizeof diagnostic)!=MEF_OK){fprintf(stderr,"Configuration: %s\n",diagnostic);goto done;}
    if(mef_config_bias_settings(config,slot,&g)!=MEF_OK)goto done;
    char *crop=p.value[22];for(int i=0;i<4;++i){char *next=strchr(crop,',');if(next)*next=0;int v;
        if(!int_number(crop,INT_MAX,&v)||v!=g.trim[i]||(i<3?!next:next!=NULL))goto done;
        crop=next?next+1:NULL;}
    detector_joint_amplifier identity;memset(&identity,0,sizeof identity);
    strcpy(identity.detector_id,p.value[0]);strcpy(identity.amplifier_id,p.value[1]);identity.signal_min=-DBL_MAX;identity.signal_max=DBL_MAX;
    int dim[1][2]={{g.trim[1]-g.trim[0]+1,g.trim[3]-g.trim[2]+1}};
    for(int kind=0;kind<2;++kind){
        if(mef_roi_config_read(argv[2+kind],"toml",NULL,&regions[kind],diagnostic,sizeof diagnostic)!=MEF_OK)goto done;
        size_t n=mef_roi_config_count(regions[kind]);if(!n||n>4096)goto done;
        rois[kind]=(malloc)(n*sizeof(detector_roi));if(!rois[kind])goto done;
        if(mef_roi_config_bind(regions[kind],1,&identity,(const int (*)[2])dim,rois[kind],n,&bound[kind],diagnostic,sizeof diagnostic)!=MEF_OK)goto done;
    }
    for(size_t i=0;i<bound[1];++i)if(rois[1][i].xmin!=rois[1][i].xmax||rois[1][i].ymin!=rois[1][i].ymax)goto done;
    mef_linearity_mask_encoding mask;
    if(!strcmp(p.value[10],"omitted"))mask=MEF_LINEARITY_MASK_OMITTED;
    else if(!strcmp(p.value[10],"binary"))mask=MEF_LINEARITY_MASK_BINARY;
    else if(!strcmp(p.value[10],"reason8"))mask=MEF_LINEARITY_MASK_REASON8;else goto done;
    if((mask!=MEF_LINEARITY_MASK_OMITTED)!=p.has_bpm)goto done;
    if (p.has_bpm && !mef_bpm_policy_matches(&mef_config_processing(config)->bpm,
        mask == MEF_LINEARITY_MASK_BINARY ? MEF_BPM_BINARY : MEF_BPM_REASON8,
        good,(unsigned int)reject,p.value[12])) {
        fprintf(stderr,"Linearity mask settings conflict with shared project BPM policy\n");goto done;
    }
    double times[FLATS];int first[FLATS],second[FLATS],pairs=0;
    for(int i=0;i<p.flats;++i){
        if(!bind_source(&p.flat[i],&p,&g,slot,bx,by,0,rw,rh)||
           !binding_matches(p.flat[i].map,p.value[0],&(mef_image_ref){p.flat[i].asset,p.value[0],p.flat[i].path,p.flat[i].hdu,NULL,0},"ADU",slot)||
           !exposure(p.flat[i].path,exphdu,p.value[18],&times[i]))goto done;
        for(int j=0;j<i;++j)if(p.flat[i].index==p.flat[j].index||!strcmp(p.flat[i].asset,p.flat[j].asset)||
            (!strcmp(p.flat[i].path,p.flat[j].path)&&p.flat[i].hdu==p.flat[j].hdu))goto done;
    }
    for(int i=0;i<p.flats;++i){int members=0,seen=0;
        for(int j=0;j<p.flats;++j)if(!strcmp(p.flat[i].pair,p.flat[j].pair)){
            ++members;if(fabs(times[i]-times[j])>tolerance)goto done;if(j<i)seen=1;}
        if(members!=2)goto done;
        if(!seen){first[pairs]=i;for(int j=i+1;j<p.flats;++j)if(!strcmp(p.flat[i].pair,p.flat[j].pair))second[pairs]=j;++pairs;}}
    if(!bind_master(&master,&p,&g,slot,bx,by))goto done;
    if(p.has_bpm&&!bind_source(&p.bpm,&p,&g,slot,bx,by,1,rw,rh))goto done;
    for(int j=0;j<2;++j)if(!bind_source(&p.bias[j],&p,&g,slot,bx,by,0,rw,rh))goto done;
    int accepted=0;
    for(int i=0;i<nbias;++i){accepted+=biases[i].accepted;
        if(!bind_source(&biases[i].input,&p,&g,slot,bx,by,0,rw,rh))goto done;
        for(int j=0;j<p.flats;++j)if(!strcmp(biases[i].input.asset,p.flat[j].asset)||
            (!strcmp(biases[i].input.path,p.flat[j].path)&&biases[i].input.hdu==p.flat[j].hdu))goto done;
    }
    if(accepted<g.minimum_frames)goto done;
    for(int j=0;j<2;++j){int found=0;for(int i=0;i<nbias;++i)if(same(&p.bias[j],&biases[i].input))++found;if(found!=1)goto done;}
    /* All geometry/header/time admission precedes raw-plane measurement. */
    f=new_output(argv[9],"bias-traces.tsv");if(!f)goto done;
    fputs("role\tinput_index\tmaster_accepted\traw_row\tcorrection_adu\n",f);
    for(int i=0;i<nbias;++i){
        if(mef_layout_load(biases[i].input.map,p.value[0],&bias_plane,NULL)!=MEF_OK)goto done;
        mef_linearity_prepare_frame_input b={bias_plane,NULL,g,MEF_PREPARE_BIAS,budget};
        if(mef_linearity_prepare_frame(&b,NULL,&bias_result)!=MEF_OK||
           !trace(f,"bias",biases[i].input.index,biases[i].accepted,bias_result->row_correction,bias_result->rows))goto done;
        mef_linearity_prepare_frame_destroy(bias_result);bias_result=NULL;image_del(bias_plane);bias_plane=NULL;
    }
    if(fclose(f)){f=NULL;goto done;}f=NULL;
    for(int pair=0;pair<pairs;++pair){
        mef_linearity_file_frame frames[2];memset(frames,0,sizeof frames);int indices[]={first[pair],second[pair]};
        for(int j=0;j<2;++j){source *s=&p.flat[indices[j]];frames[j].map=s->map;frames[j].reference=reference(s,p.value[0]);frames[j].pair_id=s->pair;frames[j].input_index=s->index;}
        mef_image_ref master_ref=reference(&master,p.value[0]),bpm_ref=reference(&p.bpm,p.value[0]),bias_ref[2];
        mef_linearity_files_input in;memset(&in,0,sizeof in);
        in.sample.configuration=config;in.sample.configuration_detector=slot;in.sample.identity=identity;
        in.sample.frames=2;in.sample.rois=(int)bound[1];in.sample.roi=rois[1];in.sample.reject_bits=(unsigned int)reject;
        in.sample.saturation_raw=saturation;in.sample.max_sites=bound[1];in.sample.max_observations=2*bound[1];
        in.input=frames;in.bias_map=master.map;in.bias_reference=&master_ref;
        in.mask_encoding=mask;in.binary_good_value=good;in.mask_registry=p.value[12];in.exposure_key=p.value[18];
        in.exposure_hdu=exphdu;in.pair_time_tolerance=tolerance;in.max_loaded_pixels=budget;
        in.measure_pairs=1;in.pair_with_mad=mad;in.max_pair_rows=rows;
        in.prepare_pairs=1;in.preparation_roi=rois[0];in.preparation_rois=(int)bound[0];in.max_working_pixels=budget;
        if(p.has_bpm){in.bpm_map=p.bpm.map;in.bpm_reference=&bpm_ref;}
        for(int j=0;j<2;++j){bias_ref[j]=reference(&p.bias[j],p.value[0]);in.raw_bias_map[j]=p.bias[j].map;in.raw_bias_reference[j]=&bias_ref[j];}
        mef_status status=mef_linearity_from_files(&in,NULL,&result);
        if(status!=MEF_OK){fprintf(stderr,"Pair %d preparation status %d\n",pair,(int)status);goto done;}
        char directory[4096];if(snprintf(directory,sizeof directory,"%s/pair-%04d",argv[9],pair)>=(int)sizeof directory||mkdir(directory,0700))goto done;
        if(!raw_table(directory,"pairs.tsv",result->prepared->raw,0)||!raw_table(directory,"bias-ron.tsv",result->prepared->raw,1)||
           !corrected(directory,result->prepared)||!export_samples(directory,result->samples,slot))goto done;
        f=new_output(directory,"flat-traces.tsv");if(!f)goto done;
        fputs("role\tinput_index\tmaster_accepted\traw_row\tcorrection_adu\n",f);
        for(int j=0;j<2;++j)if(!trace(f,"flat",frames[j].input_index,-1,
            result->prepared->row_correction+(size_t)j*result->prepared->trace_rows,result->prepared->trace_rows))goto done;
        if(fclose(f)){f=NULL;goto done;}f=NULL;mef_linearity_files_destroy(result);result=NULL;
    }
    f=new_output(argv[9],"configuration.json");if(!f)goto done;
    if(mef_config_dump(config,f)!=MEF_OK)goto done;
    if(fclose(f)){f=NULL;goto done;}f=NULL;
    f=new_output(argv[9],"master-reference.tsv");if(!f)goto done;
    fputs("path\thdu\tasset\n",f);cell(f,master.path);fprintf(f,"\t%d\t",master.hdu);cell(f,master.asset);fputc('\n',f);
    if(fclose(f)){f=NULL;goto done;}f=NULL;
    f=new_output(argv[9],"command.complete");if(!f)goto done;
    if(fputs("linearity_preparation_complete_noise_unavailable\n",f)<0)goto done;
    if(fclose(f)){f=NULL;goto done;}f=NULL;code=0;
    printf("LINEARITY_PREPARATION_COMPLETE %s pairs=%d rois=%zu sites=%zu biases=%d\n",p.value[0],pairs,bound[0],bound[1],nbias);
done:
    if(f)fclose(f);
    if(code)fputs("Linearity preparation failed; preserve partial evidence. No completed archive or fit asserted.\n",stderr);
    image_del(bias_plane);mef_linearity_prepare_frame_destroy(bias_result);mef_linearity_files_destroy(result);
    for(int i=0;i<p.flats;++i)mef_layout_map_destroy(p.flat[i].map);
    for(int j=0;j<2;++j)mef_layout_map_destroy(p.bias[j].map);
    for(int i=0;i<nbias;++i)mef_layout_map_destroy(biases[i].input.map);
    mef_layout_map_destroy(master.map);mef_layout_map_destroy(p.bpm.map);mef_config_destroy(config);
    for(int k=0;k<2;++k){mef_roi_config_destroy(regions[k]);(free)(rois[k]);}
    (free)(p.text);(free)(bias_owner);return code;
}
