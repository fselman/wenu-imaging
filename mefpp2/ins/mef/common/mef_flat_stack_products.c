#include "mef_flat_stack.h"
#include "mef_bpm_linearity.h"
#include "mef_mef_assemble.h"
#include <math.h>
#undef calloc
#undef free

static int process_detector(mef_flat_stack *flat, size_t index)
{
    mef_flat_detector *channel = flat->detectors + index;
    const float *reference = index == flat->reference ? NULL :
        &flat->detectors[flat->reference].illumination;
    const size_t count = flat->inputs.count;
    int width = channel->ccd.trimreg[1] - channel->ccd.trimreg[0] + 1;
    int height = channel->ccd.trimreg[3] - channel->ccd.trimreg[2] + 1;
    cube_t *cube = cube_new(width, height, (int)count);
    int *participation = calloc(count, sizeof(*participation));
    double *normalization = calloc(count, sizeof(*normalization));
    double *stats = calloc(count, 3 * sizeof(*stats));
    image_t *image = NULL;
    float variance;
    int okay = 0;
    mef_bb *stack = &channel->stack;

    if (!cube || !participation || !normalization || !stats)
        goto done;
    stack->ccd = &channel->ccd;
    stack->xtnum = stack->nxts = 1;
    if (flat->sky) {
        stack->sky_median = &channel->illumination;
        stack->sky_stdev = &variance;
        stack->sky_nplanes = &channel->normalized;
    } else {
        stack->dome_median = &channel->illumination;
        stack->dome_stdev = &variance;
        stack->dome_nplanes = &channel->normalized;
    }
    stack->individual_frame_avg = stats;
    stack->individual_frame_median = stats + count;
    stack->individual_frame_sigma = stats + 2 * count;

    /* Scan-correct each loaded detector plane once before building the cube. */
    for (size_t i = 0; i < count; ++i) {
        char *path = flat->inputs.rows[i].path;
        int hdu = channel->exposures[i].hdu;
        snprintf(flat->run->message, sizeof(flat->run->message),
            "Cannot correct and trim flat input %.395s.", path);
        image_t *raw = mef_load_ext(path, hdu);
        if (!raw)
            goto done;
        if (raw->lx == channel->raw_width && raw->ly == channel->raw_height)
            cube->plane[i] = mef_overscan_correction(raw, stack, (int)i, "flat");
        image_del(raw);
        if (!cube->plane[i] || cube->plane[i]->lx != width || cube->plane[i]->ly != height)
            goto done;
    }

    snprintf(flat->run->message, sizeof(flat->run->message),
        "Cannot normalize and stack the selected flat exposures.");
    image = mef_stack_flat_reference(stack, flat->sky ? "sky" : "dome", cube, NULL,
        normalization, participation, reference);
    cube = NULL;
    if (!image || !isfinite(channel->illumination) || channel->illumination <= 0)
        goto done;
    for (size_t i = 0; i < (size_t)width * (size_t)height; ++i)
        if (!isfinite(image->data[i]))
            goto done;
    for (size_t i = 0; i < count; ++i) {
        channel->exposures[i].normalization = normalization[i];
        channel->exposures[i].accepted = participation[i];
    }
    snprintf(flat->run->message, sizeof(flat->run->message),
        "Cannot stage flat detector %.68s.", channel->id);
    if (snprintf(channel->staged, sizeof(channel->staged), "%s/flat-%04zu.fits",
            flat->run->private_work_directory, index + 1) >= (int)sizeof(channel->staged) ||
        !mef_flat_stage_detector(channel->staged,
            flat->sky ? "'CALIB.MASTER_SKY_FLAT'" : "'CALIB.MASTER_DOME_FLAT'",
            flat->instrument, flat->filter, channel->id, channel->illumination, NULL, 0, image))
        goto done;
    flat->assembly[index] = (mef_assembly_detector){
        .path = channel->staged, .detector_id = channel->id,
        .configuration_detector = (size_t)channel->slot, .output_hdu = index + 1,
        .width = image->lx, .height = image->ly, .bitpix = BPP_DEFAULT, .bscale = 1, .bzero = 0
    };
    okay = 1;
done:
    if (image)
        image_del(image);
    if (cube)
        cube_del(cube);
    free(participation);
    free(normalization);
    free(stats);
    return okay;
}

int mef_flat_stack_process(mef_flat_stack *flat)
{
    /* Compute the legacy chip-1 scale first, irrespective of output order. */
    if (!process_detector(flat, flat->reference))
        return 0;
    for (size_t d = 0; d < flat->detector_count; ++d)
        if (d != flat->reference && !process_detector(flat, d))
            return 0;
    return 1;
}

static int inputs_unchanged(mef_flat_stack *flat)
{
    char digest[65];
    if (!mef_bpm_linearity_hash(flat->list_path, digest) || strcmp(digest, flat->list_sha256))
        return 0;
    for (size_t i = 0; i < flat->inputs.count; ++i)
        if (!mef_bpm_linearity_hash(flat->inputs.rows[i].path, digest) ||
            strcmp(digest, flat->frames[i].sha256))
            return 0;
    return 1;
}

