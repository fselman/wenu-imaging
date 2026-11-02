/* Shared operation skeleton. Typed payloads and algorithms stay in adapters.
 * Recipe scaffold/lessons: docs/developer/native-operation-recipe-template.md.
 * Bias is the qualified first example, not a blanket scientific/QC contract. */
#ifndef MEF_OPERATION_TEMPLATE_H
#define MEF_OPERATION_TEMPLATE_H
#include "mef_runtime.h"
typedef mef_status (*mef_operation_step)(void *, mef_error **);
typedef struct {
    /* Validate explicit config/request, per-file logical-detector/HDU/config
     * mapping, readout/units/geometry, selected dependencies and declared output
     * coverage before pixels are loaded. No filesystem discovery or invented
     * detector IDs, default masks, missing metadata or persistence policy. */
    mef_operation_step validate;
    /* Borrow immutable inputs; preserve original frame indices and per-file
     * maps. Memory accounting includes loaded planes AND private working copies. */
    mef_operation_step load;
    /* Produce a pending owned typed result and existing diagnostics. Retain
     * configured parameters, measured quantities, algorithm rejection and
     * scientific QC/exclusion decisions as distinct data. No publication here. */
    mef_operation_step calculate;
    /* NULL for requested in-memory completion. Otherwise prepare headers from
     * the pending result and explicit output coverage, then commit checked
     * output exclusively. Input HDU != config slot != output ordinal (#210).
     * Do not index/merge a qfits header after deletion: its n can be stale
     * (#211/#212). Reuse a qualified header adapter or a reviewed shared
     * extraction; structural conversion uses fresh construction/copies.
     * A processing-diagnostics record does not select JSON, ASDF or scientific
     * QC policy. Product/result persistence must follow its reviewed contract. */
    mef_operation_step publish;
    /* Release temporary owners after any attempted phase, without destroying
     * borrowed inputs or a pending result awaiting typed transfer/destruction. */
    void (*cleanup)(void *);
} mef_operation_steps;
/* No default discovery/retry or filesystem behavior. Stops at first failure;
 * status remains authoritative without an allocated diagnostic. The adapter
 * transfers its owned result only after this routine returns MEF_OK. Serial;
 * this orchestration adds no reentrancy claim for legacy numerical helpers.
 * The skeleton prescribes lifecycle only: the adapter remains responsible for
 * metadata authority, actual result completeness and publication transaction
 * scope. Tests must compare corresponding detector coverage, not require a
 * selected detector's primary parameters to equal a whole-mosaic primary. */
mef_status mef_operation_run(const mef_operation_steps *, void *, mef_error **);
#endif
