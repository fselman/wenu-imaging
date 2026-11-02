/* Synthetic numerical equivalence/lifetime controls, including legacy MEF I/O. */
#include "mef_cal_bias.h"
#include "mefp_lib.h"
#include <assert.h>
#include <float.h>
#include <stdio.h>

typedef struct { size_t calls, fail_at, owners; int persistent; } allocation_state;
static const image_t *const *reference_frames;
static int reference_count;
static const char *fixture_directory;
image_t *mef_bias_reference(mef_bb *bb, char *what);
cube_t *mef_bias_reference_load(char *name, int extension)
{
    cube_t *cube;
    int i;
    (void)name; (void)extension;
    cube = cube_new(reference_frames[0]->lx, reference_frames[0]->ly, reference_count);
    assert(cube != NULL);
    for (i = 0; i < reference_count; ++i) {
        cube->plane[i] = image_copy((image_t *)reference_frames[i]);
        assert(cube->plane[i] != NULL);
    }
    return cube;
}
static void *allocate(void *user, size_t bytes)
{
    allocation_state *state;
    void *pointer;
    state = user;
    ++state->calls;
    if (state->fail_at && (state->calls == state->fail_at ||
        (state->persistent && state->calls >= state->fail_at))) return NULL;
    pointer = (malloc)(bytes);
    if (pointer != NULL) ++state->owners;
    return pointer;
}
static void release(void *user, void *pointer)
{
    allocation_state *state;
    state = user;
    assert(pointer != NULL && state->owners > 0);
    --state->owners;
    (free)(pointer);
}
static void equal_float(float actual, float expected)
{
    assert(memcmp(&actual, &expected, sizeof(float)) == 0);
}
static mef_context *context_for(mef_bb *legacy, int count, int mode,
    const mef_allocator *allocator)
{
    mef_config *config;
    mef_request *request;
    mef_context *context;
    mef_image_ref refs[6], calibration;
    mef_bpm_selection selections[2];
    mef_calibration_role role;
    mef_resolved_request_spec spec;
    char paths[6][80], ids[6][32];
    const char *diagnostic;
    int i;
    config = NULL; request = NULL; context = NULL;
    assert(count <= 6);
    for (i = 0; i < count; ++i) {
        sprintf(paths[i], "/synthetic bias/frame %d.fits", i);
        sprintf(ids[i], "asset:%d", i);
        refs[i].asset_record_id = ids[i];
        refs[i].detector_id = mode == 2 && i == count - 1 ? "detector:other" : "detector:test";
        refs[i].resolved_path = paths[i];
        refs[i].hdu_index = mode == 3 ? 0 : 2;
        refs[i].extname = mode == 3 ? NULL : "WIN.CHIP";
        refs[i].extver = mode == 3 ? 0 : 1;
    }
    selections[0].detector_id = "detector:test";
    selections[0].state = mode == 1 ? MEF_BPM_SELECTED : MEF_BPM_OMITTED;
    selections[1].detector_id = "detector:other";
    selections[1].state = MEF_BPM_OMITTED;
    calibration = refs[0];
    calibration.asset_record_id = "mask:test";
    calibration.resolved_path = "/synthetic bias/mask.fits";
    role = MEF_CAL_BPM;
    spec.request.operation = mode == 4 ? MEF_OP_SCI_PP : MEF_OP_CAL_BIAS;
    spec.request.operation_version = 1;
    spec.request.inputs = refs;
    spec.request.input_count = (size_t)count;
    spec.request.calibrations = mode == 1 ? &calibration : NULL;
    spec.request.calibration_count = mode == 1 ? 1 : 0;
    spec.request.work_dir = "/synthetic work";
    spec.request.output_dir = "/synthetic output";
    spec.request.log_path = "/synthetic log/native.log";
    spec.calibration_roles = mode == 1 ? &role : NULL;
    spec.calibration_role_count = mode == 1 ? 1 : 0;
    spec.bpm_selections = selections;
    spec.bpm_selection_count = mode == 2 ? 2 : 1;
    assert(mef_config_from_legacy(legacy, NULL, &config, &diagnostic) == MEF_OK);
    assert(mef_request_create_resolved(&spec, NULL, &request, NULL) == MEF_OK);
    assert(mef_context_create(config, request, allocator, &context, NULL) == MEF_OK);
    mef_request_destroy(request);
    mef_config_destroy(config);
    return context;
}
static void expect_failure(mef_context *context, mef_bias_input *input,
    mef_status expected)
{
    mef_bias_result *result;
    mef_error *error;
    result = NULL; error = NULL;
    assert(mef_cal_bias(context, input, &result, &error) == expected);
    assert(result == NULL && mef_error_status(error) == expected);
    mef_error_destroy(error);
}
static void equivalence(mef_bb *legacy, int detector_index, int profile)
{
    image_t *frames[6], *expected, *actual;
    char list_path[2048];
    char *original_name;
    float reference_values[6], reference_scan[6], reference_scan_stdev[6];
    int reference_planes;
    pixelvalue saved[6][60];
    const image_t *borrowed[6], *signal;
    mef_bias_input input;
    mef_context *context;
    mef_bias_result *result, *alias;
    const mef_bias_qc *qc;
    mef_error *error;
    float scan_median[6], scan_stdev[6], avg, sig, low, high, med, stdev;
    char *names[6];
    int nplanes, count, i, x, y, successful;
    count = profile == 1 ? 6 : 5;
    for (i = 0; i < count; ++i) {
        frames[i] = image_new(10, 6);
        borrowed[i] = frames[i];
        names[i] = "synthetic.fits";
        assert(frames[i] != NULL);
        for (y = 0; y < 6; ++y) for (x = 0; x < 10; ++x) {
            frames[i]->data[x + 10*y] = (pixelvalue)(100 + y + 3*i);
            if (x >= 2 && x <= 7) {
                frames[i]->data[x + 10*y] += (pixelvalue)(10 + i + x + 2*y);
                if (profile == 2 && i == count - 1)
                    frames[i]->data[x + 10*y] += 100;
                if (profile == 3) frames[i]->data[x + 10*y] -= (pixelvalue)i;
            }
        }
        memcpy(saved[i], frames[i]->data, sizeof(saved[i]));
    }
    legacy->bias_minframe = 3;
    legacy->bias_kappa1 = profile == 2 ? 1.2 : profile == 4 ? 0.0 : 10.0;
    legacy->xtnum = 2;
    legacy->nxts = 1;
    legacy->use_prescan = profile == 5 ? 0 : 1;
    legacy->use_overscan = profile == 6 ? 0 : 1;
    legacy->scanrej[0] = profile == 7 ? 1 : 0;
    legacy->scanrej[1] = profile == 7 ? 1 : 0;
    legacy->ccd[detector_index].prescan_x[0] = 1;
    legacy->ccd[detector_index].prescan_x[1] = 2;
    legacy->ccd[detector_index].overscan_x[0] = 9;
    legacy->ccd[detector_index].overscan_x[1] = 10;
    legacy->ccd[detector_index].trimreg[0] = 3;
    legacy->ccd[detector_index].trimreg[1] = 8;
    legacy->ccd[detector_index].trimreg[2] = 2;
    legacy->ccd[detector_index].trimreg[3] = 5;
    legacy->ccd[1] = legacy->ccd[detector_index];
    legacy->bias_frame_name = names;
    legacy->bias_scan_median = scan_median;
    legacy->bias_scan_stdev = scan_stdev;
    legacy->bias_avg1 = &avg; legacy->bias_sig1 = &sig;
    legacy->bias_framethr_lo = &low; legacy->bias_framethr_hi = &high;
    legacy->bias_median = &med; legacy->bias_stdev = &stdev;
    legacy->bias_nplanes = &nplanes;
    reference_frames = borrowed;
    reference_count = count;
    expected = mef_bias_reference(legacy, "bias");
    successful = expected != NULL;
    reference_values[0] = avg; reference_values[1] = sig;
    reference_values[2] = low; reference_values[3] = high;
    if (successful) {
        reference_values[4] = med; reference_values[5] = stdev;
        reference_planes = nplanes;
    }
    memcpy(reference_scan, scan_median, (size_t)count * sizeof(float));
    memcpy(reference_scan_stdev, scan_stdev, (size_t)count * sizeof(float));
    assert(strlen(fixture_directory) + 64 < sizeof(list_path));
    sprintf(list_path, "%s/profile-%d.list", fixture_directory, profile);
    original_name = legacy->name_bias;
    legacy->name_bias = list_path;
    actual = mef_build_cal(legacy, "bias");
    legacy->name_bias = original_name;
    assert((actual != NULL) == successful);
    equal_float(avg, reference_values[0]); equal_float(sig, reference_values[1]);
    equal_float(low, reference_values[2]); equal_float(high, reference_values[3]);
    assert(memcmp(scan_median, reference_scan, (size_t)count * sizeof(float)) == 0);
    assert(memcmp(scan_stdev, reference_scan_stdev, (size_t)count * sizeof(float)) == 0);
    if (successful) {
        assert(actual->lx == expected->lx && actual->ly == expected->ly);
        assert(memcmp(actual->data, expected->data, 24 * sizeof(pixelvalue)) == 0);
        equal_float(med, reference_values[4]); equal_float(stdev, reference_values[5]);
        assert(nplanes == reference_planes);
    }
    image_del(actual);
    assert(successful == (profile != 3 && profile != 4));
    context = context_for(legacy, count, 0, NULL);
    input.frames = borrowed; input.count = (size_t)count;
    input.configuration_detector = (size_t)detector_index;
    result = NULL; error = NULL;
    if (successful) {
        assert(mef_cal_bias(context, &input, &result, &error) == MEF_OK);
        assert(error == NULL);
        /* Occupied output handles stay unchanged. */
        alias = result;
        assert(mef_cal_bias(context, &input, &alias, NULL) == MEF_ERR_INPUT && alias == result);
        assert(mef_error_create(MEF_ERR_IO, "occupied", NULL, &error) == MEF_OK);
        alias = NULL;
        assert(mef_cal_bias(context, &input, &alias, &error) == MEF_ERR_INPUT && alias == NULL);
        mef_error_destroy(error); error = NULL;
        mef_context_destroy(context); context = NULL;
        signal = mef_bias_result_signal(result);
        assert(signal->lx == 6 && signal->ly == 4);
        assert(memcmp(signal->data, expected->data, 24 * sizeof(pixelvalue)) == 0);
        qc = mef_bias_result_qc(result);
        assert(qc->variance_state == MEF_BIAS_VARIANCE_UNAVAILABLE_LEGACY);
        assert(qc->bpm_selection == MEF_BPM_OMITTED && !qc->bpm_applied);
        assert(!qc->ron_estimate_available);
        /* Independent analytic check, retaining the historical lower median
         * for even counts (six input or four retained planes). */
        for (y = 0; y < 4; ++y) for (x = 0; x < 6; ++x)
            assert(signal->data[x + 6*y] == (pixelvalue)((profile == 2 ? 11 : 12) + x + 2 + 2*(y + 1)));
        equal_float(qc->frame_mean_average, avg); equal_float(qc->frame_mean_sigma, sig);
        equal_float(qc->rejection_low, low); equal_float(qc->rejection_high, high);
        equal_float(qc->product_median, med); equal_float(qc->product_stdev, stdev);
        assert(qc->accepted_frames == nplanes && qc->input_frames == (size_t)count);
        assert(memcmp(qc->scan_median, scan_median, (size_t)count * sizeof(float)) == 0);
        assert(memcmp(qc->scan_stdev, scan_stdev, (size_t)count * sizeof(float)) == 0);
        for (i = 0; i < count; ++i) {
            double mean;
            mean = profile == 2 && i == count - 1 ? 10 + i + 4.5 + 5 + 100 :
                10 + (profile == 3 ? 0 : i) + 4.5 + 5;
            assert(qc->accepted[i] == (mean > low && mean < high));
        }
        assert(!strcmp(mef_request_view(mef_bias_result_request(result))->inputs[0].asset_record_id, "asset:0"));
    } else expect_failure(context, &input, MEF_ERR_COMPUTATION);
    mef_bias_result_destroy(result); mef_context_destroy(context); image_del(expected);
    for (i = 0; i < count; ++i) {
        assert(memcmp(frames[i]->data, saved[i], sizeof(saved[i])) == 0);
        image_del(frames[i]);
    }
    /* Test-owned automatic arrays must never reach the legacy destructor. */
    legacy->bias_frame_name = NULL; legacy->bias_nframes = 0;
    legacy->bias_scan_median = NULL; legacy->bias_scan_stdev = NULL;
    legacy->bias_avg1 = NULL; legacy->bias_sig1 = NULL;
    legacy->bias_framethr_lo = NULL; legacy->bias_framethr_hi = NULL;
    legacy->bias_median = NULL; legacy->bias_stdev = NULL; legacy->bias_nplanes = NULL;
    printf("PASS: profile %d exact legacy pixels/QC and input/result lifetimes\n", profile);
}

