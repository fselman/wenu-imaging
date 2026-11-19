"""Known SHA-256 vectors, read/block boundaries and restored-timestamp edits."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    command = args.probe.resolve(strict=True)
    case = Path(tempfile.mkdtemp(prefix='recipe-file-identity-', dir=args.work_parent))
    for name in ('raw', 'orchestration', 'reduced'):
        (case/name).mkdir()
    for n in (0, 1, 3, 55, 56, 63, 64, 65, 65535, 65536, 65537, 1000000):
        data = b'abc' if n == 3 else b'a'*n
        path = case/'raw'/str(n)
        path.write_bytes(data)
        actual = subprocess.check_output([str(command), str(path)], cwd=case/'orchestration', text=True).strip()
        assert actual == hashlib.sha256(data).hexdigest(), n
    guard = case/'raw/guard'
    guard.write_bytes(b'original')
    subprocess.run([str(command), str(guard), '--test-restored-timestamp'], cwd=case/'orchestration', check=True)
    print('PASS: SHA256 empty/abc/million-a and compression/read boundaries against independent hashlib')


if __name__ == '__main__':
    main()
