#!/bin/sh
# Generate a new review directory; no FITS data is read or changed.
set -eu
case "${1:-}" in
  ocam|OCAM|omegacam) instrument=omegacam; pictures=OCAM ;;
  wfi|WFI) instrument=wfi; pictures=WFI ;;
  *) echo "Usage: $0 ocam|wfi" >&2; exit 2 ;;
esac
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
parent="$HOME/Pictures/$pictures/wenu-imaging"
mkdir -p "$parent"
review=$(mktemp -d "$parent/detector-geometry-review-XXXXXXXX")
cat > "$review/README.md" <<EOF
# Detector geometry review

This directory contains a reproducible configuration visualization for $instrument.
Use it to inspect the raw footprint, illuminated window, retained crop, scan bands,
ROIs and schematic output-amplifier corners. It contains no FITS pixels or calibration
products. Source: $root/config/detectors/$instrument-1x1.toml and
$root/config/processing/$instrument-characterization.toml.

It may be erased once the geometry review has been accepted and any resulting
configuration corrections are committed. Regenerate it with
$root/tools/view-detector-footprints.sh $instrument.
EOF
"${WENU_IMAGING_PYTHON:-python3}" -B "$root/tools/detector-footprint.py" \
  "$root/config/detectors/$instrument-1x1.toml" \
  "$root/config/processing/$instrument-characterization.toml" \
  --output "$review/footprints.html" --open
