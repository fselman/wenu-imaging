"""S2-05 supplied-bias fixtures and exact accepted-mask oracle (#75).

Add a deterministic trimmed bias only to the science area; preserve overscan,
headers and padding. Subtracting it in production must restore accepted masks.
"""
import hashlib
import numpy as np
from bpm_metadata_cases import prepare as prepare_metadata, verify as verify_metadata


def bias_pixels():
    y, x = np.indices((9, 9))
    bias = (16 + 8 * y + 2 * x).astype(np.float32)
    # A localized large residual makes a skipped subtraction visible to the
    # proportional regression; this pixel is good in the accepted mask.
    bias[4, 5] = 4096
    return bias


def prepare(root, fixture, kind):
    # Deterministic additive fixtures: immutable parent metadata/payload checked.
    prepare_metadata(root, fixture, kind)
    bias = bias_pixels()
    for i in range(3):
        path = root / ("frame%d.fits" % i)
        raw = path.read_bytes()
        data = np.frombuffer(raw[5760:6408], dtype=">f4").reshape(9, 18).copy()
        original = data[:, :9].copy()
        data[:, :9] += bias
        if not np.array_equal(data[:, :9] - bias, original):
            raise RuntimeError("Additive bias lost input float precision")
        path.write_bytes(raw[:5760] + data.astype(">f4").tobytes() + raw[6408:])
    # Minimal primary-image FITS: the native image_load supplies a caller-owned image.
    from bpm_metadata_cases import make_card
    cards = ["SIMPLE  =                    T".ljust(80), make_card("BITPIX", -32),
             make_card("NAXIS", 2), make_card("NAXIS1", 9), make_card("NAXIS2", 9),
             "END".ljust(80)]
    header = "".join(cards).encode("ascii").ljust(2880, b" ")
    (root / "bias.fits").write_bytes(header + bias.astype(">f4").tobytes().ljust(2880, b"\0"))
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.iterdir()) if p.is_file() and p.name != "run-provenance.json"}


def verify(root, inputs, reference, flag, previous):
    # Exact accepted output and metadata: bias subtraction introduces no output change.
    outputs, origfiles = verify_metadata(root, inputs, reference, flag, previous)
    if outputs != previous:
        raise RuntimeError("Supplied-bias output differs from accepted metadata reference")
    return outputs, origfiles
