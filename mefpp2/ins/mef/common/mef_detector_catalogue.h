#ifndef MEF_DETECTOR_CATALOGUE_H
#define MEF_DETECTOR_CATALOGUE_H

#include "tomlc17.h"

typedef struct {
    const char *id;
    int slot;
    int reference_hdu; /* -1 for older profiles without a default HDU. */
    int enabled;
    toml_datum_t definition;
} mef_detector_definition;

/* Definitions borrow the parsed profile. Legacy profiles default to enabled. */
int mef_detector_catalogue_valid(toml_datum_t profile);
int mef_detector_catalogue_entry(toml_datum_t profile, int index,
    mef_detector_definition *out);
int mef_detector_catalogue_find(toml_datum_t profile, const char *id,
    mef_detector_definition *out);

#endif
