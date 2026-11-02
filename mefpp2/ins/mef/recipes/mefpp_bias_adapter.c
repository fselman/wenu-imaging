/* Opt-in first M5 command: one explicitly configured detector per invocation.
 * Not installed and never selected by the normal mefpp executable. */
#include "mef_bias_files.h"
#include "mef_bias_settings.h"
#include "mef_config_toml.h"
#include "mefp_lib.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/stat.h>
#include <unistd.h>

static int integer(const char *text, int minimum, int *out)
{
    char *end;
    long n;
    errno = 0; n = strtol(text, &end, 10);
    if (end == text || *end || errno || n < minimum || n > INT_MAX) return 0;
    *out = (int)n; return 1;
}
static int directory(const char *path)
{
    struct stat st;
    return path != NULL && path[0] == '/' && stat(path, &st) == 0 && S_ISDIR(st.st_mode);
}
static FILE *fresh(const char *path)
{
    FILE *stream;
    int fd;
    if (path == NULL || path[0] != '/') return NULL;
    fd = open(path, O_WRONLY | O_CREAT | O_EXCL, 0600);
    if (fd < 0) return NULL;
    stream = fdopen(fd, "w");
    if (stream == NULL) close(fd);
    return stream;
}
static int close_record(FILE *stream, int okay)
{
    if (stream == NULL) return 0;
    if (ferror(stream)) okay = 0;
    if (fclose(stream) != 0) okay = 0;
    return okay;
}

/* Versioned transport only: the shared Python QC writer remains the sole ASDF
 * serializer. Follow the existing config-dump JSON string escaping policy. */
