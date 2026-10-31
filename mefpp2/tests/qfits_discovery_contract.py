"""Shared qfits discovery controls, including legacy offset/card equivalence (#194/#195)."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from layout_contract import EMPTY, header, image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", type=Path, required=True)
    parser.add_argument("--work-parent", type=Path, required=True)
    args = parser.parse_args()
    args.work_parent.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="qfits-discovery-", dir=args.work_parent))
    cases = {}
    for count in (0, 1, 8, 32, 140):
        path = root / f"mef-{count}.fits"
        path.write_bytes(EMPTY + b"".join(image(str(i)) for i in range(count)))
        cases[count] = path
    duplicate = root / "duplicates.fits"
    duplicate.write_bytes(image("A", primary=True, extra=(("BSCALE", "1"), ("BSCALE", "2"))))
    overflow = root / "overflow.fits"
    overflow.write_bytes(header((("SIMPLE", "T"), ("BITPIX", "16"), ("NAXIS", "2"),
                                 ("NAXIS1", "2147483647"), ("NAXIS2", "2"))))
    sparse = root / "oversized-sparse.fits"
    with sparse.open("wb") as stream:
        stream.write(EMPTY); stream.truncate(2**31)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in root.glob("*.fits") if p != sparse}
    sparse_before = sparse.stat(); records = []

    def invoke(path, hdus, budget, passes):
        argv = [str(args.probe), str(path), str(hdus), str(budget)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        records.append({"argv": argv, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        assert result.returncode == (0 if passes else 1), records[-1]
        if not passes:
            assert result.stdout == "REJECTED\n", records[-1]
        return result.stdout

    # Existing API and checked path agree exactly with independently known offsets.
    for count, path in cases.items():
        output = invoke(path, count + 1, (count + 1) * 2880, True)
        expected = [f"EXTENSIONS {count}", "HDU 0 0 2880 2880 0 0"]
        for index in range(1, count + 1):
            start = 2880 + (index - 1) * 5760
            expected.append(f"HDU {index} {start} 2880 {start + 2880} 2880 0")
        assert output.splitlines() == expected
        if count < 128:
            assert invoke(path, 0, 0, True) == output
        else:
            invoke(path, 0, 0, False)  # Legacy fixed-count contract now rejects safely.
        invoke(path, count + 1, (count + 1) * 2880 - 1, False)
        if count:
            invoke(path, count, (count + 1) * 2880, False)
    # qfits preserves duplicate cards; the mapping validator decides conflicts.
    assert invoke(duplicate, 1, 2880, True).splitlines()[-1].endswith(" 2")
    # Reject before dangerous multiplication or int-offset conversion, with no pixel reads.
    for path in (overflow, sparse):
        invoke(path, 2, 5760, False); invoke(path, 0, 0, False)
    assert before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in root.glob("*.fits") if p != sparse}
    after = sparse.stat()
    assert (after.st_size, after.st_mtime_ns, after.st_mode) == (sparse_before.st_size, sparse_before.st_mtime_ns, sparse_before.st_mode)
    (root / "receipt.json").write_text(json.dumps({"status": "passed", "commands": records,
        "sparse_integrity": "stat only; sparse payload never hashed/read"}, indent=2) + "\n")
    print("PASS: qfits shared discovery: legacy/checked offsets, exact budgets, 140 extensions, duplicates, overflow refusal")
    print("RETAINED EVIDENCE:", root)


if __name__ == "__main__":
    main()
