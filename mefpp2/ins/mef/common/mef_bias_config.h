#ifndef MEF_BIAS_CONFIG_H
#define MEF_BIAS_CONFIG_H
#include <stddef.h>
typedef struct mef_bias_config mef_bias_config;
/* Expand only the small recipe envelope; numerical settings keep their reader.
 * Legacy CLI is borrowed unchanged when no envelope is selected. */
int mef_bias_expand(int argc, char **argv, int *expanded_argc,
    char ***expanded_argv, mef_bias_config **owner, char *, size_t);
const char *mef_bias_source(const mef_bias_config *);
const char *mef_bias_path(const mef_bias_config *);
const char *const *mef_bias_primary_keys(const mef_bias_config *, size_t *);
const char *const *mef_bias_detector_keys(const mef_bias_config *, size_t *);
const char *mef_bias_median_even_handling(const mef_bias_config *);
void mef_bias_config_destroy(mef_bias_config *);
#endif