static void record_string(FILE *stream, const char *text)
{
    const unsigned char *p;
    fputc('"',stream);
    for(p=(const unsigned char *)text; *p; ++p) {
        if(*p=='"' || *p=='\\') { fputc('\\',stream); fputc(*p,stream); }
        else if(*p<32) fprintf(stream,"\\u%04x",(unsigned int)*p);
        else fputc(*p,stream);
    }
    fputc('"',stream);
}
static void record_sample(FILE *stream, const image_sample_stats *s)
{
    fprintf(stream,"{\"region_pixels\":%lu,\"bpm_excluded\":%lu,\"nonfinite_excluded\":%lu,\"valid_pixels\":%lu,"
        "\"zone\":[%d,%d,%d,%d],\"bpm_supplied\":%d,\"level_available\":%d,\"stdev_available\":%d,\"mad_available\":%d,"
        "\"mean\":%.17g,\"median\":%.17g,\"stdev\":%.17g,\"mad\":%.17g}",
        (unsigned long)s->region_pixels,(unsigned long)s->bpm_excluded,(unsigned long)s->nonfinite_excluded,
        (unsigned long)s->valid_pixels,s->zone[0],s->zone[1],s->zone[2],s->zone[3],
        s->bpm_supplied,s->level_available,s->stdev_available,s->mad_available,s->mean,s->median,s->stdev,s->mad);
}
static int measurement_record(FILE *stream, const mef_bias_result *result,
    const mef_config *config, const mef_bias_settings *settings, int raw_height,
    const mef_bias_measurement_options *options, const char *const *values,
    int bpm_hdu, int good_value)
{
    const mef_request_spec *request;
    const mef_bias_qc *legacy_qc;
    const mef_bias_measurements *m;
    const mef_bias_frame_measurements *f;
    size_t i;
    int x,y,first;
    request=mef_request_view(mef_bias_result_request(result));
    legacy_qc=mef_bias_result_qc(result); m=mef_bias_result_measurements(result);
    fputs("{\"status\":\"complete\",\"handoff_version\":1,\"producer\":{\"name\":\"mefpp_m5\",\"version\":\"M5\",\"source_revision\":",stream);
    record_string(stream,MEFPP_CANDIDATE_REVISION);
    fputs("},\"detector_id\":",stream); record_string(stream,values[3]);
    fputs(",\"readout_id\":",stream); record_string(stream,values[6]);
    fprintf(stream,",\"bin_x\":%d,\"bin_y\":%d,\"configuration_detector\":%d,\"input_hdu\":%d,\"output_hdu\":1,\"output\":",atoi(values[7]),atoi(values[8]),atoi(values[5]),atoi(values[4]));
    record_string(stream,values[10]);
    fputs(",\"configuration_record\":",stream); record_string(stream,values[13]);
    fputs(",\"configuration\":",stream);
    if(mef_config_dump(config,stream)!=MEF_OK) return 0;
    fprintf(stream,",\"bpm\":{\"selected\":%d",options->bpm!=NULL);
    if(options->bpm) {
        fputs(",\"path\":",stream); record_string(stream,values[9]);
        fprintf(stream,",\"hdu\":%d,\"good_value\":%d,\"active_only\":%d",bpm_hdu,good_value,options->bpm_active_only);
    }
    fputs("},\"inputs\":[",stream);
    for(i=0;i<request->input_count;++i) {
        f=m->frames+i;
        if(i) fputc(',',stream);
        fputs("{\"path\":",stream); record_string(stream,request->inputs[i].resolved_path);
        fprintf(stream,",\"accepted\":%d,\"raw_active\":",legacy_qc->accepted[i]); record_sample(stream,&f->active_raw);
        fputs(",\"corrected_active\":",stream); record_sample(stream,&f->active_corrected);
        fputs(",\"prescan\":",stream); record_sample(stream,&f->prescan);
        fputs(",\"overscan\":",stream); record_sample(stream,&f->overscan);
        fprintf(stream,",\"scan_correction\":{\"median\":%.17g,\"stdev\":%.17g,\"rows\":%d,\"prescan_used\":%d,\"overscan_used\":%d,\"rejection\":[%d,%d]}}",
            legacy_qc->scan_median[i],legacy_qc->scan_stdev[i],raw_height,
            settings->use_prescan!=0,settings->use_overscan!=0,settings->rejection[0],settings->rejection[1]);
    }
    fputs("],\"master\":",stream); record_sample(stream,&m->master);
    fputs(",\"master_unmasked\":",stream); record_sample(stream,&m->master_unmasked);
    fputs(",\"raw_difference\":",stream); record_sample(stream,&m->raw_difference);
    fprintf(stream,",\"ron\":{\"pair_set\":%d,\"first\":%lu,\"second\":%lu,\"stdev_available\":%d,\"mad_available\":%d,\"stdev_adu\":%.17g,\"mad_adu\":%.17g},",
        options->ron_pair_set,(unsigned long)m->ron_first,(unsigned long)m->ron_second,
        m->ron_stdev_available,m->ron_mad_available,m->ron_stdev_adu,m->ron_mad_adu);
    fprintf(stream,"\"high_offset\":{\"available\":%d,\"degenerate\":%d,\"threshold\":%.17g,\"sigma\":%.17g,\"count\":%lu,\"locations\":[",
        m->high_offset_available,m->high_offset_degenerate,m->high_offset_threshold,options->high_sigma,(unsigned long)m->high_offset_count);
    first=1;
    if(m->high_offset_flags) for(y=0;y<m->high_offset_flags->ly;++y) for(x=0;x<m->high_offset_flags->lx;++x)
        if(m->high_offset_flags->data[y*m->high_offset_flags->lx+x]) {
            fprintf(stream,"%s[%d,%d]",first?"":",",x+1,y+1); first=0;
        }
    fputs("]}}\n",stream);
    return !ferror(stream);
}

