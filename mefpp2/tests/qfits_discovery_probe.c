/* Existing qfits APIs and additive checked discovery, synthetic inputs only. */
#include "qfits.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int count_scale(const char *key, const char *value, const char *line, void *user)
{
    int *count;
    (void)value; (void)line; count = user;
    if (!strcmp(key, "BSCALE")) ++*count;
    return 0;
}
int main(int argc, char **argv)
{
    int count, i, hs, hz, ds, dz, duplicates;
    qfits_header *header;
    if (argc != 4) return 2;
    if (atoi(argv[2]) && qfits_cache_prime_bounded(argv[1], (size_t)strtoul(argv[2], NULL, 10),
        (size_t)strtoul(argv[3], NULL, 10)) != 0) { puts("REJECTED"); return 1; }
    count = qfits_query_n_ext(argv[1]);
    if (count < 0) { puts("REJECTED"); return 1; }
    printf("EXTENSIONS %d\n", count);
    for (i = 0; i <= count; ++i) {
        if (qfits_get_hdrinfo(argv[1], i, &hs, &hz) || qfits_get_datinfo(argv[1], i, &ds, &dz)) return 2;
        header = qfits_header_readext(argv[1], i);
        if (header == NULL) return 2;
        duplicates = 0;
        if (qfits_header_visit(header, count_scale, &duplicates)) return 2;
        printf("HDU %d %d %d %d %d %d\n", i, hs, hz, ds, dz, duplicates);
        qfits_header_destroy(header);
    }
    qfits_cache_purge(); return 0;
}
