/* Internal serial M5 adapter; C90 source, not an installed or frozen ABI. */
#ifndef MEF_BIAS_FILES_H
#define MEF_BIAS_FILES_H
#include "mef_cal_bias.h"
#include "mef_layout.h"
struct _mef_bb_;

/* Header-only compatibility bridge. Owns its strings and one selected detector;
 * all statistics/input references are filled separately. Destroy with mef_bb_del.
 * Configuration index is zero-based, independent of source/output HDU. */
mef_status mef_config_bias_header_context(const mef_config *, size_t,
    struct _mef_bb_ **);

/* Exactly one selected logical detector, independently mapped in each file.
 * Reuses M4 loading, then the existing mef_cal_bias operation. No discovery,
 * cwd changes, output writes, BPM fallback or unit conversion. Request paths
 * and original order must match maps. Input maps/context are borrowed; result
 * owns signal, QC and copied request. Full raw planes and the kernel's private
 * copies coexist: this first adapter does not claim streaming/low memory. */
mef_status mef_bias_from_files(mef_context *, const mef_layout_map *const *,
    size_t, const char *, mef_bias_result **, mef_error **);

/* Same operation template including publication; result transfers only after
 * successful publication. A failure destroys the pending result. */
mef_status mef_bias_files_execute(mef_context *, const mef_layout_map *const *,
    size_t, const char *, const char *, mef_bias_result **, mef_error **);

/* Publish a one-extension MEF from an existing owned result. Reuses legacy
 * header policy/QC formatting and checked qfits pixel output, with explicit
 * input HDU, configuration detector and output ordinal. One creation identity
 * per attempt, legacy naming policy retained; final_path is an explicit path,
 * not the future configurable filename grammar. Inputs/result remain borrowed.
 * Assembly is an output temporary in the final directory, committed with an
 * exclusive hard link; existing files/symlinks/directories are never replaced.
 * No success until all FITS writes/close succeed and final publication commits.
 * Non-reentrant legacy qfits/Eclipse globals remain. Caller holds inputs stable.
 */
mef_status mef_bias_publish(const mef_config *, const mef_bias_result *, size_t,
    const char *, mef_error **);
#endif
