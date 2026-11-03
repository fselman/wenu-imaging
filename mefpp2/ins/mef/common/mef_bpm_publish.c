#include "mef_bpm_publish.h"
#include "mef_bpm_settings.h"
#include "mefp_lib.h"
#include <unistd.h>
#include <sys/stat.h>

static mef_status failed(mef_status status,const char *message,mef_error **error) {
    if(error && !*error) (void)mef_error_create(status,message,NULL,error);
    return status;
}
static const char *basename_only(const char *p) { const char *q=strrchr(p,'/'); return q?q+1:p; }
/* Bound current qfits string-card handling rather than claiming CONTINUE.
 * Long paths remain in ASDF; FITS uses unambiguous basenames only. */
static int string_card(qfits_header *h,const char *key,const char *value) {
    size_t i,budget;
    if(!value || !*value || strchr(value,'\'')) return -1;
    budget=strlen(key)<8?8:strlen(key);
    if(budget+5+strlen(value)>80) return -1;
    for(i=0;value[i];++i) if((unsigned char)value[i]<32 || (unsigned char)value[i]>126) return -1;
    qfits_header_add(h,(char *)key,(char *)value,NULL,NULL); return 0;
}
static qfits_header *plane_header(int primary,int bitpix,int lx,int ly,const char *name) {
    qfits_header *h=qfits_header_default();
    char value[32];
    if(!h) return NULL;
    if(!primary) {
        /* New structural prefix: never delete/reindex a qfits header (#212). */
        qfits_header_destroy(h); h=qfits_header_new(); if(!h) return NULL;
        qfits_header_append(h,"XTENSION","IMAGE",NULL,NULL);
        qfits_header_append(h,"END",NULL,NULL,NULL);
    }
    sprintf(value,"%d",bitpix); qfits_header_add(h,"BITPIX",value,NULL,NULL);
    qfits_header_add(h,"NAXIS","2",NULL,NULL);
    sprintf(value,"%d",lx); qfits_header_add(h,"NAXIS1",value,NULL,NULL);
    sprintf(value,"%d",ly); qfits_header_add(h,"NAXIS2",value,NULL,NULL);
    if(primary) qfits_header_add(h,"EXTEND","T",NULL,NULL);
    else { qfits_header_add(h,"PCOUNT","0",NULL,NULL); qfits_header_add(h,"GCOUNT","1",NULL,NULL); }
    if(string_card(h,"EXTNAME",name)!=0) { qfits_header_destroy(h); return NULL; }
    return h;
}
static int byte_plane(FILE *stream,const unsigned char *data,int *buffer,int lx,int ly,
    const char *name,const char *registry) {
    qfits_header *h=plane_header(0,8,lx,ly,name);
    int i,status;
    if(!h) return -1;
    if(registry && (string_card(h,"MASKENC","REASON8") || string_card(h,"MASKREG",registry))) {
        qfits_header_destroy(h); return -1;
    }
    if(registry) (void)string_card(h,"BUNIT","mask");
    if(!strcmp(name,"COVERAGE")) {
        (void)string_card(h,"COV0","not_measured"); (void)string_card(h,"COV1","fit");
        (void)string_card(h,"COV2","legacy_ls_fallback");
    }
    if(!strcmp(name,"SELECTION")) {
        qfits_header_add(h,"SELGOOD","1",NULL,NULL);
        (void)string_card(h,"SELROLE","prior_plus_new_and_coverage");
    }
    if(!strcmp(name,"PRIORSEL")) qfits_header_add(h,"SELGOOD","1",NULL,NULL);
    for(i=0;i<lx*ly;++i) buffer[i]=data[i];
    status=intimage_write_hdu_checked(stream,buffer,lx,ly,8,h);
    qfits_header_destroy(h); return status;
}
static int options_valid(const mef_bpm_publish_options *o) {
    size_t i;
    int y,m,d,hh,mm,ss,end=0,days;
    if(!o || (o->mode!=MEF_BPM_PUBLISH_NEW && o->mode!=MEF_BPM_PUBLISH_COMBINED) ||
        !o->created_at || !*o->created_at || !o->source_revision || strlen(o->source_revision)!=40) return 0;
    if(strlen(o->created_at)!=20 || o->created_at[4]!='-' || o->created_at[7]!='-' ||
        o->created_at[10]!='T' || o->created_at[13]!=':' || o->created_at[16]!=':' || o->created_at[19]!='Z' ||
        sscanf(o->created_at,"%4d-%2d-%2dT%2d:%2d:%2dZ%n",&y,&m,&d,&hh,&mm,&ss,&end)!=6 || end!=20 ||
        y<1 || m<1 || m>12 || hh<0 || hh>23 || mm<0 || mm>59 || ss<0 || ss>59) return 0;
    for(i=0;i<19;++i) if(i!=4 && i!=7 && i!=10 && i!=13 && i!=16 &&
        (o->created_at[i]<'0' || o->created_at[i]>'9')) return 0;
    days=m==2 ? 28+((y%4==0 && y%100!=0) || y%400==0) : (m==4 || m==6 || m==9 || m==11)?30:31;
    if(d<1 || d>days) return 0;
    for(i=0;i<40;++i) if(!strchr("0123456789abcdef",o->source_revision[i])) return 0;
    return 1;
}
mef_status mef_bpm_publish(const mef_bpm_files_result *result,const char *path,
    const mef_bpm_publish_options *o,mef_error **error) {
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const detector_response_result *response=mef_bpm_result_response(service);
    const mef_request_spec *request=mef_request_view(mef_bpm_result_request(service));
    const mef_bpm_files_qc *qc=mef_bpm_files_result_qc(result);
    const unsigned char *flags;
    qfits_header *h=NULL;
    FILE *stream=NULL;
    char *temporary=NULL,*slash,key[81],value[32];
    int *buffer=NULL,fd=-1,status=-1,lx,ly;
    size_t i,n,used=0;
    mef_status failure=MEF_ERR_IO;
    if(error && *error) return MEF_ERR_INPUT;
    if(!path || path[0]!='/' || !*basename_only(path) || !response || !request || !qc || !options_valid(o))
        return failed(MEF_ERR_INPUT,"Invalid BPM publication",error);
    flags=o->mode==MEF_BPM_PUBLISH_NEW?response->reasons:mef_bpm_result_combined_flags(service);
    if(!flags) return failed(MEF_ERR_UNSUPPORTED,"Binary prior has no combined reason bits; choose explicit new-reasons output",error);
    if(o->mode==MEF_BPM_PUBLISH_COMBINED && qc->mask_encoding==MEF_BPM_MASK_FLAGS8 &&
        strcmp(qc->mask_registry,"WENU_BPM_V1"))
        return failed(MEF_ERR_UNSUPPORTED,"Combined output needs the matching WENU_BPM_V1 reason registry",error);
    lx=response->valid->lx; ly=response->valid->ly; n=(size_t)lx*(size_t)ly;
    if(lx<1 || ly<1 || lx>INT_MAX/ly || lx*ly>INT_MAX/2 ||
        strlen(path)>(size_t)-1-32) return failed(MEF_ERR_INPUT,"BPM output size/path limit",error);
    h=plane_header(1,8,lx,ly,"BPM"); if(!h) { failure=MEF_ERR_MEMORY; goto done; }
    memcpy(value,o->created_at,19); value[19]='\0';
    if(string_card(h,"MASKENC","REASON8") || string_card(h,"MASKREG","WENU_BPM_V1") ||
        string_card(h,"MASKROLE",o->mode==MEF_BPM_PUBLISH_NEW?"NEW":"COMBINED") ||
        string_card(h,"BPMZERO","no_detected_reasons") ||
        string_card(h,"DATE",value) || string_card(h,"TIMESYS","UTC") || string_card(h,"BPMREV",o->source_revision) ||
        string_card(h,"DETID",request->inputs[0].detector_id) ||
        string_card(h,"READMODE",qc->readout_id) || string_card(h,"BUNIT","mask") ||
        string_card(h,"ORIGFILE",basename_only(path)) ||
        string_card(h,"HIERARCH ESO PRO REC1 ID","wenu.cal.bpm")) { failure=MEF_ERR_INPUT; goto done; }
    sprintf(value,"%lu",(unsigned long)request->input_count); qfits_header_add(h,"NRAW",value,NULL,NULL);
    sprintf(value,"%d",qc->bin_x); qfits_header_add(h,"XBINNING",value,NULL,NULL);
    sprintf(value,"%d",qc->bin_y); qfits_header_add(h,"YBINNING",value,NULL,NULL);
    for(i=0;i<request->input_count;++i) used+=mef_bpm_result_qc(service)->frames[i].included_in_fit!=0;
    sprintf(value,"%lu",(unsigned long)used); qfits_header_add(h,"NUSED",value,NULL,NULL);
    (void)string_card(h,"BPMMODE",qc->mode==MEF_BPM_QUICK?"QUICK":"PROVISIONAL");
    sprintf(value,"%.17g",qc->saturation_raw); qfits_header_add(h,"SATURATE",value,NULL,NULL);
    sprintf(value,"%.17g",qc->upper_fraction); qfits_header_add(h,"UPPERFR",value,NULL,NULL);
    sprintf(value,"%.17g",qc->span_fraction); qfits_header_add(h,"SIGSPAN",value,NULL,NULL);
    for(i=0;i<request->input_count;++i) {
        sprintf(key,"HIERARCH ESO PRO REC1 RAW%lu NAME",(unsigned long)i+1);
        if(string_card(h,key,basename_only(request->inputs[i].resolved_path))) { failure=MEF_ERR_INPUT; goto done; }
    }
    for(i=0;i<request->calibration_count;++i) {
        sprintf(key,"HIERARCH ESO PRO REC1 CAL%lu NAME",(unsigned long)i+1);
        if(string_card(h,key,basename_only(request->calibrations[i].resolved_path))) { failure=MEF_ERR_INPUT; goto done; }
    }
    buffer=malloc(n*sizeof(*buffer)); temporary=malloc(strlen(path)+32);
    if(!buffer || !temporary) { failure=MEF_ERR_MEMORY; goto done; }
    strcpy(temporary,path); slash=strrchr(temporary,'/'); strcpy(slash+1,".mefpp-bpm-XXXXXX");
    fd=mkstemp(temporary);
    if(fd<0) { temporary[0]='\0'; goto done; }
    stream=fdopen(fd,"wb"); if(!stream) goto done;
    fd=-1;
    for(i=0;i<n;++i) {
        if(response->fit_state[i]>2 || response->sample_count[i]<0 ||
            (size_t)response->sample_count[i]>request->input_count) { failure=MEF_ERR_INPUT; goto done; }
        buffer[i]=flags[i];
    }
    if(intimage_write_hdu_checked(stream,buffer,lx,ly,8,h)!=0) goto done;
    qfits_header_destroy(h); h=NULL;
    if(byte_plane(stream,response->fit_state,buffer,lx,ly,"COVERAGE",NULL)!=0) goto done;
    h=plane_header(0,16,lx,ly,"NSAMPLE"); if(!h) { failure=MEF_ERR_MEMORY; goto done; }
    (void)string_card(h,"BUNIT","count");
    if(intimage_write_hdu_checked(stream,response->sample_count,lx,ly,16,h)!=0) goto done;
    qfits_header_destroy(h); h=NULL;
    if(byte_plane(stream,response->reasons,buffer,lx,ly,"NEWFLAGS","WENU_BPM_V1")!=0 ||
        byte_plane(stream,mef_bpm_result_selection(service)->data,buffer,lx,ly,"SELECTION",NULL)!=0) goto done;
    if(mef_bpm_result_prior_flags(service) &&
        byte_plane(stream,mef_bpm_result_prior_flags(service),buffer,lx,ly,"PRIORFLAGS",qc->mask_registry)!=0) goto done;
    if(mef_bpm_result_qc(service)->prior==MEF_BPM_PRIOR_BINARY) {
        if(byte_plane(stream,mef_bpm_result_prior_selection(service)->data,buffer,lx,ly,"PRIORSEL",NULL)!=0) goto done;
    }
    if(fflush(stream)!=0 || fsync(fileno(stream))!=0) goto done;
    status=fclose(stream); stream=NULL;
    if(status!=0 || link(temporary,path)!=0) { status=-1; goto done; }
    status=0;
done:
    if(stream && fclose(stream)!=0) status=-1;
    if(fd>=0) close(fd);
    if(temporary && *temporary && unlink(temporary)!=0 && status==0)
        e_warning("BPM complete; assembly remains: %s",temporary);
    if(temporary) free(temporary);
    if(buffer) free(buffer);
    qfits_header_destroy(h);
    if(status!=0) return failed(failure,"BPM publication failed; no overwrite or success",error);
    return MEF_OK;
}

