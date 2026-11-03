/* Exact byte flags are separate from Eclipse's binary selection pixelmaps. */
#ifndef ECLIPSE_PIXELMAP_FLAGS8_H
#define ECLIPSE_PIXELMAP_FLAGS8_H
#include "pixelmaps.h"
#include "image_handling.h"

/* All output pointers must start NULL and remain unchanged on failure.
 * Arrays are owned by caller (free); pixelmaps by pixelmap_del. Input borrowed.
 * No polarity guessing: flags use 0=no reasons; reject_bits may be 0..255.
 * Geometry positive, within Eclipse limits. Return 0 / -1. */
int pixelmap_flags8_selection_checked(const unsigned char *, int, int,
    unsigned int reject_bits, pixelmap **out);
/* Exact physical integer values 0..255 only; no rounding or binarization. */
int pixelmap_flags8_from_image_checked(const image_t *, unsigned char **out);
/* Writes one primary FITS HDU to an already opened empty seekable stream. No
 * open/overwrite/close policy here: caller owns exclusive publication and close.
 * Fresh structural header, BITPIX=8, MASKENC=REASON8, explicit MASKREG tag.
 * Checks header/data/padding/flush; partial stream is not a published product.
 * Does not modify a borrowed qfits header or append guessed metadata. */
int pixelmap_flags8_write_checked(FILE *, const unsigned char *, int, int,
    const char *registry);
/* Explicit zero-based selected HDU, integer BITPIX=8, unity scaling and matching
 * encoding/registry required. Reuses qfits header and image_loadext; conversion
 * via pixelvalue is exact for every byte. Does not use pixelmap_load/ext.
 * Caller establishes detector/readout/active geometry compatibility. */
int pixelmap_flags8_load_checked(const char *, int hdu, const char *registry,
    unsigned char **out, int *width, int *height);
#endif