int main(int argc, char **argv)
{
    const char *keys[25], *values[25], *diagnostic;
    int i, j, hdu, detector, bin_x, bin_y, exit_status;
    int okay, measured, bpm_hdu, good_value;
    pixelmap *mask, *loaded_mask;
    mef_layout_map *bpm_map;
    mef_image_ref calibration;
    mef_calibration_role role;
    mef_bias_measurement_options measurements;
    const mef_bound_detector *mask_bound, *raw_bound;
    int x, y;
    char *end;
    double high_sigma;
    mef_bb *legacy;
    mef_config *config;
    mef_config_document *document;
    mef_request *request;
    mef_context *context;
    mef_bias_result *result;
    mef_error *error;
    mef_status status;
    mef_bias_settings settings;
    mef_layout_options options;
    mef_detector_binding binding;
    mef_layout *layout;
    mef_layout_map **maps;
    const mef_bound_detector *bound;
    mef_image_ref *refs;
    mef_bpm_selection bpm;
    mef_resolved_request_spec spec;
    framelist *frames;
    FILE *stream;
    char message[512], output_directory[4096], *slash;
    const mef_bias_qc *qc;
    keys[0] = "--pafname"; keys[1] = "--config"; keys[2] = "--bias";
    keys[3] = "--detector-id"; keys[4] = "--hdu"; keys[5] = "--config-detector";
    keys[6] = "--readout-id"; keys[7] = "--bin-x"; keys[8] = "--bin-y";
    keys[9] = "--input-bpm"; keys[10] = "--output"; keys[11] = "--work-dir";
    keys[12] = "--log-path"; keys[13] = "--config-record"; keys[14] = "--qc-record";
    keys[15] = "--expected-extname";
    keys[16]="--measurements"; keys[17]="--bpm-hdu"; keys[18]="--bpm-good-value";
    keys[19]="--bpm-coordinates"; keys[20]="--bpm-expected-extname"; keys[21]="--mad";
    keys[22]="--ron-first"; keys[23]="--ron-second"; keys[24]="--high-sigma";
    for (i = 0; i < 25; ++i) values[i] = NULL;
    if (argc < 3 || strcmp(argv[1], "cal") || strcmp(argv[2], "bias")) goto usage;
    for (i = 3; i < argc; i += 2) {
        if (i + 1 >= argc) goto usage;
        for (j = 0; j < 25; ++j) if (!strcmp(argv[i], keys[j])) break;
        if (j == 25 || values[j] != NULL || !*argv[i + 1]) goto usage;
        values[j] = argv[i + 1];
    }
    if ((values[0] == NULL) == (values[1] == NULL)) goto usage;
    for (i = 2; i < 15; ++i) if (values[i] == NULL) goto usage;
    if (!integer(values[4], 0, &hdu) || !integer(values[5], 0, &detector) ||
        !integer(values[7], 1, &bin_x) || !integer(values[8], 1, &bin_y) ||
        !directory(values[11])) goto usage;
    for (i = 0; i < 15; ++i)
        if ((i <= 2 || i >= 10) && values[i] != NULL && values[i][0] != '/') goto usage;
    measured = values[16] != NULL;
    memset(&measurements,0,sizeof(measurements));
    bpm_hdu=good_value=0;
    high_sigma=5;
    if (measured) {
        if (strcmp(values[16],"yes") || values[21]==NULL ||
            (strcmp(values[21],"yes") && strcmp(values[21],"no"))) goto usage;
        measurements.with_mad=!strcmp(values[21],"yes");
        if ((values[22]==NULL)!=(values[23]==NULL)) goto usage;
        if (values[22]) {
            if (!integer(values[22],0,&i) || !integer(values[23],0,&j) || i==j) goto usage;
            measurements.ron_pair_set=1; measurements.ron_first=(size_t)i; measurements.ron_second=(size_t)j;
        }
        if(values[24]) {
            errno=0; high_sigma=strtod(values[24],&end);
            if(end==values[24] || *end || errno || !isfinite(high_sigma) || high_sigma<=0) goto usage;
        }
    } else for(i=17;i<25;++i) if(values[i]) goto usage;
    measurements.high_sigma=high_sigma;
    if(strcmp(values[9],"omitted")) {
        if(!measured || values[9][0]!='/' || !values[17] || !values[18] || !values[19] ||
            !integer(values[17],0,&bpm_hdu) || !integer(values[18],0,&good_value) || good_value>1 ||
            (strcmp(values[19],"raw") && strcmp(values[19],"active"))) goto usage;
        measurements.bpm_active_only=!strcmp(values[19],"active");
    } else for(i=17;i<=20;++i) if(values[i]) goto usage;
    if (strlen(values[10]) >= sizeof(output_directory)) goto usage;
    strcpy(output_directory, values[10]); slash = strrchr(output_directory, '/');
    if (slash[1] == '\0') goto usage;
    if (slash == output_directory) slash[1] = '\0'; else *slash = '\0';
    if (!directory(output_directory)) goto usage;
    legacy = NULL; config = NULL; document = NULL; request = NULL; context = NULL;
    result = NULL; error = NULL; layout = NULL; maps = NULL; refs = NULL; frames = NULL;
    mask=loaded_mask=NULL; bpm_map=NULL;
    exit_status = EXIT_FAILURE;
    eclipse_init();
    /* A fresh log/record can never overwrite a raw file or earlier attempt. */
    stream = fresh(values[12]);
    if (!close_record(stream, 1)) goto done;
    set_logfilename((char *)values[12]); set_logfile(1);
    if (values[0] != NULL) {
        legacy = mef_bb_new_from_paf((char *)values[0]);
        if (legacy == NULL) goto done;
        status = mef_config_from_legacy(legacy, NULL, &config, &diagnostic);
    } else {
        mef_config_toml_initialize();
        status = mef_config_document_from_toml(values[1], NULL, &document, message, sizeof(message));
        if (status != MEF_OK) { fprintf(stderr, "%s\n", message); goto done; }
        status = mef_config_clone(mef_config_document_settings(document), NULL, &config, &diagnostic);
    }
    if (status != MEF_OK) goto done;
    mef_bb_del(legacy); legacy = NULL;
    if (mef_config_bias_settings(config, (size_t)detector, &settings) != MEF_OK) goto done;
    stream = fresh(values[13]);
    okay = stream != NULL && mef_config_dump(config, stream) == MEF_OK;
    if (!close_record(stream, okay)) goto done;
    frames = framelist_load((char *)values[2]);
    if (frames == NULL || frames->n <= 0 || frames->n > 100000 ||
        (size_t)frames->n > (size_t)-1 / sizeof(*maps) ||
        (size_t)frames->n > (size_t)-1 / sizeof(*refs)) goto done;
    maps = calloc((size_t)frames->n, sizeof(*maps));
    refs = calloc((size_t)frames->n, sizeof(*refs));
    if (maps == NULL || refs == NULL) goto done;
    memset(&options, 0, sizeof(options));
    options.max_hdus = 4096; options.max_header_bytes = 16 * 1024 * 1024;
    memset(&binding, 0, sizeof(binding));
    binding.detector_id = values[3]; binding.hdu_index = hdu;
    binding.extname = values[15]; binding.unit = "ADU";
    binding.readout_id = values[6]; binding.bin_x = bin_x; binding.bin_y = bin_y;
    binding.active_x = settings.trim[0]; binding.active_y = settings.trim[2];
    binding.active_width = settings.trim[1] - settings.trim[0] + 1;
    binding.active_height = settings.trim[3] - settings.trim[2] + 1;
    binding.configuration_detector = (size_t)detector;
    binding.health = MEF_HEALTH_UNKNOWN; binding.selection = MEF_OUTPUT_SELECTED;
    for (i = 0; i < frames->n; ++i) {
        if (frames->name[i][0] != '/') goto done;
        status = mef_layout_read(frames->name[i], &options, NULL, &layout, &error);
        if (status != MEF_OK) goto done;
        status = mef_layout_bind(layout, &binding, 1, NULL, maps + i, &error);
        mef_layout_destroy(layout); layout = NULL;
        if (status != MEF_OK) goto done;
        bound = mef_layout_find(maps[i], values[3]);
        refs[i].asset_record_id = frames->name[i]; /* Explicit local path identity. */
        refs[i].detector_id = values[3]; refs[i].resolved_path = frames->name[i];
        refs[i].hdu_index = hdu;
        /* M1's optional named selector requires EXTNAME and EXTVER together.
         * Use the explicit physical HDU when EXTVER is absent; never invent 1. */
        if (bound->image.has_extname && bound->image.has_extver) {
            refs[i].extname = bound->image.extname; refs[i].extver = bound->image.extver;
        }
    }
    if(strcmp(values[9],"omitted")) {
        binding.hdu_index=bpm_hdu; binding.extname=values[20]; binding.unit="mask";
        if(measurements.bpm_active_only) { binding.active_x=1; binding.active_y=1; }
        status=mef_layout_read(values[9],&options,NULL,&layout,&error);
        if(status!=MEF_OK) goto done;
        status=mef_layout_bind(layout,&binding,1,NULL,&bpm_map,&error);
        mef_layout_destroy(layout); layout=NULL;
        if(status!=MEF_OK || mef_layout_compatible(maps[0],bpm_map,"ADU","mask",NULL,&error)!=MEF_OK) goto done;
        raw_bound=mef_layout_find(maps[0],values[3]); mask_bound=mef_layout_find(bpm_map,values[3]);
        if(mask_bound->image.axes[0] != (size_t)(measurements.bpm_active_only ? binding.active_width : (int)raw_bound->image.axes[0]) ||
            mask_bound->image.axes[1] != (size_t)(measurements.bpm_active_only ? binding.active_height : (int)raw_bound->image.axes[1])) goto done;
        status=mef_layout_load_bpm(bpm_map,values[3],good_value,&loaded_mask,&error);
        if(status!=MEF_OK) goto done;
        if(measurements.bpm_active_only) {
            mask=pixelmap_new((int)raw_bound->image.axes[0],(int)raw_bound->image.axes[1]);
            if(mask==NULL) goto done;
            for(y=0;y<loaded_mask->ly;++y) for(x=0;x<loaded_mask->lx;++x)
                mask->data[(y+settings.trim[2]-1)*mask->lx+x+settings.trim[0]-1]=loaded_mask->data[y*loaded_mask->lx+x];
            pixelmap_updatecount(mask); pixelmap_del(loaded_mask); loaded_mask=NULL;
        } else { mask=loaded_mask; loaded_mask=NULL; }
        measurements.bpm=mask;
    }
    memset(&spec, 0, sizeof(spec));
    spec.request.operation = MEF_OP_CAL_BIAS; spec.request.operation_version = 1;
    spec.request.inputs = refs; spec.request.input_count = (size_t)frames->n;
    spec.request.work_dir = values[11]; spec.request.output_dir = output_directory;
    spec.request.log_path = values[12];
    bpm.detector_id = values[3]; bpm.state = MEF_BPM_OMITTED;
    if(mask!=NULL) {
        memset(&calibration,0,sizeof(calibration));
        calibration.asset_record_id=values[9]; calibration.detector_id=values[3];
        calibration.resolved_path=values[9]; calibration.hdu_index=bpm_hdu;
        role=MEF_CAL_BPM; spec.request.calibrations=&calibration; spec.request.calibration_count=1;
        spec.calibration_roles=&role; spec.calibration_role_count=1; bpm.state=MEF_BPM_SELECTED;
    }
    spec.bpm_selections = &bpm; spec.bpm_selection_count = 1;
    status = mef_request_create_resolved(&spec, NULL, &request, &error);
    if (status != MEF_OK) goto done;
    status = mef_context_create(config, request, NULL, &context, &error);
    if (status != MEF_OK) goto done;
    /* Keep output record independent of FITS commit. Reserve it now; a failure
     * leaves a truthful failed/incomplete attempt, never a completed receipt. */
    stream = fresh(values[14]);
    if (stream == NULL) goto done;
    if(measured) status = mef_bias_files_execute_measurements(context, (const mef_layout_map *const *)maps,
        (size_t)frames->n, values[3], values[10], &measurements, &result, &error);
    else status = mef_bias_files_execute(context, (const mef_layout_map *const *)maps,
        (size_t)frames->n, values[3], values[10], &result, &error);
    okay=1;
    if (status == MEF_OK && measured) okay=measurement_record(stream,result,config,&settings,
        (int)mef_layout_find(maps[0],values[3])->image.axes[1],&measurements,values,bpm_hdu,good_value);
    else if (status == MEF_OK) {
        qc = mef_bias_result_qc(result);
        fprintf(stream, "{\"status\":\"complete\",\"variance\":\"unavailable_legacy\",\"bpm\":\"omitted\",\"accepted_frames\":%d,\"frames\":[", qc->accepted_frames);
        for (i = 0; i < frames->n; ++i)
            fprintf(stream, "%s{\"index\":%d,\"accepted\":%d,\"scan_median\":%.9g,\"scan_stdev\":%.9g}",
                i ? "," : "", i, qc->accepted[i], qc->scan_median[i], qc->scan_stdev[i]);
        fprintf(stream, "]}\n");
    } else fprintf(stream, "{\"status\":\"failed\",\"code\":%d}\n", (int)status);
    okay = close_record(stream, okay);
    if (status != MEF_OK || !okay) goto done;
    exit_status = EXIT_SUCCESS;
done:
    if (error != NULL) fprintf(stderr, "%s\n", mef_error_message(error));
    if (exit_status != EXIT_SUCCESS) fprintf(stderr, "Bias attempt failed; retain its log and records.\n");
    mef_error_destroy(error); mef_layout_destroy(layout);
    if (maps != NULL && frames != NULL)
        for (i = 0; i < frames->n; ++i) mef_layout_map_destroy(maps[i]);
    pixelmap_del(mask); pixelmap_del(loaded_mask); mef_layout_map_destroy(bpm_map);
    free(maps); free(refs); framelist_del(frames);
    mef_bias_result_destroy(result); mef_context_destroy(context);
    mef_request_destroy(request); mef_config_destroy(config);
    mef_config_document_destroy(document); mef_bb_del(legacy);
    return exit_status;
usage:
    fprintf(stderr, "Opt-in M5: cal bias (--pafname PAF | --config TOML) --bias ABS_LIST --detector-id ID --hdu N --config-detector ZERO_BASED --readout-id ID --bin-x N --bin-y N --input-bpm (omitted|ABS_FITS) --output ABS_FITS --work-dir ABS_DIR --log-path ABS_LOG --config-record ABS_JSON --qc-record ABS_JSON [--expected-extname NAME] [--measurements yes --mad (yes|no) [--ron-first INDEX --ron-second INDEX] [--high-sigma K]] [--bpm-hdu N --bpm-good-value (0|1) --bpm-coordinates (raw|active) [--bpm-expected-extname NAME]]\n");
    return EXIT_FAILURE;
}
