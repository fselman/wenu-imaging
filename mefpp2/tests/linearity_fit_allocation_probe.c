/* Reuses the accepted Eclipse failure-seam/accounting scaffold. */
#include "../qfits5/src/xmemory.c"
#include "linearity_fit_fixture.h"
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
    (void)covariance_identity;
    linearity_fixture f,saved;detector_linearity_fit_result *out=NULL;resources baseline;
    linearity_fill(&f,.2);saved=f;baseline=observe();
    arm(0,0);assert(detector_linearity_fit_checked(&f.problem,&out)==0);
    assert(out->status==DETECTOR_LINEARITY_CURVE_CANDIDATE);size_t calls=dependency_calls;disarm();
    detector_linearity_fit_result_del(out);out=NULL;unchanged(baseline);assert(calls==2);
    for(int persistent=0;persistent<=1;++persistent)for(size_t failure=1;failure<=calls;++failure){
        arm(failure,persistent);assert(detector_linearity_fit_checked(&f.problem,&out)==-1);disarm();
        assert(dependency_fired&&!out);unchanged(baseline);assert(!memcmp(&f,&saved,sizeof f));
    }
    f.delta[1]=f.delta[0];
    assert(detector_linearity_fit_checked(&f.problem,&out)==-1&&!out);unchanged(baseline);
    printf("PASS: %lu composition-owner single/persistent allocation positions; nested qualified owners released\n",(unsigned long)calls);
    return 0;
}
