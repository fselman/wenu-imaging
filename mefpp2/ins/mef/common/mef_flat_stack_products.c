#include "mef_flat_stack.h"
#include "mef_bpm_linearity.h"
#include "mef_mef_assemble.h"
#include <math.h>
#undef calloc
#undef free

int mef_flat_stack_process(mef_flat_stack *flat)
{
    const size_t count = flat->inputs.count;
    int width = flat->ccd.trimreg[1] - flat->ccd.trimreg[0] + 1;
    int height = flat->ccd.trimreg[3] - flat->ccd.trimreg[2] + 1;
    cube_t *cube = cube_new(width, height, (int)count);
    int *participation = calloc(count, sizeof(*participation));
    double *normalization = calloc(count, sizeof(*normalization));
    double *stats = calloc(count, 3 * sizeof(*stats));
    float variance;
    int okay = 0;
    mef_bb *stack = &flat->stack;

    if (!cube || !participation || !normalization || !stats)
        goto done;
    stack->ccd = &flat->ccd;
    stack->xtnum = stack->nxts = 1;
    stack->dome_median = &flat->illumination;
    stack->dome_stdev = &variance;
    stack->dome_nplanes = &flat->normalized;
    stack->individual_frame_avg = stats;
    stack->individual_frame_median = stats + count;
    stack->individual_frame_sigma = stats + 2 * count;

    /* Scan-correct each loaded detector plane once before building the cube. */
    for (size_t i = 0; i < count; ++i) {
        char *path = flat->inputs.rows[i].path;
        int hdu = flat->exposures[i].hdu;
        snprintf(flat->run->message, sizeof(flat->run->message),
            "Cannot correct and trim dome input %.395s.", path);
        image_t *raw = mef_load_ext(path, hdu);
        if (!raw)
            goto done;
        if (raw->lx == flat->raw_width && raw->ly == flat->raw_height)
            cube->plane[i] = mef_overscan_correction(raw, stack, (int)i, "flat");
        image_del(raw);
        if (!cube->plane[i] || cube->plane[i]->lx != width || cube->plane[i]->ly != height)
            goto done;
    }

    /* The reference detector is the sole output of this qualification route. */
    snprintf(flat->run->message, sizeof(flat->run->message),
        "Cannot normalize and stack the selected dome exposures.");
    flat->image = mef_stack_flat_diagnostic(stack, "dome", cube, NULL, normalization, participation);
    cube = NULL;
    if (!flat->image || !isfinite(flat->illumination) || flat->illumination <= 0)
        goto done;
    for (size_t i = 0; i < (size_t)width * (size_t)height; ++i)
        if (!isfinite(flat->image->data[i]))
            goto done;
    for (size_t i = 0; i < count; ++i) {
        flat->exposures[i].normalization = normalization[i];
        flat->exposures[i].accepted = participation[i];
    }
    okay = 1;
done:
    if (cube)
        cube_del(cube);
    free(participation);
    free(normalization);
    free(stats);
    return okay;
}

static int inputs_unchanged(mef_flat_stack *flat)
{
    char digest[65];
    if (!mef_bpm_linearity_hash(flat->list_path, digest) || strcmp(digest, flat->list_sha256))
        return 0;
    for (size_t i = 0; i < flat->inputs.count; ++i)
        if (!mef_bpm_linearity_hash(flat->inputs.rows[i].path, digest) ||
            strcmp(digest, flat->exposures[i].sha256))
            return 0;
    return 1;
}

