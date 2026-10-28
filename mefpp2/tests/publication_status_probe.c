/* Test the actual publication helper with controlled qfits I/O outcomes.
 * This is a helper unit, not a recipe/scientific or qfits qualification run. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include "eclipse.h"
#include "mefp_lib.h"

static int mode;
void e_error(char *format, ...) { (void)format; }
int qfits_header_dump(qfits_header *header, FILE *stream)
{
    char data[80];
    (void)header;
    memset(data, ' ', sizeof(data));
    if (mode == 1) return -1;
    if (mode == 4) {
        if (fwrite(data, 1, sizeof(data), stream) != sizeof(data)) return -1;
        return close(fileno(stream)); /* Force the subsequent flush/close error. */
    }
    return fwrite(data, 1, sizeof(data), stream) == sizeof(data) ? 0 : -1;
}
int qfits_pixdump(qfitsdumper *dumper)
{
    FILE *stream;
    int size, i, status;
    if (mode == 2) return -1;
    size = dumper->npix * BYTESPERPIXEL(dumper->out_ptype);
    if (mode == 3) size--;
    stream = fopen(dumper->filename, "a");
    if (stream == NULL) return -1;
    status = 0;
    for (i = 0; i < size; i++) if (fputc(0, stream) == EOF) status = -1;
    if (fclose(stream) != 0) status = -1;
    return status;
}
int main(void)
{
    image_t image;
    pixelvalue pixels[4];
    qfits_header *header;
    struct stat info;
    FILE *stream;
    int i;
    header = (qfits_header *)&image; /* The stub does not dereference the header. */
    image.lx = 2; image.ly = 2; image.data = pixels;
    for (i = 0; i < 4; i++) pixels[i] = (pixelvalue)i;
    mode = 0;
    if (mef_hdrpix_dump(NULL, "good.fits", header, BPP_DEFAULT) != 0) return 1;
    if (mef_hdrpix_dump(&image, "good.fits", header, BPP_DEFAULT) != 0) return 2;
    if (stat("good.fits", &info) != 0 || info.st_size != FITS_BLOCK_SIZE) return 3;
    stream = fopen("good.fits", "rb");
    if (stream == NULL) return 12;
    for (i = 0; i < FITS_BLOCK_SIZE; i++) if (fgetc(stream) != (i < 160 ? ' ' : 0)) return 13;
    if (fgetc(stream) != EOF || fclose(stream) != 0) return 14;
    /* Failed open preserves the reserved output directory and its marker. */
    if (mkdir("blocked.fits", 0700) != 0) return 4;
    stream = fopen("blocked.fits/marker", "w");
    if (stream == NULL || fputs("preserved", stream) < 0 || fclose(stream) != 0) return 5;
    if (mef_hdrpix_dump(NULL, "blocked.fits", header, BPP_DEFAULT) == 0) return 6;
    if (stat("blocked.fits/marker", &info) != 0 || info.st_size != 9) return 7;
    mode = 1;
    if (mef_hdrpix_dump(NULL, "header-error.fits", header, BPP_DEFAULT) == 0) return 8;
    mode = 2;
    if (mef_hdrpix_dump(&image, "pixel-error.fits", header, BPP_DEFAULT) == 0) return 9;
    mode = 3;
    if (mef_hdrpix_dump(&image, "short-pixels.fits", header, BPP_DEFAULT) == 0) return 10;
    if (mef_hdrpix_dump(NULL, "null-header.fits", NULL, BPP_DEFAULT) == 0) return 11;
    mode = 4;
    if (mef_hdrpix_dump(NULL, "flush-close-error.fits", header, BPP_DEFAULT) == 0) return 15;
    puts("Publication helper controls passed; recipe launches: 0");
    return 0;
}
