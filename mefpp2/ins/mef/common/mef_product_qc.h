/* Native product QC metadata: borrowed typed values, no image processing.
 * Shared product container v2 embeds inputs instead of external QC sidecars.
 * File standard ASDF1.6 and application schema2.0.0 are different versions. */
#ifndef MEF_PRODUCT_QC_H
#define MEF_PRODUCT_QC_H
#include <stddef.h>
#include <stdint.h>
#define MEF_PRODUCT_QC_SCHEMA "2.0.0"
typedef enum { MEF_QC_MEASURED = 1, MEF_QC_UNAVAILABLE, MEF_QC_INVALID } mef_qc_state;
typedef struct {
    const char *name, *unit, *stage, *method, *reason;
    mef_qc_state state;
    /* Scalar: value_count=1 and vector=0. Profiles: vector=1, explicit values.
     * Unavailable/invalid values have no data; they are serialized as null. */
    const double *values;
    size_t value_count;
    int vector;
    uint64_t sample_count;
    const char *coordinates;
    const char *mask_policy, *mask_id; /* omitted/applied/not_applicable/unmasked_diagnostic. */
    const char *clipping, *nonfinite_policy;
    int bounds[4]; /* FITS 1-based inclusive rectangle, or zeros if inapplicable. */
    const char *const *source_ids;
    size_t source_count;
} mef_qc_measurement;
typedef struct {
    const char *id, *path, *sha256; /* sha256 NULL means explicitly unverified. */
    uint64_t original_index;
} mef_qc_input_record;
typedef struct {
    const char *input_id;
    int source_hdu, accepted;
    const char *rejection_reason;
    const mef_qc_measurement *measurements;
    size_t measurement_count;
} mef_qc_input_binding;
typedef struct {
    const char *id, *amplifier, *readout_id;
    size_t configuration_detector;
    int output_hdu, bin_x, bin_y;
    const mef_qc_measurement *measurements;
    size_t measurement_count;
    /* One binding per global input, in the same original list order. */
    const mef_qc_input_binding *inputs;
    size_t input_count;
} mef_qc_detector_record;
typedef struct {
    const char *detector_id;
    int source_hdu;
} mef_qc_calibration_binding;
typedef struct {
    const char *id, *path, *sha256, *role, *qc_path;
    const mef_qc_calibration_binding *bindings;
    size_t binding_count;
} mef_qc_calibration_record;
typedef struct {
    const char *id, *fits_path, *sha256, *log_path;
    const char *assessment_id, *recipe_name, *recipe_start;
    unsigned int recipe_version;
    unsigned long product_sequence;
    const char *producer_name, *producer_version, *source_revision;
    const char *configuration_id;
    /* Exact existing mef_config_dump output; no second native settings parser.
     * This is embedded text in ASDF, not a separate JSON handoff file. */
    const char *configuration_snapshot;
    const mef_qc_input_record *inputs;
    size_t input_count;
    const mef_qc_calibration_record *calibrations;
    size_t calibration_count;
    const mef_qc_detector_record *detectors;
    size_t detector_count;
} mef_product_qc;
/* Structural validation only. No thresholds, means, RON, plots, hashes or FITS
 * pixels are computed. Caller owns all borrowed values during the call. */
int mef_product_qc_validate(const mef_product_qc *, char *, size_t);
/* Requires the final FITS to exist; no FITS/RAW pixel reading or Pycavi calls.
 * ASDF destination must replace final .fits by .asdf in the same directory.
 * Creates/reads back a private ASDF then publishes exclusively; no overwrite.
 * Caller reports whole-recipe success only after FITS, ASDF and log completion.
 * A prior complete FITS stays intact if ASDF publication fails. */
int mef_product_qc_write(const char *, const mef_product_qc *, char *, size_t);
/* Explicit recovery after caller-established reference/QC/pixel equivalence.
 * Native writes a new staging file only; independent full-tree/schema/FITS
 * verification must succeed before caller exclusively publishes final ASDF.
 * Reference values/definitions/arrays/input records are retained unchanged.
 * Original provenance is copied into root recovery metadata; failed recipe
 * status remains explicit. Does not read FITS pixels, raw data or run recipes. */
typedef struct {
    const char *reference_asdf, *fits_path, *staging_path;
    const char *failed_log, *assembly_log, *created_at, *recipe_start, *source_revision;
} mef_qc_recovery;
int mef_product_qc_recover_verified(const mef_qc_recovery *, char *, size_t);
#endif
