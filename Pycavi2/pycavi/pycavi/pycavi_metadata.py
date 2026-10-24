"""Science exposure metadata at the detector and coaddition boundaries.

These routines change headers only. They neither normalize pixels nor supply a
photometric calibration or an effective gain/noise model. Native causes: #23/#24.
"""
import math
import os
from pathlib import Path
import shutil
import tempfile

from astropy.io import fits
from astropy.time import Time, TimeDelta


# Deliberately exclude WCS, structural cards, detector identity and detector gain.
_EXPOSURE_KEYS = ("DATE-OBS", "MJD-OBS", "MJD-END", "EXPTIME", "TIMESYS",
                  "BUNIT", "ONEADU", "SATLEVEL", "FILTER", "OBJECT", "ORIGIN",
                  "PRODCATG", "ESO PYCAVI ORIGSAT", "ESO PYCAVI LIGHTCOR")


def science_exposure_header(primary):
    """Return an independent primary header with a binary64 exposure endpoint.

    MJD-OBS and EXPTIME in the science primary are authoritative. Inherited
    MJD-END is intentionally recomputed (native binary32 endpoints are defective).
    The existing workflow uses UTC when TIMESYS is absent.
    """
    header = primary.copy()
    start, duration = float(header["MJD-OBS"]), float(header["EXPTIME"])
    if not math.isfinite(start) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Science MJD-OBS must be finite and EXPTIME positive")
    scale = str(header.get("TIMESYS", "UTC")).strip().lower()
    if scale != "utc":
        raise ValueError("Science metadata correction currently requires UTC")
    # Time/TimeDelta preserves elapsed seconds even across a UTC leap second.
    end = float((Time(start, format="mjd", scale=scale)
                 + TimeDelta(duration, format="sec")).mjd)
    header["MJD-END"] = (end, "Exposure end from science MJD-OBS and EXPTIME")
    header["TIMESYS"] = ("UTC", "Time reference system")
    if "DATE-OBS" not in header:
        header["DATE-OBS"] = Time(start, format="mjd", scale=scale).isot
    for key in ("CHECKSUM", "DATASUM"):
        header.remove(key, ignore_missing=True, remove_all=True)
    return header


def detector_science_header(detector, primary):
    """Overlay exposure-level metadata; preserve the detector's WCS and gain."""
    science = science_exposure_header(primary)
    header = detector.copy()
    for key in _EXPOSURE_KEYS:
        if key in science:
            header[key] = (science[key], science.comments[key])
        elif key in header:
            # Do not retain metadata inherited from a calibration when the
            # authoritative science primary does not provide that exposure key.
            del header[key]
    for key in ("CHECKSUM", "DATASUM"):
        header.remove(key, ignore_missing=True, remove_all=True)
    return header


def copy_science_metadata(source, destination):
    """Create a fresh corrected MEF copy, reusing pixels and solved WCS as-is.

    Neither source nor an existing destination is modified. Raw FITS storage is
    copied before header edits, avoiding rescaling BSCALE/BZERO image arrays.
    The destination is published atomically, without clobbering another writer.
    """
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    with fits.open(source, do_not_scale_image_data=True) as hdus:
        primary = science_exposure_header(hdus[0].header)
        names = [h.header.get("EXTNAME") for h in hdus[1:]
                 if isinstance(h, fits.ImageHDU)]
        if hdus[0].data is not None or not names or None in names or len(set(names)) != len(names):
            raise ValueError("Expected a science MEF with unique named image detectors")
    fd, temporary = tempfile.mkstemp(prefix=".pycavi-metadata-", dir=destination.parent)
    os.close(fd)
    try:
        shutil.copyfile(source, temporary)
        with fits.open(temporary, mode="update", do_not_scale_image_data=True) as hdus:
            hdus[0].header = primary
            for hdu in hdus[1:]:
                if isinstance(hdu, fits.ImageHDU):
                    hdu.header = detector_science_header(hdu.header, primary)
            for hdu in hdus:
                hdu.header.remove("CHECKSUM", ignore_missing=True, remove_all=True)
                hdu.header.remove("DATASUM", ignore_missing=True, remove_all=True)
                hdu.add_checksum()
        os.link(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return str(destination)


def coadd_observation_metadata(images):
    """Summarize unique science MEFs, never multiplying integration by detectors.

    EXPTIME and GAIN are deliberately absent: SWarp calculates equivalent
    exposure/noise properties. TEXPTIME is the sum of input exposure durations,
    not the time span, per-pixel coverage, or a median-stack noise estimate.
    """
    paths = [Path(image).resolve() for image in images]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("Coadd inputs must be a nonempty list of distinct science MEFs")
    headers = [science_exposure_header(fits.getheader(path, 0)) for path in paths]
    for key in ("BUNIT", "FILTER", "OBJECT", "ORIGIN"):
        values = [h.get(key) for h in headers]
        if any(v is None for v in values) or len(set(values)) != 1:
            raise ValueError("Coadd inputs require a common {}".format(key))
    first = min(headers, key=lambda h: float(h["MJD-OBS"]))
    result = fits.Header()
    for key in ("BUNIT", "FILTER", "OBJECT", "ORIGIN", "TIMESYS", "DATE-OBS", "MJD-OBS"):
        result[key] = (first[key], first.comments[key])
    result["MJD-END"] = (max(float(h["MJD-END"]) for h in headers), "Latest contributing exposure end")
    result["TEXPTIME"] = (math.fsum(float(h["EXPTIME"]) for h in headers), "Sum of input exposure times (s)")
    result["NCOMBINE"] = (len(paths), "Number of contributing science exposures")
    return result


def calibrated_saturation_cards(satlevel, cumulative_factor, magzp,
                               input_saturate=None, input_factor=None):
    """Saturation cards in calibrated pixel units, without a new noise model.

    satlevel is the existing mean from normalized parent exposures; it needs
    the cumulative e-/s-to-flux factor. input_saturate is SWarp's saturation
    in the current input image units and needs only this run's incremental
    factor. For header-only repair from an uncalibrated coadd, both factors
    are the cumulative factor (input_factor defaults to it).

    MAGSATL retains the existing pixel-level expression; it is not a measured
    point-source saturation magnitude or a Phase 3 ABMAGSAT determination.
    """
    cumulative_factor = float(cumulative_factor)
    input_factor = cumulative_factor if input_factor is None else float(input_factor)
    magzp = float(magzp)
    if (not math.isfinite(cumulative_factor) or cumulative_factor <= 0
            or not math.isfinite(input_factor) or input_factor <= 0
            or not math.isfinite(magzp)):
        raise ValueError("Calibration factors must be finite and positive; MAGZP finite")

    def scaled(value, factor):
        try:
            value = float(value)
        except (ValueError, TypeError):
            return "UNKNOWN"
        value *= factor
        return value if math.isfinite(value) and value > 0 else "UNKNOWN"

    result = fits.Header()
    level = scaled(satlevel, cumulative_factor)
    result["SATLEVEL"] = (level, "Parent mean saturation, calibrated units")
    magnitude = "UNKNOWN" if level == "UNKNOWN" else round(magzp - 2.5 * math.log10(level), 3)
    result["MAGSATL"] = (magnitude, "Pixel diagnostic, not point-source limit")
    if input_saturate is not None:
        result["SATURATE"] = (scaled(input_saturate, input_factor),
                              "SWarp saturation in calibrated pixel units")
    return result
