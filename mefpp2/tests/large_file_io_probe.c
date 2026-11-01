/* Approved IO-1 wide-discovery boundary; later stages add existing I/O calls. */
#include "mefp_lib.h"
#include "mef_layout.h"
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static int process(char *path, char *output)
{
    int i, j, count, result;
    image_t *image, *bias;
    qfits_header *header;
    if (access(output, F_OK) == 0) return 30;
    count = qfits_query_n_ext(path);
    if (count < 1) return 31;
    header = qfits_header_read(path);
    if (header == NULL) return 32;
    result = mef_hdrpix_dump(NULL, output, header, BPP_DEFAULT);
    qfits_header_destroy(header);
    if (result) return 33;
    for (i = 1; i <= count; ++i) {
        image = image_loadext(path, i, 0, 1);
        if (image == NULL) return 34;
        bias = image_new(image->lx, image->ly);
        if (bias == NULL) { image_del(image); return 35; }
        for (j = 0; j < image->lx * image->ly; ++j) bias->data[j] = 16.0f;
        result = image_sub_local(image, bias);
        image_del(bias);
        if (result) { image_del(image); return 36; }
        header = qfits_header_readext(path, i);
        if (header == NULL) { image_del(image); return 37; }
        result = mef_hdrpix_dump(image, output, header, BPP_DEFAULT);
        qfits_header_destroy(header); image_del(image);
        if (result) return 38;
    }
    qfits_cache_purge();
    return 0;
}

static int write_failure(char *output)
{
    float values[4096];
    qfitsdumper dumper;
    memset(&dumper, 0, sizeof(dumper));
    memset(values, 0, sizeof(values));
    dumper.filename = output; dumper.npix = 4096;
    dumper.ptype = PTYPE_FLOAT; dumper.out_ptype = -32; dumper.fbuf = values;
    return qfits_pixdump(&dumper) == -1 ? 0 : 40;
}

static int reads(char *path, int extension, int plane, float first, float last)
{
    image_t *image;
    qfitsloader loader;
    qfits_header *header;
    mef_layout *layout;
    int mode;
    header = qfits_header_readext(path, extension);
    if (header == NULL) return 20;
    qfits_header_destroy(header);
    if (extension) {
        if (qfits_query_ext(path, "EXTVER", extension) == NULL) return 21;
        layout = NULL;
        if (mef_layout_read(path, NULL, NULL, &layout, NULL) != MEF_OK) return 22;
        mef_layout_destroy(layout);
    }
    for (mode = 0; mode <= 1; ++mode) {
        image = image_loadext(path, extension, plane, mode);
        if (image == NULL) return 23;
        if (image->data[0] != first || image->data[image->lx * image->ly - 1] != last ||
            image->data[image->lx + 1] != 0.0f) return 24;
        image_del(image);
    }
    memset(&loader, 0, sizeof(loader));
    loader.filename = path; loader.xtnum = extension; loader.pnum = plane;
    loader.ptype = PTYPE_FLOAT; loader.map = 0;
    if (qfitsloader_init(&loader) || qfits_loadpix_window(&loader, 1, 1, 2, 2)) return 25;
    if (loader.fbuf[0] != first || loader.fbuf[1] != 0.0f ||
        loader.fbuf[2] != 0.0f || loader.fbuf[3] != 0.0f) return 26;
    free(loader.fbuf);
    loader.map = 1;
    if (qfits_loadpix_window(&loader, 1, 1, 2, 2) != -1) return 27;
    loader.map = 0; loader.pnum = -1;
    if (qfits_loadpix(&loader) != -1) return 28;
    loader.pnum = loader.np;
    if (qfits_loadpix(&loader) != -1) return 29;
    qfits_cache_purge();
    return 0;
}

static int discover(char *path)
{
    int count, i, small_start, small_size, rc;
    off_t start, size;
    count = qfits_query_n_ext(path);
    if (count < 0) return 1;
    printf("EXTENSIONS %d\n", count);
    for (i = 0; i <= count; ++i) {
        if (qfits_get_hdrinfo_wide(path, i, &start, &size)) return 2;
        printf("HEADER %d %ld %ld\n", i, (long)start, (long)size);
        small_start = 17; small_size = 19;
        rc = qfits_get_hdrinfo(path, i, &small_start, &small_size);
        if (start > INT_MAX || size > INT_MAX) {
            if (rc != -1 || small_start != 17 || small_size != 19) return 3;
        } else if (rc || small_start != start || small_size != size) return 4;
        /* A representable requested length still succeeds at a late header. */
        if (qfits_get_hdrinfo(path, i, NULL, &small_size) || small_size != size) return 5;
        if (qfits_get_datinfo_wide(path, i, &start, &size)) return 6;
        printf("DATA %d %ld %ld\n", i, (long)start, (long)size);
        small_start = 17; small_size = 19;
        rc = qfits_get_datinfo(path, i, &small_start, &small_size);
        if (start > INT_MAX || size > INT_MAX) {
            if (rc != -1 || small_start != 17 || small_size != 19) return 7;
        } else if (rc || small_start != start || small_size != size) return 8;
    }
    qfits_cache_purge();
    return 0;
}
int main(int argc, char **argv)
{
    if (argc == 3 && !strcmp(argv[1], "discover")) return discover(argv[2]);
    if (argc == 3 && !strcmp(argv[1], "read-mef")) return reads(argv[2], 65, 0, 65.0f, 165.0f);
    if (argc == 3 && !strcmp(argv[1], "read-cube")) return reads(argv[2], 0, 64, 73.0f, 0.0f);
    if (argc == 4 && !strcmp(argv[1], "process")) return process(argv[2], argv[3]);
    if (argc == 3 && !strcmp(argv[1], "pad")) { qfits_zeropad(argv[2]); return 0; }
    if (argc == 3 && !strcmp(argv[1], "write-failure")) return write_failure(argv[2]);
    return 64;
}
