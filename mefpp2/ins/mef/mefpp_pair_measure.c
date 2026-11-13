/* Expert raw-pair command: explicit bounded plan, one detector, no fit. */
#include "mef_linearity_raw_files.h"
#include "mef_linearity_pairs_export.h"
#include "mef_roi_config.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include "mef_measure_plan_internal.h"
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
    if(!read_plan(argv[3],&p)||p.biases!=2||!empty_directory(argv[4])){fputs("Invalid explicit plan or nonempty output directory\n",stderr);goto done;}
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
