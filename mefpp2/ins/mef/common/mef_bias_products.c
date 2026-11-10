#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include "mef_bias.h"
#include "mef_bias_qc_fits.h"
#include <errno.h>
#include <limits.h>
#include <unistd.h>
#undef malloc
#undef calloc
#undef realloc
#undef free

int mef_bias_begin(mef_bias *recipe)
{
    recipe->archive = mef_bias_product_qc_new(recipe->config, &recipe->run->paths,
        recipe->run->recipe_start, MEFPP_CANDIDATE_REVISION, (const char *const *)recipe->raw_paths,
        recipe->frame_count, recipe->arguments.detector_count);
    if (recipe->archive == NULL) {
        return 0;
    }
    return mef_recipe_run_begin(recipe->run, recipe->config_path, recipe->listing_path,
        (const char *const *)recipe->raw_paths, recipe->frame_count);
}

int mef_bias_verify(mef_bias *recipe)
{
    if (mef_bias_product_qc_check(
            recipe->archive, recipe->run->message, sizeof(recipe->run->message))) {
        return 0;
    }
    return 1;
}

int mef_bias_publish_products(mef_bias *recipe)
{
    size_t i;
    fprintf(recipe->run->log, "MEF_ASSEMBLY_START\n");
    if (fflush(recipe->run->log)) {
        return 0;
    }
    printf("BIAS_MEF_ASSEMBLY %s\n", recipe->run->paths.fits);
    fflush(stdout);
    if (mef_mef_assemble(recipe->run->paths.fits, recipe->arguments.reference_detector_id,
            recipe->assembly, recipe->arguments.detector_count, recipe->run->message,
            sizeof(recipe->run->message))) {
        return 0;
    }
    fprintf(recipe->run->log, "NATIVE_ASDF_START\n");
    if (fflush(recipe->run->log)) {
        return 0;
    }
    printf("BIAS_NATIVE_ASDF %s\n", recipe->run->paths.asdf);
    fflush(stdout);
    if (recipe->recipe_document) {
        size_t primary_count, detector_count;
        const char *const *primary_keys =
            mef_bias_primary_keys(recipe->recipe_document, &primary_count);
        const char *const *detector_keys =
            mef_bias_detector_keys(recipe->recipe_document, &detector_count);
        if (mef_bias_product_qc_headers(recipe->archive, primary_keys, primary_count, detector_keys,
                detector_count, mef_bias_path(recipe->recipe_document),
                mef_bias_source(recipe->recipe_document), recipe->run->message,
                sizeof(recipe->run->message))) {
            return 0;
        }
    }
    if (mef_bias_product_qc_write(
            recipe->archive, recipe->run->message, sizeof(recipe->run->message))) {
        return 0;
    }
    set_logfile(0);
    for (i = 0; i < recipe->arguments.detector_count; ++i) {
        mef_recipe_run_discard_temporary(
            recipe->run, recipe->arguments.detectors[i].temporary_path);
    }
    return 1;
}
