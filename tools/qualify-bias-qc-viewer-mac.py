#!/usr/bin/env python3
"""Export only viewer assets and generate a fresh retained-product inspection.
No native build, source/build mutation, dependency install or reduction.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import tempfile
import time


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--revision', required=True)
    a = p.parse_args()
    repo = a.repository.resolve(strict=True)
    base = 'af24c3699957d03a11f26c0bc47172b202ca0ede'
    orch = Path('/Users/fselman/Pictures/OCAM/test_recipes/orchestration')
    products = Path('/Users/fselman/Pictures/OCAM/test_recipes/reduced/cal/bias')
    reader = Path('/Users/fselman/Software/build/wenu-imaging/mac-asdf6-transfer-ntb2et4J/Mac-private-k4i17lwh/environment/bin/python')
    require(platform.system() == 'Darwin' and socket.gethostname().split('.')[0] == 'MC02VV0HPHTDG', 'Expected selected Mac')
    require(str(repo) == '/Users/fselman/Developer/wenu-imaging', 'Unexpected checkout')

    def git(*args):
        return subprocess.check_output(['git', *args], cwd=repo)

    require(git('remote', 'get-url', 'origin').decode().strip() == 'git@github.com:fselman/wenu-imaging.git', 'Unexpected origin')
    require(git('branch', '--show-current').decode().strip() == 'main', 'Preserve main checkout')
    require(git('rev-parse', 'HEAD').decode().strip() == base, 'Main differs from accepted baseline')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'Checkout is dirty')
    require(len(a.revision) == 40 and all(c in '0123456789abcdef' for c in a.revision), 'Require full candidate revision')
    require(git('rev-parse', a.revision).decode().strip() == a.revision, 'Candidate is not available')
    subprocess.run(['git', 'merge-base', '--is-ancestor', base, a.revision], cwd=repo, check=True)
    require(reader.is_file() and os.access(reader, os.X_OK), 'Qualified ASDF interpreter missing')
    require(orch.is_dir() and products.is_dir(), 'Expected normal workflow directories')
    require((products/'CMDP.2026-11-07T21:05:44.919Z.001.asdf').is_file(), 'Accepted clipped product missing')
    assets = ['tools/view-bias-qc.py', 'tools/bias-qc-viewer.html', 'tools/bias-qc-inspection.js',
              'tools/qc-plot-inspection.js', 'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json']
    payloads = {name: git('show', a.revision + ':' + name) for name in assets}
    for name in assets[-2:]:
        require(payloads[name] == git('show', base + ':' + name), 'Shared helper/schema unexpectedly changed: ' + name)

    def signature(path):
        s = path.stat()
        return [s.st_size, s.st_mtime_ns, s.st_ctime_ns, s.st_ino]

    before = {str(path): signature(path) for path in sorted(products.glob('*.asdf'))}
    require(before, 'No product ASDF files')
    work = Path(tempfile.mkdtemp(prefix='bias-qc-common-', dir=orch))
    source = work/'source'
    for name, content in payloads.items():
        target = source/name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f:
            f.write(content)
    page, log = work/'overview.html', work/'generation.log'
    command = [str(reader), '-B', str(source/'tools/view-bias-qc.py'),
               '--products', str(products), '--output', str(page)]
    print('INSPECTION:', work, flush=True)
    print('READING:', len(before), 'product ASDF files once; no FITS/raw reads.', flush=True)
    start = time.monotonic()
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=orch, stdout=stream, stderr=subprocess.STDOUT,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1'), timeout=180)
    elapsed = time.monotonic() - start
    print(log.read_text(), end='', flush=True)
    after = {str(path): signature(path) for path in sorted(products.glob('*.asdf'))}
    unchanged = before == after
    receipt = dict(successful=result.returncode == 0 and unchanged, exit_status=result.returncode,
        page=str(page), generation_seconds=elapsed, products_unchanged=unchanged,
        asdf_files=len(before), source_revision=a.revision, main_revision=base,
        asset_sha256={name: hashlib.sha256(value).hexdigest() for name,value in payloads.items()},
        fits_or_raw_files_read=False, native_build_changed=False, installed=False,
        browser_visual_acceptance='owner_review_pending')
    (work/'inspection-results.json').write_text(json.dumps(receipt, indent=2) + '\n')
    require(unchanged, 'Product collection changed during generation; inspect retained receipt')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'Main checkout changed')
    print('RECEIPT:', work/'inspection-results.json', flush=True)
    if page.is_file() and result.returncode in (0, 2):
        subprocess.run(['/usr/bin/open', str(page)], check=True)
    require(result.returncode == 0, 'Incomplete/failed generation; inspect retained page/log')
    print('PASS: all products loaded once; common QC overview opened for browser review.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
