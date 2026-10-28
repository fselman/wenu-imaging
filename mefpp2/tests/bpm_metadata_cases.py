"""S2-05 header-only derived BPM fixtures and independent metadata oracle (#75).

Keep accepted pixel payloads and original native driver/observer unchanged.
"""
import hashlib
from pathlib import Path
from bpm_ownership_cases import prepare as prepare_original, verify as verify_original

PRIMARY = [dict(ORIGIN="ESO S2 METADATA %d" % i, TELESCOP="VST-META-%d" % i,
                INSTRUME="OMEGACAM-META-%d" % i, **{
                    "MJD-OBS": 61314.125 + i * 0.25,
                    "DATE-OBS": "2026-10-01T01:02:%02d.125" % (3 + i),
                    "ESO DET WIN1 BINX": 1, "ESO DET WIN1 BINY": 1})
           for i in range(3)]
EXTENSION = {"EXTNAME": "META_CCD_17"}
CHANGED = set(PRIMARY[0]) | set(EXTENSION)


def header_block(block, values):
    """Replace/append explicit FITS cards in one fixed 2880-byte header block."""
    if len(block) != 2880:
        raise RuntimeError("Unexpected fixture header block size")
    pending = dict(values)
    cards = []
    found_end = False
    for offset in range(0, 2880, 80):
        card = block[offset:offset + 80].decode("ascii")
        key = card[:8].strip()
        if key == "END":
            found_end = True
            break
        if key == "HIERARCH":
            key = card.split("=", 1)[0].removeprefix("HIERARCH").strip()
        if key in pending:
            cards.append(make_card(key, pending.pop(key)))
        else:
            cards.append(card)
    if not found_end:
        raise RuntimeError("Missing fixture END card")
    cards += [make_card(k, v) for k, v in pending.items()]
    cards.append("END".ljust(80))
    result = "".join(cards).encode("ascii")
    if len(result) > 2880:
        raise RuntimeError("Metadata exceeds retained header block")
    return result.ljust(2880, b" ")


def make_card(key, value):
    if isinstance(value, str):
        literal = "'" + value.replace("'", "''") + "'"
    else:
        literal = str(value).rjust(20)
    prefix = "HIERARCH " + key + " = " if len(key) > 8 else key.ljust(8) + "= "
    card = prefix + literal
    if len(card) > 80:
        raise RuntimeError("Metadata card too long")
    return card.ljust(80)


def prepare(root, fixture, kind):
    # The runner first checks every immutable source fixture against its manifest.
    prepare_original(root, fixture, kind)
    for i in range(3):
        path = root / ("frame%d.fits" % i)
        raw = path.read_bytes()
        if len(raw) != 8640:
            raise RuntimeError("Unexpected retained FITS layout")
        path.write_bytes(header_block(raw[:2880], PRIMARY[i]) +
                         header_block(raw[2880:5760], EXTENSION) + raw[5760:])
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.iterdir()) if p.is_file() and p.name != "run-provenance.json"}


def verify(root, inputs, reference, flag, previous):
    """Read actual native FITS products; first-frame values must outlive input headers."""
    from astropy.io import fits
    outputs, origfiles = verify_original(root, inputs, reference, flag)
    with fits.open(root / outputs["saved_name"], memmap=False) as hdus:
        for index, hdu in enumerate(hdus):
            wanted = dict(PRIMARY[0])
            if index:
                wanted.update(EXTENSION)
            for key, value in wanted.items():
                if hdu.header.get(key) != value or hdu.header.count(key) != 1:
                    raise RuntimeError("Copied first-frame metadata mismatch: " + key)
        if "EXTNAME" in hdus[0].header:
            raise RuntimeError("Unexpected extension identity in primary header")
    # Preserve all other raw cards and card order from inspected pre-metadata run.
    for actual, prior in zip(outputs["saved_headers"], previous["saved_headers"]):
        left = [fits.Card.fromstring(card) for card in actual]
        right = [fits.Card.fromstring(card) for card in prior]
        if ([c.keyword for c in left] != [c.keyword for c in right] or
                [c.comment for c in left] != [c.comment for c in right]):
            raise RuntimeError("Header order/comment contract changed")
        if ([c.image for c in left if c.keyword not in CHANGED] !=
                [c.image for c in right if c.keyword not in CHANGED]):
            raise RuntimeError("Unrelated raw header cards changed")
    for key in ("good", "bad", "pixels_checked", "mask_pixels_sha256", "saved_name"):
        if outputs[key] != previous[key]:
            raise RuntimeError("Reference mask/product contract changed: " + key)
    outputs["metadata_source_frame"] = "frame0.fits"
    outputs["expected_primary_metadata"] = PRIMARY[0]
    return outputs, origfiles
