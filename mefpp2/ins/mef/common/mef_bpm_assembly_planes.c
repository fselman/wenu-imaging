/* Shared final BPM plane mapping; reads headers only, never pixel arrays. */
#define _POSIX_C_SOURCE 200809L
#include "mef_mef_assemble.h"
#include "qfits.h"
#include <stdio.h>
#include <stdlib.h>
#undef calloc
#undef free

char *mef_bpm_assembly_plane_map(const char *path,
    const mef_bpm_assembly_detector *detectors, size_t count)
{
    char *text = NULL;
    size_t length = 0, extensions = 0, hdu = 0;
    int okay = 0;
    FILE *stream = NULL;
    int *planes;

    if (!path || !detectors || !count || count > 4096) return NULL;
    planes = calloc(count, sizeof(*planes));
    if (!planes) return NULL;
    for (size_t i = 0; i < count; ++i) {
        int source_extensions = qfits_query_n_ext((char *)detectors[i].path);
        if (source_extensions < 0) goto done;
        planes[i] = source_extensions + 1;
        extensions += (size_t)planes[i];
    }

    /* Assembly validates a temporary pathname. Prime the published pathname
     * separately, with enough HDUs for all of the detector planes. */
    size_t hdus = extensions + 1;
    if (qfits_cache_prime_bounded((char *)path, hdus, hdus * 1048576) ||
        qfits_query_n_ext((char *)path) != (int)extensions) goto done;

    stream = open_memstream(&text, &length);
    if (!stream) goto done;
    for (int pass = 0; pass < 2; ++pass) {
        for (size_t i = 0; i < count; ++i) {
            for (int source = pass ? 1 : 0; source < (pass ? planes[i] : 1); ++source) {
                qfits_header *header = qfits_header_readext((char *)path, (int)++hdu);
                char *name = header ? qfits_header_getstr(header, "EXTNAME") : NULL;
                int written = name ? fprintf(stream, "%s\t%d\t%zu\t%s\n",
                    detectors[i].detector_id, source, hdu,
                    source ? qfits_pretty_string(name) : "BPM") : -1;
                qfits_header_destroy(header);
                if (written < 0) goto done;
            }
        }
    }
    okay = 1;
done:
    if (stream && fclose(stream)) okay = 0;
    if (!okay) {
        free(text);
        text = NULL;
    }
    free(planes);
    return text;
}
