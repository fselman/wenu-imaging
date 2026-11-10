/* One detector owns the image payloads; downstream services only borrow them. */
#ifndef MEF_DETECTOR_CUBE_H
#define MEF_DETECTOR_CUBE_H
#include "mef_linearity_prepare.h"
#include "mef_layout.h"

typedef struct {
    char *path;
    int hdu, is_flat;
    image_t *raw, *active;
    pixelvalue *trace;
    size_t rows;
} mef_detector_plane;

typedef struct mef_detector_cube {
    mef_detector_plane planes[128];
    size_t count, flat_count, image_loads, corrections;
    image_t *master;
    pixelmap *binary;
    unsigned char *flags;
    int mask_width, mask_height, qc;
    mef_config *configuration;
    mef_bias_settings settings;
} mef_detector_cube;

/* The existing explicit preparation controls define input order and bindings.
 * A supplied master and prior mask are each loaded once. No global cache.
 */
int mef_detector_cube_ingest(mef_detector_cube *, int, char **, int);
void mef_detector_cube_destroy(mef_detector_cube *);
const mef_detector_plane *mef_detector_cube_find(const mef_detector_cube *, const char *, int);
const mef_detector_plane *mef_detector_cube_bound(const mef_detector_cube *, const mef_layout_map *, const char *);
#endif
