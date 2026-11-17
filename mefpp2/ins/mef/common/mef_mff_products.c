#define _POSIX_C_SOURCE 200809L
#include "mef_mff.h"
#include "mef_flat_product.h"
#include "mefp_lib.h"
#include "mef_bpm_linearity.h" /* Shared streaming file identity. */
#include <math.h>

static const char *const source_ids[] = {"dome", "sky"};

static void number(qfits_header *header, char *key, int integer)
{
    char value[32];
    snprintf(value, sizeof(value), "%d", integer);
    qfits_header_append(header, key, value, NULL, NULL);
}

int mef_flat_stage_detector(const char *destination, const char *category,
    const char *instrument, const char *filter, const char *id, double median,
    const char *source_path, int source_hdu, image_t *image)
{
    static const char *const geometry[] = {"DATASEC", "DETSEC", "CCDSEC", "CRPIX1",
        "CRPIX2", "CRVAL1", "CRVAL2", "CTYPE1", "CTYPE2", "CUNIT1", "CUNIT2",
        "CD1_1", "CD1_2", "CD2_1", "CD2_2", "PC1_1", "PC1_2", "PC2_1", "PC2_2",
        "CDELT1", "CDELT2", "RADESYS", "EQUINOX", "LONPOLE", "LATPOLE"};
    qfits_header *source = source_path ? qfits_header_readext((char *)source_path, source_hdu) : NULL;
    qfits_header *primary = qfits_header_new(), *extension = qfits_header_new();
    char value[80];
    int okay = 0;
    if (!primary || !extension || (source_path && !source))
        goto done;

    qfits_header_append(primary, "SIMPLE", "T", NULL, NULL);
    qfits_header_append(primary, "BITPIX", "8", NULL, NULL);
    qfits_header_append(primary, "NAXIS", "0", NULL, NULL);
    qfits_header_append(primary, "EXTEND", "T", NULL, NULL);
    qfits_header_append(primary, "PRODCATG", (char *)category, NULL, NULL);
    qfits_header_append(primary, "INSTRUME", (char *)instrument, NULL, NULL);
    qfits_header_append(primary, "FILTER", (char *)filter, NULL, NULL);
    qfits_header_append(primary, "END", NULL, NULL, NULL);

    qfits_header_append(extension, "XTENSION", "'IMAGE   '", NULL, NULL);
    number(extension, "BITPIX", BPP_DEFAULT);
    number(extension, "NAXIS", 2);
    number(extension, "NAXIS1", image->lx);
    number(extension, "NAXIS2", image->ly);
    number(extension, "PCOUNT", 0);
    number(extension, "GCOUNT", 1);
    snprintf(value, sizeof(value), "'%s'", id);
    qfits_header_append(extension, "EXTNAME", value, NULL, NULL);
    const char *extver = source ? qfits_header_getstr(source, "EXTVER") : NULL;
    if (extver)
        qfits_header_append(extension, "EXTVER", (char *)extver, NULL, NULL);
    qfits_header_append(extension, "BUNIT", "'1'", NULL, NULL);
    snprintf(value, sizeof(value), "%.17g", median);
    qfits_header_append(extension, "HIERARCH ESO MPP QC FRMEDIAN", value, NULL, NULL);
    for (size_t i = 0; source && i < sizeof(geometry) / sizeof(*geometry); ++i) {
        char *card = qfits_header_getstr(source, geometry[i]);
        if (card)
            qfits_header_append(extension, (char *)geometry[i], card, NULL, NULL);
    }
    qfits_header_append(extension, "END", NULL, NULL, NULL);

    okay = mef_hdrpix_dump(NULL, (char *)destination, primary, BPP_DEFAULT) == 0 &&
           mef_hdrpix_dump(image, (char *)destination, extension, BPP_DEFAULT) == 0;
done:
    qfits_header_destroy(source);
    qfits_header_destroy(primary);
    qfits_header_destroy(extension);
    return okay;
}

