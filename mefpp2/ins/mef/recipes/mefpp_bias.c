/* Master-bias coordinator. Read these phases in execution order.
 * Supporting modules expose the mechanics; the typed services own the science.
 */

#include "mef_bias.h"

int main(int argc, char **argv)
{
    mef_recipe_run run;
    mef_bias recipe;
    size_t detector_index;
    int succeeded = 0;

    mef_recipe_run_initialize(&run, "cal.bias", "BIAS", "bias", "Bias", MEFPP_CANDIDATE_REVISION);
    mef_bias_initialize(&recipe, &run);

    /* [BIAS-RECIPE-ADMISSION]
     * Sample the start once. Admit configuration and every detector binding
     * before opening the log, private workspace or detector products.
     */

    if (!mef_recipe_run_start(&run) || !mef_bias_prepare(&recipe, argc, argv) ||
        !mef_bias_admit(&recipe) || !mef_bias_begin(&recipe)) {
        goto finish;
    }

    /* [BIAS-DETECTOR-LOOP]
     * Each detector has its own corrections, frame membership and private MEF.
     */

    for (detector_index = 0; detector_index < recipe.arguments.detector_count; ++detector_index) {
        if (!mef_bias_process(&recipe, detector_index)) {
            goto finish;
        }
    }

    /* [BIAS-PRODUCT-PUBLICATION]
     * Verify complete detector coverage before assembly and ASDF publication.
     * Bias adds no cross-detector normalization or balancing.
     */

    if (!mef_bias_verify(&recipe) || !mef_bias_publish_products(&recipe) ||
        !mef_recipe_run_complete(&run)) {
        goto finish;
    }
    succeeded = 1;

finish:

    /* Report while diagnostics are alive, then release in-memory owners.
     * Failed file products and private work remain available as evidence.
     */

    if (recipe.show_usage) {
        mef_bias_usage();
    }
    mef_recipe_run_finish(&run, succeeded, recipe.error, recipe.diagnostic);
    mef_bias_destroy(&recipe);
    return succeeded ? EXIT_SUCCESS : EXIT_FAILURE;
}
