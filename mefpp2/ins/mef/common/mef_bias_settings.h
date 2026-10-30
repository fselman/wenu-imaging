/* Internal C90 bias settings view; copied values, no borrowed pointers. */
#ifndef MEF_BIAS_SETTINGS_H
#define MEF_BIAS_SETTINGS_H
#include "mef_config.h"
typedef struct {
    int prescan[2], overscan[2], trim[4], rejection[2];
    int use_prescan, use_overscan, minimum_frames;
    double kappa;
} mef_bias_settings;
/* Explicit zero-based configuration index, independent of physical HDU index. */
mef_status mef_config_bias_settings(const mef_config *config, size_t detector,
    mef_bias_settings *out);
#endif
