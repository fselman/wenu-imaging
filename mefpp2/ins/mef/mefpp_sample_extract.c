/* Explicit singleton-pixel extraction. No noise model, fit or calibration. */
#include "mef_linearity_files.h"
#include "mef_roi_config.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include "mef_measure_plan_internal.h"
#include <float.h>

static int bind_master(source *s,const plan *p,const mef_bias_settings *g,size_t slot,int bx,int by)
{
    mef_layout_options o;memset(&o,0,sizeof o);o.max_hdus=128;o.max_header_bytes=1048576;
    o.identity_key=p->value[4];o.amplifier_key=p->value[5];o.bin_x_key=p->value[6];o.bin_y_key=p->value[7];
    mef_detector_binding b;memset(&b,0,sizeof b);
    b.detector_id=p->value[0];b.expected_header_id=p->value[0];b.hdu_index=s->hdu;b.unit="ADU";
    b.readout_id=p->value[3];b.bin_x=bx;b.bin_y=by;b.configuration_detector=slot;
    b.active_x=b.active_y=1;b.active_width=g->trim[1]-g->trim[0]+1;b.active_height=g->trim[3]-g->trim[2]+1;
    b.health=MEF_HEALTH_UNKNOWN;b.selection=MEF_OUTPUT_SELECTED;
    mef_layout *layout=NULL;mef_error *error=NULL;
    mef_status status=mef_layout_read(s->path,&o,NULL,&layout,&error);
    if(status==MEF_OK)status=mef_layout_bind(layout,&b,1,NULL,&s->map,&error);
    if(status!=MEF_OK)fprintf(stderr,"Master binding: %s\n",error?mef_error_message(error):"no diagnostic");
    mef_error_destroy(error);mef_layout_destroy(layout);return status==MEF_OK;
}
/* Same escaping convention as native pair TSVs, without a locale-dependent
 * serializer or new dependency. Empty signal is unavailable, never zero. */
