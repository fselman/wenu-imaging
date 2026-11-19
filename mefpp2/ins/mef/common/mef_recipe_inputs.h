/* Shared observation-list admission. Calibrations are separate reduced products. */
#ifndef MEF_RECIPE_INPUTS_H
#define MEF_RECIPE_INPUTS_H
#include <stddef.h>

typedef struct {
    char *path, *dpr_type;
    size_t ordinal;
    int pair;
    double seconds;
} mef_recipe_input;

typedef struct {
    mef_recipe_input *rows;
    size_t count;
} mef_recipe_inputs;

int mef_recipe_inputs_read(const char *, const char *, int, mef_recipe_inputs *, char *, size_t);
int mef_recipe_inputs_pair(mef_recipe_inputs *, const char *, int, double, char *, size_t);
void mef_recipe_inputs_destroy(mef_recipe_inputs *);
#endif
