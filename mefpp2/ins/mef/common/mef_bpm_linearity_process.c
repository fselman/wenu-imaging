#include "mef_bpm_linearity.h"
#include "mef_detector_cube.h"
#include <stdio.h>

int mef_bpm_linearity_process(mef_bpm_linearity *recipe,size_t index)
{
    mef_bpm_linearity_detector *detector=recipe->detectors+index;
    mef_detector_cube cube;
    int okay=0;
    recipe->diagnostic="Detector cube ingestion, BPM creation or linearity measurement failed";
    if(!mef_bpm_linearity_observe(recipe)) return 0;
    fprintf(recipe->run->log,"DETECTOR_START %lu %s CONFIGURATION %lu QC %s\n",
        (unsigned long)index,detector->detector_id,(unsigned long)detector->configuration_detector,
        recipe->qc?"true":"false");
    printf("BPM_LINEARITY_DETECTOR %lu/%lu %s\n",(unsigned long)index+1,
        (unsigned long)recipe->detector_count,detector->detector_id);
    fflush(stdout);

    /* [BPM-LINEARITY-INGESTION] One owner; scientific consumers borrow its planes. */

    if(!mef_detector_cube_ingest(&cube,detector->preparation_argc,detector->preparation_argv,recipe->qc)) return 0;
    detector->image_loads=cube.image_loads;detector->corrections=cube.corrections;
    fprintf(recipe->run->log,"CUBE_READY %s IMAGE_LOADS %lu CORRECTIONS %lu FLATS %lu\n",
        detector->detector_id,(unsigned long)cube.image_loads,(unsigned long)cube.corrections,
        (unsigned long)cube.flat_count);

    /* [BPM-LINEARITY-CANDIDATE] A supplied mask bypasses candidate creation. */

    detector->bpm_skipped=cube.binary!=NULL || cube.flags!=NULL;
    if(detector->bpm_skipped) {
        fprintf(recipe->run->log,"BPM_CREATION_SKIPPED %s REASON input_bpm_supplied\n",detector->detector_id);
    } else if(mef_bpm_command_from_cube(detector->bpm_argc,detector->bpm_argv,&cube)) goto done;
    if(!mef_bpm_linearity_observe(recipe)) goto done;

    /* [BPM-LINEARITY-MEASUREMENTS] Reuse corrected planes; never repeat correction. */

    if(mef_linearity_prepare_from_cube(detector->preparation_argc,detector->preparation_argv,&cube) ||
       !mef_bpm_linearity_observe(recipe)) goto done;
    fprintf(recipe->run->log,"DETECTOR_DONE %s\n",detector->detector_id);
    okay=fflush(recipe->run->log)==0;
done:
    mef_detector_cube_destroy(&cube);
    return okay;
}
