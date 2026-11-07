/* Reuses the accepted Eclipse failure-seam/accounting scaffold. */
#include "../qfits5/src/xmemory.c"
#define main gain_numerical_main
#include "gain_pair_probe.c"
#undef main
static int dependency_active, dependency_persistent;
static size_t dependency_calls, dependency_fail_at, dependency_fired;
static const char *site_file[4096];
static int site_line[4096];
static int fail_dependency(const char *file, int line)
{
    if (!dependency_active) return 0;
    assert(dependency_calls < 4096);
    site_file[dependency_calls] = file;
    site_line[dependency_calls] = line;
    ++dependency_calls;
    if (dependency_fail_at && (dependency_calls == dependency_fail_at ||
        (dependency_persistent && dependency_calls >= dependency_fail_at))) {
        ++dependency_fired;
        return 1;
    }
    return 0;
}
void *mef_test_dependency_malloc(size_t size, const char *file, int line)
{
    if (fail_dependency(file, line)) return NULL;
    return xmemory_malloc(size, file, line);
}
void *mef_test_dependency_calloc(size_t n, size_t size, const char *file, int line)
{
    if (fail_dependency(file, line)) return NULL;
    return xmemory_calloc(n, size, file, line);
}
typedef struct {
    size_t bytes, ram, swap;
    int cells, swapfiles, files, mappings;
    unsigned long identities;
} resources;
static resources observe(void)
{
    resources value;
    int i;
    memset(&value, 0, sizeof(value));
    value.bytes = xmemory_table.alloc_total; value.ram = xmemory_table.alloc_ram;
    value.swap = xmemory_table.alloc_swap; value.cells = xmemory_table.ncells;
    value.swapfiles = xmemory_table.nswapfiles; value.files = xmemory_table.n_mm_files;
    value.mappings = xmemory_table.n_mm_mappings;
    for (i = 0; i < XMEMORY_MAXPTRS; ++i) if (xmemory_p_val[i] != NULL)
        value.identities ^= (unsigned long)xmemory_p_val[i] ^ xmemory_p_size[i];
    return value;
}
static void unchanged(resources before)
{
    resources after;
    after = observe();
    assert(before.bytes == after.bytes && before.ram == after.ram &&
        before.swap == after.swap && before.cells == after.cells &&
        before.swapfiles == after.swapfiles && before.files == after.files &&
        before.mappings == after.mappings && before.identities == after.identities);
}
static void arm(size_t position, int persistent)
{
    dependency_active = 1; dependency_calls = 0;
    dependency_fail_at = position; dependency_persistent = persistent;
    dependency_fired = 0;
}
static void disarm(void) { dependency_active = 0; }

int main(void)
{
    image_t *im[4];
    detector_gain_pair_result r,sentinel;
    resources baseline;
    size_t calls,failure;
    int k,persistent;
    assert(gain_numerical_main()==0);
    for(k=0;k<4;++k) { im[k]=image_new(4,1); assert(im[k]); }
    fill_pair(im); memset(&sentinel,0x5a,sizeof(sentinel));
    baseline=observe();
    arm(0,0); assert(measure(im,NULL,NULL,1,&r)==0); calls=dependency_calls; disarm();
    unchanged(baseline); assert(calls>0);
    for(persistent=0;persistent<=1;++persistent) for(failure=1;failure<=calls;++failure) {
        r=sentinel; arm(failure,persistent);
        assert(measure(im,NULL,NULL,1,&r)==-1); disarm();
        assert(dependency_fired && !memcmp(&r,&sentinel,sizeof(r)));
        unchanged(baseline);
        assert(im[0]->data[0]==101 && im[1]->data[0]==99 && im[2]->data[0]==11);
    }
    for(k=0;k<4;++k) image_del(im[k]);
    printf("PASS: %lu single and persistent allocation-failure positions; owners and output preserved\n",(unsigned long)calls);
    return 0;
}
