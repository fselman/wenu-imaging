
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mefp_lib.h"

int main(int argc, char **argv)
{
    mef_bb bb;
    mef_ccd ccd[4];
    float medians[4], deviations[4];
    float scan_medians[3], scan_deviations[3];
    double averages[3], frame_medians[3], frame_sigmas[3];
    int planes[4], detector, i, order;
    double responses[2][4] = {
        {1.0, 2.0, 4.0, 0.5},
        {4.0, 1.0, 0.5, 2.0}
    };
    double expected, feature;
    image_t *flat;
    char *names[3] = {
        "frame0.fits", "frame1.fits", "frame2.fits"
    };

    if (argc != 3) return 2;
    order = atoi(argv[2]);
    if (order < 0 || order > 1) return 2;
    if (strcmp(argv[1], "dome") && strcmp(argv[1], "sky"))
        return 2;

    memset(&bb, 0, sizeof(bb));
    memset(ccd, 0, sizeof(ccd));
    memset(medians, 0, sizeof(medians));
    memset(deviations, 0, sizeof(deviations));
    memset(planes, 0, sizeof(planes));

    /* Configure a bounded four-detector production context. */
    bb.ccd = ccd;
    bb.nchips = bb.nxts = 4;
    bb.use_overscan = 1;
    bb.median_reg[0] = bb.median_reg[2] = 0;
    bb.median_reg[1] = bb.median_reg[3] = 8;
    bb.median_surf = 81;
    bb.pixrej_lo = bb.pixrej_hi = 1000.0;
    bb.name_dome = bb.name_sky = "frames.list";
    bb.dome_framethr_lo = bb.sky_framethr_lo = 1.0;
    bb.dome_framethr_hi = bb.sky_framethr_hi = 1000000.0;
    bb.dome_minframe = bb.sky_minframe = 3;
    bb.dome_median = bb.sky_median = medians;
    bb.dome_stdev = bb.sky_stdev = deviations;
    bb.dome_nplanes = bb.sky_nplanes = planes;
    bb.dome_scan_median = bb.sky_scan_median = scan_medians;
    bb.dome_scan_stdev = bb.sky_scan_stdev = scan_deviations;
    bb.dome_frame_name = bb.sky_frame_name = names;
    bb.dome_nframes = bb.sky_nframes = 3;
    bb.individual_frame_avg = averages;
    bb.individual_frame_median = frame_medians;
    bb.individual_frame_sigma = frame_sigmas;

    for (detector = 0; detector < 4; detector++) {
        ccd[detector].gain = 1.0;
        ccd[detector].ron = 1.0;
        ccd[detector].prescan_x[0] = 1;
        ccd[detector].prescan_x[1] = 1;
        ccd[detector].overscan_x[0] = 10;
        ccd[detector].overscan_x[1] = 18;
        ccd[detector].trimreg[0] = 1;
        ccd[detector].trimreg[1] = 9;
        ccd[detector].trimreg[2] = 1;
        ccd[detector].trimreg[3] = 9;
    }

    eclipse_init();

    /* Exercise the real constructor and check every returned pixel. */
    for (detector = 0; detector < 4; detector++) {
        bb.xtnum = detector + 1;
        flat = mef_build_cal(&bb, argv[1]);
        if (flat == NULL) return 3;
        if (flat->lx != 9 || flat->ly != 9 ||
            planes[detector] != 3) {
            image_del(flat);
            return 4;
        }

        expected = responses[order][detector] / responses[order][0];
        for (i = 0; i < 81; i++) {
            feature = (i == 40) ? 2.0 : 1.0;
            if ((double)flat->data[i] != expected * feature) {
                fprintf(stderr,
                    "FAIL detector=%d pixel=%d actual=%.17g expected=%.17g\n",
                    detector + 1, i,
                    (double)flat->data[i], expected * feature);
                image_del(flat);
                return 5;
            }
        }
        printf(
            "PASS: %s order=%d detector=%d response=%.8g center=%.8g\n",
            argv[1], order, detector + 1,
            expected, expected * 2.0);
        image_del(flat);
    }
    return 0;
}
