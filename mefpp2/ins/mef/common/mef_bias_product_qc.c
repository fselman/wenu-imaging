/* Own the measured bias product/input records and their provenance references.
 * Copy service results into one QC archive for native ASDF serialization and
 * FITS mapping. This layer does not correct pixels or choose frame membership.
 */

#define _POSIX_C_SOURCE 200809L
#include "mef_bias_product_qc.h"
#include "mef_product_qc.h"
#include "mef_processing.h"
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>
#include <math.h>
#include "qfits.h"
#include <string.h>

/* Eclipse's public image headers expose allocator macros. These metadata owners
 * use libc; numerical image owners still use their library destructors. */

#undef malloc
#undef calloc
#undef realloc
#undef free

#define QC_CAPACITY 64

typedef struct {
    mef_qc_measurement *measurement;
    double *values;
    char (*names)[80];
    const char *source[1];
    size_t count;
} qc_measurement_storage;

typedef struct {
    qc_measurement_storage product, *inputs;
    const char *pair[2];
    double *hot_x, *hot_y;
} detector_storage;

struct mef_bias_product_qc {
    mef_product_qc product;
    mef_processing_policy processing;
    const mef_product_paths *paths;
    char *snapshot;
    mef_qc_input_record *inputs;
    char (*input_ids)[40], (*calibration_ids)[40];
    mef_qc_detector_record *detectors;
    mef_qc_calibration_record *calibrations;
    detector_storage *storage;
    mef_qc_fits_card *header_cards;
};

static int allocate_measurements(qc_measurement_storage *storage, const char *source)
{
    storage->measurement = calloc(QC_CAPACITY, sizeof(*storage->measurement));
    storage->values = calloc(QC_CAPACITY, sizeof(*storage->values));
    storage->names = calloc(QC_CAPACITY, sizeof(*storage->names));
    storage->source[0] = source;
    return storage->measurement != NULL && storage->values != NULL && storage->names != NULL;
}

static void release_measurements(qc_measurement_storage *storage)
{
    free(storage->measurement);
    free(storage->values);
    free(storage->names);
}

static mef_qc_measurement *append_scalar_measurement(qc_measurement_storage *storage,
    const char *name, double value, const char *unit, const char *stage, const char *method,
    int available, const char *reason, size_t samples, const int *bounds, const char *mask,
    const char *mask_id, const char *const *sources, size_t source_count)
{
    size_t i = storage->count;
    mef_qc_measurement *measurement;
    if (i == QC_CAPACITY || strlen(name) >= sizeof(storage->names[i])) {
        return NULL;
    }
    strcpy(storage->names[i], name);
    storage->values[i] = value;
    measurement = storage->measurement + i;
    measurement->name = storage->names[i];
    measurement->unit = unit;
    measurement->stage = stage;
    measurement->method = method;
    measurement->state = available ? MEF_QC_MEASURED : MEF_QC_UNAVAILABLE;
    measurement->reason = available ? NULL : reason;
    measurement->values = available ? storage->values + i : NULL;
    measurement->value_count = available ? 1 : 0;
    measurement->sample_count = samples;
    measurement->coordinates = "FITS-1-based-inclusive";
    measurement->mask_policy = mask;
    measurement->mask_id = mask_id;
    measurement->clipping = "none";
    measurement->nonfinite_policy = "excluded";
    if (bounds != NULL) {
        memcpy(measurement->bounds, bounds, sizeof(measurement->bounds));
    }
    measurement->source_ids = sources ? sources : storage->source;
    measurement->source_count = sources ? source_count : 1;
    ++storage->count;
    return measurement;
}