static void detector_qc(mef_flat_stack *flat, size_t index, const mef_qc_input_record *inputs,
    mef_qc_input_binding *bindings, const char **sources, double *illumination,
    mef_qc_measurement *output, mef_qc_detector_record *detector)
{
    mef_flat_detector *channel = flat->detectors + index;
    size_t count = flat->inputs.count, source_count = 0;
    *illumination = channel->illumination;

    for (size_t i = 0; i < count; ++i) {
        mef_flat_exposure *exposure = channel->exposures + i;
        int measured = isfinite(exposure->normalization);
        exposure->measurement = (mef_qc_measurement){
            .name = "frame_normalization", .unit = "ADU", .stage = flat->sky ? "sky_stack" : "dome_stack",
            .method = "clipped_median", .state = measured ? MEF_QC_MEASURED : MEF_QC_UNAVAILABLE,
            .reason = measured ? NULL : "Exposure has no usable normalization median.",
            .values = measured ? &exposure->normalization : NULL, .value_count = measured ? 1 : 0,
            .sample_count = measured ? 1 : 0,
            .coordinates = "active_detector", .mask_policy = "not_applicable",
            .clipping = "frame_mean_and_noise_scale", .nonfinite_policy = "reject_product",
            .source_ids = &inputs[i].id, .source_count = 1
        };
        /* The legacy stack may retain an unscaled near-zero plane. Record
         * participation separately from the availability of its median. */
        int accepted = exposure->accepted;
        if (measured)
            sources[source_count++] = inputs[i].id;
        bindings[i] = (mef_qc_input_binding){
            .input_id = inputs[i].id, .source_hdu = exposure->hdu, .accepted = accepted,
            .rejection_reason = accepted ? NULL : "Frame mean is outside the flat admission interval.",
            .measurements = &exposure->measurement, .measurement_count = 1
        };
    }
    *output = (mef_qc_measurement){
        .name = "mean_frame_normalization", .unit = "ADU", .stage = flat->sky ? "sky_stack" : "dome_stack",
        .method = "mean_of_frame_medians", .state = MEF_QC_MEASURED,
        .values = illumination, .value_count = 1, .sample_count = channel->normalized,
        .coordinates = "active_detector", .mask_policy = "not_applicable",
        .clipping = "frame_mean_and_noise_scale", .nonfinite_policy = "reject_product",
        .source_ids = sources, .source_count = source_count
    };
    *detector = (mef_qc_detector_record){
        .id = channel->id, .amplifier = channel->amplifier, .readout_id = flat->readout,
        .configuration_detector = (size_t)channel->slot, .output_hdu = (int)index + 1,
        .bin_x = flat->bin_x, .bin_y = flat->bin_y,
        .measurements = output, .measurement_count = 1,
        .inputs = bindings, .input_count = count
    };
}

int mef_flat_stack_publish(mef_flat_stack *flat)
{
    mef_recipe_run *run = flat->run;
    size_t count = flat->inputs.count, detectors = flat->detector_count;
    mef_qc_input_record *inputs = calloc(count, sizeof(*inputs));
    mef_qc_input_binding *bindings = calloc(detectors * count, sizeof(*bindings));
    const char **sources = calloc(detectors * count, sizeof(*sources));
    mef_qc_detector_record *records = calloc(detectors, sizeof(*records));
    mef_qc_measurement *measurements = calloc(detectors, sizeof(*measurements));
    double *illumination = calloc(detectors, sizeof(*illumination));
    char digest[65];
    int okay = 0;
    const char *reference_id = flat->detectors[flat->reference].id;

    snprintf(run->message, sizeof(run->message), "Cannot prepare flat FITS and QC records.");
    if (!inputs || !bindings || !sources || !records || !measurements || !illumination)
        goto done;
    for (size_t i = 0; i < count; ++i)
        inputs[i] = (mef_qc_input_record){
            flat->frames[i].id, flat->inputs.rows[i].path, flat->frames[i].sha256, i
        };
    for (size_t d = 0; d < detectors; ++d)
        detector_qc(flat, d, inputs, bindings + d * count, sources + d * count,
            illumination + d, measurements + d, records + d);

    mef_qc_text_evidence evidence[] = {
        {"project", "toml", flat->project.source}, {"detector_profile", "toml", flat->detector.source},
        {"observation_list_sha256", "hex", flat->list_sha256},
        {"normalization_reference", "text", reference_id}
    };
    mef_product_qc product = {
        .id = strrchr(run->paths.fits, '/') + 1, .fits_path = run->paths.fits,
        .log_path = run->paths.log, .assessment_id = flat->sky ? "master_sky_flat" : "master_dome_flat",
        .recipe_name = run->operation,
        .recipe_start = run->recipe_start, .recipe_version = 1, .product_sequence = 1,
        .producer_name = "mefpp_recipe", .producer_version = "1", .source_revision = run->revision,
        .configuration_id = flat->recipe.path, .configuration_snapshot = flat->recipe.source,
        .configuration_format = flat->sky ? "skyff_recipe_toml_v1" : "domeff_recipe_toml_v1",
        .inputs = inputs, .input_count = count,
        .detectors = records, .detector_count = detectors,
        .evidence = evidence, .evidence_count = sizeof(evidence) / sizeof(*evidence)
    };

    if (mef_product_qc_validate(&product, run->message, sizeof(run->message)) != 0)
        goto done;
    if (!inputs_unchanged(flat)) {
        snprintf(run->message, sizeof(run->message), "Flat observation list or exposure changed during processing.");
        goto done;
    }
    if (mef_mef_assemble(run->paths.fits, reference_id, flat->assembly, detectors,
            run->message, sizeof(run->message)) != 0 ||
        !mef_bpm_linearity_hash(run->paths.fits, digest))
        goto done;
    product.sha256 = digest;
    if (mef_product_qc_write(run->paths.asdf, &product, run->message, sizeof(run->message)) != 0)
        goto done;
    for (size_t d = 0; d < detectors; ++d)
        mef_recipe_run_discard_temporary(run, flat->detectors[d].staged);
    okay = 1;
done:
    free(illumination);
    free(measurements);
    free(records);
    free(sources);
    free(inputs);
    free(bindings);
    return okay;
}