static void json_string(FILE *f,const char *text) {
    const unsigned char *p;
    fputc('"',f);
    for(p=(const unsigned char *)text;*p;++p) {
        if(*p=='"' || *p=='\\') { fputc('\\',f); fputc(*p,f); }
        else if(*p<32) fprintf(f,"\\u%04x",(unsigned int)*p);
        else fputc(*p,f);
    }
    fputc('"',f);
}
static void image_ref(FILE *f,const mef_image_ref *ref) {
    fputs("{\"path\":",f); json_string(f,ref->resolved_path);
    fprintf(f,",\"hdu\":%d,\"asset_id\":",ref->hdu_index); json_string(f,ref->asset_record_id);
    fputc('}',f);
}
mef_status mef_bpm_write_handoff(FILE *f,const mef_bpm_files_result *result,
    const char *path,const mef_bpm_publish_options *o,mef_error **error) {
    const mef_bpm_result *service=mef_bpm_files_result_service(result);
    const mef_config *config=mef_bpm_result_configuration(service);
    const mef_request *owner=mef_bpm_result_request(service);
    const mef_request_spec *rq=mef_request_view(owner);
    const mef_resolved_request_spec *resolved=mef_request_resolved_view(owner);
    const detector_response_result *response=mef_bpm_result_response(service);
    const mef_bpm_files_qc *qc=mef_bpm_files_result_qc(result);
    const mef_bpm_qc *native=mef_bpm_result_qc(service);
    const unsigned char *flags;
    const size_t *indices=mef_bpm_result_fit_indices(service);
    size_t histogram[256],coverage[3],i,j,n;
    mef_bpm_settings settings;
    struct stat st;
    if(error && *error) return MEF_ERR_INPUT;
    if(!f || !rq || !qc || !response || !options_valid(o) || !path || path[0]!='/' ||
        stat(path,&st)!=0 || !S_ISREG(st.st_mode) ||
        mef_config_bpm_settings(config,qc->configuration_detector,&settings)!=MEF_OK)
        return failed(MEF_ERR_INPUT,"Incomplete BPM handoff",error);
    /* Thresholds are shared config fields; geometry is already bound in result. */
    flags=o->mode==MEF_BPM_PUBLISH_NEW?response->reasons:mef_bpm_result_combined_flags(service);
    if(!flags) return failed(MEF_ERR_UNSUPPORTED,"Combined binary-prior reasons unavailable",error);
    memset(histogram,0,sizeof(histogram)); memset(coverage,0,sizeof(coverage));
    n=(size_t)response->valid->lx*(size_t)response->valid->ly;
    for(i=0;i<n;++i) {
        if(response->fit_state[i]>2) return failed(MEF_ERR_INPUT,"Invalid fit coverage state",error);
        ++histogram[flags[i]]; ++coverage[response->fit_state[i]];
    }
    fputs("{\"status\":\"complete\",\"handoff_version\":1,\"operation\":\"cal.bpm\",\"output\":",f); json_string(f,path);
    fputs(",\"created_at\":",f); json_string(f,o->created_at);
    fputs(",\"source_revision\":",f); json_string(f,o->source_revision);
    fputs(",\"detector_id\":",f); json_string(f,rq->inputs[0].detector_id);
    fprintf(f,",\"configuration_detector\":%lu",(unsigned long)qc->configuration_detector);
    fputs(",\"prior_registry\":",f); json_string(f,qc->mask_registry);
    fputs(",\"exposure_key\":",f); json_string(f,qc->exposure_key);
    fputs(",\"readout_id\":",f); json_string(f,qc->readout_id);
    fprintf(f,",\"bin_x\":%d,\"bin_y\":%d",qc->bin_x,qc->bin_y);
    fprintf(f,",\"exposure_hdu\":%d",qc->exposure_hdu);
    fprintf(f,",\"output_mode\":%d,\"shape\":[%d,%d],\"mode\":%d,\"mask_encoding\":%d,\"prior_active_only\":%d,\"binary_good_value\":%d,\"reject_bits\":%u,",
        o->mode,response->valid->ly,response->valid->lx,qc->mode,qc->mask_encoding,qc->prior_active_only,qc->binary_good_value,qc->reject_bits);
    fprintf(f,"\"parameters\":{\"saturation_raw\":%.17g,\"upper_fraction\":%.17g,\"minimum_span_fraction\":%.17g,\"maximum_pair_difference\":%.17g,\"response_low\":%.17g,\"response_high\":%.17g,\"proportional\":%d},",
        qc->saturation_raw,qc->upper_fraction,qc->minimum_span_fraction,qc->maximum_pair_difference,settings.low,settings.high,response->proportional);
    fprintf(f,"\"coverage\":{\"usable_pairs\":%lu,\"distinct_times\":%lu,\"paired_levels\":%lu,\"span_fraction\":%.17g},\"rois\":[",
        (unsigned long)qc->usable_pairs,(unsigned long)qc->distinct_times,(unsigned long)qc->paired_levels,qc->span_fraction);
    for(i=0;i<qc->roi_count;++i) fprintf(f,"%s[%d,%d,%d,%d]",i?",":"",qc->rois[i][0],qc->rois[i][1],qc->rois[i][2],qc->rois[i][3]);
    fputs("],\"configuration\":",f);
    if(mef_config_dump(config,f)!=MEF_OK) return failed(MEF_ERR_IO,"Configuration handoff failed",error);
    fputs(",\"inputs\":[",f);
    for(i=0;i<rq->input_count;++i) {
        const mef_bpm_frame_qc *q=native->frames+i;
        if(i) fputc(',',f);
        fputs("{\"file\":",f); image_ref(f,rq->inputs+i);
        fprintf(f,",\"integration_seconds\":%.17g,\"pair_id\":%lu,\"included\":%d,\"saturated\":%lu,\"margin_excluded\":%lu,\"sample_excluded\":%lu,\"nonfinite\":%lu,\"reference_samples\":%lu,\"reference_fraction\":",
            qc->integration_seconds[i],(unsigned long)qc->pair_ids[i],q->included_in_fit,(unsigned long)q->saturated,
            (unsigned long)q->margin_excluded,(unsigned long)q->sample_excluded,(unsigned long)q->nonfinite,(unsigned long)q->reference_samples);
        if(q->included_in_fit) fprintf(f,"%.17g",q->reference_fraction_median); else fputs("null",f);
        fputs(",\"reference_level\":",f);
        for(j=0;j<(size_t)response->plane_count;++j) if(indices[j]==i) break;
        if(j<(size_t)response->plane_count) fprintf(f,"%.17g",response->reference_levels[j]); else fputs("null",f);
        fputc('}',f);
    }
    fputs("],\"calibrations\":[",f);
    for(i=0;i<rq->calibration_count;++i) {
        if(i) fputc(',',f);
        fputs("{\"role\":",f); json_string(f,resolved->calibration_roles[i]==MEF_CAL_BIAS?"bias":"bpm");
        fputs(",\"file\":",f); image_ref(f,rq->calibrations+i); fputc('}',f);
    }
    fputs("],\"reason_histogram\":[",f);
    for(i=0;i<256;++i) fprintf(f,"%s%lu",i?",":"",(unsigned long)histogram[i]);
    fprintf(f,"],\"fit_histogram\":[%lu,%lu,%lu]}\n",(unsigned long)coverage[0],(unsigned long)coverage[1],(unsigned long)coverage[2]);
    if(fflush(f)!=0 || ferror(f)) return failed(MEF_ERR_IO,"BPM handoff write failed",error);
    return MEF_OK;
}