static void record_detector(mef_mff *mff, size_t index, const image_t *combined)
{
    mef_mff_detector *detector = mff->detectors + index;
    for (size_t input = 0; input < 2; ++input) {
        const mef_bound_detector *binding = mef_layout_find(mff->components[input].mapping, detector->id);
        detector->input_qc[input] = (mef_qc_measurement){
            .name = "frame_normalization", .unit = "ADU", .stage = "supplied_master",
            .reason = "Exposure-level normalization belongs to the supplied master.",
            .state = MEF_QC_UNAVAILABLE, .coordinates = "active_detector",
            .mask_policy = "not_applicable", .clipping = "not_applicable",
            .nonfinite_policy = "not_applicable", .source_ids = source_ids + input,
            .source_count = 1
        };
        detector->input[input] = (mef_qc_input_binding){
            .input_id = source_ids[input], .source_hdu = binding->image.hdu_index, .accepted = 1,
            .measurements = detector->input_qc + input, .measurement_count = 1
        };
    }
    if (mff->bpm_bindings) {
        const mef_bound_detector *bpm = mef_layout_find(mff->components[MFF_BPM].mapping, detector->id);
        mff->bpm_bindings[index] = (mef_qc_calibration_binding){detector->id, bpm->image.hdu_index};
    }
    detector->output_qc = (mef_qc_measurement){
        .name = "master_median", .unit = "1", .stage = "combined_flat",
        .method = "eclipse_image_getmedian", .state = MEF_QC_MEASURED,
        .values = &detector->median, .value_count = 1,
        .sample_count = (uint64_t)combined->lx * (uint64_t)combined->ly,
        .coordinates = "active_detector", .mask_policy = "unmasked_diagnostic",
        .clipping = "none", .nonfinite_policy = "reject_product",
        .source_ids = source_ids, .source_count = 2
    };
    mff->qc[index] = (mef_qc_detector_record){
        .id = detector->id, .amplifier = detector->amplifier, .readout_id = mff->readout,
        .configuration_detector = (size_t)detector->slot, .output_hdu = (int)(index + 1),
        .bin_x = mff->bin_x, .bin_y = mff->bin_y,
        .measurements = &detector->output_qc, .measurement_count = 1,
        .inputs = detector->input, .input_count = 2
    };
    mff->assembly[index] = (mef_assembly_detector){
        .path = detector->temporary_path, .detector_id = detector->id,
        .configuration_detector = (size_t)detector->slot, .output_hdu = index + 1,
        .width = combined->lx, .height = combined->ly, .bitpix = BPP_DEFAULT,
        .bscale = 1, .bzero = 0
    };
}