static int append_sample_statistics(qc_measurement_storage *storage, const char *name,
    const char *stage, const image_sample_stats *sample_statistics, int scan, const char *mask_id,
    const char *const *sources, size_t source_count)
{
    static const char *suffix[] = {"mean", "median", "stdev", "scaled_mad", "region_pixels",
        "bpm_excluded", "nonfinite_excluded", "valid_pixels"};
    static const char *method[] = {"arithmetic_mean", "median_averaged_central_pair",
        "sample_standard_deviation_n_minus_1", "1.4826_times_median_absolute_deviation"};
    double values[8];
    int available[8];
    size_t i;
    char key[80];
    const char *mask = scan                              ? "not_applicable"
                       : sample_statistics->bpm_supplied ? "applied"
                       : mask_id                         ? "unmasked_diagnostic"
                                                         : "omitted";
    const char *record = !scan && sample_statistics->bpm_supplied ? mask_id : NULL;
    values[0] = sample_statistics->mean;
    values[1] = sample_statistics->median;
    values[2] = sample_statistics->stdev;
    values[3] = 1.4826 * sample_statistics->mad;
    values[4] = (double)sample_statistics->region_pixels;
    values[5] = (double)sample_statistics->bpm_excluded;
    values[6] = (double)sample_statistics->nonfinite_excluded;
    values[7] = (double)sample_statistics->valid_pixels;
    available[0] = available[1] = sample_statistics->level_available;
    available[2] = sample_statistics->stdev_available;
    available[3] = sample_statistics->mad_available;
    for (i = 4; i < 8; ++i) {
        available[i] = sample_statistics->region_pixels != 0;
    }
    for (i = 0; i < 8; ++i) {
        snprintf(key, sizeof(key), "%s.%s", name, suffix[i]);
        if (append_scalar_measurement(storage, key, values[i], i < 4 ? "ADU" : "count", stage,
                i < 4 ? method[i] : "explicit_sample_partition", available[i],
                i < 4 ? "not_requested_or_insufficient_samples" : "region_not_configured",
                i < 4 ? sample_statistics->valid_pixels : sample_statistics->region_pixels,
                sample_statistics->zone, mask, record, sources, source_count) == NULL) {
            return 0;
        }
    }
    return 1;
}

mef_bias_product_qc *mef_bias_product_qc_new(const mef_config *config,
    const mef_product_paths *paths, const char *start, const char *revision,
    const char *const *inputs, size_t count, size_t detectors)
{
    mef_bias_product_qc *archive;
    FILE *stream;
    size_t length = 0, i;
    int okay;
    if (config == NULL || paths == NULL || start == NULL || revision == NULL || inputs == NULL ||
        count == 0 || count > 100000 || detectors == 0 || detectors > 4096) {
        return NULL;
    }
    archive = calloc(1, sizeof(*archive));
    if (archive == NULL) {
        return NULL;
    }
    archive->processing = *mef_config_processing(config);
    if (archive->processing.bpm.supplied && archive->processing.bpm.encoding == MEF_BPM_REASON8) {
        archive->product.bpm_registry = archive->processing.bpm.registry;
    }
    archive->product.input_count = count;
    archive->product.detector_count = detectors;
    archive->paths = paths;
    archive->inputs = calloc(count, sizeof(*archive->inputs));
    archive->input_ids = calloc(count, sizeof(*archive->input_ids));
    archive->detectors = calloc(detectors, sizeof(*archive->detectors));
    archive->storage = calloc(detectors, sizeof(*archive->storage));
    archive->calibrations = calloc(detectors, sizeof(*archive->calibrations));
    archive->calibration_ids = calloc(detectors, sizeof(*archive->calibration_ids));
    if (!archive->inputs || !archive->input_ids || !archive->detectors || !archive->storage ||
        !archive->calibrations || !archive->calibration_ids) {
        goto failed;
    }
    stream = open_memstream(&archive->snapshot, &length);
    if (stream == NULL) {
        goto failed;
    }
    okay = mef_config_dump(config, stream) == MEF_OK;
    if (fclose(stream) != 0 || !okay) {
        goto failed;
    }
    for (i = 0; i < count; ++i) {
        snprintf(
            archive->input_ids[i], sizeof(archive->input_ids[i]), "raw-%06lu", (unsigned long)i);
        archive->inputs[i].id = archive->input_ids[i];
        archive->inputs[i].path = inputs[i];
        archive->inputs[i].original_index = i;
    }
    archive->product.id = paths->fits;
    archive->product.fits_path = paths->fits;
    archive->product.log_path = paths->log;
    archive->product.assessment_id = paths->fits;
    archive->product.recipe_name = "cal.bias";
    archive->product.recipe_start = start;
    archive->product.recipe_version = 1;
    archive->product.product_sequence = 1;
    archive->product.producer_name = "mefpp_bias_recipe";
    archive->product.producer_version = "1";
    archive->product.source_revision = revision;
    archive->product.configuration_id = "effective-native-settings";
    archive->product.configuration_snapshot = archive->snapshot;
    archive->product.inputs = archive->inputs;
    archive->product.detectors = archive->detectors;
    archive->product.calibrations = archive->calibrations;
    return archive;
failed:
    mef_bias_product_qc_destroy(archive);
    return NULL;
}

