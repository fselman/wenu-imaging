"""Python-only S2-05/#75 fixture/oracle checks; never native acceptance.

Run with --work pointing to a new retained directory outside the checkout.
Constructed products test the oracle, not production calibration algorithms.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from astropy.io import fits
from bpm_bias_cases import prepare, verify, bias_pixels
from qualify_mac_leaks import digest, save


def verify_inputs(root, fixture, kind):
    # Independent Astropy readback, including headers, overscan and padding.
    from bpm_metadata_cases import header_block, PRIMARY, EXTENSION
    with fits.open(root / "bias.fits", memmap=False) as hdus:
        if (len(hdus) != 1 or hdus[0].header["BITPIX"] != -32 or
                "BSCALE" in hdus[0].header or "BZERO" in hdus[0].header or
                not np.array_equal(hdus[0].data, bias_pixels())):
            raise RuntimeError("Declared bias pixels/type changed")
    for i in range(3):
        path = root / ("frame%d.fits" % i)
        original = fixture / kind / path.name
        raw, parent = path.read_bytes(), original.read_bytes()
        expected_header = header_block(parent[:2880], PRIMARY[i]) + header_block(parent[2880:5760], EXTENSION)
        if raw[:5760] != expected_header or raw[6408:] != parent[6408:]:
            raise RuntimeError("Header/padding preservation failed")
        with fits.open(path, memmap=False) as actual, fits.open(original, memmap=False) as prior:
            if (len(actual) != 2 or actual[1].data.shape != (9, 18) or
                    not np.array_equal(actual[1].data[:, :9] - bias_pixels(), prior[1].data[:, :9]) or
                    not np.array_equal(actual[1].data[:, 9:], prior[1].data[:, 9:])):
                raise RuntimeError("Exact cancellation/overscan preservation failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    work = args.work.resolve()
    # Provenance: retain all constructed products, rejected mutations and checks.
    work.mkdir(exist_ok=False)
    identity = dict(commit=subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
        dirty=bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=repo)))
    record = dict(purpose="Python-only supplied-bias fixture/oracle preparation",
                  tested_source=identity, created_utc=datetime.now(timezone.utc).isoformat(),
                  status="running", native_execution=False, python=sys.executable,
                  retention_roles=["preparation_evidence"], cases=[], rejected=[])
    record["source_sha256"] = {str(p.relative_to(repo)): digest(p) for p in [
        Path(__file__).resolve(), repo / "mefpp2/tests/bpm_bias_cases.py",
        repo / "mefpp2/tests/bpm_bias_probe.c", repo / "mefpp2/tests/bpm_bias_ownership_probe.c",
        repo / "mefpp2/tests/qualify_bpm_bias.py",
        repo / "mefpp2/tests/fixtures/bpm-bias/manifest.json"]}
    import astropy
    record.update(numpy=np.__version__, astropy=astropy.__version__)
    save(work / "run-provenance.json", record)
    fixture = repo / "mefpp2/tests/fixtures/bpm-cleanup"
    manifest_path = repo / "mefpp2/tests/fixtures/bpm-bias/manifest.json"
    manifest = json.loads(manifest_path.read_text())
    parent = json.loads((fixture / "manifest.json").read_text())
    protected = {name: digest(fixture / name) for name in parent["files"]}

    def reject(label, function):
        try:
            function()
        except RuntimeError:
            record["rejected"].append(label)
        else:
            raise RuntimeError("Oracle accepted deliberate corruption: " + label)

    try:
        # Source identities: immutable accepted inputs and declared new derivatives.
        if protected != parent["files"]:
            raise RuntimeError("Immutable fixture mismatch")
        reference = json.loads((repo / "docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json").read_text())
        references = {c["case"]: c for c in reference["cases"]}
        metadata = json.loads((repo / "docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json").read_text())
        for case in metadata["cases"]:
            label, kind, flag, mode = case["case"], case["fixture"], case["proportional_flag"], case["mode"]
            root = work / label
            root.mkdir()
            save(root / "run-provenance.json", dict(parent=str(work / "run-provenance.json"),
                 tested_source=identity, purpose="Constructed products, not native output", status="running"))
            inputs = prepare(root, fixture, kind)
            if inputs != manifest["cases"][kind]["inputs_sha256"]:
                raise RuntimeError("Declared supplied-bias derivative mismatch")
            verify_inputs(root, fixture, kind)
            # Independent sensitivity: proportional median ratios must reject omitted bias.
            original = np.stack([fits.getdata(fixture / kind / ("frame%d.fits" % i), 1)[:, :9]
                                 for i in range(3)]).astype(np.float32)
            bias = bias_pixels()

            def proportional_mask(cube):
                medians = np.median(cube, axis=(1, 2)).astype(np.float64)
                gains = np.median(cube.astype(np.float64) / medians[:, None, None], axis=0).astype(np.float32)
                normalized = (gains / float(gains.astype(np.float64).mean())).astype(np.float32)
                return ((normalized >= 0.5) & (normalized <= 1.5)).astype(np.uint8)

            mask = proportional_mask(original)
            if mask[4, 5] != 1 or proportional_mask(original + bias)[4, 5] != 0:
                raise RuntimeError("Omitted-bias sentinel is insensitive")
            prior = references["c%d-%s-flag%d" % (mode, kind, flag)]
            if hashlib.sha256(mask.tobytes()).hexdigest() != prior["mask_pixels_sha256"]:
                raise RuntimeError("Independent expected mask differs from accepted reference")
            previous = case["roles"]["ordinary"]["outputs"]
            # Constructed FITS: preserve exact accepted canonical cards and mask pixels.
            chunks = []
            for index, cards in enumerate(previous["saved_headers"]):
                header = fits.Header([fits.Card.fromstring(c) for c in cards])
                header.append(("ORIGFILE", "PREPARATION_ONLY"))
                chunks.append(header.tostring().encode("ascii"))
                if index:
                    chunks.append(mask.tobytes().ljust(2880, b"\0"))
            product = root / previous["saved_name"]
            product.write_bytes(b"".join(chunks))
            fits.PrimaryHDU(mask).writeto(root / "returned.fits")
            actual, _ = verify(root, inputs, prior, flag, previous)
            if {k: v for k, v in actual.items() if k != "supplied_bias_sha256"} != previous:
                raise RuntimeError("Constructed canonical product differs")
            # Negative products: changed mask and first-frame metadata must be rejected.
            returned = root / "returned.fits"
            good_returned = returned.read_bytes()
            damaged = bytearray(good_returned)
            damaged[2880] ^= 1
            returned.write_bytes(damaged)
            reject(label + ":mask", lambda: verify(root, inputs, prior, flag, previous))
            (root / "rejected-mask.bin").write_bytes(damaged)
            returned.write_bytes(good_returned)
            # Preserve rejected bytes outside the strict product-set directory.
            (root / "rejected-mask.bin").rename(work / (label + "-rejected-mask.bin"))
            good_product = product.read_bytes()
            damaged = good_product.replace(b"ESO S2 METADATA 0", b"ESO S2 METADATA 1", 1)
            if damaged == good_product:
                raise RuntimeError("Metadata mutation was not applied")
            product.write_bytes(damaged)
            reject(label + ":metadata", lambda: verify(root, inputs, prior, flag, previous))
            (work / (label + "-rejected-metadata.bin")).write_bytes(damaged)
            product.write_bytes(good_product)
            # Negative input: corrupting the bias is rejected by independent readback.
            bias_path = root / "bias.fits"
            good_bias = bias_path.read_bytes()
            damaged = bytearray(good_bias)
            damaged[2880:2884] = b"\0\0\0\0"
            bias_path.write_bytes(damaged)
            reject(label + ":bias", lambda: verify_inputs(root, fixture, kind))
            (work / (label + "-rejected-bias.bin")).write_bytes(damaged)
            bias_path.write_bytes(good_bias)
            record["cases"].append(label)
            save(root / "run-provenance.json", dict(parent=str(work / "run-provenance.json"),
                 tested_source=identity, purpose="Constructed products, not native output", status="passed"))
        record["status"] = "passed"
    except BaseException as error:
        record.update(status="failed", error=str(error))
        raise
    finally:
        # Preservation: all accepted source fixture bytes must remain immutable.
        record["immutable_fixtures_unchanged"] = all(digest(fixture / n) == h for n, h in protected.items())
        if not record["immutable_fixtures_unchanged"]:
            record["status"] = "failed"
        record["completed_utc"] = datetime.now(timezone.utc).isoformat()
        save(work / "run-provenance.json", record)
    print("PREPARATION:", record["status"], "constructed cases:", len(record["cases"]),
          "deliberate rejections:", len(record["rejected"]), "native execution: false")
    print("REPORT:", work / "run-provenance.json")
    return 0 if record["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
