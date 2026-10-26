#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "eclipse.h"
/* Header compatibility: C99+ must retain the language keyword for system headers. */
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 199901L
#ifdef inline
#error Eclipse must not replace the C99/C17 inline keyword
#endif
#endif
#include <ctype.h>
#include <math.h>
#if defined(__linux__)
#include <sys/ipc.h>
#include <sys/shm.h>
#ifndef M_PI
#error Required legacy math constants are unavailable in this language mode
#endif
#endif
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
#if defined(__linux__)
    struct shmid_ds shared_memory_descriptor;
#endif
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
    if (fputs("PAF.HDR.START ;\nPROBE.VALUE 17;\nPROBE.EMPTY \"\";\nPROBE.MISSING \n", stream) == EOF) return 4;
    if (fclose(stream) != 0) return 5;
    answer = qfits_paf_query("probe.paf", "PROBE.VALUE");
    if (answer == NULL || atoi(answer) != 17) return 6;
    /* Missing PAF values cannot reuse a previous query; quoted empty stays valid. */
    if (qfits_paf_query("probe.paf", "PROBE.MISSING") != NULL) return 12;
    answer = qfits_paf_query("probe.paf", "PROBE.EMPTY");
    if (answer == NULL || answer[0] != '\0') return 13;
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
    /* System-header integration: call ctype/math after the Eclipse includes. */
    if (toupper((unsigned char)'a') != 'A' || fabs(-2.0) != 2.0) return 11;
#if defined(__linux__)
    /* Header availability only: no shared memory object is created or attached. */
    shared_memory_descriptor.shm_segsz = 0;
    if (M_PI < 3.14 || M_PI > 3.15 || shared_memory_descriptor.shm_segsz != 0) return 14;
#endif
    puts("PASS: Eclipse/qfits primitives and system-header integration");
    return 0;
}
