/* S2-02 baseline: call unchanged production context constructor/destructor. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "mefp_lib.h"
#include "xmemory.h"

static void account(const char *label)
{
    fprintf(stderr, "ACCOUNTING BEGIN %s\n", label);
    xmemory_status();
    fprintf(stderr, "ACCOUNTING END %s\n", label);
    fflush(stderr);
}

int main(int argc, char **argv)
{
    mef_bb *context;
    int expected_chips, repeats, i, created, chips, mismatch;
    char boundary[32];
    if (argc != 4) return 2;
    expected_chips = atoi(argv[2]);
    repeats = atoi(argv[3]);
    if ((expected_chips != 0 && expected_chips != 8 && expected_chips != 32) ||
        repeats < 1 || repeats > 3) return 2;
    account("process-start");
    eclipse_init();
    account("baseline");
    for (i = 1; i <= repeats; i++) {
        context = mef_bb_new_from_paf(argv[1]);
        created = context != NULL;
        chips = created ? context->nchips : 0;
        mismatch = expected_chips ? (!created || chips != expected_chips) : created;
        printf("CONTEXT RESULT iteration=%d created=%d chips=%d\n", i, created, chips);
        if (created) {
            printf("CONFIG iteration=%d chips=%d proportional=%d lo=%.17g hi=%.17g instrument=%s\n",
                   i, chips, context->bpm_proportional_flag,
                   (double)context->bpm_gainthr_lo, (double)context->bpm_gainthr_hi,
                   context->instrument ? context->instrument : "(null)");
            mef_bb_del(context);
            context = NULL;
        }
        sprintf(boundary, "after-%d", i);
        account(boundary);
        fflush(stdout);
        if (mismatch) return 3;
    }
    account("final");
    printf("CONTEXT COMPLETE repeats=%d\n", repeats);
    fflush(stdout);
    return 0;
}
