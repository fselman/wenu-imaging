#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias_product_qc.h"
#include "mef_config_toml.h"
#include "mef_mef_assemble.h"
#include "mefp_lib.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

/* This uninstalled command is an explicit native caller of the existing bias
 * operation template. The installed legacy executable is unchanged. */
enum { CFG, READOUT, BINX, BINY, BPM, BPM_HDU, GOOD, COORDS, BPM_NAME, AMP, FIELD_COUNT };
typedef struct {
    const char *id, *field[FIELD_COUNT];
    int *hdus; size_t hdu_count, configured;
    int bin_x, bin_y, bpm_hdu, good, active_only;
    char *bpm_path;
    mef_bias_settings settings;
    mef_layout_map **maps, *mask_map;
    char temporary[MEF_PRODUCT_PATH_SIZE];
    mef_assembly_detector assembly;
} detector_plan;
typedef struct {
    const char *paf, *toml, *listing, *output, *output_dir, *reference, *mad, *first, *second, *sigma;
    detector_plan *detectors; size_t count;
} arguments;
static int number(const char *s, int *n)
{
    char *end; long v;
    if(s==NULL || !*s) return 0;
    errno=0; v=strtol(s,&end,10);
    if(errno || *end || v<0 || v>INT_MAX) return 0;
    *n=(int)v; return 1;
}
static int set(const char **slot,const char *value)
{ if(*slot!=NULL) return 0; *slot=value; return 1; }
static int parse(int argc,char **argv,arguments *a)
{
    static const char *keys[FIELD_COUNT]={"--config-detector","--readout-id","--bin-x","--bin-y",
        "--input-bpm","--bpm-hdu","--bpm-good-value","--bpm-coordinates","--bpm-expected-extname","--amplifier-id"};
    int i,j; detector_plan *d=NULL;
    if(argc<3 || strcmp(argv[1],"cal") || strcmp(argv[2],"bias")) return 0;
    a->detectors=calloc((size_t)argc/2,sizeof(*a->detectors)); if(a->detectors==NULL) return 0;
    for(i=3;i<argc;i+=2) {
        const char *key=argv[i], *v;
        if(i+1>=argc || !*argv[i+1]) return 0;
        v=argv[i+1];
#define ARG(name,member) if(!strcmp(key,name)) { if(!set(&a->member,v)) return 0; continue; }
        ARG("--pafname",paf) ARG("--config",toml) ARG("--bias",listing)
        ARG("--output",output) ARG("--output-dir",output_dir) ARG("--reference-detector",reference)
        ARG("--mad",mad) ARG("--ron-first",first) ARG("--ron-second",second) ARG("--high-sigma",sigma)
#undef ARG
        if(!strcmp(key,"--detector-id")) {
            if(a->count==4096) return 0;
            d=a->detectors+a->count++; d->id=v; continue;
        }
        if(d==NULL) return 0;
        if(!strcmp(key,"--hdu")) {
            int n, *next;
            if(!number(v,&n)) return 0;
            next=realloc(d->hdus,(d->hdu_count+1)*sizeof(*next)); if(next==NULL) return 0;
            d->hdus=next; d->hdus[d->hdu_count++]=n; continue;
        }
        for(j=0;j<FIELD_COUNT;++j) if(!strcmp(key,keys[j])) break;
        if(j==FIELD_COUNT || !set(d->field+j,v)) return 0;
    }
    if((a->paf==NULL)==(a->toml==NULL) || a->listing==NULL || a->reference==NULL ||
        a->mad==NULL || (strcmp(a->mad,"yes") && strcmp(a->mad,"no")) || !a->count ||
        (a->first==NULL)!=(a->second==NULL)) return 0;
    return 1;
}
static int bind_inputs(detector_plan *d,mef_layout *const *layouts,size_t n,
    const mef_config *config,mef_error **error)
{
    mef_detector_binding binding; size_t i; int configured;
    if(!number(d->field[CFG],&configured) || !number(d->field[BINX],&d->bin_x) || d->bin_x==0 ||
        !number(d->field[BINY],&d->bin_y) || d->bin_y==0 || !d->field[READOUT] ||
        !d->field[AMP] || !d->field[BPM] || (d->hdu_count!=1 && d->hdu_count!=n)) return 0;
    d->configured=(size_t)configured;
    if(mef_config_bias_settings(config,d->configured,&d->settings)!=MEF_OK) return 0;
    d->maps=calloc(n,sizeof(*d->maps)); if(d->maps==NULL) return 0;
    memset(&binding,0,sizeof(binding)); binding.detector_id=d->id; binding.unit="ADU";
    binding.extname=d->id; binding.readout_id=d->field[READOUT]; binding.bin_x=d->bin_x; binding.bin_y=d->bin_y;
    binding.active_x=d->settings.trim[0]; binding.active_y=d->settings.trim[2];
    binding.active_width=d->settings.trim[1]-d->settings.trim[0]+1;
    binding.active_height=d->settings.trim[3]-d->settings.trim[2]+1;
    binding.configuration_detector=d->configured; binding.health=MEF_HEALTH_UNKNOWN;
    binding.selection=MEF_OUTPUT_SELECTED;
    for(i=0;i<n;++i) {
        binding.hdu_index=d->hdus[d->hdu_count==1?0:i];
        /* First integrated command: explicit named MEF detector extensions.
         * The older single-primary operation remains available in mefpp_m5. */
        if(binding.hdu_index<1 || mef_layout_bind(layouts[i],&binding,1,NULL,d->maps+i,error)!=MEF_OK ||
            mef_layout_compatible(d->maps[0],d->maps[i],"ADU","ADU",NULL,error)!=MEF_OK) return 0;
        {
            const mef_bound_detector *raw=mef_layout_find(d->maps[i],d->id);
            if(raw->image.axes[0]==0 || raw->image.axes[1]==0 ||
                raw->image.axes[0]>INT_MAX || raw->image.axes[1]>INT_MAX ||
                raw->image.axes[0]>INT_MAX/raw->image.axes[1]) return 0;
        }
    }
    if(!strcmp(d->field[BPM],"omitted")) {
        for(i=BPM_HDU;i<=BPM_NAME;++i) if(d->field[i]) return 0;
    } else {
        mef_layout_options options; mef_layout *layout=NULL; mef_status status;
        const mef_bound_detector *raw,*mask;
        if(!number(d->field[BPM_HDU],&d->bpm_hdu) || !number(d->field[GOOD],&d->good) || d->good>1 ||
            !d->field[COORDS] || (strcmp(d->field[COORDS],"raw") && strcmp(d->field[COORDS],"active"))) return 0;
        d->bpm_path=realpath(d->field[BPM],NULL); if(d->bpm_path==NULL) return 0;
        d->active_only=!strcmp(d->field[COORDS],"active");
        memset(&options,0,sizeof(options)); options.max_hdus=4096; options.max_header_bytes=16*1024*1024;
        binding.hdu_index=d->bpm_hdu; binding.unit="mask"; binding.extname=d->field[BPM_NAME];
        if(d->active_only) { binding.active_x=1; binding.active_y=1; }
        status=mef_layout_read(d->bpm_path,&options,NULL,&layout,error);
        if(status==MEF_OK) status=mef_layout_bind(layout,&binding,1,NULL,&d->mask_map,error);
        mef_layout_destroy(layout);
        if(status!=MEF_OK || mef_layout_compatible(d->maps[0],d->mask_map,"ADU","mask",NULL,error)!=MEF_OK) return 0;
        raw=mef_layout_find(d->maps[0],d->id); mask=mef_layout_find(d->mask_map,d->id);
        if(mask->image.axes[0]!=(size_t)(d->active_only?binding.active_width:(int)raw->image.axes[0]) ||
            mask->image.axes[1]!=(size_t)(d->active_only?binding.active_height:(int)raw->image.axes[1])) return 0;
    }
    return 1;
}
static int process(detector_plan *d,size_t index,size_t n,char *const *raw_paths,
    const mef_config *config,const mef_product_paths *paths,const char *work,
    const mef_bias_measurement_options *options,mef_bias_product_qc *archive,mef_error **error)
{
    mef_image_ref *refs=NULL,calibration; mef_request *request=NULL; mef_context *context=NULL;
    mef_resolved_request_spec spec; mef_bpm_selection selection; mef_calibration_role role=MEF_CAL_BPM;
    mef_bias_result *result=NULL; mef_status status=MEF_ERR_INPUT;
    mef_bias_measurement_options measurements=*options;
    pixelmap *mask=NULL,*loaded=NULL; const mef_bound_detector *first;
    size_t i; int okay=0,x,y; const image_t *image;
    refs=calloc(n,sizeof(*refs)); if(refs==NULL) goto done;
    for(i=0;i<n;++i) {
        const mef_bound_detector *b=mef_layout_find(d->maps[i],d->id);
        refs[i].asset_record_id=raw_paths[i]; refs[i].resolved_path=raw_paths[i];
        refs[i].detector_id=d->id; refs[i].hdu_index=b->image.hdu_index;
        if(b->image.has_extname && b->image.has_extver) { refs[i].extname=b->image.extname; refs[i].extver=b->image.extver; }
    }
    first=mef_layout_find(d->maps[0],d->id);
    if(d->mask_map) {
        status=mef_layout_load_bpm(d->mask_map,d->id,d->good,&loaded,error); if(status!=MEF_OK) goto done;
        if(d->active_only) {
            mask=pixelmap_new((int)first->image.axes[0],(int)first->image.axes[1]); if(mask==NULL) goto done;
            for(y=0;y<loaded->ly;++y) for(x=0;x<loaded->lx;++x)
                mask->data[(y+d->settings.trim[2]-1)*mask->lx+x+d->settings.trim[0]-1]=loaded->data[y*loaded->lx+x];
            pixelmap_updatecount(mask);
        } else { mask=loaded; loaded=NULL; }
        measurements.bpm=mask; measurements.bpm_active_only=d->active_only;
    }
    memset(&spec,0,sizeof(spec)); memset(&calibration,0,sizeof(calibration));
    spec.request.operation=MEF_OP_CAL_BIAS; spec.request.operation_version=1;
    spec.request.inputs=refs; spec.request.input_count=n;
    spec.request.work_dir=work; spec.request.output_dir=paths->directory; spec.request.log_path=paths->log;
    selection.detector_id=d->id; selection.state=mask?MEF_BPM_SELECTED:MEF_BPM_OMITTED;
    spec.bpm_selections=&selection; spec.bpm_selection_count=1;
    if(mask) {
        calibration.asset_record_id=d->bpm_path; calibration.resolved_path=d->bpm_path;
        calibration.detector_id=d->id; calibration.hdu_index=d->bpm_hdu;
        spec.request.calibrations=&calibration; spec.request.calibration_count=1;
        spec.calibration_roles=&role; spec.calibration_role_count=1;
    }
    status=mef_request_create_resolved(&spec,NULL,&request,error);
    if(status==MEF_OK) status=mef_context_create(config,request,NULL,&context,error);
    if(status!=MEF_OK) goto done;
    if(snprintf(d->temporary,sizeof(d->temporary),"%s/detector-%06lu.fits",work,(unsigned long)index)>=(int)sizeof(d->temporary)) goto done;
    status=mef_bias_files_execute_measurements(context,(const mef_layout_map *const *)d->maps,n,d->id,
        d->temporary,&measurements,&result,error);
    if(status!=MEF_OK || !mef_bias_product_qc_add(archive,index,d->id,d->field[AMP],d->field[READOUT],
        d->configured,d->bin_x,d->bin_y,result,&measurements,&d->settings,(int)first->image.axes[1],
        d->bpm_path,d->bpm_hdu,d->good)) goto done;
    image=mef_bias_result_signal(result);
    d->assembly.path=d->temporary; d->assembly.detector_id=d->id;
    d->assembly.configuration_detector=d->configured; d->assembly.output_hdu=index+1;
    d->assembly.width=image->lx; d->assembly.height=image->ly; d->assembly.bitpix=BPP_DEFAULT;
    d->assembly.bscale=1; d->assembly.bzero=0;
    okay=1;
done:
    mef_bias_result_destroy(result); mef_context_destroy(context); mef_request_destroy(request);
    pixelmap_del(mask); pixelmap_del(loaded); free(refs);
    return okay;
}
int main(int argc,char **argv)
{
    arguments a; mef_product_paths paths; char start[MEF_RECIPE_TIME_SIZE],message[512]="";
    char cwd[MEF_PRODUCT_PATH_SIZE],work[MEF_PRODUCT_PATH_SIZE]="";
    char *config_path=NULL,*listing_path=NULL,**raw_paths=NULL,*end;
    mef_config *config=NULL; mef_config_document *document=NULL; mef_bb *legacy=NULL;
    mef_layout **layouts=NULL; mef_layout_options layout_options; mef_error *error=NULL;
    mef_bias_product_qc *archive=NULL; mef_assembly_detector *assembly=NULL;
    framelist *frames=NULL; FILE *log=NULL; int fd=-1,okay=0,first,second;
    mef_bias_measurement_options options; const char *diagnostic=NULL;
    mef_status status; size_t i,j,n=0; int reference_found=0;
    memset(&a,0,sizeof(a)); memset(&options,0,sizeof(options));
    /* One sampled recipe-start instant, independent of detector count. */
    if(mef_recipe_start_time(start,sizeof(start),message,sizeof(message)) ||
        getcwd(cwd,sizeof(cwd))==NULL || !parse(argc,argv,&a)) goto usage;
    if(mef_product_paths_resolve(cwd,a.output_dir,a.output,"CMDP",start,1,&paths,message,sizeof(message))) goto done;
    {
        const char *name=strrchr(paths.fits,'/')+1;
        if(strlen(name)>68 || strchr(name,'\'')) {
            strcpy(message,"Final basename exceeds the existing single-card ORIGFILE contract"); goto done;
        }
        for(i=0;name[i];++i) if((unsigned char)name[i]<32 || (unsigned char)name[i]>126) {
            strcpy(message,"Final FITS basename must use printable ASCII"); goto done;
        }
    }
    options.with_mad=!strcmp(a.mad,"yes"); options.high_sigma=5;
    if(a.sigma) { errno=0; options.high_sigma=strtod(a.sigma,&end);
        if(errno || end==a.sigma || *end || !isfinite(options.high_sigma) || options.high_sigma<=0) goto usage; }
    if(a.first) {
        if(!number(a.first,&first) || !number(a.second,&second) || first==second) goto usage;
        options.ron_pair_set=1; options.ron_first=(size_t)first; options.ron_second=(size_t)second;
    }
    config_path=realpath(a.paf?a.paf:a.toml,NULL); listing_path=realpath(a.listing,NULL);
    if(config_path==NULL || listing_path==NULL) { strcpy(message,"Missing explicit configuration or bias list"); goto done; }
    eclipse_init(); set_logfile(0);
    if(a.paf) {
        legacy=mef_bb_new_from_paf(config_path); if(legacy==NULL) goto done;
        status=mef_config_from_legacy(legacy,NULL,&config,&diagnostic);
    } else {
        mef_config_toml_initialize();
        status=mef_config_document_from_toml(config_path,NULL,&document,message,sizeof(message));
        if(status==MEF_OK) status=mef_config_clone(mef_config_document_settings(document),NULL,&config,&diagnostic);
    }
    if(status!=MEF_OK) goto done;
    mef_bb_del(legacy); legacy=NULL;
    frames=framelist_load(listing_path);
    if(frames==NULL || frames->n<3 || frames->n>100000) { strcpy(message,"Require an explicit list of at least three bias inputs"); goto done; }
    n=(size_t)frames->n;
    if(options.ron_pair_set && (options.ron_first>=n || options.ron_second>=n)) goto usage;
    layouts=calloc(n,sizeof(*layouts)); raw_paths=calloc(n,sizeof(*raw_paths));
    assembly=calloc(a.count,sizeof(*assembly));
    if(layouts==NULL || raw_paths==NULL || assembly==NULL) goto done;
    memset(&layout_options,0,sizeof(layout_options)); layout_options.max_hdus=4096;
    layout_options.max_header_bytes=16*1024*1024;
    /* Header-only admission of every input/detector precedes output creation. */
    for(i=0;i<n;++i) {
        if(frames->name[i][0]!='/' || (raw_paths[i]=realpath(frames->name[i],NULL))==NULL) goto done;
        for(j=0;j<i;++j) if(!strcmp(raw_paths[i],raw_paths[j])) { strcpy(message,"Duplicate raw input path"); goto done; }
        if(mef_layout_read(raw_paths[i],&layout_options,NULL,layouts+i,&error)!=MEF_OK) goto done;
    }
    for(i=0;i<a.count;++i) {
        detector_plan *d=a.detectors+i;
        if(!bind_inputs(d,layouts,n,config,&error)) { strcpy(message,"Invalid explicit detector/BPM binding or geometry"); goto done; }
        if(!strcmp(d->id,a.reference)) reference_found=1;
        for(j=0;j<i;++j) if(!strcmp(d->id,a.detectors[j].id) || d->configured==a.detectors[j].configured) {
            strcpy(message,"Duplicate detector identity or configuration slot"); goto done;
        }
    }
    if(!reference_found) { strcpy(message,"Reference detector must be in the selected set"); goto done; }
    archive=mef_bias_product_qc_new(config,&paths,start,MEFPP_CANDIDATE_REVISION,
        (const char *const *)raw_paths,n,a.count);
    if(archive==NULL) goto done;
    fd=open(paths.log,O_WRONLY|O_CREAT|O_EXCL|O_APPEND,0600); if(fd<0) goto done;
    log=fdopen(fd,"a"); if(log==NULL) goto done; fd=-1;
    fprintf(log,"RECIPE cal.bias\nSTART %s\nSOURCE %s\nINVOCATION %s\nCONFIG %s\nINPUT_LIST %s\nFITS %s\nASDF %s\n",
        start,MEFPP_CANDIDATE_REVISION,cwd,config_path,listing_path,paths.fits,paths.asdf);
    for(i=0;i<n;++i) fprintf(log,"INPUT %lu %s\n",(unsigned long)i,raw_paths[i]);
    if(snprintf(work,sizeof(work),"%s/.mefpp-bias-XXXXXX",paths.directory)>=(int)sizeof(work) ||
        mkdtemp(work)==NULL) { work[0]='\0'; goto done; }
    fprintf(log,"PRIVATE_WORK %s\n",work); if(fflush(log)) goto done;
    set_logfilename(paths.log); set_logfile(1);
    for(i=0;i<a.count;++i) {
        fprintf(log,"DETECTOR_START %lu %s CONFIGURATION %lu\n",(unsigned long)i,a.detectors[i].id,(unsigned long)a.detectors[i].configured);
        if(fflush(log)) goto done;
        printf("BIAS_DETECTOR %lu/%lu %s\n",(unsigned long)i+1,(unsigned long)a.count,a.detectors[i].id); fflush(stdout);
        if(!process(a.detectors+i,i,n,raw_paths,config,&paths,work,&options,archive,&error)) goto done;
        assembly[i]=a.detectors[i].assembly;
        fprintf(log,"DETECTOR_DONE %s\n",a.detectors[i].id); if(fflush(log)) goto done;
    }
    /* Coordination barrier: all selected detector products are complete. Bias
     * adds no cross-detector numerical operation; flat harmonization is future. */
    if(mef_bias_product_qc_check(archive,message,sizeof(message))) goto done;
    fprintf(log,"MEF_ASSEMBLY_START\n"); if(fflush(log)) goto done;
    printf("BIAS_MEF_ASSEMBLY %s\n",paths.fits); fflush(stdout);
    if(mef_mef_assemble(paths.fits,a.reference,assembly,a.count,message,sizeof(message))) goto done;
    fprintf(log,"NATIVE_ASDF_START\n"); if(fflush(log)) goto done;
    printf("BIAS_NATIVE_ASDF %s\n",paths.asdf); fflush(stdout);
    if(mef_bias_product_qc_write(archive,message,sizeof(message))) goto done;
    set_logfile(0);
    for(i=0;i<a.count;++i) if(unlink(a.detectors[i].temporary)) fprintf(log,"RETAINED_TEMPORARY %s\n",a.detectors[i].temporary);
    if(rmdir(work)) fprintf(log,"RETAINED_PRIVATE_WORK %s\n",work);
    fprintf(log,"OUTPUTS_WRITTEN; final success requires zero command exit\n");
    if(ferror(log)) goto done;
    if(fclose(log)) { log=NULL; goto done; } log=NULL;
    printf("BIAS_RECIPE_COMPLETE\nFITS %s\nASDF %s\nLOG %s\n",paths.fits,paths.asdf,paths.log);
    okay=1; goto done;
usage:
    fprintf(stderr,"Standalone candidate: cal bias (--pafname PAF|--config TOML) --bias ABS_LIST (--output-dir DIR|--output FITS) --reference-detector ID --mad (yes|no) [--ron-first INDEX --ron-second INDEX] [--high-sigma K]\n"
        "Repeat detector blocks: --detector-id EXTNAME --config-detector ZERO_BASED --readout-id ID --bin-x N --bin-y N --amplifier-id ID --input-bpm (omitted|FITS) --hdu N [--hdu N ... one per input]\n"
        "Selected BPM additionally requires --bpm-hdu N --bpm-good-value (0|1) --bpm-coordinates (raw|active) [--bpm-expected-extname NAME]. Output parent must exist; no overwrite.\n");
done:
    set_logfile(0);
    if(!okay) {
        if(*message) fprintf(stderr,"%s\n",message);
        if(error) fprintf(stderr,"%s\n",mef_error_message(error));
        if(diagnostic) fprintf(stderr,"%s\n",diagnostic);
        if(log) { fprintf(log,"FAILED; retain existing outputs and private work %s\n",work); fclose(log); log=NULL; }
        if(*work) fprintf(stderr,"Retained private work: %s\n",work);
        fprintf(stderr,"Bias recipe incomplete; no overall success reported.\n");
    }
    if(fd>=0) close(fd);
    mef_bias_product_qc_destroy(archive); mef_error_destroy(error);
    for(i=0;i<a.count;++i) {
        if(a.detectors[i].maps) for(j=0;j<n;++j) mef_layout_map_destroy(a.detectors[i].maps[j]);
        mef_layout_map_destroy(a.detectors[i].mask_map);
        free(a.detectors[i].maps); free(a.detectors[i].hdus); free(a.detectors[i].bpm_path);
    }
    for(i=0;i<n;++i) { if(layouts) mef_layout_destroy(layouts[i]); if(raw_paths) free(raw_paths[i]); }
    free(layouts); free(raw_paths); free(assembly); free(a.detectors); free(config_path); free(listing_path);
    framelist_del(frames); mef_config_destroy(config); mef_config_document_destroy(document); mef_bb_del(legacy);
    return okay?EXIT_SUCCESS:EXIT_FAILURE;
}
