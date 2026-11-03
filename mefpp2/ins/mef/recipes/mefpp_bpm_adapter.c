/* Opt-in cal bpm command. Compose qualified services; no new estimator. */
#include "mef_bpm_publish.h"
#include "mef_bpm_settings.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>

#define MAX_FLATS 1024
#define MAX_ROIS 1024
static int number(const char *s,int minimum,int *value) {
    char *end; long n;
    errno=0; n=strtol(s,&end,10);
    if(end==s || *end || errno || n<minimum || n>INT_MAX) return 0;
    *value=(int)n; return 1;
}
static int real_number(const char *s,double *value) {
    char *end;
    errno=0; *value=strtod(s,&end);
    return end!=s && !*end && !errno && isfinite(*value);
}
static int dir(const char *s) {
    struct stat st;
    return s && s[0]=='/' && !stat(s,&st) && S_ISDIR(st.st_mode);
}
static int absent(const char *s) {
    struct stat st;
    return s && s[0]=='/' && lstat(s,&st)<0 && errno==ENOENT;
}
static FILE *fresh(const char *s) {
    int fd=open(s,O_WRONLY|O_CREAT|O_EXCL,0600); FILE *f;
    if(fd<0) return NULL;
    f=fdopen(fd,"w"); if(!f) close(fd); return f;
}
static int finish(FILE *f,int okay) {
    if(!f) return 0;
    if(ferror(f) || fflush(f) || fsync(fileno(f))) okay=0;
    if(fclose(f)) okay=0;
    return okay;
}
static mef_status bind(const char *path,int hdu,int active,int mask,
    const char *detector,const char *readout,int bx,int by,int slot,
    const mef_bias_settings *s,mef_layout_map **out,mef_error **error) {
    mef_layout_options o; mef_detector_binding b; mef_layout *layout=NULL;
    mef_status status;
    memset(&o,0,sizeof(o)); o.max_hdus=4096; o.max_header_bytes=16*1024*1024;
    memset(&b,0,sizeof(b)); b.detector_id=detector; b.hdu_index=hdu;
    b.unit=mask?"mask":"ADU"; b.readout_id=readout; b.bin_x=bx; b.bin_y=by;
    b.configuration_detector=(size_t)slot;
    b.active_x=active?1:s->trim[0]; b.active_y=active?1:s->trim[2];
    b.active_width=s->trim[1]-s->trim[0]+1; b.active_height=s->trim[3]-s->trim[2]+1;
    b.health=MEF_HEALTH_UNKNOWN; b.selection=MEF_OUTPUT_SELECTED;
    status=mef_layout_read(path,&o,NULL,&layout,error);
    if(status==MEF_OK) status=mef_layout_bind(layout,&b,1,NULL,out,error);
    mef_layout_destroy(layout); return status;
}
int mef_bpm_command(int argc,char **argv) {
    enum {PAF,CONFIG,FLATS,DET,SLOT,READOUT,BX,BY,BIAS,BIASHDU,PRIOR,PRIORHDU,
        ENCODING,GOOD,COORD,REGISTRY,REJECT,MODE,EXPOSUREKEY,EXPOSUREHDU,SAT,UPPER,
        SPAN,PAIRDIFF,ROI,MAD,OUTPUTMODE,DATE,OUTPUT,WORK,LOG,CONFIGREC,HANDOFF,NKEYS};
    const char *keys[NKEYS]={"--pafname","--config","--flats","--detector-id","--config-detector",
        "--readout-id","--bin-x","--bin-y","--master-bias","--bias-hdu","--input-bpm","--bpm-hdu",
        "--bpm-encoding","--bpm-good-value","--bpm-coordinates","--bpm-registry","--reject-bits",
        "--acquisition","--exposure-key","--exposure-hdu","--saturation","--upper-fraction",
        "--minimum-span","--maximum-pair-difference","--roi-file","--mad","--output-mode",
        "--created-at","--output","--work-dir","--log-path","--config-record","--qc-record"};
    const char *v[NKEYS],*diagnostic=NULL;
    int i,j,slot,bx,by,bias_hdu,prior_hdu=0,good=0,reject,exposure_hdu,exit_status=EXIT_FAILURE;
    size_t count=0,nroi=0,k,pairs[MAX_FLATS];
    int hdus[MAX_FLATS],rois[MAX_ROIS][4];
    char *paths[MAX_FLATS]={0},*line=NULL,*p,*q,*end;
    size_t capacity=0; ssize_t length;
    char output_dir[4096],message[512];
    FILE *f=NULL,*record=NULL;
    mef_bb *legacy=NULL; mef_config *config=NULL; mef_config_document *document=NULL;
    mef_layout_map *maps[MAX_FLATS]={0},*bias=NULL,*prior=NULL;
    mef_image_ref refs[MAX_FLATS],cal[2]; mef_calibration_role roles[2]={MEF_CAL_BIAS,MEF_CAL_BPM};
    mef_bpm_selection selection; mef_resolved_request_spec spec;
    mef_request *request=NULL; mef_context *context=NULL; mef_bpm_files_result *result=NULL;
    mef_error *error=NULL; mef_status status; mef_bpm_settings settings;
    mef_bpm_files_options o; mef_bpm_publish_options publication;
    memset(v,0,sizeof(v)); memset(&o,0,sizeof(o)); memset(refs,0,sizeof(refs));
    memset(cal,0,sizeof(cal)); memset(&spec,0,sizeof(spec));
    for(i=3;i<argc;i+=2) {
        if(i+1>=argc) goto usage;
        for(j=0;j<NKEYS;++j) if(!strcmp(keys[j],argv[i])) break;
        if(j==NKEYS || v[j] || !*argv[i+1]) goto usage;
        v[j]=argv[i+1];
    }
    if((v[PAF]==NULL)==(v[CONFIG]==NULL)) goto usage;
    for(i=FLATS;i<NKEYS;++i)
        if(i!=PRIORHDU && i!=GOOD && i!=COORD && i!=REGISTRY && !v[i]) goto usage;
    if(!number(v[SLOT],0,&slot) || !number(v[BX],1,&bx) || !number(v[BY],1,&by) ||
       !number(v[BIASHDU],0,&bias_hdu) || !number(v[EXPOSUREHDU],0,&exposure_hdu) ||
       !number(v[REJECT],0,&reject) || reject>255 || !dir(v[WORK])) goto usage;
    if(strcmp(v[MAD],"yes") && strcmp(v[MAD],"no")) goto usage;
    o.with_mad=!strcmp(v[MAD],"yes"); o.exposure_key=v[EXPOSUREKEY]; o.exposure_hdu=exposure_hdu;
    if(!real_number(v[SAT],&o.saturation_raw) || o.saturation_raw<=0 ||
       !real_number(v[UPPER],&o.upper_fraction) || o.upper_fraction<=0 || o.upper_fraction>1 ||
       !real_number(v[SPAN],&o.minimum_span_fraction) || o.minimum_span_fraction<=0 || o.minimum_span_fraction>1 ||
       !real_number(v[PAIRDIFF],&o.maximum_pair_difference) || o.maximum_pair_difference<0) goto usage;
    if(!strcmp(v[MODE],"quick")) o.mode=MEF_BPM_QUICK;
    else if(!strcmp(v[MODE],"provisional")) o.mode=MEF_BPM_PROVISIONAL; else goto usage;
    if(!strcmp(v[OUTPUTMODE],"new")) publication.mode=MEF_BPM_PUBLISH_NEW;
    else if(!strcmp(v[OUTPUTMODE],"combined")) publication.mode=MEF_BPM_PUBLISH_COMBINED; else goto usage;
    publication.created_at=v[DATE]; publication.source_revision=MEFPP_CANDIDATE_REVISION;
    if(!strcmp(v[PRIOR],"omitted")) {
        if(strcmp(v[ENCODING],"omitted") || v[PRIORHDU] || v[GOOD] || v[COORD] || v[REGISTRY]) goto usage;
        o.mask_encoding=MEF_BPM_MASK_OMITTED;
    } else {
        if(v[PRIOR][0]!='/' || !v[PRIORHDU] || !v[COORD] || !number(v[PRIORHDU],0,&prior_hdu) ||
           (strcmp(v[COORD],"active") && strcmp(v[COORD],"raw"))) goto usage;
        o.prior_active_only=!strcmp(v[COORD],"active");
        if(!strcmp(v[ENCODING],"reason8")) {
            if(!v[REGISTRY] || v[GOOD]) goto usage;
            o.mask_encoding=MEF_BPM_MASK_FLAGS8; o.mask_registry=v[REGISTRY];
        } else if(!strcmp(v[ENCODING],"binary")) {
            if(!v[GOOD] || v[REGISTRY] || !number(v[GOOD],0,&good) || good>1 || publication.mode!=MEF_BPM_PUBLISH_NEW) goto usage;
            o.mask_encoding=MEF_BPM_MASK_BINARY; o.binary_good_value=good;
        } else goto usage;
    }
    o.reject_bits=(unsigned int)reject;
    for(i=0;i<NKEYS;++i) if(v[i] && (i==PAF || i==CONFIG || i==FLATS || i==BIAS || i==ROI || i>=OUTPUT) && v[i][0]!='/') goto usage;
    if(strlen(v[OUTPUT])>=sizeof(output_dir)) goto usage;
    strcpy(output_dir,v[OUTPUT]); p=strrchr(output_dir,'/');
    if(!p[1]) goto usage;
    if(p==output_dir) p[1]=0; else *p=0;
    if(!dir(output_dir)) goto usage;
    /* Reject collisions before any computation or attempt-file creation. */
    for(i=LOG;i<NKEYS;++i) if(!absent(v[i])) goto done;
    if(!absent(v[OUTPUT])) goto done;
    f=fopen(v[FLATS],"r"); if(!f) goto done;
    while((length=getline(&line,&capacity,f))>=0) {
        if(count==MAX_FLATS || length>16384 || !length || memchr(line,0,(size_t)length)) goto done;
        if(line[length-1]=='\n') line[--length]=0;
        if(length && line[length-1]=='\r') line[--length]=0;
        p=strchr(line,'\t'); if(!p || line[0]!='/') goto done; *p++=0;
        q=strchr(p,'\t'); if(!q) goto done; *q++=0;
        if(strchr(q,'\t') || !number(p,0,&hdus[count]) || !number(q,0,&j) || j>=MAX_FLATS) goto done;
        paths[count]=strdup(line); if(!paths[count]) goto done;
        pairs[count++]=(size_t)j;
    }
    if(ferror(f) || !count) goto done;
    if(fclose(f)) { f=NULL; goto done; } f=NULL;
    f=fopen(v[ROI],"r"); if(!f) goto done;
    while((length=getline(&line,&capacity,f))>=0) {
        if(nroi==MAX_ROIS || length>256 || !length || memchr(line,0,(size_t)length)) goto done;
        p=line;
        for(i=0;i<4;++i) {
            long n; errno=0; n=strtol(p,&end,10);
            if(end==p || errno || n<1 || n>INT_MAX) goto done;
            if(i<3 && *end!=' ' && *end!='\t') goto done;
            rois[nroi][i]=(int)n; p=end;
        }
        while(*p==' ' || *p=='\t' || *p=='\r' || *p=='\n') ++p;
        if(*p) goto done;
        ++nroi;
    }
    if(ferror(f) || !nroi) goto done;
    if(fclose(f)) { f=NULL; goto done; } f=NULL;
    eclipse_init();
    f=fresh(v[LOG]); if(!finish(f,1)) { f=NULL; goto done; } f=NULL;
    set_logfilename((char *)v[LOG]); set_logfile(1);
    if(v[PAF]) {
        legacy=mef_bb_new_from_paf((char *)v[PAF]); if(!legacy) goto done;
        status=mef_config_from_legacy(legacy,NULL,&config,&diagnostic);
    } else {
        mef_config_toml_initialize();
        status=mef_config_document_from_toml(v[CONFIG],NULL,&document,message,sizeof(message));
        if(status!=MEF_OK) { fprintf(stderr,"%s\n",message); goto done; }
        status=mef_config_clone(mef_config_document_settings(document),NULL,&config,&diagnostic);
    }
    if(status!=MEF_OK || mef_config_bpm_settings(config,(size_t)slot,&settings)!=MEF_OK) goto done;
    f=fresh(v[CONFIGREC]);
    if(!finish(f,f && mef_config_dump(config,f)==MEF_OK)) { f=NULL; goto done; } f=NULL;
    for(k=0;k<count;++k) {
        if(bind(paths[k],hdus[k],0,0,v[DET],v[READOUT],bx,by,slot,&settings.scan,&maps[k],&error)!=MEF_OK) goto done;
        refs[k].asset_record_id=paths[k]; refs[k].resolved_path=paths[k]; refs[k].detector_id=v[DET]; refs[k].hdu_index=hdus[k];
    }
    if(bind(v[BIAS],bias_hdu,1,0,v[DET],v[READOUT],bx,by,slot,&settings.scan,&bias,&error)!=MEF_OK) goto done;
    cal[0].asset_record_id=v[BIAS]; cal[0].resolved_path=v[BIAS]; cal[0].detector_id=v[DET]; cal[0].hdu_index=bias_hdu;
    if(o.mask_encoding!=MEF_BPM_MASK_OMITTED) {
        if(bind(v[PRIOR],prior_hdu,o.prior_active_only,1,v[DET],v[READOUT],bx,by,slot,&settings.scan,&prior,&error)!=MEF_OK) goto done;
        cal[1].asset_record_id=v[PRIOR]; cal[1].resolved_path=v[PRIOR]; cal[1].detector_id=v[DET]; cal[1].hdu_index=prior_hdu;
    }
    selection.detector_id=v[DET]; selection.state=prior?MEF_BPM_SELECTED:MEF_BPM_OMITTED;
    spec.request.operation=MEF_OP_CAL_BPM; spec.request.operation_version=1;
    spec.request.inputs=refs; spec.request.input_count=count; spec.request.calibrations=cal;
    spec.request.calibration_count=prior?2:1; spec.request.work_dir=v[WORK]; spec.request.output_dir=output_dir; spec.request.log_path=v[LOG];
    spec.calibration_roles=roles; spec.calibration_role_count=prior?2:1;
    spec.bpm_selections=&selection; spec.bpm_selection_count=1;
    if(mef_request_create_resolved(&spec,NULL,&request,&error)!=MEF_OK ||
       mef_context_create(config,request,NULL,&context,&error)!=MEF_OK) goto done;
    o.pair_ids=pairs; o.rois=(const int (*)[4])rois; o.roi_count=nroi;
    record=fresh(v[HANDOFF]); if(!record) goto done;
    if(mef_bpm_from_files(context,(const mef_layout_map *const *)maps,count,v[DET],bias,prior,&o,&result,&error)!=MEF_OK ||
       mef_bpm_publish(result,v[OUTPUT],&publication,&error)!=MEF_OK) goto done;
    status=mef_bpm_write_handoff(record,result,v[OUTPUT],&publication,&error);
    if(!finish(record,status==MEF_OK)) { record=NULL; goto done; } record=NULL;
    exit_status=EXIT_SUCCESS;
    goto done;
usage:
    fprintf(stderr,"Opt-in M5: cal bpm (--pafname ABS_PAF | --config ABS_TOML)\n"
        "Required key/value options: --flats ABS_TSV(path TAB hdu TAB pair_id per row), --roi-file ABS_TEXT(xlo xhi ylo yhi per row),\n"
        "--detector-id ID --config-detector N --readout-id ID --bin-x N --bin-y N --master-bias ABS_FITS --bias-hdu N,\n"
        "--input-bpm (omitted|ABS_FITS) --bpm-encoding (omitted|reason8|binary) --reject-bits N,\n"
        "selected prior: --bpm-hdu N --bpm-coordinates (raw|active) and --bpm-registry ID or --bpm-good-value (0|1),\n"
        "--acquisition (quick|provisional) --exposure-key FULL_KEY --exposure-hdu N --saturation ADU --upper-fraction F\n"
        "--minimum-span F --maximum-pair-difference F --mad (yes|no) --output-mode (new|combined) --created-at UTC\n"
        "--output ABS_FITS --work-dir ABS_DIR --log-path ABS_LOG --config-record ABS_JSON --qc-record ABS_JSON.\n");
done:
    if(error) fprintf(stderr,"%s\n",mef_error_message(error));
    if(exit_status) fprintf(stderr,"BPM attempt failed; retain log, records and any completed FITS.\n");
    if(f) fclose(f);
    if(record) fclose(record);
    free(line); for(k=0;k<MAX_FLATS;++k) { free(paths[k]); mef_layout_map_destroy(maps[k]); }
    mef_layout_map_destroy(bias); mef_layout_map_destroy(prior); mef_bpm_files_result_destroy(result);
    mef_context_destroy(context); mef_request_destroy(request); mef_config_destroy(config);
    mef_config_document_destroy(document); mef_bb_del(legacy); mef_error_destroy(error);
    return exit_status;
}
