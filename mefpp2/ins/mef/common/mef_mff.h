#ifndef MEF_MFF_H
#define MEF_MFF_H

#include "mef_layout.h"
#include "mef_mef_assemble.h"
#include "mef_product_qc.h"
#include "mef_recipe_run.h"
#include "mef_toml_file.h"

enum { MFF_DOME, MFF_SKY, MFF_BPM, MFF_COMPONENTS };

typedef struct {
    char *path;
    char sha256[65];
    mef_layout *layout;
    mef_layout_map *mapping;
} mef_mff_component;

typedef struct {
    const char *id, *amplifier;
    int slot;
    char temporary_path[MEF_PRODUCT_PATH_SIZE];
    double median;
    mef_qc_measurement input_qc[2], output_qc;
    mef_qc_input_binding input[2];
} mef_mff_detector;

typedef struct {
    mef_recipe_run *run;
    mef_error *error;
    mef_toml_file recipe, profile, project_evidence;
    char *output;
    const char *reference, *filter, *instrument, *readout;
    int radius, bin_x, bin_y, bpm_good;
    mef_mff_component components[MFF_COMPONENTS];
    size_t detector_count;
    mef_mff_detector *detectors;
    mef_assembly_detector *assembly;
    mef_qc_detector_record *qc;
    mef_qc_calibration_binding *bpm_bindings;
} mef_mff;

int mef_mff_admit(mef_mff *, const char *);
void mef_mff_destroy(mef_mff *);
int mef_mff_inputs_unchanged(mef_mff *);
int mef_mff_process(mef_mff *, size_t);
int mef_mff_publish(mef_mff *);
#endif
