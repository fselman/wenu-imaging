#include "mef_operation_template.h"
mef_status mef_operation_run(const mef_operation_steps *steps, void *state,
    mef_error **error)
{
    mef_status status;
    if (steps == NULL || steps->validate == NULL || steps->load == NULL ||
        steps->calculate == NULL || steps->cleanup == NULL || state == NULL ||
        (error != NULL && *error != NULL)) return MEF_ERR_INPUT;
    status = steps->validate(state, error);
    if (status == MEF_OK) status = steps->load(state, error);
    if (status == MEF_OK) status = steps->calculate(state, error);
    if (status == MEF_OK && steps->publish != NULL)
        status = steps->publish(state, error);
    steps->cleanup(state);
    return status;
}
