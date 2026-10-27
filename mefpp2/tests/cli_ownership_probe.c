/* S2-03 (#75): observe the unchanged CLI entry point in one process per case.
 * Only recipe references to the constructor/destructor are redirected. The
 * real common-library functions, including partial-construction cleanup, run
 * unchanged. No observation callback allocates through qfits. */
#include <stdio.h>
#include "mefp_lib.h"
#include "xmemory.h"

static mef_bb *observed_owner;
static int constructed, destroyed, mismatch;
static mef_bb *observe_new(char *name);
static void observe_del(mef_bb *context);

#define main observed_cli_main
#define mef_bb_new_from_paf observe_new
#define mef_bb_del observe_del
#include "../ins/mef/recipes/mefpp.c"
#undef main
#undef mef_bb_new_from_paf
#undef mef_bb_del

static mef_bb *observe_new(char *name)
{
    mef_bb *context;
    context = mef_bb_new_from_paf(name);
    if (context != NULL) {
        if (observed_owner != NULL) mismatch++;
        observed_owner = context;
        constructed++;
    }
    return context;
}

static void observe_del(mef_bb *context)
{
    if (context == NULL || context != observed_owner) mismatch++;
    destroyed++;
    observed_owner = NULL;
    mef_bb_del(context);
}

static void account(const char *label)
{
    fprintf(stderr, "ACCOUNTING BEGIN %s\n", label);
    xmemory_status();
    fprintf(stderr, "ACCOUNTING END %s\n", label);
    fflush(stderr);
}

int main(int argc, char **argv)
{
    int status;
    account("process-start");
    status = observed_cli_main(argc, argv);
    account("after-cli");
    printf("CLI RESULT native_exit=%d constructed=%d destroyed=%d mismatch=%d owner_live=%d\n",
           status, constructed, destroyed, mismatch, observed_owner != NULL);
    fflush(stdout);
    /* Separate the leaks launcher's status from an expected CLI rejection.
     * The runner checks native_exit against an independent ordinary CLI run. */
    return 0;
}
