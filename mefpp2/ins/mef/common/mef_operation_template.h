/* Shared operation skeleton. Typed payloads and algorithms stay in adapters. */
#ifndef MEF_OPERATION_TEMPLATE_H
#define MEF_OPERATION_TEMPLATE_H
#include "mef_runtime.h"
typedef mef_status (*mef_operation_step)(void *, mef_error **);
typedef struct {
    mef_operation_step validate;
    mef_operation_step load;
    mef_operation_step calculate;
    mef_operation_step publish; /* NULL for a requested in-memory result. */
    void (*cleanup)(void *);    /* Safe after any partial step, always called. */
} mef_operation_steps;
/* No default discovery/retry or filesystem behavior. Stops at first failure;
 * status remains authoritative without an allocated diagnostic. The adapter
 * transfers its owned result only after this routine returns MEF_OK. Serial;
 * this orchestration adds no reentrancy claim for legacy numerical helpers. */
mef_status mef_operation_run(const mef_operation_steps *, void *, mef_error **);
#endif
