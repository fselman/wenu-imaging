# OCAM readout geometry and analogous ROIs — 3 November 2026

The owner's ocam_field_geometry_for_HC.png fixes the detector identity/native
number/mosaic position mapping. The blue numbers match the original raw-HDU and
native PAF CHIP numbers in the selected March 2017 sequence, not Python .cfg entry
order. This resolves that configuration-slot association for this reference
sequence. Future files still bind independently by identity: a reordered HDU must
not change the detector's PAF slot.

ESO's period-96 manual, section 2.2.1, states that each CCD is read through its
manufacturer-designated left output. The lower-half register is at the bottom;
the upper half is rotated 180 degrees. The PAF's reversed prescan/overscan sides
and cropped vertical ranges agree with this geometry. Therefore manufacturer
output L does not mean the amplifier appears on the left of every displayed CCD.
For the upper half it appears at the upper-right in the supplied mosaic.

## Mapping and coordinates

All bounds below are FITS 1-based inclusive. The present native crop returns
2044 columns by 4091 rows; that retained area is smaller than the full illuminated
2048 x 4100 area reported in the detector headers. These must remain distinct.

| Mosaic half | CCD identities | Native PAF CHIP numbers | Readout corner in supplied mosaic | Raw crop X | Raw crop Y | Serial overscan X |
|---|---|---|---|---|---|---|
| Lower two rows | #65–#80 | 1–8, 17–24 | lower-left | 51–2094 | 5–4095 | 2100–2142 |
| Upper two rows | #81–#96 | 9–16, 25–32 | upper-right | 51–2094 | 105–4195 | 5–48 |

Within each row, the supplied diagram gives the following explicit map:

| Mosaic row, bottom to top | CCD identities, left to right | Native CHIP numbers, left to right |
|---|---|---|
| 1 | 65,66,67,68,69,70,71,72 | 1,2,3,4,17,18,19,20 |
| 2 | 73,74,75,76,77,78,79,80 | 5,6,7,8,21,22,23,24 |
| 3 | 81,82,83,84,85,86,87,88 | 9,10,11,12,25,26,27,28 |
| 4 | 89,90,91,92,93,94,95,96 | 13,14,15,16,29,30,31,32 |

Define readout-relative coordinates u,v starting at the readout-nearest corner of
the RETAINED active area, with both coordinates increasing away from that corner.
They describe equivalent positions within the retained area; they are not exact
full-device charge-transfer counts or physical amplifier coordinates.

Let x,y be ordinary retained-active FITS coordinates. Then:

| Half | Active coordinates from u,v | Raw FITS coordinates from u,v |
|---|---|---|
| Lower | x=u; y=v | Xraw=50+u; Yraw=4+v |
| Upper | x=2045−u; y=4092−v | Xraw=2095−u; Yraw=4196−v |

For rectangle endpoints, reflect and reorder: upper xmin=2045−umax and
xmax=2045−umin; ymin=4092−vmax and ymax=4092−vmin. Keep the stored images and BPM
in their original orientation. Only the region bounds are reflected. This uses
native crop geometry; no resampling, rotating arrays or WCS dependence is needed.
The readout-nearest retained pixel is raw (51,5) below and (2094,4195) above; the
physical amplifier is outside that retained pixel rectangle.

## Dataset-specific first-pass ROI proposal

Use five nonoverlapping 512 x 512 regions per detector, with the four corner
regions inset 128 retained pixels from their respective edges. Coordinates here
are u,v, so the names have the same readout-relative meaning on every detector:

| ROI suffix | u bounds | v bounds | Purpose |
|---|---|---|---|
| near_readout | 129–640 | 129–640 | near both readout directions |
| serial_far | 1405–1916 | 129–640 | far in serial direction, near parallel register |
| parallel_far | 129–640 | 3452–3963 | near serial output, far in parallel direction |
| far_corner | 1405–1916 | 3452–3963 | far in both directions |
| center | 767–1278 | 1790–2301 | central comparison region |

For example CCD65.near_readout is active x=129–640,y=129–640; the analogous
CCD96.near_readout is x=1405–1916,y=3452–3963. The central rectangle is reflected
using the same exact rule, including the one-pixel asymmetry arising from an odd
4091-row retained area and an even 512-row rectangle.

This is an explicit initial measurement configuration, not a universal instrument
default or a claim that all regions are clean. Each rectangle remains configurable
per detector. Five regions distinguish central/edge behavior and distances along
both readout directions while leaving the readout-adjacent borders out of the
first pass. Review the spatial measurements for illumination structure and
cosmetic defects; do not replace actual pixels by one fictitious ROI pixel in
later linearity fitting. Shared flats/biases still correlate the measured rows.

## Saved configuration and validation

- [TOML ROI supplement](../../config/characterization/omegacam-20170313-rois.toml)
- [Equivalent PAF ROI supplement](../../config/characterization/omegacam-20170313-rois.paf)
- [Explicit geometry/identity map](../../config/characterization/omegacam-20170313-geometry.json)

There are 160 unique named regions, five for each exact ESO_CCD_# identity, with
amplifier label L. The geometry file records native CHIP/configuration index,
reference original HDU, mosaic row/column, raw crop, both scan ranges and coordinate
signs. Full raw-header checks must still confirm each selected output/readout;
the manual and first-two-header printout do not replace those admission checks.

Preparation validated all 32 PAF associations, all rectangle sizes/bounds and
within-detector nonoverlap, exact CCD65/CCD96 reflection examples, and TOML
serialization roundtrip. This is configuration/geometry validation, not a new
native or real-data numerical qualification. The exact-identity parser itself
passed actual Mac C17 at f02eb695, 1/1 in 1.27 s total (#230 closed).
No raw observations or new fitter run were used to define these rectangles.

Saturation and bias-pair choices remain separate from this geometry definition.
Actual retained measurement products must go under an appropriately named
~/Pictures/OCAM/wenu-imaging subdirectory with a purpose/deletion README. Build
work remains subject to the closeout retention review.

Sources: owner-supplied mosaic PNG (SHA256 in geometry JSON); repository
mefpp2/ins/mef/config/omegacam.paf (exact SHA256 in geometry JSON); actual Mac
30-file header inventory; [ESO OmegaCAM manual, period 96, section 2.2.1](https://www.eso.org/sci/facilities/paranal/instruments/omegacam/doc/VST-MAN-OCM-23100-3110_p96.pdf).
