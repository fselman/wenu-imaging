/* Internal M4 C90 layout boundary (#182); not an installed/frozen ABI. */
#ifndef MEF_LAYOUT_H
#define MEF_LAYOUT_H
#include "mef_runtime.h"
#include "image_handling.h"

#define MEF_LAYOUT_TEXT 81
typedef struct mef_layout mef_layout;
typedef struct mef_layout_map mef_layout_map;
typedef enum { MEF_HDU_EMPTY = 1, MEF_HDU_IMAGE, MEF_HDU_TABLE } mef_hdu_kind;
typedef enum { MEF_HEALTH_UNKNOWN = 1, MEF_HEALTH_GOOD, MEF_HEALTH_BAD } mef_detector_health;
typedef enum { MEF_OUTPUT_SELECTED = 1, MEF_OUTPUT_EXCLUDED } mef_detector_selection;

typedef struct {
    size_t max_hdus, max_header_bytes; /* Total header bytes, including padding. */
    /* Explicit FITS keyword spellings; NULL means no such identity asserted.
     * HIERARCH keys include their HIERARCH prefix, as qfits_getkey returns it. */
    const char *identity_key;
    const char *amplifier_key;
    const char *bin_x_key;
    const char *bin_y_key;
} mef_layout_options;

typedef struct {
    int hdu_index;                 /* Zero-based original file order. */
    mef_hdu_kind kind;
    int bitpix, naxis;
    size_t axes[3];                /* Unused dimensions are zero. */
    double bscale, bzero;          /* FITS defaults 1/0 when absent. */
    int has_bscale, has_bzero, has_extname, has_extver, extver;
    int has_bin_x, has_bin_y, bin_x, bin_y;
    char extname[MEF_LAYOUT_TEXT], reported_id[MEF_LAYOUT_TEXT];
    char amplifier[MEF_LAYOUT_TEXT], bunit[MEF_LAYOUT_TEXT];
    /* Raw geometry evidence, not a verified hardware/active-area model. */
    char datasec[MEF_LAYOUT_TEXT], detsec[MEF_LAYOUT_TEXT], ccdsec[MEF_LAYOUT_TEXT];
} mef_hdu_layout;

typedef struct {
    const char *detector_id;       /* Explicit stable logical ID, never an ordinal. */
    const char *physical_id;       /* Optional configured claim, not hardware verification. */
    int hdu_index;                 /* >=0 explicit; -1 requires expected_header_id. */
    const char *expected_header_id;
    const char *extname;           /* Optional independent assertion. */
    int has_extver, extver;        /* No absent EXTVER is fabricated. */
    const char *unit;              /* Explicit fallback if BUNIT absent; conflicts fail. */
    const char *readout_id;        /* Explicit configured readout/geometry context,
                                   * including detector origin/orientation. */
    int bin_x, bin_y;              /* Explicit positive configured binning. */
    /* Explicit FITS-1-based active rectangle. Science may include scans while
     * a calibration already contains only the trimmed active plane. */
    int active_x, active_y, active_width, active_height;
    size_t configuration_detector; /* Configuration index, independent of HDU/ID. */
    mef_detector_health health;
    mef_detector_selection selection;
} mef_detector_binding;

typedef struct {
    mef_hdu_layout image;
    char detector_id[MEF_LAYOUT_TEXT], physical_id[MEF_LAYOUT_TEXT];
    char unit[MEF_LAYOUT_TEXT], readout_id[MEF_LAYOUT_TEXT];
    int unit_from_header, identity_header_matched;
    int bin_x, bin_y;
    int active_x, active_y, active_width, active_height;
    size_t configuration_detector;
    mef_detector_health health;
    mef_detector_selection selection;
} mef_bound_detector;

/* Bounded header-only catalogue. Uses existing qfits card parsing; no arrays,
 * writes, association or hardware-ID inference. Currently Mac/Linux absolute
 * paths and regular immutable files; source identity is checked before/after.
 * Existing qfits owns headers/offsets; no second FITS framing parser here.
 * Limits: 4096 HDUs, 16 MiB header bytes; NAXIS<=3, no random groups.
 * Existing int offset APIs limit files to INT_MAX bytes; larger files fail
 * explicitly. The bounded raw-image profile excludes nonzero PCOUNT/heaps
 * and GCOUNT other than one. No general large-file/table migration is claimed.
 * Caller freezes files during read/bind/load; this is not a snapshot lock.
 * Owners use the selected allocator. Error starts NULL; occupied outputs/error
 * are rejected intact. Status remains authoritative if error allocation fails.
 */
mef_status mef_layout_read(const char *path, const mef_layout_options *options,
    const mef_allocator *allocator, mef_layout **out, mef_error **error);
void mef_layout_destroy(mef_layout *layout);
const mef_hdu_layout *mef_layout_hdus(const mef_layout *layout, size_t *count);
const char *mef_layout_path(const mef_layout *layout);

/* Each file binds independently. Selected image must be two-dimensional;
 * duplicate IDs/HDUs, missing/ambiguous identity or inconsistent selectors fail.
 * Map owns its path/metadata and outlives the catalogue and caller descriptors.
 * All entries, including excluded ones, are returned in original file HDU order.
 * Health, output selection and later processing outcome remain independent.
 * Multiple HDUs/amplifiers for one detector are unsupported by this first map;
 * explicit amplifier/geometry evidence remains available, never reassembled here.
 */
mef_status mef_layout_bind(const mef_layout *layout,
    const mef_detector_binding *bindings, size_t count,
    const mef_allocator *allocator, mef_layout_map **out, mef_error **error);
void mef_layout_map_destroy(mef_layout_map *map);
const mef_bound_detector *mef_layout_map_view(const mef_layout_map *map, size_t *count);
const mef_bound_detector *mef_layout_find(const mef_layout_map *map, const char *id);

/* Caller supplies already selected calibrations and their intended units.
 * Pair by logical ID, not position. Check every selected output plus separately
 * required normalization reference (which may be excluded from output).
 * Units/readout/binning/shape must be explicitly compatible. Flat units can
 * differ from science units: each expected unit is supplied, never inferred.
 * Reference availability does not choose or change a normalization algorithm.
 */
mef_status mef_layout_compatible(const mef_layout_map *science,
    const mef_layout_map *calibration, const char *science_unit,
    const char *calibration_unit, const char *normalization_reference,
    mef_error **error);

/* Reuse image_loadext(path,index,0,1), its scaling and allocation owner.
 * One existing working-plane allocation/conversion; no new full-frame copy.
 * Returned image is destroyed with image_del, not the map allocator.
 * No result completion state is fabricated. Unknown units are metadata only:
 * the numerical caller must establish its required unit/correction contract.
 * qfits/Eclipse globals are unchanged; no new thread-safety/OOM guarantee.
 */
mef_status mef_layout_load(const mef_layout_map *map, const char *detector_id,
    image_t **out, mef_error **error);
#endif
