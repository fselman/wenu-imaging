#ifndef MEF_FLAT_PRODUCT_H
#define MEF_FLAT_PRODUCT_H

#include "mef_recipe_run.h"
#include "mef_toml_file.h"
#include "image_handling.h"

char *mef_flat_resolve(const char *directory, const char *name);
char *mef_flat_relative_to_file(const char *file, const char *name);
int mef_flat_below(const char *root, const char *path);
int mef_flat_project_paths(mef_recipe_run *, const mef_toml_file *recipe,
    const char *project, const char *run_name, mef_toml_file *evidence,
    char **output, char **calibration, char **raw);
int mef_flat_stage_detector(const char *destination, const char *category,
    const char *instrument, const char *filter, const char *id, double median,
    const char *source_path, int source_hdu, image_t *image);

#endif
