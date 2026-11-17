#ifndef MEF_FLAT_STACK_H
#define MEF_FLAT_STACK_H

#include "mef_flat_product.h"
#include "mef_mef_assemble.h"
#include "mef_recipe_inputs.h"
#include "mef_product_qc.h"
#include "mefp_lib.h"

typedef struct {
    char id[32], sha256[65];
} mef_flat_input;

typedef struct {
    int hdu, accepted;
    double normalization;
    mef_qc_measurement measurement;
} mef_flat_exposure;

typedef struct {
    const char *id, *amplifier;
    int normalized, slot, raw_width, raw_height;
    mef_ccd ccd;
    mef_bb stack;
    mef_flat_exposure *exposures;
    float illumination;
    char staged[MEF_PRODUCT_PATH_SIZE];
} mef_flat_detector;

typedef struct {
    mef_recipe_run *run;
    mef_error *error;
    mef_toml_file recipe, project, detector;
    char list_sha256[65];
    char *output;
    const char *list_path, *instrument, *filter, *readout;
    int bin_x, bin_y;
    mef_recipe_inputs inputs;
    mef_flat_input *frames;
    mef_flat_detector *detectors;
    size_t detector_count, reference;
    mef_assembly_detector *assembly;
} mef_flat_stack;

int mef_flat_stack_admit(mef_flat_stack *, const char *);
int mef_flat_stack_process(mef_flat_stack *);
int mef_flat_stack_publish(mef_flat_stack *);
void mef_flat_stack_destroy(mef_flat_stack *);

#endif