static void cell(FILE *f,const char *s)
{
    for(const unsigned char *p=(const unsigned char *)s;*p;++p){
        if(*p=='\\')fputs("\\\\",f);
        else if(*p<32||*p==127)fprintf(f,"\\x%02X",(unsigned int)*p);
        else fputc(*p,f);
    }
}
static int export_samples(const char *dir,const mef_linearity_sample_result *r,size_t slot)
{
    FILE *f=new_output(dir,"samples.tsv");if(!f)return 0;
    fputs("schema_version\tdetector\tamplifier\tconfiguration_detector\tsource_roi\tactive_x\tactive_y\traw_x\traw_y\tasset\tinput_index\thdu\tpair_id\tseconds\tadmission_state\tsignal_adu\tnoise_state\n",f);
    for(int frame=0;frame<r->frames;++frame)for(int i=0;i<r->rois;++i){
        const detector_roi *q=r->roi+i;const mef_linearity_frame *v=r->frame+frame;
        const detector_joint_observation *found=NULL;
        for(int j=0;j<r->observations;++j){const detector_joint_observation *ob=r->observation+j;
            const detector_joint_site *site=r->site+ob->site;
            if(ob->input_index==v->input_index&&site->x==q->xmin&&site->y==q->ymin){found=ob;break;}}
        fputs("1\t",f);cell(f,r->identity.detector_id);fputc('\t',f);cell(f,r->identity.amplifier_id);
        fprintf(f,"\t%zu\t",slot);cell(f,q->roi_id);
        fprintf(f,"\t%d\t%d\t%d\t%d\t",q->xmin,q->ymin,q->xmin+r->scan.trim[0]-1,q->ymin+r->scan.trim[2]-1);
        cell(f,v->asset_id);fprintf(f,"\t%d\t%d\t",v->input_index,v->hdu);cell(f,v->pair_id);
        fprintf(f,"\t%.17g\t%s\t",v->seconds,found?"admitted":"not_admitted");
        if(found)fprintf(f,"%.17g",found->signal);
        fputs("\tunavailable\n",f);
    }
    int bad=ferror(f);if(fclose(f)||bad)return 0;
    f=new_output(dir,"population.tsv");if(!f)return 0;
    fputs("input_index\toutside_selected_sites\tbpm_excluded\tsample_excluded\tnonfinite\tsaturated\tadmitted\n",f);
    for(int i=0;i<r->frames;++i){const mef_linearity_population *p=r->population+i;
        fprintf(f,"%d\t%zu\t%zu\t%zu\t%zu\t%zu\t%zu\n",r->frame[i].input_index,
            p->outside_roi,p->bpm_excluded,p->sample_excluded,p->nonfinite,p->saturated,p->admitted);}
    bad=ferror(f);return fclose(f)==0&&!bad;
}
int main(int argc,char **argv)
{
    if(argc!=10){fprintf(stderr,"Usage: %s NATIVE.paf SINGLETONS.toml RAW-SELECTION.tsv MASTER.fits MASTER-HDU MASTER-ASSET MAX-SITES MAX-OBSERVATIONS EMPTY-OUTPUT\n",argv[0]);return 2;}
    plan p;memset(&p,0,sizeof p);source master;memset(&master,0,sizeof master);
    mef_config *config=NULL;mef_roi_config *regions=NULL;detector_roi *rois=NULL;
    mef_bb *bb=NULL;mef_linearity_files_result *result=NULL;int code=1;
    if(!read_plan(argv[3],&p)||!empty_directory(argv[9]))goto done;
    size_t slot,budget,max_sites,max_observations;int bx,by,good,reject,rw,rh,exphdu;
    double saturation,tolerance;
    master.path=argv[4];master.asset=argv[6];
    if(strlen(p.value[0])>63||strlen(p.value[1])>63||master.path[0]!='/'||!master.asset[0]||strlen(master.asset)>127||
       !int_number(argv[5],127,&master.hdu)||!unsigned_number(argv[7],4096,&max_sites)||!max_sites||
       !unsigned_number(argv[8],INT_MAX,&max_observations)||!max_observations||
       !unsigned_number(p.value[2],4095,&slot)||!int_number(p.value[8],64,&bx)||!bx||
       !int_number(p.value[9],64,&by)||!by||!int_number(p.value[11],1,&good)||
       !int_number(p.value[13],255,&reject)||!real_number(p.value[14],&saturation)||saturation<=0||
       !real_number(p.value[15],&tolerance)||tolerance<0||!unsigned_number(p.value[16],SIZE_MAX,&budget)||!budget||
       !int_number(p.value[19],127,&exphdu)||!int_number(p.value[23],MAX_COLUMN_NUMBER,&rw)||!rw||
       !int_number(p.value[24],MAX_LINE_NUMBER,&rh)||!rh)goto done;
    mef_linearity_mask_encoding mask;
    if(!strcmp(p.value[10],"omitted"))mask=MEF_LINEARITY_MASK_OMITTED;
    else if(!strcmp(p.value[10],"binary"))mask=MEF_LINEARITY_MASK_BINARY;
    else if(!strcmp(p.value[10],"reason8"))mask=MEF_LINEARITY_MASK_REASON8;
    else goto done;
    if((mask!=MEF_LINEARITY_MASK_OMITTED)!=p.has_bpm)goto done;
    bb=mef_bb_new_from_paf(argv[1]);if(!bb||mef_config_from_legacy(bb,NULL,&config,NULL)!=MEF_OK)goto done;
    mef_bb_del(bb);bb=NULL;mef_bias_settings g;
    if(mef_config_bias_settings(config,slot,&g)!=MEF_OK)goto done;
    char *crop=p.value[22];
    for(int i=0;i<4;++i){char *next=strchr(crop,',');if(next)*next=0;int v;
        if(!int_number(crop,INT_MAX,&v)||v!=g.trim[i]||(i<3?!next:next!=NULL))goto done;
        crop=next?next+1:NULL;}
    mef_config_toml_initialize();char diagnostic[256];
    if(mef_roi_config_read(argv[2],"toml",NULL,&regions,diagnostic,sizeof diagnostic)!=MEF_OK)goto done;
    size_t n=mef_roi_config_count(regions),bound=0;
    if(!n||n>max_sites)goto done;
    rois=(malloc)(n*sizeof *rois);if(!rois)goto done;
    detector_joint_amplifier identity;memset(&identity,0,sizeof identity);
    strcpy(identity.detector_id,p.value[0]);strcpy(identity.amplifier_id,p.value[1]);
    /* Finite transport domain ONLY, never an admitted inversion/fit interval.
     * The extraction result has noise unavailable and cannot enter a fit. */
    identity.signal_min=-DBL_MAX;identity.signal_max=DBL_MAX;
    int dimensions[1][2]={{g.trim[1]-g.trim[0]+1,g.trim[3]-g.trim[2]+1}};
    if(mef_roi_config_bind(regions,1,&identity,(const int (*)[2])dimensions,rois,n,&bound,diagnostic,sizeof diagnostic)!=MEF_OK)goto done;
    for(size_t i=0;i<bound;++i){if(rois[i].xmin!=rois[i].xmax||rois[i].ymin!=rois[i].ymax)goto done;
        for(size_t j=0;j<i;++j)if(rois[i].xmin==rois[j].xmin&&rois[i].ymin==rois[j].ymin)goto done;}
    mef_linearity_file_frame frames[FLATS];memset(frames,0,sizeof frames);mef_image_ref bpm,bias;
    for(int i=0;i<p.flats;++i){if(!bind_source(&p.flat[i],&p,&g,slot,bx,by,0,rw,rh))goto done;
        frames[i].map=p.flat[i].map;frames[i].reference=reference(&p.flat[i],p.value[0]);
        frames[i].pair_id=p.flat[i].pair;frames[i].input_index=p.flat[i].index;}
    if(!bind_master(&master,&p,&g,slot,bx,by))goto done;
    bias=reference(&master,p.value[0]);
    if(p.has_bpm){if(!bind_source(&p.bpm,&p,&g,slot,bx,by,1,rw,rh))goto done;bpm=reference(&p.bpm,p.value[0]);}
    mef_linearity_files_input in;memset(&in,0,sizeof in);
    in.sample.configuration=config;in.sample.configuration_detector=slot;in.sample.identity=identity;
    in.sample.frames=p.flats;in.sample.rois=(int)bound;in.sample.roi=rois;
    in.sample.reject_bits=(unsigned int)reject;in.sample.saturation_raw=saturation;
    in.sample.max_sites=max_sites;in.sample.max_observations=max_observations;
    in.input=frames;in.bias_map=master.map;in.bias_reference=&bias;
    in.mask_encoding=mask;in.binary_good_value=good;in.mask_registry=p.value[12];
    in.max_loaded_pixels=budget;in.exposure_key=p.value[18];in.exposure_hdu=exphdu;in.pair_time_tolerance=tolerance;
    if(p.has_bpm){in.bpm_map=p.bpm.map;in.bpm_reference=&bpm;}
    mef_status status=mef_linearity_from_files(&in,NULL,&result);
    if(status!=MEF_OK){fprintf(stderr,"Corrected extraction status %d\n",status);goto done;}
    if(!export_samples(argv[9],result->samples,slot))goto done;
    FILE *f=new_output(argv[9],"configuration.json");if(!f)goto done;
    status=mef_config_dump(config,f);int closed=fclose(f);if(status!=MEF_OK||closed)goto done;
    f=new_output(argv[9],"command.complete");if(!f)goto done;
    int wrote=fputs("corrected_samples_complete_noise_unavailable\n",f);closed=fclose(f);if(wrote<0||closed)goto done;
    printf("CORRECTED_SAMPLES_COMPLETE %s sites=%d observations=%d noise=unavailable\n",p.value[0],result->samples->sites,result->samples->observations);code=0;
done:
    if(code)fputs("Sample extraction failed; retain partial files/log. No fit asserted.\n",stderr);
    mef_linearity_files_destroy(result);mef_config_destroy(config);if(bb)mef_bb_del(bb);
    mef_roi_config_destroy(regions);(free)(rois);mef_layout_map_destroy(master.map);
    for(int i=0;i<p.flats;++i)mef_layout_map_destroy(p.flat[i].map);
    mef_layout_map_destroy(p.bpm.map);(free)(p.text);return code;
}
