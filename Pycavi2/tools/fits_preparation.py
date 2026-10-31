"""Shared bounded FITS header/copy primitives; no classification or camera policy."""
import hashlib
import json
from astropy.io import fits

MAX_HEADER = 256 * 1024

def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stamp(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_mode]


def raw_header(path):
    """Read bounded complete primary header blocks; retain original card bytes."""
    blocks = bytearray()
    with path.open("rb") as stream:
        while len(blocks) + 2880 <= MAX_HEADER:
            block = stream.read(2880)
            require(len(block) == 2880, "Truncated primary header")
            blocks.extend(block)
            for offset in range(0, 2880, 80):
                if block[offset:offset + 8] == b"END     ":
                    end = len(blocks) - 2880 + offset
                    require(block[offset + 8:] == b" " * (2880 - offset - 8),
                            "Nonblank bytes after END")
                    return bytes(blocks), end
    raise ValueError("Primary header exceeds limit")


def outside(path, root):
    return not path.resolve().is_relative_to(root.resolve())


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=True)
        stream.write("\n")


def copy_prepared(source, target, record, plan_sha, history="Bath DPR prep plan "):
    """Insert cards at byte level; copy and independently verify opaque payload."""
    raw, end = raw_header(source)
    cards = [raw[i:i + 80] for i in range(0, end, 80)]
    preserved = [c for c in cards if c[:8] not in (b"CHECKSUM", b"DATASUM ")]
    old = fits.Header.fromstring(raw.decode("ascii"), sep="")
    added = [fits.Card(key if len(key) <= 8 else "HIERARCH " + key, value).image.encode("ascii")
             for key, value in record.get("additions", record["classification"]).items() if key not in old]
    added.append(fits.Card("HISTORY", history + plan_sha[:32]).image.encode("ascii"))
    new_header = b"".join(preserved + added) + b"END" + b" " * 77
    new_header += b" " * ((-len(new_header)) % 2880)
    full_source, payload = hashlib.sha256(), hashlib.sha256()
    target.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, target.open("xb") as dst:
        prefix = src.read(len(raw))
        require(prefix == raw, "Source header changed before copy")
        full_source.update(prefix)
        dst.write(new_header)
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            full_source.update(chunk)
            payload.update(chunk)
            dst.write(chunk)
    output_payload, full_output = hashlib.sha256(), hashlib.sha256()
    with target.open("rb") as stream:
        require(stream.read(len(new_header)) == new_header, "Prepared header mismatch")
        full_output.update(new_header)
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            output_payload.update(chunk)
            full_output.update(chunk)
    require(output_payload.digest() == payload.digest(), "Payload bytes changed")
    out_header = fits.Header.fromstring(new_header.decode("ascii"), sep="")
    require(all(out_header[k] == v for k, v in record.get("additions", record["classification"]).items()),
            "Prepared classification mismatch")
    require(stamp(source) == record["source_stat"], "Source changed during copy")
    return {"file": record["file"], "source_sha256": full_source.hexdigest(),
            "prepared_sha256": full_output.hexdigest(),
            "payload_sha256": payload.hexdigest(), "data_offset": len(new_header),
            "removed_cards": record["checksum_cards_removed_in_copy"]}
