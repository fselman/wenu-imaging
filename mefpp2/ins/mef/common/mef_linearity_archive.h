/* Preparation metadata only. Shared product QC owns validation and ASDF I/O. */
#ifndef MEF_LINEARITY_ARCHIVE_H
#define MEF_LINEARITY_ARCHIVE_H
#include "mef_linearity_files.h"
#include "mef_product_qc.h"
typedef struct mef_linearity_archive mef_linearity_archive;
/* Identity strings and configuration remain borrowed until destroy. Global input
 * order is flats then biases; declared indices are retained unchanged and
 * must be unique across both cohorts. */
typedef struct {
    const char *path, *asset, *role;
    int index, hdu, master_accepted;
} mef_linearity_archive_source;
typedef struct {
    const char *table_path, *log_path, *created_at, *source_revision;
    const char *detector, *amplifier, *readout;
    size_t configuration_detector, flat_count, input_count, max_roi_rows;
    int bin_x, bin_y;
    const mef_linearity_archive_source *input;
    const mef_image_ref *master, *bpm;
    const mef_config *configuration;
} mef_linearity_archive_options;
mef_linearity_archive *mef_linearity_archive_new(const mef_linearity_archive_options *);
/* Copies small ROI metadata before the caller releases the pair's images. */
int mef_linearity_archive_add_pair(mef_linearity_archive *, const mef_linearity_files_result *);
/* Reads only completed native text evidence; never opens image pixels. */
int mef_linearity_archive_add_evidence(mef_linearity_archive *, const char *name,
    const char *format, const char *path);
/* Exclusively writes the measured table in original flat/configured ROI order.
 * The caller then sends view() to the shared ASDF writer. No noise model/fit. */
int mef_linearity_archive_table(mef_linearity_archive *);
const mef_product_qc *mef_linearity_archive_view(const mef_linearity_archive *);
void mef_linearity_archive_destroy(mef_linearity_archive *);
#endif
