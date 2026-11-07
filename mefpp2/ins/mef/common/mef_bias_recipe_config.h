#ifndef MEF_BIAS_RECIPE_CONFIG_H
#define MEF_BIAS_RECIPE_CONFIG_H
#include <stddef.h>
typedef struct mef_bias_recipe_config mef_bias_recipe_config;
/* Expand only the small recipe envelope; numerical settings keep their reader.
 * Legacy CLI is borrowed unchanged when no envelope is selected. */
int mef_bias_recipe_expand(int argc, char **argv, int *expanded_argc,
    char ***expanded_argv, mef_bias_recipe_config **owner, char *, size_t);
const char *mef_bias_recipe_source(const mef_bias_recipe_config *);
const char *mef_bias_recipe_path(const mef_bias_recipe_config *);
const char *const *mef_bias_recipe_primary_keys(const mef_bias_recipe_config *, size_t *);
const char *const *mef_bias_recipe_detector_keys(const mef_bias_recipe_config *, size_t *);
void mef_bias_recipe_config_destroy(mef_bias_recipe_config *);
#endif
