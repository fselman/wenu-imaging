/* S2-04 (#75): observe the unchanged CLI entry point in one process per case.
 * Only recipe references to the constructor/destructor are redirected. The
 * real common-library functions, including partial-construction cleanup, run
 * unchanged. No observation callback allocates through qfits. */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/resource.h>
#include <sys/stat.h>
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

/* Observe descriptor identity as well as count, excluding no open descriptor.
 * The scan uses no extra descriptor and no qfits allocation. */
static int descriptors(unsigned long *identity)
{
    struct rlimit limit;
    struct stat info;
    int fd, flags, count;
    unsigned long value;
    if (getrlimit(RLIMIT_NOFILE, &limit) != 0 ||
        limit.rlim_cur == RLIM_INFINITY || limit.rlim_cur > 1048576) return -1;
    count = 0;
    value = 0;
    for (fd = 0; fd < (int)limit.rlim_cur; fd++) {
        errno = 0;
        flags = fcntl(fd, F_GETFD);
        if (flags < 0) {
            if (errno == EBADF) continue;
            return -1;
        }
        if (fstat(fd, &info) != 0) return -1;
        count++;
        value = value * 33UL + (unsigned long)fd;
        value = value * 33UL + (unsigned long)flags;
        value = value * 33UL + (unsigned long)info.st_dev;
        value = value * 33UL + (unsigned long)info.st_ino;
        value = value * 33UL + (unsigned long)info.st_mode;
    }
    *identity = value;
    return count;
}

int main(int argc, char **argv)
{
    int status, before, after, restricted;
    unsigned long before_identity, after_identity;
    struct rlimit original_limit, limited;
    void (*original_signal)(int);
    original_signal = SIG_DFL;
    before = descriptors(&before_identity);
    if (before < 0) return 2;
    restricted = getenv("S2_SPLIT_WRITE_LIMIT") != NULL;
    if (restricted) {
        if (getrlimit(RLIMIT_FSIZE, &original_limit) != 0) return 2;
        limited = original_limit;
        limited.rlim_cur = 4096;
        if (setrlimit(RLIMIT_FSIZE, &limited) != 0) return 2;
        original_signal = signal(SIGXFSZ, SIG_IGN);
        if (original_signal == SIG_ERR) return 2;
    }
    account("process-start");
    status = observed_cli_main(argc, argv);
    /* Restore the soft limit before exit-time external leak observation. */
    if (restricted) {
        if (setrlimit(RLIMIT_FSIZE, &original_limit) != 0) return 2;
        if (signal(SIGXFSZ, original_signal) == SIG_ERR) return 2;
    }
    account("after-cli");
    after = descriptors(&after_identity);
    if (after < 0) return 2;
    printf("DESCRIPTORS before=%d after=%d identity_equal=%d\n",
           before, after, before_identity == after_identity);
    printf("CLI RESULT native_exit=%d constructed=%d destroyed=%d mismatch=%d owner_live=%d\n",
           status, constructed, destroyed, mismatch, observed_owner != NULL);
    fflush(stdout);
    return 0;
}
