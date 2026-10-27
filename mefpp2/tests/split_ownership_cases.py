"""S2-04 synthetic split inputs and independent byte-level output checks (#75)."""
import hashlib
from pathlib import Path
import resource
import signal
import struct


def card(key, value=None):
    text = key if value is None else f"{key:<8}= {value:>20}"
    return text.ljust(80).encode("ascii")


def header(cards):
    block = b"".join(cards + [card("END")])
    return block + b" " * (-len(block) % 2880)


def mosaic(path):
    primary = header([card("SIMPLE", "T"), card("BITPIX", "8"),
                      card("NAXIS", "0"), card("EXTEND", "T"),
                      card("OBJECT", "'synthetic'")])
    blocks = [primary]
    for name, values in (("CCD_A", (1, 2, 3, 4, 5, 6)),
                         ("CCD_B", (-1, -2, -3, -4, -5, -6))):
        blocks.append(header([
            card("XTENSION", "'IMAGE   '"), card("BITPIX", "16"),
            card("NAXIS", "2"), card("NAXIS1", "3"), card("NAXIS2", "2"),
            card("PCOUNT", "0"), card("GCOUNT", "1"), card("EXTNAME", repr(name)),
        ]))
        data = struct.pack(">6h", *values)
        blocks.append(data + b"\0" * (-len(data) % 2880))
    path.write_bytes(b"".join(blocks))


def cases():
    # Existing split semantics plus bounded corrupt/geometry/list cases.
    return ("valid-relative", "valid-absolute", "explicit-paf-spaces", "valid-list",
            "missing-input", "non-fits", "invalid-geometry", "truncated-data",
            "partial-publish", "failed-write")


def prepare(root, original_paf, variant):
    paf = root / "mefpp.paf"
    paf.write_text(original_paf)
    raw = root / "mosaic.fits"
    args = ["--split", raw.name]
    expected_exit, diagnostic = 0, None
    expected_outputs = [1, 2]
    if variant == "missing-input":
        args = ["--split", "missing.list"]
        expected_exit, diagnostic, expected_outputs = 1, "missing.list", []
    elif variant == "non-fits":
        raw.write_bytes(b"not-a-fits-file\n")
        expected_exit, diagnostic, expected_outputs = 1, "FITS", []
    else:
        mosaic(raw)
        if variant == "valid-absolute":
            args = ["--split", str(raw)]
        elif variant == "explicit-paf-spaces":
            directory = root / "configuration with spaces"
            directory.mkdir()
            chosen = directory / "chosen.paf"
            paf.rename(chosen)
            args += ["--pafname", str(chosen)]
        elif variant == "valid-list":
            (root / "frames.list").write_text("mosaic.fits\n")
            args = ["--split", "frames.list"]
        elif variant == "invalid-geometry":
            data = bytearray(raw.read_bytes())
            target = card("NAXIS1", "3")
            offset = data.find(target, 2880, 5760)
            if offset < 0:
                raise RuntimeError("Geometry card absent")
            data[offset:offset+80] = card("NAXIS1", "0")
            raw.write_bytes(data)
            expected_exit, diagnostic, expected_outputs = 1, "geometry", []
        elif variant == "truncated-data":
            # First extension header is intact; its advertised pixels are absent.
            raw.write_bytes(raw.read_bytes()[:5760])
            expected_exit, diagnostic, expected_outputs = 1, "data", []
        elif variant == "partial-publish":
            blocker = root / "mosaic_02.fits"
            blocker.mkdir()
            (blocker / "sentinel").write_bytes(b"preserve")
            expected_exit, diagnostic, expected_outputs = 1, "publish", [1]
        elif variant == "failed-write":
            expected_exit, diagnostic, expected_outputs = 1, "output", []
    return args, expected_exit, diagnostic, expected_outputs


def restrict_output():
    # Ordinary CLI only; the observer applies/restores the same soft limit in C.
    _, maximum = resource.getrlimit(resource.RLIMIT_FSIZE)
    signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
    resource.setrlimit(resource.RLIMIT_FSIZE, (4096, maximum))


def input_hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and p.name != "run-provenance.json"}


def read_output(path, index):
    # Independent FITS readback: reference cards, big-endian pixels and padding.
    data = path.read_bytes()
    if len(data) != 5760:
        raise RuntimeError("Unexpected split length: " + path.name)
    cards = [data[i:i+80] for i in range(0, 2880, 80)]
    end = next(i for i, row in enumerate(cards) if row[:8].strip() == b"END")
    parsed = {}
    for row in cards[:end]:
        if row[8:10] == b"= ":
            key = row[:8].decode().strip()
            if key in parsed:
                raise RuntimeError("Duplicate output header key: " + key)
            parsed[key] = row[10:].decode().split("/", 1)[0].strip().strip("'").strip()
    expected = dict(SIMPLE="T", BITPIX="16", NAXIS="2", NAXIS1="3", NAXIS2="2",
                    OBJECT="synthetic", EXTNAME="CCD_A" if index == 1 else "CCD_B")
    if any(parsed.get(k) != v for k, v in expected.items()):
        raise RuntimeError("Unexpected split metadata: " + repr(parsed))
    values = list(struct.unpack(">6h", data[2880:2892]))
    wanted = [i if index == 1 else -i for i in range(1, 7)]
    if values != wanted or data[2892:] != b"\0" * (5760 - 2892):
        raise RuntimeError("Split pixel/padding mismatch")
    if "BSCALE" in parsed or "BZERO" in parsed:
        raise RuntimeError("Unexpected scaling metadata")
    return dict(name=path.name, pixels=values, metadata=expected,
                sha256=hashlib.sha256(data).hexdigest())


def verify(root, protected, expected_outputs):
    for name, sha in protected.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise RuntimeError("Staged input/sentinel changed: " + name)
    if list(root.rglob("*.tmp.*")):
        raise RuntimeError("Unfinished temporary split output")
    outputs = [read_output(root / ("mosaic_%02d.fits" % i), i) for i in expected_outputs]
    permitted = set(protected) | {"run-provenance.json"} | {x["name"] for x in outputs}
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    if actual != permitted:
        raise RuntimeError("Unexpected/missing files: " + repr(sorted(actual ^ permitted)))
    return outputs

