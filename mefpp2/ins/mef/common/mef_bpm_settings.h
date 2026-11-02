#ifndef MEF_BPM_SETTINGS_H
#define MEF_BPM_SETTINGS_H
#include "mef_bias_settings.h"
typedef struct {
    mef_bias_settings scan;
    int proportional;
    double low, high;
} mef_bpm_settings;
/* Copied settings at explicit configuration index, independent of input HDU. */
mef_status mef_config_bpm_settings(const mef_config *, size_t, mef_bpm_settings *);
#endif
