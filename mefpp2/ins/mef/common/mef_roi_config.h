/* Explicit characterization ROI supplement; not an installed/stable ABI. */
#ifndef MEF_ROI_CONFIG_H
#define MEF_ROI_CONFIG_H
#include "mef_config.h"
#include "detector_roi.h"
typedef struct mef_roi_config mef_roi_config;
/* Formats: "paf" or "toml". No includes, overrides, defaults or implicit file.
 * TOML uses the existing parser and requires its serial initialization first.
 * Snapshot owns exact source bytes and named entries. Allocator covers these
 * owners, not the dependency parser. Limits: 1 MiB text, 4096 named regions.
 * IDs: 1..63 ASCII letters/digits/._:-# (quoted values). Globally unique ROI IDs.
 * *out must be NULL; failures leave it untouched. Diagnostic is optional. */
mef_status mef_roi_config_read(const char *path, const char *format,
    const mef_allocator *allocator, mef_roi_config **out,
    char *diagnostic, size_t capacity);
void mef_roi_config_destroy(mef_roi_config *config);
size_t mef_roi_config_count(const mef_roi_config *config);
const char *mef_roi_config_source(const mef_roi_config *config);
/* Resolve BOTH detector_id and amplifier_id, independent of HDU/order. Bounds
 * are inclusive FITS 1-based ACTIVE amplifier-local coordinates, checked against
 * supplied active dimensions. An ROI never crosses an amplifier. Overlap is
 * permitted. Every entry must bind exactly once; duplicate input identities,
 * unknown IDs, bad dimensions/capacity fail atomically. Caller owns output;
 * no pixel reads or estimator changes. Bind again for a reordered amplifier
 * list; the returned numerical indices belong only to that specific list. */
mef_status mef_roi_config_bind(const mef_roi_config *config, int amplifiers,
    const detector_joint_amplifier *identity, const int (*dimensions)[2],
    detector_roi *output, size_t capacity, size_t *count,
    char *diagnostic, size_t diagnostic_capacity);
#endif
