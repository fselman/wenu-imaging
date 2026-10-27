
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "xmemory.h"
#undef malloc
#undef free

int main(int argc, char **argv)
{
    int use_qfits;
    char *p;
    volatile char observed;
    volatile size_t beyond;
    volatile int maximum;
    volatile int overflowed;

    if (argc != 3) return 2;
    use_qfits = strcmp(argv[1], "qfits") == 0;
    if (strcmp(argv[2], "overflow") == 0) {
        maximum = INT_MAX;
        overflowed = maximum + 1;
        printf("%d\n", overflowed);
        return 0;
    }

    p = use_qfits ? xmemory_malloc(16, __FILE__, __LINE__) : malloc(16);
    if (p == NULL) return 3;
    memset(p, 7, 16);

    if (strcmp(argv[2], "bounds") == 0) {
        beyond = 16;
        p[beyond] = 9;
    }
    if (use_qfits) xmemory_free(p, __FILE__, __LINE__);
    else free(p);

    if (strcmp(argv[2], "use-after-free") == 0) {
        observed = p[0];
        printf("%d\n", (int)observed);
    }
    if (strcmp(argv[2], "double-free") == 0) {
        if (use_qfits) xmemory_free(p, __FILE__, __LINE__);
        else free(p);
    }
    if (strcmp(argv[2], "clean") == 0) puts("CLEAN_OK");
    return 0;
}