int mef_flat_stack_publish(mef_flat_stack *flat)
{
    mef_recipe_run *run = flat->run;
    size_t count = flat->inputs.count;
    mef_qc_input_record *inputs = calloc(count, sizeof(*inputs));
    mef_qc_input_binding *bindings = calloc(count, sizeof(*bindings));
    const char **sources = calloc(count, sizeof(*sources));
    size_t source_count = 0;
    char digest[65];
    int okay = 0;
    double illumination = flat->illumination;

    snprintf(run->message, sizeof(run->message), "Cannot prepare dome FITS and QC records.");
    if (!inputs || !bindings || !sources || snprintf(flat->staged, sizeof(flat->staged), "%s/dome.fits",
            run->private_work_directory) >= (int)sizeof(flat->staged))
        goto done;
    for (size_t i = 0; i < count; ++i) {
        mef_flat_exposure *exposure = flat->exposures + i;
        int measured = isfinite(exposure->normalization);
        inputs[i] = (mef_qc_input_record){
            exposure->id, flat->inputs.rows[i].path, exposure->sha256, i
        };
        exposure->measurement = (mef_qc_measurement){
            .name = "frame_normalization", .unit = "ADU", .stage = "dome_stack",
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
            sources[source_count++] = exposure->id;
        bindings[i] = (mef_qc_input_binding){
            .input_id = exposure->id, .source_hdu = exposure->hdu, .accepted = accepted,
            .rejection_reason = accepted ? NULL : "Frame mean is outside the dome admission interval.",
            .measurements = &exposure->measurement, .measurement_count = 1
        };
    }
    mef_qc_measurement output = {
        .name = "mean_frame_normalization", .unit = "ADU", .stage = "dome_stack",
        .method = "mean_of_frame_medians", .state = MEF_QC_MEASURED,
        .values = &illumination, .value_count = 1, .sample_count = flat->normalized,
        .coordinates = "active_detector", .mask_policy = "not_applicable",
        .clipping = "frame_mean_and_noise_scale", .nonfinite_policy = "reject_product",
        .source_ids = sources, .source_count = source_count
    };
    mef_qc_detector_record detector = {
        .id = flat->id, .amplifier = flat->amplifier, .readout_id = flat->readout,
        .configuration_detector = (size_t)flat->slot, .output_hdu = 1,
        .bin_x = flat->bin_x, .bin_y = flat->bin_y,
        .measurements = &output, .measurement_count = 1,
        .inputs = bindings, .input_count = count
    };
    mef_qc_text_evidence evidence[] = {
        {"project", "toml", flat->project.source}, {"detector_profile", "toml", flat->detector.source},
        {"observation_list_sha256", "hex", flat->list_sha256}
    };
    mef_product_qc product = {
        .id = strrchr(run->paths.fits, '/') + 1, .fits_path = run->paths.fits,
        .log_path = run->paths.log, .assessment_id = "master_dome_flat", .recipe_name = run->operation,
        .recipe_start = run->recipe_start, .recipe_version = 1, .product_sequence = 1,
        .producer_name = "mefpp_recipe", .producer_version = "1", .source_revision = run->revision,
        .configuration_id = flat->recipe.path, .configuration_snapshot = flat->recipe.source,
        .configuration_format = "domeff_recipe_toml_v1", .inputs = inputs, .input_count = count,
        .detectors = &detector, .detector_count = 1,
        .evidence = evidence, .evidence_count = sizeof(evidence) / sizeof(*evidence)
    };
    mef_assembly_detector assembly = {
        .path = flat->staged, .detector_id = flat->id, .configuration_detector = (size_t)flat->slot,
        .output_hdu = 1, .width = flat->image->lx, .height = flat->image->ly,
        .bitpix = BPP_DEFAULT, .bscale = 1, .bzero = 0
    };

    if (mef_product_qc_validate(&product, run->message, sizeof(run->message)) != 0)
        goto done;
    if (!inputs_unchanged(flat)) {
        snprintf(run->message, sizeof(run->message), "Dome observation list or exposure changed during processing.");
        goto done;
    }
    if (!mef_flat_stage_detector(flat->staged, "'CALIB.MASTER_DOME_FLAT'", flat->instrument,
            flat->filter, flat->id, illumination, NULL, 0, flat->image) ||
        mef_mef_assemble(run->paths.fits, flat->id, &assembly, 1, run->message, sizeof(run->message)) != 0 ||
        !mef_bpm_linearity_hash(run->paths.fits, digest))
        goto done;
    product.sha256 = digest;
    if (mef_product_qc_write(run->paths.asdf, &product, run->message, sizeof(run->message)) != 0)
        goto done;
    mef_recipe_run_discard_temporary(run, flat->staged);
    okay = 1;
done:
    free(sources);
    free(inputs);
    free(bindings);
    return okay;
}
