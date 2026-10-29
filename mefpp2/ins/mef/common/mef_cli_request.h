/* Internal C90 compatibility bridge, not the resolved single-operation ABI. */
#ifndef MEF_CLI_REQUEST_H
#define MEF_CLI_REQUEST_H
#include "mef_runtime.h"

typedef struct mef_cli_request mef_cli_request;
typedef struct {
    const char *base_dir; /* Explicit absolute base; bindings remain verbatim. */
    int argc;
    const char *const *argv; /* Original order, before getopt permutation. */
    const char *paf_path;
    const char *bias_path;
    const char *bpm_path;
    const char *dome_path;
    const char *sky_path;
    const char *mff_path;
    const char *mff_output;
    const char *science_path;
    const char *split_path;
    int noverify;
    int xtnum;
    int bias_subtract;
    int bias_save;
    int dome_save;
    int sky_save;
    int sat_check;
    int median_surface;
} mef_cli_view;

/* Source is the existing successful loader's object, before engine mutation.
 * It may describe several operations. No reparsing, path normalization, list
 * expansion, FITS inspection, file discovery or cwd/environment changes occur.
 * Relative/null/empty bindings and raw flags are copied exactly. base_dir must
 * be explicit and absolute. Caller supplies original argv, not getopt's permuted
 * pointer array; correspondence of argv/source is the adapter caller's contract.
 * All data needed after construction is copied, including effective config.
 * Output starts NULL; occupied request/error outputs are rejected unchanged.
 * Returned status is authoritative if optional error allocation also fails.
 * Allocator callbacks/user data must outlive request and any returned error.
 */
mef_status mef_cli_request_from_legacy(const struct _mef_bb_ *source,
    const char *base_dir, int argc, const char *const *argv,
    const mef_allocator *allocator, mef_cli_request **out, mef_error **error);
void mef_cli_request_destroy(mef_cli_request *request);
const mef_cli_view *mef_cli_request_view(const mef_cli_request *request);
const mef_config *mef_cli_request_config(const mef_cli_request *request);
/* Deterministic inspection JSON, not project persistence. Caller owns stream;
 * inspect final fflush/fclose for buffered write errors. Config has its own dump.
 * Accessor views are borrowed until request destruction; never free/mutate them.
 */
mef_status mef_cli_request_dump(const mef_cli_request *request, FILE *stream);
#endif
