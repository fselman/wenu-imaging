/* Lossless joining of completed native detector QC; no measurement replay. */
#ifndef MEF_BPM_ASSEMBLY_QC_H
#define MEF_BPM_ASSEMBLY_QC_H
#include "mef_mef_assemble.h"
typedef struct {
    const char *fits_path, *asdf_path, *log_path, *created_at;
    const char *source_revision, *detector_source_revision;
    const char *recipe_path, *recipe_snapshot;
    const mef_bpm_assembly_detector *detectors;
    const char *const *sidecars;
    size_t detector_count;
    /* Explicit rows: detector_id, source_hdu, output_hdu, plane name. */
    const char *plane_map;
} mef_bpm_assembly_qc;
int mef_bpm_assembly_qc_write(const mef_bpm_assembly_qc *, char *, size_t);
#endif