static void controls(mef_bb *legacy, int detector_index)
{
    mef_context *context;
    mef_bias_input input;
    image_t *frames[3];
    const image_t *borrowed[3];
    mef_allocator allocator;
    allocation_state state;
    mef_bias_result *result;
    mef_error *error;
    size_t base, calls, failure;
    int i, j, mode, persistent;
    legacy->bias_minframe = 3; legacy->bias_kappa1 = 10.0;
    for (i = 0; i < 3; ++i) {
        frames[i] = image_new(10, 6); borrowed[i] = frames[i];
        for (j = 0; j < 60; ++j) frames[i]->data[j] =
            (pixelvalue)(100 + ((j % 10 >= 2 && j % 10 <= 7) ? 10 + i + j / 10 : 0));
    }
    input.frames = borrowed; input.count = 3; input.configuration_detector = (size_t)detector_index;
    expect_failure(NULL, &input, MEF_ERR_INPUT);
    for (mode = 1; mode <= 4; ++mode) {
        if (mode == 3) continue; /* Primary-image numerical equality is checked by M4. */
        context = context_for(legacy, 3, mode, NULL);
        expect_failure(context, &input, mode == 4 ? MEF_ERR_INPUT : MEF_ERR_UNSUPPORTED);
        mef_context_destroy(context);
    }
    context = context_for(legacy, 3, 0, NULL);
    input.configuration_detector = (size_t)legacy->nchips;
    expect_failure(context, &input, MEF_ERR_CONFIG);
    input.configuration_detector = (size_t)detector_index;
    input.count = 2; expect_failure(context, &input, MEF_ERR_INPUT); input.count = 3;
    frames[1]->lx = 9; expect_failure(context, &input, MEF_ERR_INPUT); frames[1]->lx = 10;
    frames[0]->data[0] = (pixelvalue)HUGE_VAL;
    expect_failure(context, &input, MEF_ERR_INPUT); frames[0]->data[0] = 100;
    mef_context_destroy(context);
    legacy->ccd[detector_index].trimreg[1] = 11;
    context = context_for(legacy, 3, 0, NULL);
    expect_failure(context, &input, MEF_ERR_CONFIG); mef_context_destroy(context);
    legacy->ccd[detector_index].trimreg[1] = 8;
    state.calls = state.fail_at = state.owners = 0; state.persistent = 0;
    allocator.user = &state; allocator.allocate = allocate; allocator.release = release;
    context = context_for(legacy, 3, 0, &allocator);
    base = state.owners;
    state.calls = 0; result = NULL;
    assert(mef_cal_bias(context, &input, &result, NULL) == MEF_OK);
    calls = state.calls; mef_bias_result_destroy(result); assert(state.owners == base);
    for (persistent = 0; persistent <= 1; ++persistent) for (failure = 1; failure <= calls; ++failure) {
        state.calls = 0; state.fail_at = failure; state.persistent = persistent;
        result = NULL; error = NULL;
        assert(mef_cal_bias(context, &input, &result, &error) == MEF_ERR_MEMORY);
        assert(result == NULL);
        if (error != NULL) assert(mef_error_status(error) == MEF_ERR_MEMORY);
        mef_error_destroy(error); assert(state.owners == base);
    }
    state.fail_at = 0;
    for (i = 0; i < 20; ++i) {
        result = NULL; assert(mef_cal_bias(context, &input, &result, NULL) == MEF_OK);
        mef_bias_result_destroy(result); assert(state.owners == base);
    }
    mef_context_destroy(context); assert(state.owners == 0);
    for (i = 0; i < 3; ++i) image_del(frames[i]);
    printf("PASS: input/selection/geometry controls; %lu allocation positions x 2; 20 cycles; zero new owners\n", (unsigned long)calls);
}

