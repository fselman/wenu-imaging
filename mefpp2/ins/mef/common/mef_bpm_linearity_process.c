#include "mef_bpm_linearity.h"
#include <stdio.h>

int mef_bpm_linearity_process(mef_bpm_linearity *recipe, size_t index)
{
    mef_bpm_linearity_detector *detector=recipe->detectors+index;
    recipe->diagnostic="Native detector preparation or BPM characterization failed";
    if (!mef_bpm_linearity_observe(recipe)) return 0;
    fprintf(recipe->run->log,"DETECTOR_START %lu %s CONFIGURATION %lu\n",
        (unsigned long)index,detector->detector_id,(unsigned long)detector->configuration_detector);
    if (fflush(recipe->run->log)) return 0;
    printf("BPM_LINEARITY_DETECTOR %lu/%lu %s\n",(unsigned long)index+1,
        (unsigned long)recipe->detector_count,detector->detector_id);
    fflush(stdout);

    /* [BPM-LINEARITY-MEASUREMENTS]
     * Existing native preparation preserves scan -> bias -> trim -> ROI order.
     * This function returns after releasing its pair's images and metadata owner.
     */

    if (mef_linearity_prepare_command(detector->preparation_argc,detector->preparation_argv) ||
        !mef_bpm_linearity_observe(recipe)) return 0;

    /* [BPM-LINEARITY-CANDIDATE]
     * The same admitted master/prior are bound again by the BPM service.
     * Candidate publication does not modify either calibration dependency.
     */

    if (mef_bpm_command(detector->bpm_argc,detector->bpm_argv) ||
        !mef_bpm_linearity_observe(recipe)) return 0;
    fprintf(recipe->run->log,"DETECTOR_DONE %s\n",detector->detector_id);
    return fflush(recipe->run->log)==0;
}
