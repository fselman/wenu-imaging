
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mefp_lib.h"
#include "xmemory.h"

int main(int argc, char **argv)
{
    mef_bb *bb;
    pixelmap *mask;
    eclipse_init();
    bb = mef_bb_new_from_paf("mefpp.paf");
    if (bb == NULL) return 2;
    if (bb->name_bpm != NULL) free(bb->name_bpm);
    bb->name_bpm = strdup("frames.list");
    bb->bpm_proportional_flag = (argc == 2) ? atoi(argv[1]) : 1;
    bb->bpm_gainthr_lo = 0.5;
    bb->bpm_gainthr_hi = 1.5;
    bb->xtnum = 1;
    bb->nxts = 1;
    bb->use_prescan = 0;
    bb->use_overscan = 1;
    bb->scanrej[0] = bb->scanrej[1] = 0;
    bb->ccd[0].prescan_x[0] = bb->ccd[0].prescan_x[1] = 1;
    bb->ccd[0].overscan_x[0] = 10;
    bb->ccd[0].overscan_x[1] = 18;
    bb->ccd[0].trimreg[0] = bb->ccd[0].trimreg[2] = 1;
    bb->ccd[0].trimreg[1] = bb->ccd[0].trimreg[3] = 9;
    fprintf(stderr, "ENTER production mef_build_bpm proportional\n");
    fflush(stderr);
    mask = mef_build_bpm(bb, NULL);
    if (mask == NULL) return 3;
    if (mask->lx != 9 || mask->ly != 9) return 5;
    pixelmap_dump(mask, "returned.fits", NULL);
    printf("PASS: returned 9x9 mask good=%d\n", mask->ngoodpix);
    pixelmap_del(mask);
    mef_bb_del(bb);
    return 0;
}
