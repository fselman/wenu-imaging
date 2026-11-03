#!/bin/bash
# Display MEF extensions in a matched 4x2 DS9 view, without WCS alignment.
# Usage: tools/ds9-mosaic.sh /path/to/image.fits
set -eu

if [ "$#" -eq 1 ]; then
    case "$1" in
        -h|--help)
            printf 'Usage: %s FILE.fits\n' "$0"
            exit 0
            ;;
    esac
fi
if [ "$#" -ne 1 ]; then
    printf 'Usage: %s FILE.fits\n' "$0" >&2
    exit 2
fi

image=$1
case "$image" in
    /*) ;;
    *) image="$PWD/$image" ;;
esac
if [ ! -f "$image" ] || [ ! -r "$image" ]; then
    printf 'Cannot read FITS file: %s\n' "$image" >&2
    exit 1
fi

exec open -n -a SAOImageDS9 --args \
    -multiframe "$image" \
    -tile yes -tile mode grid -tile grid mode manual \
    -tile grid layout 4 2 \
    -frame 1 -zoom to fit -scale linear -scale mode zscale -cmap grey \
    -match frame image -match scale -match scalelimits -match colorbar \
    -lock frame image -lock scale yes -lock scalelimits yes -lock colorbar yes
