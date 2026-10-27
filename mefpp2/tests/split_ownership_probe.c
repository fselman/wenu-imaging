/* S2-04 (#75): observe the unchanged CLI entry point in one process per case.
 * Only recipe references to the constructor/destructor are redirected. The
 * real common-library functions, including partial-construction cleanup, run
 * unchanged. No observation callback allocates through qfits. */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <dirent.h>
#include <limits.h>
#include <signal.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include "mefp_lib.h"
#include "xmemory.h"
#include "qfits.h"

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

/* Enumerate open descriptors independently of the soft limit: the production
 * allocator raises that limit on first use (#106). Exclude only this scan's
 * temporary directory descriptor; close it before returning. */
static int descriptors(unsigned long *identity)
{
    DIR *directory;
    struct dirent *item;
    struct stat info;
    const char *location;
    char *end;
    long number;
    int fd, flags, count, scan_fd, failed;
    unsigned long value, cell;
#if defined(__APPLE__)
    location = "/dev/fd";
#elif defined(__linux__)
    location = "/proc/self/fd";
#else
    fprintf(stderr, "DESCRIPTORS ERROR unsupported platform\n");
    return -1;
#endif
    directory = opendir(location);
    if (directory == NULL) {
        fprintf(stderr, "DESCRIPTORS ERROR opendir errno=%d\n", errno);
        return -1;
    }
    scan_fd = dirfd(directory);
    failed = scan_fd < 0;
    count = 0;
    value = 0;
    while (!failed) {
        errno = 0;
        item = readdir(directory);
        if (item == NULL) {
            failed = errno != 0;
            break;
        }
        number = strtol(item->d_name, &end, 10);
        if (end == item->d_name || *end != '\0') continue;
        if (errno == ERANGE || number < 0 || number > INT_MAX) {
            failed = 1;
            break;
        }
        fd = (int)number;
        if (fd == scan_fd) continue;
        flags = fcntl(fd, F_GETFD);
        if (flags < 0 || fstat(fd, &info) != 0) {
            fprintf(stderr, "DESCRIPTORS ERROR inspect fd=%d errno=%d\n", fd, errno);
            failed = 1;
            break;
        }
        count++;
        cell = (unsigned long)fd;
        cell = cell * 33UL + (unsigned long)flags;
        cell = cell * 33UL + (unsigned long)info.st_dev;
        cell = cell * 33UL + (unsigned long)info.st_ino;
        cell = cell * 33UL + (unsigned long)info.st_mode;
        value += cell; /* Enumeration order is not an ownership property. */
    }
    if (closedir(directory) != 0) failed = 1;
    if (failed) {
        fprintf(stderr, "DESCRIPTORS ERROR incomplete enumeration\n");
        return -1;
    }
    *identity = value;
    return count;
}

static void descriptor_limit(const char *phase)
{
    struct rlimit limit;
    if (getrlimit(RLIMIT_NOFILE, &limit) == 0)
        printf("DESCRIPTOR LIMIT %s soft=%lu hard=%lu soft_unlimited=%d\n",
               phase, (unsigned long)limit.rlim_cur, (unsigned long)limit.rlim_max,
               limit.rlim_cur == RLIM_INFINITY);
    else
        fprintf(stderr, "DESCRIPTOR LIMIT ERROR %s errno=%d\n", phase, errno);
}

int main(int argc, char **argv)
{
    int status, before, after, restricted;
    unsigned long before_identity, after_identity;
    struct rlimit original_limit, limited;
    void (*original_signal)(int);
    original_signal = SIG_DFL;
    descriptor_limit("before");
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
    /* Report the native result even if a resource observation cannot complete. */
    printf("CLI RESULT native_exit=%d constructed=%d destroyed=%d mismatch=%d owner_live=%d\n",
           status, constructed, destroyed, mismatch, observed_owner != NULL);
    fflush(stdout);
    descriptor_limit("after");
    after = descriptors(&after_identity);
    printf("DESCRIPTORS before=%d after=%d identity_equal=%d\n",
           before, after, after >= 0 && before_identity == after_identity);
    fflush(stdout);
    if (after < 0) return 2;
    if (getenv("S2_SPLIT_CACHE_CONTROL") != NULL) {
        /* Diagnostic intervention only: keep the original after-cli state.
         * Repeat the public purge to test its empty-cache behavior as well. */
        qfits_cache_purge();
        account("after-purge");
        after = descriptors(&after_identity);
        printf("CACHE DESCRIPTORS after-purge before=%d after=%d identity_equal=%d\n",
               before, after, after >= 0 && before_identity == after_identity);
        if (after < 0) return 2;
        qfits_cache_purge();
        account("after-second-purge");
        after = descriptors(&after_identity);
        printf("CACHE DESCRIPTORS after-second-purge before=%d after=%d identity_equal=%d\n",
               before, after, after >= 0 && before_identity == after_identity);
        fflush(stdout);
        if (after < 0) return 2;
    }
    return 0;
}
