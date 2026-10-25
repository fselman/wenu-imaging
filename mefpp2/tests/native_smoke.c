#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "eclipse.h"
#include "qfits.h"
#include "xmemory.h"
int main(void)
{
    image_t *image;
    FILE *stream;
    char *answer;
    byte *bytes;
    float *decoded;
    float pixels[3];
    /* Eclipse arithmetic: allocate an image, set pixels and measure its mean. */
    image = image_new(3, 1);
    if (image == NULL) return 1;
    image->data[0] = 1.0f;
    image->data[1] = 2.0f;
    image->data[2] = 3.0f;
    if (image_getmean(image) != 2.0) return 2;
    image_del(image);
    /* PAF parsing: call the production reader on a controlled configuration. */
    stream = fopen("probe.paf", "w");
    if (stream == NULL) return 3;
    if (fputs("PAF.HDR.START ;\nPROBE.VALUE 17;\n", stream) == EOF) return 4;
    if (fclose(stream) != 0) return 5;
    answer = qfits_paf_query("probe.paf", "PROBE.VALUE");
    if (answer == NULL || atoi(answer) != 17) return 6;
    /* FITS pixel conversion: exercise native big-endian serialization/readback. */
    pixels[0] = -2.0f; pixels[1] = 0.0f; pixels[2] = 7.5f;
    bytes = qfits_pixdump_float(pixels, 3, BPP_IEEE_FLOAT);
    if (bytes == NULL) return 7;
    decoded = qfits_pixin_float(bytes, 3, BPP_IEEE_FLOAT, 1.0, 0.0);
    if (decoded == NULL) return 8;
    if (decoded[0] != -2.0f || decoded[1] != 0.0f || decoded[2] != 7.5f) return 9;
    free(decoded);
    free(bytes);
    if (remove("probe.paf") != 0) return 10;
    puts("PASS: Eclipse image mean, qfits PAF and float pixel conversion");
    return 0;
}
