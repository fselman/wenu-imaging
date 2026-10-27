/* Diagnostic controls only; no astronomy processing or production change. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "xmemory.h"

/* Use ordinary malloc/free for system controls; call qfits explicitly below. */
#undef malloc
#undef free

#define CONTROL_BYTES 8192
static void *system_root = NULL;
static volatile unsigned long scrub_sum = 0;

static void account(const char *label)
{
    fprintf(stderr, "ACCOUNTING BEGIN %s\n", label);
    xmemory_status();
    fprintf(stderr, "ACCOUNTING END %s\n", label);
    fflush(stderr);
}

static int allocate_unreachable(void)
{
    void * volatile pointer;
    pointer = malloc(CONTROL_BYTES);
    if (pointer == NULL) return 2;
    memset(pointer, 0, CONTROL_BYTES);
    /* Deliberately abandon this diagnostic allocation, then clear the local. */
    pointer = NULL;
    return 0;
}

static void scrub_old_stack(void)
{
    volatile unsigned char scratch[32768];
    unsigned int i;
    for (i = 0; i < sizeof(scratch); i++) scratch[i] = 0;
    scrub_sum += scratch[0];
}

int main(int argc, char **argv)
{
    void *pointer;
    int status;
    if (argc != 2) return 2;
    pointer = NULL;
    status = 0;
    account("initial");

    if (!strcmp(argv[1], "system-clean")) {
        pointer = malloc(CONTROL_BYTES);
        if (pointer == NULL) return 2;
        memset(pointer, 0, CONTROL_BYTES);
        free(pointer);
        pointer = NULL;
    } else if (!strcmp(argv[1], "system-unreachable")) {
        status = allocate_unreachable();
        if (status != 0) return status;
        scrub_old_stack();
    } else if (!strcmp(argv[1], "system-rooted")) {
        system_root = malloc(CONTROL_BYTES);
        if (system_root == NULL) return 2;
        memset(system_root, 0, CONTROL_BYTES);
    } else if (!strcmp(argv[1], "qfits-clean") ||
               !strcmp(argv[1], "qfits-registered")) {
        pointer = xmemory_malloc(CONTROL_BYTES, __FILE__, __LINE__);
        if (pointer == NULL) return 2;
        memset(pointer, 0, CONTROL_BYTES);
        account("allocated");
        if (!strcmp(argv[1], "qfits-clean")) {
            xmemory_free(pointer, __FILE__, __LINE__);
        }
        /* The registered control retains only qfits' own table reference. */
        pointer = NULL;
        scrub_old_stack();
    } else {
        return 2;
    }

    account("final");
    printf("CONTROL COMPLETE %s\n", argv[1]);
    fflush(stdout);
    return 0;
}
