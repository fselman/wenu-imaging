/* Native assembly only: no detector calculation, raw discovery or Pycavi. */
#ifndef MEF_MEF_ASSEMBLE_H
#define MEF_MEF_ASSEMBLE_H
#include <stddef.h>
typedef struct {
    const char *path;                 /* Absolute private one-extension MEF. */
    const char *detector_id;          /* Must match its EXTNAME. */
    size_t configuration_detector;   /* Independent of source/output HDU. */
    size_t output_hdu;               /* Explicit manifest order, starting at 1. */
    int width, height, bitpix;
    double bscale, bzero;
} mef_assembly_detector;
/* Caller holds completed temporary products stable throughout this serial call.
 * Reference detector is explicit; its primary retains reference-detector cards.
 * Final basename replaces ORIGFILE in every HDU. NEXTEND is the final count.
 * Existing EXTNAME/EXTVER and all other detector cards/data bytes are preserved.
 * CHECKSUM is removed after header edits; DATASUM is retained (data unchanged).
 * Writes/read-checks a private sibling then links exclusively to final_path.
 * Existing destinations are never replaced. No ASDF/log/recipe success implied.
 * One 64 KiB copy buffer; qfits globals mean concurrent calls are unsupported.
 */
int mef_mef_assemble(const char *final_path, const char *reference_detector_id,
    const mef_assembly_detector *, size_t count, char *message, size_t size);
#endif
