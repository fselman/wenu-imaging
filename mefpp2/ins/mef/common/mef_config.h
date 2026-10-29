/* Internal M1 API; not an installed or stable public ABI. ANSI C90. */
#ifndef MEF_CONFIG_H
#define MEF_CONFIG_H

#include <stddef.h>
#include <stdio.h>

typedef enum {
    MEF_OK = 0, MEF_ERR_CONFIG = 1, MEF_ERR_INPUT = 2,
    MEF_ERR_UNSUPPORTED = 3, MEF_ERR_MEMORY = 4,
    MEF_ERR_COMPUTATION = 5, MEF_ERR_IO = 6, MEF_ERR_CANCELLED = 7
} mef_status;

typedef struct {
    void *user;
    void *(*allocate)(void *user, size_t bytes);
    void (*release)(void *user, void *pointer);
} mef_allocator;

typedef struct mef_config mef_config;
struct _mef_bb_;

/* Deep copy only constructor-mapped settings. Source is borrowed for this call.
 * *out must be NULL; occupied outputs are never overwritten. A NULL allocator
 * selects malloc/free; otherwise callbacks must provide malloc-compatible
 * alignment/fresh storage and matching release. Both are required and user must
 * outlive the snapshot. release is called only with non-NULL pointers.
 * diagnostic is optional, borrowed static text, independent of object lifetime.
 * No engine execution, ownership transfer, scientific validation or PAF I/O.
 */
mef_status mef_config_from_legacy(const struct _mef_bb_ *source,
    const mef_allocator *allocator, mef_config **out, const char **diagnostic);
/* Independently owned copy, preserving the same stored types and bits. */
mef_status mef_config_clone(const mef_config *source, const mef_allocator *allocator,
    mef_config **out, const char **diagnostic);
void mef_config_destroy(mef_config *config);

/* Deterministic JSON: integers and strings, floating object bits in big-endian
 * hex with explicit type. Requires IEEE binary32/binary64, as in native builds.
 * Caller owns stream; no flush/close. Check fclose as well for buffered errors.
 * Snapshot is read-only; use separate streams for concurrent inspection.
 */
mef_status mef_config_dump(const mef_config *config, FILE *stream);

#endif
