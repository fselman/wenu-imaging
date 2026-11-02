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
int main(int argc, char **argv)
{
    const char *keys[16], *values[16], *diagnostic;
    int i, j, hdu, detector, bin_x, bin_y, exit_status;
    int okay;
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
    for (i = 0; i < 16; ++i) values[i] = NULL;
    if (argc < 3 || strcmp(argv[1], "cal") || strcmp(argv[2], "bias")) goto usage;
    for (i = 3; i < argc; i += 2) {
        if (i + 1 >= argc) goto usage;
        for (j = 0; j < 16; ++j) if (!strcmp(argv[i], keys[j])) break;
        if (j == 16 || values[j] != NULL || !*argv[i + 1]) goto usage;
        values[j] = argv[i + 1];
    }
    if ((values[0] == NULL) == (values[1] == NULL)) goto usage;
    for (i = 2; i < 15; ++i) if (values[i] == NULL) goto usage;
    if (!integer(values[4], 0, &hdu) || !integer(values[5], 0, &detector) ||
        !integer(values[7], 1, &bin_x) || !integer(values[8], 1, &bin_y) ||
        strcmp(values[9], "omitted") || !directory(values[11])) goto usage;
    for (i = 0; i < 15; ++i)
        if ((i <= 2 || i >= 10) && values[i] != NULL && values[i][0] != '/') goto usage;
    if (strlen(values[10]) >= sizeof(output_directory)) goto usage;
    strcpy(output_directory, values[10]); slash = strrchr(output_directory, '/');
    if (slash[1] == '\0') goto usage;
    if (slash == output_directory) slash[1] = '\0'; else *slash = '\0';
    if (!directory(output_directory)) goto usage;
    legacy = NULL; config = NULL; document = NULL; request = NULL; context = NULL;
    result = NULL; error = NULL; layout = NULL; maps = NULL; refs = NULL; frames = NULL;
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
    memset(&spec, 0, sizeof(spec));
    spec.request.operation = MEF_OP_CAL_BIAS; spec.request.operation_version = 1;
    spec.request.inputs = refs; spec.request.input_count = (size_t)frames->n;
    spec.request.work_dir = values[11]; spec.request.output_dir = output_directory;
    spec.request.log_path = values[12];
    bpm.detector_id = values[3]; bpm.state = MEF_BPM_OMITTED;
    spec.bpm_selections = &bpm; spec.bpm_selection_count = 1;
    status = mef_request_create_resolved(&spec, NULL, &request, &error);
    if (status != MEF_OK) goto done;
    status = mef_context_create(config, request, NULL, &context, &error);
    if (status != MEF_OK) goto done;
    /* Keep output record independent of FITS commit. Reserve it now; a failure
     * leaves a truthful failed/incomplete attempt, never a completed receipt. */
    stream = fresh(values[14]);
    if (stream == NULL) goto done;
    status = mef_bias_files_execute(context, (const mef_layout_map *const *)maps,
        (size_t)frames->n, values[3], values[10], &result, &error);
    if (status == MEF_OK) {
        qc = mef_bias_result_qc(result);
        fprintf(stream, "{\"status\":\"complete\",\"variance\":\"unavailable_legacy\",\"bpm\":\"omitted\",\"accepted_frames\":%d,\"frames\":[", qc->accepted_frames);
        for (i = 0; i < frames->n; ++i)
            fprintf(stream, "%s{\"index\":%d,\"accepted\":%d,\"scan_median\":%.9g,\"scan_stdev\":%.9g}",
                i ? "," : "", i, qc->accepted[i], qc->scan_median[i], qc->scan_stdev[i]);
        fprintf(stream, "]}\n");
    } else fprintf(stream, "{\"status\":\"failed\",\"code\":%d}\n", (int)status);
    okay = close_record(stream, 1);
    if (status != MEF_OK || !okay) goto done;
    exit_status = EXIT_SUCCESS;
done:
    if (error != NULL) fprintf(stderr, "%s\n", mef_error_message(error));
    if (exit_status != EXIT_SUCCESS) fprintf(stderr, "Bias attempt failed; retain its log and records.\n");
    mef_error_destroy(error); mef_layout_destroy(layout);
    if (maps != NULL && frames != NULL)
        for (i = 0; i < frames->n; ++i) mef_layout_map_destroy(maps[i]);
    free(maps); free(refs); framelist_del(frames);
    mef_bias_result_destroy(result); mef_context_destroy(context);
    mef_request_destroy(request); mef_config_destroy(config);
    mef_config_document_destroy(document); mef_bb_del(legacy);
    return exit_status;
usage:
    fprintf(stderr, "Opt-in M5: cal bias (--pafname PAF | --config TOML) --bias ABS_LIST --detector-id ID --hdu N --config-detector ZERO_BASED --readout-id ID --bin-x N --bin-y N --input-bpm omitted --output ABS_FITS --work-dir ABS_DIR --log-path ABS_LOG --config-record ABS_JSON --qc-record ABS_JSON [--expected-extname NAME]\n");
    return EXIT_FAILURE;
}
