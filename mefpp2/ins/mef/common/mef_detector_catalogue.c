/* Shared detector defaults for native recipe admission. */
#include "mef_detector_catalogue.h"
#include <limits.h>
#include <string.h>

int mef_detector_catalogue_entry(toml_datum_t profile, int index,
    mef_detector_definition *out)
{
    toml_datum_t entries = toml_get(profile, "detector");
    toml_datum_t entry, id, slot, hdu, enabled;

    if (!out || entries.type != TOML_ARRAY || index < 0 || index >= entries.u.arr.size) {
        return 0;
    }
    entry = entries.u.arr.elem[index];
    id = toml_get(entry, "id");
    slot = toml_get(entry, "native_paf_chip");
    hdu = toml_get(entry, "reference_hdu");
    enabled = toml_get(entry, "enabled");

    if (entry.type != TOML_TABLE || id.type != TOML_STRING || id.u.str.len < 1 ||
        strlen(id.u.s) != (size_t)id.u.str.len || slot.type != TOML_INT64 ||
        slot.u.int64 < 1 || slot.u.int64 > INT_MAX ||
        (hdu.type != TOML_UNKNOWN &&
            (hdu.type != TOML_INT64 || hdu.u.int64 < 0 || hdu.u.int64 > 4095)) ||
        (enabled.type != TOML_UNKNOWN && enabled.type != TOML_BOOLEAN)) {
        return 0;
    }
    out->id = id.u.s;
    /* Existing instrument profiles number native slots from one. */
    out->slot = (int)slot.u.int64 - 1;
    out->reference_hdu = hdu.type == TOML_UNKNOWN ? -1 : (int)hdu.u.int64;
    out->enabled = enabled.type == TOML_UNKNOWN || enabled.u.boolean;
    out->definition = entry;
    return 1;
}

int mef_detector_catalogue_valid(toml_datum_t profile)
{
    toml_datum_t version = toml_get(profile, "footprint_schema_version");
    toml_datum_t entries = toml_get(profile, "detector");
    mef_detector_definition current, earlier;
    int i, j;

    if (version.type != TOML_INT64 || version.u.int64 != 1 ||
        entries.type != TOML_ARRAY || entries.u.arr.size < 1 || entries.u.arr.size > 4096) {
        return 0;
    }

    for (i = 0; i < entries.u.arr.size; ++i) {
        if (!mef_detector_catalogue_entry(profile, i, &current)) {
            return 0;
        }
        for (j = 0; j < i; ++j) {
            if (!mef_detector_catalogue_entry(profile, j, &earlier) ||
                !strcmp(current.id, earlier.id) || current.slot == earlier.slot) {
                return 0;
            }
        }
    }
    return 1;
}

int mef_detector_catalogue_find(toml_datum_t profile, const char *id,
    mef_detector_definition *out)
{
    toml_datum_t entries = toml_get(profile, "detector");
    int i;

    if (!id || !out || entries.type != TOML_ARRAY) {
        return 0;
    }
    for (i = 0; i < entries.u.arr.size; ++i) {
        if (mef_detector_catalogue_entry(profile, i, out) && !strcmp(id, out->id)) {
            return 1;
        }
    }
    return 0;
}
