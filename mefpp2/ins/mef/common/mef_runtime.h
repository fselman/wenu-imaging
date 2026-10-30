/* Internal M1 lifetime boundary; ANSI C90, not an installed/frozen ABI. */
#ifndef MEF_RUNTIME_H
#define MEF_RUNTIME_H
#include "mef_config.h"

typedef struct mef_request mef_request;
typedef struct mef_context mef_context;
typedef struct mef_result mef_result;
typedef struct mef_error mef_error;

typedef enum {
    MEF_OP_CAL_BIAS = 1, MEF_OP_CAL_BPM, MEF_OP_CAL_DARK,
    MEF_OP_CAL_FRINGES, MEF_OP_CAL_LINEARITY, MEF_OP_CAL_DOMEFF,
    MEF_OP_CAL_SKYFF, MEF_OP_CAL_MFF, MEF_OP_SCI_PP
} mef_operation;

typedef struct {
    const char *asset_record_id;
    const char *detector_id;
    const char *resolved_path;
    int hdu_index;
    const char *extname; /* NULL if absent. extver must then be zero. */
    int extver;         /* Positive if extname is present. */
} mef_image_ref;

typedef struct {
    mef_operation operation;
    unsigned int operation_version; /* Initial contract supports version 1. */
    const mef_image_ref *inputs;
    size_t input_count;
    const mef_image_ref *calibrations;
    size_t calibration_count;
    const char *work_dir;
    const char *output_dir;
    const char *log_path;
} mef_request_spec;

/* Role names describe resolved calibration products, never raw file lists. */
typedef enum {
    MEF_CAL_BIAS = 1, MEF_CAL_BPM, MEF_CAL_DARK, MEF_CAL_FRINGES,
    MEF_CAL_LINEARITY, MEF_CAL_DOMEFF, MEF_CAL_SKYFF, MEF_CAL_MFF
} mef_calibration_role;
typedef enum { MEF_BPM_OMITTED = 1, MEF_BPM_SELECTED } mef_bpm_selection_state;
typedef struct {
    const char *detector_id;
    mef_bpm_selection_state state;
} mef_bpm_selection;
typedef struct {
    mef_request_spec request;
    /* One role per request.calibrations entry, in that same order. */
    const mef_calibration_role *calibration_roles;
    size_t calibration_role_count;
    /* Exactly one explicit choice for each distinct input detector. */
    const mef_bpm_selection *bpm_selections;
    size_t bpm_selection_count;
} mef_resolved_request_spec;

/* Structural metadata only: a selected BPM has exactly one matching detector
 * reference of role MEF_CAL_BPM; omission permits none. No file is read, no
 * geometry/applicability is verified and no calibration is reported applied.
 * Zero state is invalid. Selection cannot fall back to a PAF default here.
 * Old mef_request_create remains a legacy/untyped metadata constructor.
 * The resolved builder owns all copied role/selection data; contexts retain it.
 * Variance initialization/propagation remains required later at M6a, not
 * implemented or made optional by this descriptor boundary.
 */
mef_status mef_request_create_resolved(const mef_resolved_request_spec *spec,
    const mef_allocator *allocator, mef_request **out, mef_error **error);
/* NULL for NULL or a legacy/untyped request. Borrowed until destruction. */
const mef_resolved_request_spec *mef_request_resolved_view(const mef_request *request);

/* Builders deep-copy all descriptor arrays and strings. Descriptors are borrowed
 * only for the call. Allocator semantics/lifetime follow mef_config.h.
 * Every output starts NULL; occupied result/error outputs are rejected intact.
 * On failure result stays NULL; optional error is independently owned or NULL
 * if error allocation also failed. Status is always authoritative.
 * Destructors accept NULL. Views are const, borrowed until owner destruction.
 * No FITS/list I/O, file existence checks, cwd/environment changes or scientific
 * applicability checks. Unix paths must already be absolute; M3 resolves them.
 */
mef_status mef_request_create(const mef_request_spec *spec,
    const mef_allocator *allocator, mef_request **out, mef_error **error);
void mef_request_destroy(mef_request *request);
const mef_request_spec *mef_request_view(const mef_request *request);

mef_status mef_context_create(const mef_config *config, const mef_request *request,
    const mef_allocator *allocator, mef_context **out, mef_error **error);
void mef_context_destroy(mef_context *context);
const mef_config *mef_context_config(const mef_context *context);
/* Borrowed allocator; its callbacks/user data retain their original lifetime. */
const mef_allocator *mef_context_allocator(const mef_context *context);
const mef_request *mef_context_request(const mef_context *context);

/* Metadata construction only, not evidence that processing succeeded. No files
 * are created/published. Zero products is valid (NULL refs with count zero).
 */
mef_status mef_result_create(mef_operation operation, const mef_image_ref *products,
    size_t count, const mef_allocator *allocator, mef_result **out, mef_error **error);
void mef_result_destroy(mef_result *result);
mef_operation mef_result_operation(const mef_result *result); /* 0 for NULL */
const mef_image_ref *mef_result_products(const mef_result *result, size_t *count);

mef_status mef_error_create(mef_status status, const char *message,
    const mef_allocator *allocator, mef_error **out);
void mef_error_destroy(mef_error *error);
mef_status mef_error_status(const mef_error *error); /* MEF_OK for NULL */
const char *mef_error_message(const mef_error *error); /* NULL for NULL */

/* This metadata-only dispatcher has no image payload and returns UNSUPPORTED.
 * The opt-in mef_cal_bias service takes its explicit operation-specific image
 * payload through mef_cal_bias.h; no fake metadata-only processing success.
 */
mef_status mef_execute(mef_context *context, mef_result **out, mef_error **error);
#endif
