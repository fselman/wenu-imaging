/* S2-05 (#75): retain the accepted #90 fixture driver unchanged. Wrappers
 * observe its returned context/mask and forward every operation to production.
 * No production cleanup policy is changed by these diagnostic boundaries. */
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <dirent.h>
#include <limits.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include "mefp_lib.h"
#include "xmemory.h"
#include "qfits.h"

static mef_bb *owner;
static pixelmap *returned_mask;
static int constructed, destroyed, builds, masks_released, mismatch;
static void account(const char *label);
static mef_bb *observe_new(char *name);
static void observe_del(mef_bb *context);
static pixelmap *observe_build(mef_bb *context, image_t *bias);
static void observe_mask_del(pixelmap *mask);

#define main retained_bpm_main
#define mef_bb_new_from_paf observe_new
#define mef_bb_del observe_del
#define mef_build_bpm observe_build
#define pixelmap_del observe_mask_del
#include "fixtures/bpm-cleanup/bpm_cleanup_probe.c"
#undef main
#undef mef_bb_new_from_paf
#undef mef_bb_del
#undef mef_build_bpm
#undef pixelmap_del

static void account(const char *label)
{
    fprintf(stderr, "ACCOUNTING BEGIN %s\n", label);
    xmemory_status();
    fprintf(stderr, "ACCOUNTING END %s\n", label);
    fflush(stderr);
}

static mef_bb *observe_new(char *name)
{
    mef_bb *context;
    context = mef_bb_new_from_paf(name);
    if (context != NULL) {
        if (owner != NULL) mismatch++;
        owner = context;
        constructed++;
    }
    account("after-context");
    return context;
}

static pixelmap *observe_build(mef_bb *context, image_t *bias)
{
    if (context != owner || returned_mask != NULL) mismatch++;
    account("before-build");
    builds++;
    returned_mask = mef_build_bpm(context, bias);
    account("after-build");
    return returned_mask;
}

static void observe_mask_del(pixelmap *mask)
{
    if (mask == NULL || mask != returned_mask) mismatch++;
    pixelmap_del(mask);
    returned_mask = NULL;
    masks_released++;
    account("after-mask-release");
}

static void observe_del(mef_bb *context)
{
    if (context == NULL || context != owner) mismatch++;
    mef_bb_del(context);
    owner = NULL;
    destroyed++;
    account("after-context-release");
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
    int status, before, after;
    unsigned long first_identity, last_identity;
    descriptor_limit("before");
    before = descriptors(&first_identity);
    if (before < 0) return 2;
    account("process-start");
    status = retained_bpm_main(argc, argv);
    account("after-driver");
    printf("BPM RESULT native_exit=%d constructed=%d destroyed=%d builds=%d masks_released=%d mismatch=%d owner_live=%d mask_live=%d\n",
           status, constructed, destroyed, builds, masks_released, mismatch,
           owner != NULL, returned_mask != NULL);
    descriptor_limit("after");
    after = descriptors(&last_identity);
    printf("DESCRIPTORS before=%d after=%d identity_equal=%d\n",
           before, after, after >= 0 && first_identity == last_identity);
    qfits_cache_purge();
    account("after-purge");
    after = descriptors(&last_identity);
    printf("CACHE DESCRIPTORS after-purge before=%d after=%d identity_equal=%d\n",
           before, after, after >= 0 && first_identity == last_identity);
    qfits_cache_purge();
    account("after-second-purge");
    after = descriptors(&last_identity);
    printf("CACHE DESCRIPTORS after-second-purge before=%d after=%d identity_equal=%d\n",
           before, after, after >= 0 && first_identity == last_identity);
    fflush(stdout);
    return 0;
}
