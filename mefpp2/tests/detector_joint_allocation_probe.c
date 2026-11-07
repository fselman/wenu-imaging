/* Reuses the accepted Eclipse failure-seam/accounting scaffold. */
#include "../qfits5/src/xmemory.c"
#define main joint_numerical_main
#include "detector_joint_probe.c"
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
    fixture f,snapshot;detector_joint_result *out=NULL;resources baseline;
    size_t calls,failure;int persistent;
    /* Numerical suite is a separate CTest. Exhaust owners on this same full-rank fixture. */
    fill(&f,.2,1);f.p.starts=1;snapshot=f;baseline=observe();
    arm(0,0);assert(detector_joint_response_fit_checked(&f.p,&f.o,&out)==0);
    assert(out->status==DETECTOR_JOINT_CANDIDATE);calls=dependency_calls;disarm();
    detector_joint_result_del(out);out=NULL;unchanged(baseline);assert(calls>0);
    for(persistent=0;persistent<=1;++persistent)for(failure=1;failure<=calls;++failure){
        arm(failure,persistent);assert(detector_joint_response_fit_checked(&f.p,&f.o,&out)==-1);
        disarm();assert(dependency_fired&&!out);unchanged(baseline);assert(!memcmp(&f,&snapshot,sizeof f));
    }
    f.o.inversion_iterations=1;
    assert(detector_joint_response_fit_checked(&f.p,&f.o,&out)==-1&&!out);unchanged(baseline);
    printf("PASS: %lu joint-fit single and persistent failure positions; qfits owners and inputs preserved\n",(unsigned long)calls);
    return 0;
}
