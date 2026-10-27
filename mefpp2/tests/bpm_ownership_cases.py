"""S2-05 retained fixture staging and independent BPM output checks (#75)."""
import hashlib
from pathlib import Path
import shutil


def prepare(root, fixture, kind):
    inputs = {}
    for path in sorted((fixture / kind).iterdir()):
        shutil.copyfile(path, root / path.name)
        inputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return inputs


def verify(root, inputs, reference, flag):
    import numpy as np
    from astropy.io import fits
    for name, sha in inputs.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise RuntimeError("Staged input changed: " + name)
    generated = [p for p in root.glob("*.fits") if p.name not in inputs and p.name != "returned.fits"]
    if len(generated) != 1:
        raise RuntimeError("Expected one production BPM")
    expected_files = set(inputs) | {"returned.fits", generated[0].name, "run-provenance.json"}
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if actual != expected_files:
        raise RuntimeError("Unexpected/missing files: " + repr(sorted(actual ^ expected_files)))
    with fits.open(root / "returned.fits", memmap=False) as returned, fits.open(generated[0], memmap=False) as saved, fits.open(root / "frame0.fits", memmap=False) as raw:
        mask = returned[0].data
        if len(returned) != 1 or len(saved) != 2 or mask.shape != (9, 9):
            raise RuntimeError("BPM HDU/geometry mismatch")
        if returned[0].header["BITPIX"] != 8 or saved[1].header["BITPIX"] != 8:
            raise RuntimeError("BPM storage type changed")
        if saved[0].data is not None or saved[1].data.shape != (9, 9):
            raise RuntimeError("Production BPM geometry mismatch")
        if not np.isin(mask, [0, 1]).all() or not np.array_equal(mask, saved[1].data):
            raise RuntimeError("Returned/saved mask polarity or pixel mismatch")
        sha = hashlib.sha256(mask.astype(np.uint8).tobytes()).hexdigest()
        good, bad = int(mask.sum()), int(mask.size - mask.sum())
        if (sha, good, bad) != (reference["mask_pixels_sha256"], reference["good"], reference["bad"]):
            raise RuntimeError("Accepted mask pixels/counts changed")
        h = saved[1].header
        extname = h["EXTNAME"]
        if extname != raw[1].header["EXTNAME"]:
            raise RuntimeError("Extension identity changed")
        for key, value in {"ESO MPP BPM PROPFLAG": flag, "ESO MPP BPM LGAINTHR": 0.5,
                           "ESO MPP BPM HGAINTHR": 1.5, "ESO MPP QC NGOODPIX": good,
                           "ESO MPP QC NBADPIX": bad}.items():
            if h[key] != value:
                raise RuntimeError("BPM metadata changed: " + key)
        for hdus in (returned, saved):
            for hdu in hdus:
                if "BSCALE" in hdu.header or "BZERO" in hdu.header:
                    raise RuntimeError("Unexpected BPM scaling")
        # Generated ORIGFILE timestamps are recorded separately, not compared.
        headers = [[card.image for card in hdu.header.cards if card.keyword != "ORIGFILE"]
                   for hdu in saved]
        origfiles = [hdu.header.get("ORIGFILE") for hdu in saved]
        if not all(isinstance(x, str) and x for x in origfiles):
            raise RuntimeError("Missing production ORIGFILE")
    return dict(good=good, bad=bad, pixels_checked=81, mask_pixels_sha256=sha,
                extension=extname, saved_name=generated[0].name, saved_headers=headers), origfiles
