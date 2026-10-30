/* Compile the actual allocator with test-local syscall seams: no production
 * fault switches, resource exhaustion, or alternative allocator. Refs #164/#168. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <stdarg.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>

static void *test_malloc(size_t);
static int test_open(const char *, int, ...);
static int test_truncate(int, off_t);
static ssize_t test_write(int, const void *, size_t);
static void *test_map(void *, size_t, int, int, int, off_t);
static int test_unlink(const char *);
static int test_unmap(void *, size_t);
static int test_close(int);
#define malloc test_malloc
#define open test_open
#define ftruncate test_truncate
#define write test_write
#define mmap test_map
#define unlink test_unlink
#define munmap test_unmap
#define close test_close
#include "../qfits5/src/xmemory.c"
#undef malloc
#undef open
#undef ftruncate
#undef write
#undef mmap
#undef unlink
#undef munmap
#undef close

static const char *fault = "";
static int forced, fired, opens, baseline[256];
static unsigned char *ram, *retained;
static size_t retained_size;

static void require(int condition, const char *message)
{
    if (!condition) { fprintf(stderr, "PROBE FAILURE: %s\n", message); _exit(92); }
}
static int trigger(const char *name)
{
    if (!fired && !strcmp(fault, name)) { fired = 1; return 1; }
    return 0;
}
static void *test_malloc(size_t size) { return forced ? NULL : malloc(size); }
static int test_open(const char *name, int flags, ...)
{
    int fd, mode;
    va_list args;
    struct stat st;
    va_start(args, flags); mode = (flags & O_CREAT) ? va_arg(args, int) : 0; va_end(args);
    require((flags & (O_CREAT | O_EXCL)) == (O_CREAT | O_EXCL), "exclusive creation");
    require(mode == 0600, "explicit owner-only mode");
    if (trigger("open")) { errno = EACCES; return -1; }
    fd = open(name, flags, mode);
    if (fd >= 0) {
        ++opens;
        require(fstat(fd, &st) == 0 && (st.st_mode & 0777) == 0600, "private actual permissions");
    }
    return fd;
}
static int test_truncate(int fd, off_t size)
{
    if (trigger("truncate")) { errno = ENOSPC; return -1; }
    return ftruncate(fd, size);
}
static ssize_t test_write(int fd, const void *data, size_t size)
{
    if (trigger("write")) { errno = ENOSPC; return -1; }
    if (trigger("write-zero")) return 0;
    if (trigger("write-eintr")) { errno = EINTR; return -1; }
    if (trigger("write-short")) return write(fd, data, size > 7 ? 7 : size);
    return write(fd, data, size);
}
static void *test_map(void *addr, size_t size, int prot, int flags, int fd, off_t off)
{
    if (trigger("map")) { errno = ENOMEM; return MAP_FAILED; }
    return mmap(addr, size, prot, flags, fd, off);
}
static int test_unlink(const char *name)
{
    if (trigger("unlink")) { errno = EACCES; return -1; }
    return unlink(name);
}
static int test_unmap(void *addr, size_t size)
{
    if (trigger("unmap")) { errno = EIO; return -1; }
    return munmap(addr, size);
}
static int test_close(int fd)
{
    int result;
    result = close(fd);
    /* A close error may occur after the descriptor was closed. Never retry it. */
    if (trigger("close")) { errno = EIO; return -1; }
    return result;
}
static void check_retained(void)
{
    size_t i;
    for (i = 0; i < 17; ++i) require(ram[i] == 0x5a, "retained RAM contents");
    if (retained != NULL) for (i = 0; i < retained_size; ++i)
        require(retained[i] == 0xa5, "retained swap contents");
    puts("PASS: retained allocation data");
}
static void final_observer(void)
{
    int i;
    /* Registered before allocator initialization: observes its atexit cleanup. */
    if (*fault) require(fired, "requested syscall fault exercised");
    require(xmemory_table.nswapfiles == 0 && xmemory_table.alloc_swap == 0, "swap owners cleared");
    for (i = 0; i < 256; ++i)
        require((fcntl(i, F_GETFD) != -1) == baseline[i], "descriptor baseline restored");
    if (ram != NULL) {
        for (i = 0; i < 17; ++i) require(ram[i] == 0x5a, "RAM preserved after swap cleanup");
        xmemory_free(ram, __FILE__, __LINE__);
    }
    require(xmemory_table.ncells == 0 && xmemory_table.alloc_total == 0, "owner totals restored");
    puts("PASS: descriptors, owners and RAM after exit cleanup");
}
static unsigned char *allocate(size_t size)
{
    unsigned char *p;
    size_t i;
    int slot;
    struct stat st;
    p = xmemory_malloc(size, __FILE__, __LINE__);
    require(p != NULL, "allocation returned");
    for (i = 0; i < size; ++i) require(p[i] == 0, "zero-filled swap storage");
    for (slot = 0; slot < XMEMORY_MAXPTRS; ++slot) if (xmemory_p_val[slot] == p) break;
    require(slot < XMEMORY_MAXPTRS && xmemory_p_memtype[slot] == MEMTYPE_SWAP, "forced real swap path");
    require(fstat(xmemory_p_swapfd[slot], &st) == 0 && st.st_nlink == 0 && (size_t)st.st_size >= size,
            "mapped storage unlinked and sized");
    memset(p, 0xa5, size);
    return p;
}
int main(int argc, char **argv)
{
    unsigned char *p[6], *q;
    size_t sizes[6] = {1, 2047, 2048, 2049, 4096, 4097};
    size_t i, j;
    char name[1024];
    int fd;
    require(argc == 4, "scenario, scratch, alternate scratch arguments");
    umask(0);
    for (i = 0; i < 256; ++i) baseline[i] = fcntl((int)i, F_GETFD) != -1;
    require(atexit(final_observer) == 0, "register final observer");
    require(xmemory_set_tmpdir(argv[2]) == 0, "select scratch");
    ram = xmemory_malloc(17, __FILE__, __LINE__); require(ram != NULL, "RAM allocation");
    memset(ram, 0x5a, 17);
    if (!strcmp(argv[1], "ram")) { require(opens == 0, "RAM route unchanged"); return 0; }
    if (!strcmp(argv[1], "cleanup-collision")) {
        xmemory_table.file_reg = 1;
        strcpy(name, xmemory_tmpfilename(1));
        fd = open(name, O_RDWR | O_CREAT | O_EXCL, 0600); require(fd >= 0, "create unowned sentinel");
        require(write(fd, "sentinel", 8) == 8 && close(fd) == 0, "write sentinel");
        xmemory_cleanup();
        require(access(name, F_OK) == 0, "exit cleanup preserves unowned path");
        return 0;
    }
    forced = 1;
    if (!strcmp(argv[1], "success")) {
        for (i = 0; i < 6; ++i) p[i] = allocate(sizes[i]);
        require(xmemory_set_tmpdir(argv[3]) == -1, "no scratch switch while swap live");
        for (i = 0; i < 6; ++i) {
            for (j = i; j < 6; ++j) {
                size_t k;
                for (k = 0; k < sizes[j]; ++k) require(p[j][k] == 0xa5, "other swaps preserved");
            }
            if (i % 2) xmemory_fdealloc(p[i], 0, sizes[i], __FILE__, __LINE__);
            else xmemory_free(p[i], __FILE__, __LINE__);
        }
        require(xmemory_set_tmpdir(argv[3]) == 0, "switch scratch after release");
        q = allocate(23); xmemory_free(q, __FILE__, __LINE__);
        puts("PASS: boundaries, free/fdealloc, permissions, scratch selection");
        return 0;
    }
    retained_size = 4097; retained = allocate(retained_size);
    require(atexit(check_retained) == 0, "register pre-cleanup data observer");
    if (!strcmp(argv[1], "exit")) return 0;
    if (!strcmp(argv[1], "signal")) {
        check_retained(); fflush(stdout);
        raise(SIGTERM);
        require(0, "termination signal must stop the process");
    }
    if (!strcmp(argv[1], "realloc")) {
        q = xmemory_realloc(retained, 8193, __FILE__, __LINE__);
        for (i = 0; i < retained_size; ++i) require(q[i] == 0xa5, "realloc copies swap data");
        for (i = retained_size; i < 8193; ++i) require(q[i] == 0, "realloc extension zeroed");
        memset(q + retained_size, 0xa5, 8193 - retained_size);
        retained = q; retained_size = 8193;
        return 0;
    }
    if (!strcmp(argv[1], "collision") || !strcmp(argv[1], "symlink")) {
        strcpy(name, xmemory_tmpfilename(2));
        if (!strcmp(argv[1], "symlink")) require(symlink(argv[3], name) == 0, "collision symlink");
        else {
            fd = open(name, O_RDWR | O_CREAT | O_EXCL, 0600); require(fd >= 0, "collision sentinel");
            require(write(fd, "sentinel", 8) == 8 && close(fd) == 0, "write collision");
        }
    } else if (!strcmp(argv[1], "overflow")) {
        (void)xmemory_malloc((size_t)-1, __FILE__, __LINE__);
        require(0, "size overflow must fail");
    } else if (!strcmp(argv[1], "registration-overflow")) {
        xmemory_table.file_reg = INT_MAX;
        (void)xmemory_malloc(1, __FILE__, __LINE__);
        require(0, "registration overflow must fail");
    } else if (!strcmp(argv[1], "unmap") || !strcmp(argv[1], "close")) {
        q = allocate(32);
        fault = argv[1];
        xmemory_free(q, __FILE__, __LINE__);
        require(0, "cleanup failure must return a failed process");
    } else fault = argv[1];
    q = allocate(4097);
    if (!strcmp(argv[1], "write-eintr") || !strcmp(argv[1], "write-short")) {
        require(fired, "write recovery seam exercised");
        xmemory_free(q, __FILE__, __LINE__);
        return 0;
    }
    require(0, "fault must fail allocation");
    return 92;
}
