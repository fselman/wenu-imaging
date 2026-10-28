/* Frozen F1-F5 campaign (#75/#116): observe the real recipe, no cleanup repairs.
 * Test-only POSIX harness; the production algorithm and allocator stay unchanged. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <dirent.h>
#include <limits.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>
#include "mefp_lib.h"
#include "xmemory.h"
#include "qfits.h"

static mef_bb *owner;
static void *products[32];
static int kinds[32];
static int contexts, destroyed, cal_calls, bpm_calls, combine_calls, science_loads, mismatch, checkpoint_seq;
static void account(const char *label);
static mef_bb *observe_new(char *name);
static void observe_del(mef_bb *context);
static image_t *observe_cal(mef_bb *context, char *what);
static pixelmap *observe_bpm(mef_bb *context, image_t *bias);
static image_t *observe_combine(mef_bb *context, image_t *dome, image_t *sky, image_t *bias, pixelmap *mask);
static cube_t *observe_cube_load(char *name, int xt);
static void observe_image_del(image_t *image);
static void observe_mask_del(pixelmap *mask);
static void observe_cube_del(cube_t *cube);

#define main observed_recipe_main
#define mef_bb_new_from_paf observe_new
#define mef_bb_del observe_del
#define mef_build_cal observe_cal
#define mef_build_bpm observe_bpm
#define mef_ff_combine observe_combine
#define mef_cube_load observe_cube_load
#define image_del observe_image_del
#define pixelmap_del observe_mask_del
#define cube_del observe_cube_del
#include "../ins/mef/recipes/mefpp.c"
#undef main
#undef mef_bb_new_from_paf
#undef mef_bb_del
#undef mef_build_cal
#undef mef_build_bpm
#undef mef_ff_combine
#undef mef_cube_load
#undef image_del
#undef pixelmap_del
#undef cube_del

static void account(const char *label)
{
    fprintf(stderr, "ACCOUNTING BEGIN %s\n", label);
    xmemory_status();
    fprintf(stderr, "ACCOUNTING END %s\n", label);
    fflush(stderr);
}

static int live_products(void)
{
    int i, count;
    count = 0;
    for (i = 0; i < 32; i++) if (products[i] != NULL) count++;
    return count;
}

static void remember(void *pointer, int kind)
{
    int i, slot;
    if (pointer == NULL) return;
    slot = -1;
    for (i = 0; i < 32; i++) {
        if (products[i] == pointer) mismatch++;
        if (products[i] == NULL && slot < 0) slot = i;
    }
    if (slot < 0) { mismatch++; return; }
    products[slot] = pointer;
    kinds[slot] = kind;
}

static void forget(void *pointer, int kind)
{
    int i;
    if (pointer == NULL) return;
    for (i = 0; i < 32; i++) {
        if (products[i] == pointer) {
            if (kinds[i] != kind) mismatch++;
            products[i] = NULL;
            return;
        }
    }
    mismatch++;
}

static void stage(const char *what, int xt, const char *boundary)
{
    char label[96];
    snprintf(label, sizeof(label), "%s-%d-%s-%03d", what, xt, boundary, checkpoint_seq++);
    account(label);
}

static mef_bb *observe_new(char *name)
{
    mef_bb *context;
    context = mef_bb_new_from_paf(name);
    if (context != NULL) {
        if (owner != NULL) mismatch++;
        owner = context;
        contexts++;
    }
    account("after-context");
    return context;
}

static void observe_del(mef_bb *context)
{
    if (context == NULL || context != owner) mismatch++;
    account("before-context-release");
    mef_bb_del(context);
    owner = NULL;
    destroyed++;
    account("after-context-release");
}

static image_t *observe_cal(mef_bb *context, char *what)
{
    image_t *image;
    if (context != owner) mismatch++;
    stage(what, context->xtnum, "before");
    cal_calls++;
    image = mef_build_cal(context, what);
    remember(image, 1);
    stage(what, context->xtnum, "after");
    return image;
}

static pixelmap *observe_bpm(mef_bb *context, image_t *bias)
{
    pixelmap *mask;
    if (context != owner) mismatch++;
    stage("bpm", context->xtnum, "before");
    bpm_calls++;
    mask = mef_build_bpm(context, bias);
    remember(mask, 2);
    stage("bpm", context->xtnum, "after");
    return mask;
}

static image_t *observe_combine(mef_bb *context, image_t *dome, image_t *sky, image_t *bias, pixelmap *mask)
{
    image_t *image;
    if (context != owner) mismatch++;
    stage("combined", context->xtnum, "before");
    combine_calls++;
    image = mef_ff_combine(context, dome, sky, bias, mask);
    remember(image, 1);
    stage("combined", context->xtnum, "after");
    return image;
}

static cube_t *observe_cube_load(char *name, int xt)
{
    cube_t *cube;
    stage("science-load", xt, "before");
    science_loads++;
    cube = mef_cube_load(name, xt);
    remember(cube, 3);
    stage("science-load", xt, "after");
    return cube;
}

static void observe_image_del(image_t *image)
{
    forget(image, 1);
    image_del(image);
    stage("image-release", owner == NULL ? 0 : owner->xtnum, "after");
}

static void observe_mask_del(pixelmap *mask)
{
    forget(mask, 2);
    pixelmap_del(mask);
    stage("mask-release", owner == NULL ? 0 : owner->xtnum, "after");
}

static void observe_cube_del(cube_t *cube)
{
    forget(cube, 3);
    cube_del(cube);
    stage("science-release", owner == NULL ? 0 : owner->xtnum, "after");
}

#include "integrated_descriptor_observer.h"

int main(int argc, char **argv)
{
    int status, before, after, cycle, cycles, measured;
    unsigned long first_identity, last_identity;
    char root[PATH_MAX], path[PATH_MAX];
    char *repeat;
    repeat = getenv("S2_INTEGRATED_REPEAT");
    measured = repeat == NULL ? 0 : atoi(repeat);
    if (repeat != NULL && measured != 10) return 2;
    cycles = repeat == NULL ? 1 : measured + 1;
    if (getcwd(root, sizeof(root)) == NULL) return 2;
    for (cycle = 0; cycle < cycles; cycle++) {
        /* Repetition uses fresh staged directories; native global state stays alive. */
        if (repeat != NULL) {
            if (snprintf(path, sizeof(path), "%s/cycle-%02d", root, cycle) >= (int)sizeof(path)) return 2;
            if (chdir(path) != 0) return 2;
        }
        if (owner != NULL || live_products() != 0) return 2;
        contexts = destroyed = cal_calls = bpm_calls = combine_calls = science_loads = mismatch = checkpoint_seq = 0;
        printf("INTEGRATED CYCLE BEGIN %d\n", cycle);
        fflush(stdout);
        descriptor_limit("before");
        before = descriptors("before", &first_identity);
        if (before < 0) return 2;
        account("process-start");
        /* The actual recipe uses getopt; each repeated invocation parses anew. */
        optind = 1;
        status = observed_recipe_main(argc, argv);
        account("after-driver");
        printf("INTEGRATED RESULT native_exit=%d contexts=%d destroyed=%d calibration_calls=%d bpm_calls=%d combine_calls=%d science_loads=%d live_products=%d owner_live=%d mismatch=%d\n",
               status, contexts, destroyed, cal_calls, bpm_calls, combine_calls, science_loads,
               live_products(), owner != NULL, mismatch);
        descriptor_limit("after");
        after = descriptors("after-driver", &last_identity);
        printf("DESCRIPTORS before=%d after=%d identity_equal=%d\n", before, after,
               after >= 0 && first_identity == last_identity);
        qfits_cache_purge();
        account("after-purge");
        after = descriptors("after-purge", &last_identity);
        printf("CACHE DESCRIPTORS after-purge before=%d after=%d identity_equal=%d\n", before, after,
               after >= 0 && first_identity == last_identity);
        qfits_cache_purge();
        account("after-second-purge");
        after = descriptors("after-second-purge", &last_identity);
        printf("CACHE DESCRIPTORS after-second-purge before=%d after=%d identity_equal=%d\n", before, after,
               after >= 0 && first_identity == last_identity);
        printf("INTEGRATED CYCLE END %d\n", cycle);
        fflush(stdout);
        if (chdir(root) != 0) return 2;
        if (status || owner != NULL || live_products() || mismatch) break;
    }
    /* Native status is retained above; external leak-tool status stays independent. */
    return 0;
}