static void measurements(mef_bb *legacy, int detector_index)
{
    image_t *frames[5];
    const image_t *borrowed[5];
    mef_bias_input input;
    mef_bias_result *result;
    const mef_bias_measurements *qc;
    mef_bias_measurement_options options;
    mef_context *context;
    pixelmap *map;
    pixelvalue saved[5][60];
    double sum, squares, expected, corrected_mean;
    int i, x, y, mode;
    allocation_state state;
    mef_allocator allocator;
    size_t base, calls, failure;
    /* Deliberate row-dependent raw pedestal: correction removes it, whereas
     * the required raw-pair difference must retain it. Add scan outliers and active
     * defects: detector BPM affects active measurements/rejection only. */
    legacy->bias_minframe=3; legacy->bias_kappa1=1.5;
    legacy->use_prescan=legacy->use_overscan=1;
    legacy->scanrej[0]=legacy->scanrej[1]=0;
    map=pixelmap_new(10,6); assert(map);
    for(y=0;y<6;++y) { map->data[10*y]=0; map->data[10*y+2]=0; }
    for(i=0;i<5;++i) {
        frames[i]=image_new(10,6); assert(frames[i]); borrowed[i]=frames[i];
        for(y=0;y<6;++y) for(x=0;x<10;++x) {
            frames[i]->data[10*y+x]=(pixelvalue)(100+i*(y+1));
            if(x>=2 && x<=7) frames[i]->data[10*y+x]+=(pixelvalue)(10+i+x+2*y);
        }
        for(y=0;y<6;++y) {
            frames[i]->data[10*y]+=10000;
            frames[i]->data[10*y+2]+=1000;
            if(i==4) frames[i]->data[10*y+2]+=10000;
        }
        memcpy(saved[i],frames[i]->data,sizeof(saved[i]));
    }
    input.frames=borrowed; input.count=5; input.configuration_detector=(size_t)detector_index;
    memset(&options,0,sizeof(options)); options.bpm=map; options.with_mad=1;
    options.ron_pair_set=1; options.ron_first=0; options.ron_second=1; options.high_sigma=5;
    context=context_for(legacy,5,1,NULL); result=NULL;
    assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_OK);
    qc=mef_bias_result_measurements(result); assert(qc && qc->count==5);
    assert(qc->frames[0].active_raw.valid_pixels==20 && qc->frames[0].active_raw.bpm_excluded==4);
    assert(qc->frames[0].prescan.bpm_excluded==0 && !qc->frames[0].prescan.bpm_supplied);
    assert(qc->frames[0].prescan.valid_pixels==8 && !qc->frames[0].overscan.bpm_supplied);
    /* Raw differences per active row are -3,-4,-5,-6 (five good columns each).
     * Independent sample variance: sum= -90, squares=430, N=20. */
    sum=-90; squares=430; expected=sqrt((squares-sum*sum/20)/19)/sqrt(2.0);
    assert(fabs(qc->ron_stdev_adu-expected)<1e-10);
    assert(fabs(qc->ron_mad_adu-1.4826/sqrt(2.0))<1e-10);
    assert(qc->raw_difference.bpm_excluded==4 && qc->ron_stdev_available);
    assert(qc->master.valid_pixels==20 && qc->master_unmasked.valid_pixels==24);
    assert(mef_bias_result_qc(result)->accepted_frames==5);
    assert(qc->high_offset_available && qc->high_offset_count==4 && qc->high_offset_flags->data[0]==1);
    corrected_mean=qc->frames[4].active_corrected.mean;
    assert(fabs(corrected_mean-(24-2500))<1e-10);
    assert(qc->frames[4].active_raw.mean>corrected_mean+100);
    mef_context_destroy(context); context=NULL; /* Result owns QC, not borrowed data. */
    assert(qc->frames[4].active_corrected.mean==corrected_mean);
    mef_bias_result_destroy(result);
    /* Result allocator failure at every observed new-service allocation: no
     * partial owner and no leak, including the owned per-frame QC allocation. */
    memset(&state,0,sizeof(state));
    allocator.user=&state; allocator.allocate=allocate; allocator.release=release;
    context=context_for(legacy,5,1,&allocator); base=state.owners;
    state.calls=0; result=NULL;
    assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_OK);
    calls=state.calls; mef_bias_result_destroy(result); assert(state.owners==base);
    for(failure=1;failure<=calls;++failure) {
        state.calls=0; state.fail_at=failure; result=NULL;
        assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_ERR_MEMORY);
        assert(result==NULL && state.owners==base);
    }
    state.fail_at=0; mef_context_destroy(context); assert(state.owners==0);
    /* Omitted BPM path still works, and the unmasked scan outlier remains
     * observable; optional MAD/pair are explicitly unavailable. */
    options.bpm=NULL; options.with_mad=0; options.ron_pair_set=0;
    context=context_for(legacy,5,0,NULL); result=NULL;
    assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)==MEF_OK);
    qc=mef_bias_result_measurements(result);
    assert(!qc->ron_stdev_available && !qc->master.mad_available && !qc->high_offset_available);
    assert(fabs(qc->frames[4].active_corrected.mean-(23.5+11000.0/6-2500))<1e-4);
    assert(mef_bias_result_qc(result)->accepted_frames==4 && !mef_bias_result_qc(result)->accepted[4]);
    mef_bias_result_destroy(result); mef_context_destroy(context);
    /* Reject contradictory metadata, malformed geometry, exhausted active samples,
     * and aliased/out-of-range raw-pair selections without transferring output. */
    options.bpm=map; options.with_mad=1; options.ron_pair_set=1;
    for(mode=0;mode<5;++mode) {
        context=context_for(legacy,5,mode==0?0:1,NULL); result=NULL;
        if(mode==1) options.ron_second=0;
        if(mode==2) options.ron_second=5;
        if(mode==3) { options.ron_second=1; map->lx=9; }
        if(mode==4) { map->lx=10; for(x=0;x<60;++x) map->data[x]=0; }
        assert(mef_cal_bias_measurements(context,&input,&options,&result,NULL)!=MEF_OK && !result);
        mef_context_destroy(context);
    }
    for(i=0;i<5;++i) {
        assert(!memcmp(saved[i],frames[i]->data,sizeof(saved[i]))); image_del(frames[i]);
    }
    pixelmap_del(map);
    puts("PASS: opt-in bias active-only BPM/rejection/stage QC, raw RON, MAD, lifetimes, metadata and failure controls");
}
int main(int argc, char **argv)
{
    mef_bb *legacy;
    int detector_index, profile;
    assert(argc == 3);
    fixture_directory = argv[2];
    legacy = mef_bb_new_from_paf(argv[1]); assert(legacy != NULL);
    detector_index = legacy->nchips - 1; /* Deliberately differs from physical HDU 2. */
    for (profile = 0; profile < 8; ++profile) equivalence(legacy, detector_index, profile);
    controls(legacy, detector_index);
    measurements(legacy, detector_index);
    mef_bias_result_destroy(NULL); mef_bb_del(legacy);
    puts("PASS: bias service contract; legacy-compatible ADU signal, variance unavailable");
    return 0;
}
