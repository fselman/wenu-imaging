# Detector footprints and processing regions

The owner's request adds two separate editable TOMLs per instrument and a small
read-only configuration viewer. This does not migrate or activate native processing
configuration. Existing native PAF/TOML readers and reduction numerics are unchanged.

| Instrument | Detector geometry | Processing choices |
|---|---|---|
| OCAM | `config/detectors/omegacam-1x1.toml` | `config/processing/omegacam-characterization.toml` |
| WFI | `config/detectors/wfi-1x1.toml` | `config/processing/wfi-characterization.toml` |

Detector files contain the 1x1 raw footprint, nominal illuminated/valid window,
full prescan/overscan bands, exact detector/output identities, amplifier corner,
and explicit mosaic row/column. Processing files contain the native PAF crop and
scan sample ranges, enabled scan policies/rejection counts, and candidate named
ROIs in retained-active coordinates. These two visualization schemas are not
interchangeable with native reduction configuration files. The existing native ROI
profile remains available under `config/characterization`.

## Run on the Mac

From an exported source tree or checkout containing these files:

```sh
WENU_IMAGING_PYTHON=/Users/fselman/anaconda3/envs/wenu-imaging/bin/python \
  sh tools/view-detector-footprints.sh ocam
WENU_IMAGING_PYTHON=/Users/fselman/anaconda3/envs/wenu-imaging/bin/python \
  sh tools/view-detector-footprints.sh wfi
```

The wrapper opens the HTML in the default browser and prints its path. It creates
a small new review directory under `~/Pictures/OCAM/wenu-imaging/` or
`~/Pictures/WFI/wenu-imaging/`, with a README explaining purpose and deletion
conditions. It neither reads FITS data nor changes installed software. Python 3.11+
uses only the standard library; older Python needs tomli. No plotting packages,
web server, internet connection or WCS are needed by the viewer.

For custom files or an explicit destination:

```sh
python3 tools/detector-footprint.py DETECTORS.toml PROCESSING.toml \
  --output /path/to/new-footprints.html --open
```

An existing output is refused. Click a mosaic panel or select an exact detector
identity to inspect it. The detailed diagram supports 1x/2x/4x/8x magnification and
scrolling; hover over rectangles for raw bounds. Tables show all boundaries and
numbered ROI names. Print/save PDF uses the browser. Mosaic gaps are schematic,
while each raw footprint keeps its true pixel aspect ratio and FITS orientation.
Changing mosaic positions does not rotate the detector arrays or swap scan sides.

All rectangles are **FITS 1-based inclusive** `[xmin,xmax,ymin,ymax]`. ROIs are
stored relative to the retained crop and translated to raw pixels only for display.
The blue outline encloses the retained area after trimming; everything outside
is discarded. The full illuminated window is green, full prescan purple, full
overscan orange, and extra rows outside the illuminated Y extent grey. Dashed
outlines show the narrower configured scan sample rectangles. Scan bands span
all raw rows, including their intersections with extra rows. Thin regions remain
thin at true scale: use detail magnification and the coordinate table.

A red square marks the configured output corner outside the raw pixel array.
It is a schematic marker, not a measured amplifier-package coordinate. This
explicit distinction avoids calling the nearest retained pixel the amplifier.

## Reference geometry and limits

OCAM uses the owner's labelled mosaic and the period-96 manual, section 2.2.1:
https://www.eso.org/sci/facilities/paranal/instruments/omegacam/doc/VST-MAN-OCM-23100-3110_p96.pdf
Raw size 2144x4200; nominal valid window 2048x4100, after 48 serial prescan
samples and with 100 extra rows at the opposite end. Upper-half detectors have
the opposite displayed corner. The retained PAF crop is only 2044x4091. The five
512x512 ROIs match the earlier OCAM proposal exactly.

WFI uses the Handbook 2.0, section 2.2.6 and its extension-header examples:
https://www.eso.org/sci/facilities/lasilla/instruments/wfi/doc/2P2-MAN-ESO-90100-0001.pdf
Raw size 2142x4128; the header-valid window is 2046x4098, with 48 serial samples
on each side and 30 extra rows. Here “illuminated” means this nominal valid data
window, not a measured illumination mask or the physical silicon dimensions.
Top-row outputs are upper-left. Physical CCD57 (`WIN1.CHIP5.OUT2`) is lower-left
and uses R; CCD54/55/56 are lower-right and use L. Top row, left to right:
WIN1.CHIP1/2/3/4.OUT1; bottom row: WIN1.CHIP5.OUT2, CHIP6/7/8.OUT1.
The selected May-2003 raw HDU order differs from that spatial order: 1,2,3,4,8,7,6,5.
Native PAF CHIP slots follow that reference HDU sequence in the accepted bias run.
The WFI crop is 2044x4097. Its five analogous ROIs are a new inspection proposal,
not scientifically accepted characterization regions.

These reference geometries must be checked against the actual selected raw
headers/readout/binning before numerical use. A reference HDU is not a future
identity-binding rule. The viewer rejects mismatched instruments, duplicate
identities/positions, missing trims, invalid/out-of-bounds rectangles, scan samples
outside full bands, unknown ROI detectors and mismatched amplifier bindings.

## Validation, 3 November 2026

Four Python regression checks pass: all 40 detector crops and scan selections
against the current PAFs, independent named OCAM reflections, WFI exceptional
output/spatial-order landmarks, and refusal of cross-instrument or out-of-bounds
ROI inputs. Both complete SVG mosaics were rasterized with librsvg and visually
inspected. HTML JavaScript selection/zoom passed a mocked-DOM execution check.
A real headless Chromium launch was blocked by this host's socket restrictions;
interactive browser confirmation on the Mac remains pending. No native test replay,
Mac reduction, calibration product or scientific fit was performed.
