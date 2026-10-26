# Qualified fixture origin

These files are preserved byte-for-byte from Fernando's Mac-qualified archive,
SHA256 16f0bba19bb09e2f3d8e8626b8f4c4d5d51c3b7d2aec9b29e9a84b8e8e2afa7a.
transfer-manifest.json records the original driver, Mac report and eight inputs.
README.md is the only newly added file in this fixture directory.

Each order contains three synthetic four-detector MEF FITS inputs. A 9x18 raw
extension has a 9x9 science region and zero overscan. Plane illumination levels
are 1,2,4; the central pixel has twice its background response. No observational
images or external reference catalogues are present.

The driver invokes actual mef_build_cal and checks exact shared normalization,
not a replacement implementation. Run through tests/shared_normalization_contract.py
from CTest; do not use this source directory as a writable working directory.

See docs/developer/shared-normalization-regression.md for acceptance limits.
