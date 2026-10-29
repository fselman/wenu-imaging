/* Transitional file/list adapter; internal ANSI C90 interface, not installed. */
#ifndef MEF_INPUT_REQUEST_H
#define MEF_INPUT_REQUEST_H
#include "mef_runtime.h"

typedef enum { MEF_INPUT_FILE = 1, MEF_INPUT_LEGACY_LIST } mef_input_kind;
typedef struct {
    mef_resolved_request_spec request;
    mef_input_kind kind;
    const char *input_path; /* Absolute file/list path, no format guessing. */
    const char *member_base; /* Absolute original execution base for a list. */
    /* Explicit preselected image descriptors, ordered within each file.
     * IDs/HDU selectors come from the caller's inventory, never filenames.
     */
    const mef_image_ref *catalogue;
    size_t catalogue_count;
} mef_input_request_spec;

/* request.request.inputs must be NULL/count 0: the adapter fills this array.
 * Reuses Eclipse charmatrix_read (the existing framelist parser), retaining
 * first-column tokens, order and duplicates. Legacy quoting/space limitations
 * remain. Relative members use member_base, not cwd or the list directory.
 * Matching is lexical absolute-path equality; no realpath/symlink rewrite.
 * Reads list text and opens referenced regular files/calibrations for checking
 * readability only. No FITS headers/pixels, scientific applicability, automatic
 * BPM discovery or output file creation. The supplied catalogue must already
 * contain the intended detector/HDU selection. Primary HDU 0 stays explicit.
 * Input files/catalogue must remain stable for the call (no snapshot lock).
 * Descriptors are borrowed only during the call; returned request owns copies.
 * Per-object allocator covers adapter/request owners, not legacy parser memory.
 * Eclipse parser/allocator globals are unchanged; thread safety is not claimed.
 */
mef_status mef_request_from_input(const mef_input_request_spec *spec,
    const mef_allocator *allocator, mef_request **out, mef_error **error);
#endif
