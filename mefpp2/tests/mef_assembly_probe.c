#include "mef_mef_assemble.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static long number(const char *s)
{
    char *end; long n;
    errno = 0; n = strtol(s, &end, 10);
    if (errno || !*s || *end || n < -64 || n > 2147483647L) exit(2);
    return n;
}
int main(int argc, char **argv)
{
    mef_assembly_detector *d;
    char message[512], *end;
    char before[4096], after[4096];
    size_t i, n;
    int status;
    if (argc < 12 || (argc - 3) % 9) return 2;
    n = (size_t)(argc - 3) / 9;
    d = calloc(n, sizeof(*d));
    if (d == NULL) return 2;
    for (i = 0; i < n; ++i) {
        char **a = argv + 3 + i * 9;
        d[i].path = a[0]; d[i].detector_id = a[1];
        d[i].configuration_detector = (size_t)number(a[2]);
        d[i].output_hdu = (size_t)number(a[3]);
        d[i].width = (int)number(a[4]); d[i].height = (int)number(a[5]);
        d[i].bitpix = (int)number(a[6]);
        d[i].bscale = strtod(a[7], &end); if (*end) return 2;
        d[i].bzero = strtod(a[8], &end); if (*end) return 2;
    }
    if (getcwd(before, sizeof(before)) == NULL) return 2;
    status = mef_mef_assemble(argv[1], argv[2], d, n, message, sizeof(message));
    if (getcwd(after, sizeof(after)) == NULL || strcmp(before, after)) return 2;
    free(d);
    if (*message) fprintf(stderr, "%s\n", message);
    return status == 0 ? 0 : 1;
}
