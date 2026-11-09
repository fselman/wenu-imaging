#ifndef MEF_BPM_PUBLISH_H
#define MEF_BPM_PUBLISH_H
#include "mef_bpm_files.h"
typedef enum { MEF_BPM_PUBLISH_NEW=1, MEF_BPM_PUBLISH_COMBINED } mef_bpm_publish_mode;
typedef struct {
    mef_bpm_publish_mode mode; /* Explicit; combined needs known prior bits. */
    const char *created_at; /* Explicit UTC YYYY-MM-DDTHH:MM:SSZ; also ASDF. */
    const char *source_revision;
} mef_bpm_publish_options;
/* One checked, exclusive multi-HDU product: primary unsigned-byte reasons;
 * COVERAGE byte fit state (0 missing/1 fitted/2 legacy fallback), NSAMPLE signed
 * 16-bit count, NEWFLAGS byte reasons, SELECTION byte usable selection; optional
 * PRIORFLAGS or PRIORSEL retains original prior semantics. Active coordinates.
 * Fresh headers, full HIERARCH names, bounded string cards; not ESO Phase3.
 * Existing files/symlinks/directories never overwritten. Atomic final hard link
 * after every write/flush/fsync/close succeeds; no half-written final path.
 * Combined mode with legacy binary prior fails rather than inventing reasons.
 */
mef_status mef_bpm_publish(const mef_bpm_files_result *, const char *,
    const mef_bpm_publish_options *, mef_error **);
/* Native values -> versioned internal transport, NOT the saved QC format.
 * Caller creates a fresh handoff stream after publish success. Retained Python
 * completion consumes this transport; the native product-QC adapter embeds the
 * same versioned context and uses the shared C ASDF writer directly. */
mef_status mef_bpm_write_handoff(FILE *, const mef_bpm_files_result *,
    const char *, const mef_bpm_publish_options *, mef_error **);
#endif