static const char *register_calibration(
    mef_bias_product_qc *archive, const char *path, const char *id, int hdu)
{
    size_t i, n = archive->product.calibration_count;
    mef_qc_calibration_binding *bindings;
    for (i = 0; i < n; ++i) {
        if (!strcmp(path, archive->calibrations[i].path)) {
            break;
        }
    }
    if (i == n) {
        snprintf(archive->calibration_ids[i], sizeof(archive->calibration_ids[i]), "bpm-%06lu",
            (unsigned long)i);
        archive->calibrations[i].id = archive->calibration_ids[i];
        archive->calibrations[i].path = path;
        archive->calibrations[i].role = "bpm";
        archive->calibrations[i].bindings =
            calloc(archive->product.detector_count, sizeof(*bindings));
        if (archive->calibrations[i].bindings == NULL) {
            return NULL;
        }
        ++archive->product.calibration_count;
    }
    bindings = (mef_qc_calibration_binding *)archive->calibrations[i].bindings;
    n = archive->calibrations[i].binding_count;
    bindings[n].detector_id = id;
    bindings[n].source_hdu = hdu;
    ++archive->calibrations[i].binding_count;
    return archive->calibrations[i].id;
}

int mef_bias_product_qc_add(mef_bias_product_qc *archive, size_t index, const char *id,
    const char *amplifier, const char *readout, size_t configured, int bin_x, int bin_y,
    const mef_bias_result *result, const mef_bias_measurement_options *options,
    const mef_bias_settings *settings, int rows, const char *bpm_path, int bpm_hdu, int good)
{
    detector_storage *store;
    mef_qc_detector_record *d;
    mef_qc_input_binding *bindings;
    const mef_bias_measurements *m = mef_bias_result_measurements(result);
    const mef_bias_qc *legacy = mef_bias_result_qc(result);
    const mef_request_spec *request = mef_request_view(mef_bias_result_request(result));
    const char *mask = NULL;
    qc_measurement_storage *storage;
    size_t i, n;
    int bounds[4] = {1, 1, 1, rows};
    const char *const *pair = NULL;
    size_t pair_count = 0;
    if (archive == NULL || index >= archive->product.detector_count || m == NULL ||
        legacy == NULL || request == NULL || options == NULL || settings == NULL ||
        m->count != archive->product.input_count ||
        request->input_count != archive->product.input_count ||
        archive->detectors[index].id != NULL) {
        return 0;
    }
    store = archive->storage + index;
    d = archive->detectors + index;
    if (bpm_path != NULL) {
        mask = register_calibration(archive, bpm_path, id, bpm_hdu);
        if (mask == NULL) {
            return 0;
        }
    }
    store->inputs = calloc(m->count, sizeof(*store->inputs));
    bindings = calloc(m->count, sizeof(*bindings));
    d->inputs = bindings;
    if (store->inputs == NULL || bindings == NULL ||
        !allocate_measurements(&store->product, archive->product.id)) {
        return 0;
    }
    if (legacy->median_even_handling != MEDIAN_EVEN_AVERAGE &&
        legacy->median_even_handling != MEDIAN_EVEN_LOWER) {
        return 0;
    }
    d->median_even_handling =
        legacy->median_even_handling == MEDIAN_EVEN_LOWER ? "lower" : "average";
    d->id = id;
    d->amplifier = amplifier;
    d->readout_id = readout;
    d->configuration_detector = configured;
    d->output_hdu = (int)index + 1;
    d->bin_x = bin_x;
    d->bin_y = bin_y;
    d->input_count = m->count;
    for (i = 0; i < m->count; ++i) {
        const mef_bias_frame_measurements *f = m->frames + i;
        if (strcmp(request->inputs[i].resolved_path, archive->inputs[i].path)) {
            return 0;
        }
        storage = store->inputs + i;
        if (!allocate_measurements(storage, archive->inputs[i].id)) {
            return 0;
        }
        if (!append_sample_statistics(
                storage, "raw_active", "raw_before_correction", &f->active_raw, 0, mask, NULL, 0) ||
            !append_sample_statistics(storage, "corrected_active", "overscan_corrected_trimmed",
                &f->active_corrected, 0, mask, NULL, 0) ||
            !append_sample_statistics(
                storage, "prescan", "raw_prescan_empty_reads", &f->prescan, 1, mask, NULL, 0) ||
            !append_sample_statistics(
                storage, "overscan", "raw_overscan_empty_reads", &f->overscan, 1, mask, NULL, 0)) {
            return 0;
        }
#define SCAN(name, value, unit, method)                                                            \
    if (append_scalar_measurement(storage, name, (double)(value), unit, "scan_correction_profile", \
            method, 1, NULL, rows, bounds, "not_applicable", NULL, NULL, 0) == NULL)               \
    return 0
        SCAN("scan_correction.median", legacy->scan_median[i], "ADU",
            "legacy_median_of_row_corrections");
        SCAN("scan_correction.stdev", legacy->scan_stdev[i], "ADU",
            "legacy_sample_stdev_of_row_corrections");
        SCAN("scan_correction.prescan_used", settings->use_prescan != 0, "count",
            "explicit_native_setting");
        SCAN("scan_correction.overscan_used", settings->use_overscan != 0, "count",
            "explicit_native_setting");
        SCAN("scan_correction.rejected_low", settings->rejection[0], "count",
            "explicit_native_setting");
        SCAN("scan_correction.rejected_high", settings->rejection[1], "count",
            "explicit_native_setting");
#undef SCAN
        bindings[i].input_id = archive->inputs[i].id;
        bindings[i].source_hdu = request->inputs[i].hdu_index;
        bindings[i].accepted = legacy->accepted[i];
        bindings[i].rejection_reason = legacy->accepted[i] ? NULL : "native_frame_mean_rejection";
        bindings[i].measurements = storage->measurement;
        bindings[i].measurement_count = storage->count;
    }
    storage = &store->product;
    if (!append_sample_statistics(
            storage, "master", "median_stacked_master", &m->master, 0, mask, NULL, 0) ||
        !append_sample_statistics(storage, "master_unmasked", "median_stacked_master_unmasked",
            &m->master_unmasked, 0, mask, NULL, 0)) {
        return 0;
    }
    if (options->ron_pair_set) {
        if (m->ron_first >= m->count || m->ron_second >= m->count) {
            return 0;
        }
        store->pair[0] = archive->inputs[m->ron_first].id;
        store->pair[1] = archive->inputs[m->ron_second].id;
        pair = store->pair;
        pair_count = 2;
    }
    if (!append_sample_statistics(storage, "raw_difference",
            "raw_pair_difference_before_any_correction", &m->raw_difference, 0, mask, pair,
            pair_count)) {
        return 0;
    }
#define PRODUCT(                                                                                   \
    name, value, unit, stage, method, available, reason, samples, zone, sources, source_count)     \
    if (append_scalar_measurement(storage, name, (double)(value), unit, stage, method, available,  \
            reason, samples, zone, "not_applicable", NULL, sources, source_count) == NULL)         \
    return 0
    PRODUCT("read_noise", m->ron_stdev_adu, "ADU", "raw_pair_difference_before_any_correction",
        "sample_stdev_raw_difference_div_sqrt2", m->ron_stdev_available,
        "pair_not_requested_or_insufficient_samples", m->raw_difference.valid_pixels,
        m->raw_difference.zone, pair, pair_count);
    PRODUCT("read_noise.mad", m->ron_mad_adu, "ADU", "raw_pair_difference_before_any_correction",
        "1.4826_MAD_raw_difference_div_sqrt2", m->ron_mad_available,
        "pair_not_requested_or_insufficient_samples", m->raw_difference.valid_pixels,
        m->raw_difference.zone, pair, pair_count);

    /* These two RON quantities use exactly the same mask as the raw difference. */

    if (mask != NULL && options->ron_pair_set) {
        for (i = storage->count - 2; i < storage->count; ++i) {
            storage->measurement[i].mask_policy = "applied";
            storage->measurement[i].mask_id = mask;
        }
    }
    if (options->ron_clip_enabled) {
        const image_clipped_stats *c = &m->clipped_difference;
        const image_sample_stats *sample_statistics = &c->sample;
        const char *reason = sample_statistics->valid_pixels < 2 ? "insufficient_clipped_samples"
                                                                 : "clipping_not_converged";
        size_t begin = storage->count;
        PRODUCT("read_noise.clipped", m->ron_clipped_adu, "ADU",
            "raw_pair_difference_before_any_correction",
            "clipped_sample_stdev_raw_difference_div_sqrt2", m->ron_clipped_available, reason,
            sample_statistics->valid_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.mean", sample_statistics->mean, "ADU",
            "raw_pair_difference_before_any_correction", "arithmetic_mean",
            sample_statistics->level_available, "insufficient_clipped_samples",
            sample_statistics->valid_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.median", sample_statistics->median, "ADU",
            "raw_pair_difference_before_any_correction", "median_averaged_central_pair",
            sample_statistics->level_available, "insufficient_clipped_samples",
            sample_statistics->valid_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.stdev", sample_statistics->stdev, "ADU",
            "raw_pair_difference_before_any_correction", "sample_standard_deviation_n_minus_1",
            sample_statistics->stdev_available, "insufficient_clipped_samples",
            sample_statistics->valid_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.retained", sample_statistics->valid_pixels, "count",
            "raw_pair_difference_before_any_correction", "explicit_sample_partition", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.rejected_low", c->rejected_low, "count",
            "raw_pair_difference_before_any_correction", "explicit_sample_partition", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.rejected_high", c->rejected_high, "count",
            "raw_pair_difference_before_any_correction", "explicit_sample_partition", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.bpm_excluded", sample_statistics->bpm_excluded, "count",
            "raw_pair_difference_before_any_correction", "explicit_sample_partition", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.nonfinite_excluded", sample_statistics->nonfinite_excluded, "count",
            "raw_pair_difference_before_any_correction", "explicit_sample_partition", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.iterations", c->iterations, "count",
            "raw_pair_difference_before_any_correction", "explicit_native_setting", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        PRODUCT("ron_clip.converged", c->converged, "count",
            "raw_pair_difference_before_any_correction", "explicit_native_flag", 1, NULL,
            sample_statistics->region_pixels, sample_statistics->zone, pair, pair_count);
        for (i = begin; i < storage->count; ++i) {
            storage->measurement[i].clipping = "median_centered_monotone_sigma";
            storage->measurement[i].mask_policy = mask ? "applied" : "omitted";
            storage->measurement[i].mask_id = mask;
        }
        PRODUCT("ron_clip.sigma_low", options->ron_clip.sigma_low, "dimensionless",
            "recipe_parameters", "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
        PRODUCT("ron_clip.sigma_high", options->ron_clip.sigma_high, "dimensionless",
            "recipe_parameters", "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
        PRODUCT("ron_clip.max_iterations", options->ron_clip.max_iterations, "count",
            "recipe_parameters", "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
    }
    PRODUCT("pixels.hot", m->high_offset_count, "count", "median_stacked_master",
        "all_master_pixels_above_masked_median_plus_k_scaled_MAD", m->high_offset_available,
        "MAD_not_requested", m->master.region_pixels, m->master.zone, NULL, 0);
    PRODUCT("pixels.hot.threshold", m->high_offset_threshold, "ADU", "median_stacked_master",
        "all_master_pixels_above_masked_median_plus_k_scaled_MAD", m->high_offset_available,
        "MAD_not_requested", m->master.region_pixels, m->master.zone, NULL, 0);
    storage->measurement[storage->count - 2].mask_policy = mask ? "unmasked_diagnostic" : "omitted";
    storage->measurement[storage->count - 2].mask_id = mask;
    storage->measurement[storage->count - 1].mask_policy = mask ? "applied" : "omitted";
    storage->measurement[storage->count - 1].mask_id = mask;
    PRODUCT("pixels.hot.sigma", options->high_sigma, "dimensionless", "recipe_parameters",
        "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
    PRODUCT("recipe.mad_requested", options->with_mad, "count", "recipe_parameters",
        "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
    PRODUCT("recipe.ron_pair_requested", options->ron_pair_set, "count", "recipe_parameters",
        "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
    PRODUCT("pixels.hot.threshold_degenerate", m->high_offset_degenerate, "count",
        "median_stacked_master", "explicit_native_flag", m->high_offset_available,
        "MAD_not_requested", m->master.region_pixels, m->master.zone, NULL, 0);
    if (mask != NULL) {
        if (!archive->processing.bpm.supplied ||
            archive->processing.bpm.encoding == MEF_BPM_BINARY) {
            PRODUCT("bpm.good_value", good, "count", "recipe_parameters", "explicit_native_setting",
                1, NULL, 1, NULL, NULL, 0);
        }
        if (archive->processing.bpm.supplied) {
            PRODUCT("bpm.encoding", archive->processing.bpm.encoding, "count", "recipe_parameters",
                "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
            PRODUCT("bpm.bad_when_nonzero", archive->processing.bpm.bad_when_nonzero, "count",
                "recipe_parameters", "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
            if (archive->processing.bpm.encoding == MEF_BPM_REASON8) {
                PRODUCT("bpm.reject_bits", archive->processing.bpm.reject_bits, "count",
                    "recipe_parameters", "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
            }
        }
        PRODUCT("bpm.active_coordinates", options->bpm_active_only, "count", "recipe_parameters",
            "explicit_native_setting", 1, NULL, 1, NULL, NULL, 0);
    }
    PRODUCT("legacy.frame_mean_average", legacy->frame_mean_average, "ADU", "frame_mean_rejection",
        "legacy_frame_mean_average", 1, NULL, m->count, NULL, NULL, 0);
    PRODUCT("legacy.frame_mean_sigma", legacy->frame_mean_sigma, "ADU", "frame_mean_rejection",
        "legacy_frame_mean_sigma", 1, NULL, m->count, NULL, NULL, 0);
    PRODUCT("legacy.rejection_low", legacy->rejection_low, "ADU", "frame_mean_rejection",
        "legacy_rejection_boundary", 1, NULL, m->count, NULL, NULL, 0);
    PRODUCT("legacy.rejection_high", legacy->rejection_high, "ADU", "frame_mean_rejection",
        "legacy_rejection_boundary", 1, NULL, m->count, NULL, NULL, 0);
    PRODUCT("legacy.product_median", legacy->product_median, "ADU", "median_stacked_master",
        "legacy_image_median", 1, NULL, m->master.region_pixels, m->master.zone, NULL, 0);
    PRODUCT("legacy.product_stdev", legacy->product_stdev, "ADU", "median_stacked_master",
        "legacy_image_stdev", 1, NULL, m->master.region_pixels, m->master.zone, NULL, 0);
    PRODUCT("variance", 0, "ADU2", "median_stacked_master", NULL, 0, "legacy_variance_unavailable",
        0, NULL, NULL, 0);
#undef PRODUCT
    n = m->high_offset_count;
    if (n) {
        const pixelmap *flags = m->high_offset_flags;
        size_t k = 0;
        int x, y;
        if (flags == NULL || n > SIZE_MAX / sizeof(double)) {
            return 0;
        }
        store->hot_x = malloc(n * sizeof(double));
        store->hot_y = malloc(n * sizeof(double));
        if (!store->hot_x || !store->hot_y) {
            return 0;
        }
        for (y = 0; y < flags->ly; ++y) {
            for (x = 0; x < flags->lx; ++x) {
                if (flags->data[y * flags->lx + x]) {
                    if (k == n) {
                        return 0;
                    }
                    store->hot_x[k] = x + 1;
                    store->hot_y[k] = y + 1;
                    ++k;
                }
            }
        }
        if (k != n) {
            return 0;
        }
    }
    for (i = 0; i < 2; ++i) {
        mef_qc_measurement *measurement =
            append_scalar_measurement(storage, i ? "pixels.hot.y" : "pixels.hot.x", 0, "pixel",
                "median_stacked_master", "stored_high_offset_flag_locations", n != 0,
                n                          ? NULL
                : m->high_offset_available ? "empty_location_set_zero_flagged_pixels"
                                           : "MAD_not_requested",
                m->master.region_pixels, m->master.zone, "unmasked_diagnostic", mask, NULL, 0);
        if (measurement == NULL) {
            return 0;
        }
        measurement->coordinates = "FITS-1-based-active";
        if (n) {
            measurement->vector = 1;
            measurement->value_count = n;
            measurement->values = i ? store->hot_y : store->hot_x;
        }
    }
    d->measurements = storage->measurement;
    d->measurement_count = storage->count;
    return 1;
}

int mef_bias_product_qc_check(mef_bias_product_qc *archive, char *message, size_t size)
{
    return archive == NULL ? -1 : mef_product_qc_validate(&archive->product, message, size);
}

const mef_product_qc *mef_bias_product_qc_view(const mef_bias_product_qc *archive)
{
    return archive == NULL ? NULL : &archive->product;
}

int mef_bias_product_qc_write(mef_bias_product_qc *archive, char *message, size_t size)
{
    return archive == NULL
               ? -1
               : mef_product_qc_write(archive->paths->asdf, &archive->product, message, size);
}

void mef_bias_product_qc_destroy(mef_bias_product_qc *archive)
{
    size_t i, j;
    if (archive == NULL) {
        return;
    }
    if (archive->storage) {
        for (i = 0; i < archive->product.detector_count; ++i) {
            release_measurements(&archive->storage[i].product);
            if (archive->storage[i].inputs) {
                for (j = 0; j < archive->product.input_count; ++j) {
                    release_measurements(archive->storage[i].inputs + j);
                }
            }
            free(archive->storage[i].inputs);
            free(archive->storage[i].hot_x);
            free(archive->storage[i].hot_y);
            if (archive->detectors) {
                free((void *)archive->detectors[i].inputs);
            }
        }
    }
    if (archive->calibrations) {
        for (i = 0; i < archive->product.calibration_count; ++i) {
            free((void *)archive->calibrations[i].bindings);
        }
    }
    free(archive->header_cards);
    free(archive->snapshot);
    free(archive->inputs);
    free(archive->input_ids);
    free(archive->detectors);
    free(archive->storage);
    free(archive->calibrations);
    free(archive->calibration_ids);
    free(archive);
}

static void classify_header_value(mef_qc_fits_card *c)
{
    char number[81], *end;
    size_t i, n;
    if (!c->present) {
        c->type = "missing";
        return;
    }
    if (!*c->fits_value) {
        c->type = "undefined";
        return;
    }
    c->type = "fits_literal";
    strcpy(c->value, c->fits_value);
    if (c->fits_value[0] == '\'') {
        n = 0;
        for (i = 1; c->fits_value[i]; ++i) {
            if (c->fits_value[i] == '\'') {
                if (c->fits_value[i + 1] == '\'') {
                    ++i;
                } else {
                    size_t tail = i + 1;
                    while (isspace((unsigned char)c->fits_value[tail])) {
                        ++tail;
                    }
                    while (n && c->value[n - 1] == ' ') {
                        --n;
                    }
                    if (c->fits_value[tail] || (n && c->value[n - 1] == '&')) {
                        strcpy(c->value, c->fits_value);
                        return;
                    }
                    c->value[n] = 0;
                    c->type = "string";
                    return;
                }
            }
            c->value[n++] = c->fits_value[i];
        }
        strcpy(c->value, c->fits_value);
        return;
    }
    if (!strcmp(c->fits_value, "T") || !strcmp(c->fits_value, "F")) {
        c->boolean = c->fits_value[0] == 'T';
        c->type = "boolean";
        return;
    }
    errno = 0;
    c->integer = strtoll(c->fits_value, &end, 10);
    while (isspace((unsigned char)*end)) {
        ++end;
    }
    if (!errno && end != c->fits_value && !*end) {
        c->type = "integer";
        return;
    }
    strcpy(number, c->fits_value);
    for (i = 0; number[i]; ++i) {
        if (number[i] == 'D' || number[i] == 'd') {
            number[i] = 'E';
        }
    }
    errno = 0;
    c->real = strtod(number, &end);
    while (isspace((unsigned char)*end)) {
        ++end;
    }
    if (!errno && end != number && !*end && isfinite(c->real)) {
        c->type = "real";
    }
}

static int capture_selected_header(qfits_header *h, const char *const *keys, size_t count,
    mef_qc_fits_card *cards, int hdu, const char *id, char *message, size_t size)
{
    size_t j;
    int i;
    for (j = 0; j < count; ++j) {
        mef_qc_fits_card *c = cards + j;
        c->hdu = hdu;
        c->detector_id = id;
        if (!keys[j] || strlen(keys[j]) > 79) {
            return 0;
        }
        strcpy(c->keyword, keys[j]);
        for (i = 0; i < h->n; ++i) {
            char key[81], value[81], comment[81], line[81];
            const char *canonical;
            if (qfits_header_getitem(h, i, key, value, comment, line)) {
                return 0;
            }
            canonical = !strncmp(key, "HIERARCH ", 9) ? key + 9 : key;
            if (strcmp(canonical, keys[j])) {
                continue;
            }
            if (c->present) {
                return 0; /* Ambiguous selected keyword is not first-wins. */
            }
            c->present = 1;
            strcpy(c->fits_value, value);
            strcpy(c->comment, comment);
            if (strlen(line) != 80) {
                if (message && size) {
                    snprintf(message, size, "Selected card %s has no complete 80-byte source card",
                        keys[j]);
                }
                return 0;
            }
            strcpy(c->card, line);
        }
        classify_header_value(c);
    }
    return 1;
}

int mef_bias_product_qc_headers(mef_bias_product_qc *archive, const char *const *primary, size_t np,
    const char *const *detector, size_t nd, const char *path, const char *snapshot, char *message,
    size_t size)
{
    size_t i, total;
    qfits_header *h = NULL;
    int okay = 0;
    if (message && size) {
        *message = 0;
    }
    if (!archive || np > 16 || nd > 16 || (np && !primary) || (nd && !detector) || !path ||
        !snapshot || archive->header_cards) {
        return -1;
    }
    total = np + nd * archive->product.detector_count;
    archive->product.recipe_config_path = path;
    archive->product.recipe_config_snapshot = snapshot;
    if (!total) {
        return 0;
    }

    /* Same existing bounded qfits scanner; final product only, never raw pixels. */

    if (qfits_cache_prime_bounded(
            (char *)archive->paths->fits, archive->product.detector_count + 1, 16 * 1024 * 1024)) {
        if (message && size) {
            snprintf(message, size, "Cannot prime bounded final FITS headers");
        }
        goto done;
    }
    archive->header_cards = calloc(total, sizeof(*archive->header_cards));
    if (!archive->header_cards) {
        goto done;
    }
    if (np) {
        h = qfits_header_read((char *)archive->paths->fits);
        if (!h || !capture_selected_header(
                      h, primary, np, archive->header_cards, 0, NULL, message, size)) {
            goto done;
        }
        qfits_header_destroy(h);
        h = NULL;
    }
    for (i = 0; nd && i < archive->product.detector_count; ++i) {
        h = qfits_header_readext((char *)archive->paths->fits, archive->detectors[i].output_hdu);
        if (!h || !capture_selected_header(h, detector, nd, archive->header_cards + np + i * nd,
                      archive->detectors[i].output_hdu, archive->detectors[i].id, message, size)) {
            goto done;
        }
        qfits_header_destroy(h);
        h = NULL;
    }
    archive->product.header_cards = archive->header_cards;
    archive->product.header_card_count = total;
    okay = 1;
done:
    qfits_header_destroy(h);
    if (!okay && message && size && !*message) {
        snprintf(message, size, "Selected final FITS header capture failed");
    }
    return okay ? 0 : -1;
}
