"""Pure legacy product conventions shared by clients and read-only inspection.

Locations describe expectations, never processing or publication success. Refs #159.
"""
from pathlib import Path

NORMALIZED_UNIT = "e-/s"


def wcs_product_path(preprocessed):
    """Preserve create_wcs_frame's basename/sibling-directory convention."""
    path = Path(preprocessed)
    stem = path.name[:-5]
    return path.parent / stem / (stem + "_wcs.fits")


def science_product_paths(raw, partition):
    """Native output naming; normalization updates that same file in place."""
    preprocessed = Path(partition) / (Path(raw).stem + "_pre.fits")
    return {"preprocessing": preprocessed, "normalization": preprocessed,
            "wcs": wcs_product_path(preprocessed)}
