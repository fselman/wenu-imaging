/* Internal bias coordinator owners and explicit phases. See GitHub issue #292. */

#ifndef MEF_BIAS_RECIPE_H
#define MEF_BIAS_RECIPE_H
#include "mef_bias_product_qc.h"
#include "mef_bias_recipe_config.h"
#include "mef_config_toml.h"
#include "mef_mef_assemble.h"
#include "mefp_lib.h"
#include "mef_recipe_run.h"

enum { CFG, READOUT, BINX, BINY, BPM, BPM_HDU, GOOD, COORDS, BPM_NAME, AMP, RAW_NAME, FIELD_COUNT };

typedef struct {
    const char *detector_id, *option_values[FIELD_COUNT];
    int *hdus;
    size_t hdu_count, configuration_index;
    int bin_x, bin_y, bpm_hdu, bpm_good_value, bpm_active_only;
    char *bpm_path;
    mef_bias_settings settings;
    mef_layout_map **raw_layouts, *mask_map;
    char temporary_path[MEF_PRODUCT_PATH_SIZE];
    mef_assembly_detector assembly;
} detector_plan;

typedef struct {
    const char *paf_path, *toml_path, *bias_list_path, *output_path, *output_directory,
        *reference_detector_id, *mad_option, *ron_first_option, *ron_second_option,
        *high_sigma_option, *qc_option;
    detector_plan *detectors;
    size_t detector_count;
} bias_recipe_arguments;

/* Safely destructible from initialization onward. Input strings remain borrowed
 * from argv or recipe_document until all processing and reporting has finished. */

typedef struct {
    mef_recipe_run *run;
    bias_recipe_arguments arguments;
    mef_bias_recipe_config *recipe_document;
    char *config_path, *listing_path, **raw_paths;
    mef_config *config;
    mef_config_document *document;
    mef_bb *legacy;
    mef_layout **layouts;
    mef_error *error;
    mef_bias_product_qc *archive;
    mef_assembly_detector *assembly;
    framelist *frames;
    mef_bias_measurement_options options;
    const char *diagnostic;
    size_t frame_count;
    int show_usage;
} mef_bias_recipe;

int mef_bias_recipe_parse_nonnegative_int(const char *, int *);
void mef_bias_recipe_initialize(mef_bias_recipe *, mef_recipe_run *);
int mef_bias_recipe_prepare(mef_bias_recipe *, int, char **);
int mef_bias_recipe_admit(mef_bias_recipe *);
int mef_bias_recipe_begin(mef_bias_recipe *);
int mef_bias_recipe_process(mef_bias_recipe *, size_t);
int mef_bias_recipe_verify(mef_bias_recipe *);
int mef_bias_recipe_publish(mef_bias_recipe *);
void mef_bias_recipe_usage(void);
void mef_bias_recipe_destroy(mef_bias_recipe *);
#endif