int mef_mff_process(mef_mff *mff, size_t index)
{
    mef_mff_detector *detector = mff->detectors + index;
    image_t *dome = NULL, *sky = NULL, *combined = NULL;
    pixelmap *bpm = NULL;
    pixelvalue median;
    int okay = 0;
    fprintf(mff->run->log, "DETECTOR %s\n", detector->id);
    snprintf(mff->run->message, sizeof(mff->run->message), "Cannot combine detector %.68s.", detector->id);

    /* [MFF-COMBINE] The resident master planes are read-only to the combiner. */
    if (mef_layout_load(mff->components[MFF_DOME].mapping, detector->id, &dome, &mff->error) != MEF_OK ||
        mef_layout_load(mff->components[MFF_SKY].mapping, detector->id, &sky, &mff->error) != MEF_OK)
        goto done;
    if (mff->bpm_bindings && mef_layout_load_bpm(mff->components[MFF_BPM].mapping,
            detector->id, mff->bpm_good, &bpm, &mff->error) != MEF_OK)
        goto done;
    combined = mef_flat_combine(dome, sky, mff->radius, bpm);
    if (!combined)
        goto done;
    for (size_t i = 0; i < (size_t)combined->lx * (size_t)combined->ly; ++i) {
        if (!isfinite(combined->data[i])) {
            snprintf(mff->run->message, sizeof(mff->run->message),
                "Combined detector %.68s contains nonfinite pixels.", detector->id);
            goto done;
        }
    }
    if (image_getmedian_checked(combined, &median) != 0 ||
        snprintf(detector->temporary_path, sizeof(detector->temporary_path),
            "%s/detector-%06zu.fits", mff->run->private_work_directory, index)
            >= (int)sizeof(detector->temporary_path))
        goto done;
    detector->median = median;
    const mef_bound_detector *binding = mef_layout_find(mff->components[MFF_SKY].mapping,
        detector->id);
    if (!mef_flat_stage_detector(detector->temporary_path, "'CALIB.MASTER_FLAT'",
            mff->instrument, mff->filter, detector->id, detector->median,
            mff->components[MFF_SKY].path, binding->image.hdu_index, combined))
        goto done;
    record_detector(mff, index, combined);
    mff->run->message[0] = '\0';
    okay = 1;
done:
    if (combined)
        image_del(combined);
    if (bpm)
        pixelmap_del(bpm);
    if (sky)
        image_del(sky);
    if (dome)
        image_del(dome);
    return okay;
}

int mef_mff_publish(mef_mff *mff)
{
    mef_recipe_run *run = mff->run;
    mef_qc_input_record inputs[2];
    char digest[65];
    for (size_t i = 0; i < 2; ++i) {
        inputs[i] = (mef_qc_input_record){source_ids[i], mff->components[i].path,
            mff->components[i].sha256, i};
    }
    const mef_mff_component *bpm = mff->components + MFF_BPM;
    mef_qc_calibration_record calibration = {
        .id = "smoothing_bpm", .path = bpm->path, .sha256 = bpm->sha256, .role = "bpm",
        .bindings = mff->bpm_bindings, .binding_count = mff->detector_count
    };
    mef_qc_text_evidence evidence[] = {
        {"project", "toml", mff->project_evidence.source},
        {"detector_profile", "toml", mff->profile.source}
    };
    mef_product_qc product = {
        .id = strrchr(run->paths.fits, '/') + 1, .fits_path = run->paths.fits,
        .log_path = run->paths.log, .assessment_id = "master_flat", .recipe_name = run->operation,
        .recipe_start = run->recipe_start, .recipe_version = 1, .product_sequence = 1,
        .producer_name = "mefpp_recipe", .producer_version = "1",
        .source_revision = run->revision, .configuration_id = mff->recipe.path,
        .configuration_snapshot = mff->recipe.source, .configuration_format = "mff_recipe_toml_v1",
        .inputs = inputs, .input_count = 2, .input_file_kind = "calibration",
        .calibrations = bpm->path ? &calibration : NULL, .calibration_count = bpm->path ? 1 : 0,
        .detectors = mff->qc, .detector_count = mff->detector_count,
        .evidence = evidence, .evidence_count = sizeof(evidence) / sizeof(*evidence)
    };

    /* [MFF-PUBLISH] Validate the archive records before assembly reserves the final FITS. */
    if (mef_product_qc_validate(&product, run->message, sizeof(run->message)) != 0 ||
        mef_mef_assemble(run->paths.fits, mff->reference, mff->assembly, mff->detector_count,
            run->message, sizeof(run->message)) != 0)
        return 0;
    if (!mef_bpm_linearity_hash(run->paths.fits, digest)) {
        snprintf(run->message, sizeof(run->message), "Cannot fingerprint the combined FITS product.");
        return 0;
    }
    product.sha256 = digest;
    if (mef_product_qc_write(run->paths.asdf, &product, run->message, sizeof(run->message)) != 0)
        return 0;
    for (size_t i = 0; i < mff->detector_count; ++i)
        mef_recipe_run_discard_temporary(run, mff->detectors[i].temporary_path);
    return 1;
}
