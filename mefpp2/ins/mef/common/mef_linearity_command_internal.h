/* Private shared master binding / singleton TSV transport. No estimator. */
#ifndef MEF_LINEARITY_COMMAND_INTERNAL_H
#define MEF_LINEARITY_COMMAND_INTERNAL_H
static int bind_master(source *s,const plan *p,const mef_bias_settings *g,size_t slot,int bx,int by)
{
    mef_layout_options o = {0};
    o.max_hdus = 128;
    /* The limit covers all HDUs. Master biases can retain per-frame QC cards
     * in every detector extension, even when binding just one detector. */
    o.max_header_bytes = MEF_LAYOUT_DEFAULT_HEADER_BYTES;
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

#endif
