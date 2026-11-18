#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

#include "mefp_lib.h"

static cube_t *flat_exposures(const image_t *bias)
{
    const int illumination[] = {20, 2, 40, 80};
    const int response[] = {1, 2, 3};
    cube_t *cube = cube_new(bias->lx, bias->ly, 4);
    assert(cube != NULL);
    for (int frame = 0; frame < cube->np; ++frame) {
        image_t *plane = image_new(cube->lx, cube->ly);
        assert(plane != NULL);
        cube->plane[frame] = plane;
        for (int pixel = 0; pixel < cube->lx; ++pixel)
            plane->data[pixel] = bias->data[pixel] + illumination[frame] * response[pixel];
    }
    return cube;
}

static void check_combination(void)
{
    const pixelvalue dome_pixels[] = {1, 2, 3, 1, 2, 3, 1, 2, 3};
    const pixelvalue sky_pixels[] = {2, 8, 18, 2, 8, 18, 2, 8, 18};
    const pixelvalue expected[] = {3, 8, 15, 3, 8, 15, 3, 8, 15};
    const pixelvalue masked_expected[] = {2, 8, 18, 2, 8, 18, 2, 8, 18};
    image_t *dome = image_new(3, 3);
    image_t *sky = image_new(3, 3);
    pixelmap *mask = pixelmap_new(3, 3);
    assert(dome != NULL && sky != NULL && mask != NULL);
    memcpy(dome->data, dome_pixels, sizeof(dome_pixels));
    memcpy(sky->data, sky_pixels, sizeof(sky_pixels));
    for (int i = 0; i < 9; ++i)
        mask->data[i] = (i % 3 == 1) ? PIXELMAP_0 : PIXELMAP_1;

    image_t *combined = mef_flat_combine(dome, sky, 1, NULL);
    assert(combined != NULL && memcmp(combined->data, expected, sizeof(expected)) == 0);
    image_del(combined);

    combined = mef_flat_combine(dome, sky, 1, mask);
    assert(combined != NULL &&
           memcmp(combined->data, masked_expected, sizeof(masked_expected)) == 0);
    image_del(combined);

    assert(mef_flat_combine(dome, sky, 0, mask) == NULL);
    assert(memcmp(dome->data, dome_pixels, sizeof(dome_pixels)) == 0);
    assert(memcmp(sky->data, sky_pixels, sizeof(sky_pixels)) == 0);
    pixelmap_del(mask);
    image_del(sky);
    image_del(dome);
}

static void check_bias_before_normalization(const char *kind)
{
    mef_bb settings = {0};
    mef_ccd detector = {.gain = 1.0f, .ron = 100.0f};
    float mean_normalization = 0.0f, stdev = 0.0f;
    int normalized = 0;
    int participation[4];
    const int expected_participation[] = {1, 0, 1, 1};
    double means[4], medians[4], sigmas[4], normalization[4];

    settings.xtnum = 1;
    settings.nxts = 1;
    settings.ccd = &detector;
    settings.dome_minframe = 3;
    settings.dome_framethr_lo = 10;
    settings.dome_framethr_hi = 200;
    settings.dome_median = &mean_normalization;
    settings.dome_stdev = &stdev;
    settings.dome_nplanes = &normalized;
    settings.sky_minframe = 3;
    settings.sky_framethr_lo = 10;
    settings.sky_framethr_hi = 200;
    settings.sky_median = &mean_normalization;
    settings.sky_stdev = &stdev;
    settings.sky_nplanes = &normalized;
    settings.pixrej_lo = 3;
    settings.pixrej_hi = 3;
    settings.median_reg[1] = 2;
    settings.median_surf = 3;
    settings.individual_frame_avg = means;
    settings.individual_frame_median = medians;
    settings.individual_frame_sigma = sigmas;

    image_t *bias = image_new(3, 1);
    assert(bias != NULL);
    bias->data[0] = 20;
    bias->data[1] = 4;
    bias->data[2] = 12;

    /* After subtraction each row is L × [1, 2, 3] with median and mean 2L.
       The L=2 exposure then fails the lower bound. The admitted rows all
       normalize to [0.5, 1, 1.5], which is also their pixelwise median. */
    image_t *flat = mef_stack_flat_diagnostic(&settings, kind, flat_exposures(bias),
        bias, normalization, participation);
    assert(flat != NULL);
    assert(memcmp(participation, expected_participation, sizeof(participation)) == 0);
    assert(normalization[0] == 40 && isnan(normalization[1]));
    assert(normalization[2] == 80 && normalization[3] == 160);
    assert(normalized == 3 && mean_normalization == 280.0f / 3.0f);
    assert(flat->data[0] == 0.5 && flat->data[1] == 1.0 && flat->data[2] == 1.5);
    image_del(flat);

    /* Use the same stack with correction disabled and a fixed three-frame sample. */
    settings.dome_framethr_lo = 30;
    settings.sky_framethr_lo = 30;
    flat = mef_stack_flat_diagnostic(&settings, kind, flat_exposures(bias),
        NULL, normalization, participation);
    assert(flat != NULL);
    assert(memcmp(participation, expected_participation, sizeof(participation)) == 0);
    assert(normalization[0] == 44 && isnan(normalization[1]));
    assert(normalization[2] == 84 && normalization[3] == 164);
    assert(normalized == 3 && mean_normalization == 292.0f / 3.0f);
    assert(flat->data[0] == (pixelvalue)(60.0 / 84.0));
    assert(flat->data[1] == 1.0);
    assert(flat->data[2] == (pixelvalue)(132.0 / 84.0));
    image_del(flat);

    assert(bias->data[0] == 20 && bias->data[1] == 4 && bias->data[2] == 12);
    image_del(bias);
    printf("PASS: %s bias before admission and normalization, exact stack and input preservation\n",
        kind);
}

int main(void)
{
    check_bias_before_normalization("dome");
    check_bias_before_normalization("sky");
    check_combination();
    puts("PASS: ratio smoothing, BPM and unsmoothed component preservation");
    return 0;
}
