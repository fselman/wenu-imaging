"""Retain and verify a successful BPM multiext run for transfer (#118).

Preserve root build logs while selecting only build records/executables inside
build directories. Never delete or rewrite the source run or an earlier archive.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import platform
import tarfile
import tempfile

BUILD_KEEP = {'build-info.json', 'CMakeCache.txt', 'compile_commands.json',
              'bpm_original_probe', 'bpm_ownership_probe'}


def include(relative):
    # #118: root build-*.log files are evidence, not build directories.
    return not (len(relative.parts) > 1 and relative.parts[0].startswith('build-')) or (
        len(relative.parts) == 2 and relative.name in BUILD_KEEP)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--expected-commit', required=True)
    args = parser.parse_args()
    run = args.run.expanduser().resolve(strict=True)
    # Guards and source report: completed, successful run on the current host.
    report = json.loads((run / 'run-provenance.json').read_text())
    if (report['tested_source']['commit'] != args.expected_commit or
            report['tested_source']['dirty'] or report['host'].split('.')[0] != platform.node().split('.')[0] or
            report['status'] != 'passed' or not report['execution_complete'] or
            not report['cases'] or any(c['status'] != 'passed' or c['findings'] for c in report['cases']) or
            not all(v for k, v in report.items() if k.endswith('_unchanged'))):
        raise RuntimeError('STOP: incomplete, changed or unexpected run')
    # Provenance before any evidence packaging; fresh transfer directory only.
    transfer = Path(tempfile.mkdtemp(prefix='bpm-multiext-transfer-', dir=run.parent))
    receipt = transfer / 'run-provenance.json'
    record = dict(purpose=__doc__, status='running', source_run=str(run),
                  created_utc=datetime.now(timezone.utc).isoformat())
    receipt.write_text(json.dumps(record, indent=2) + '\n')
    try:
        # Select retained evidence; keep root logs and both executable/build records.
        files = {}
        for path in sorted(run.rglob('*')):
            relative = path.relative_to(run)
            if not include(relative):
                continue
            if path.is_symlink():
                raise RuntimeError('Unexpected evidence symlink: ' + str(path))
            if path.is_file():
                files[relative.as_posix()] = sha(path)
        # Require every command log, including root-level build logs, before archiving.
        for command in report['commands']:
            name = Path(command['log']).name
            if files.get(name) != command['log_sha256']:
                raise RuntimeError('Missing/changed command log: ' + name)
        manifest = dict(source_run=str(run), source_commit=args.expected_commit, files=files)
        payload = (json.dumps(manifest, indent=2) + '\n').encode()
        archive = transfer / 'bpm-multiext-evidence.tar.gz'
        with tarfile.open(archive, 'x:gz') as bundle:
            for name in files:
                bundle.add(run / name, arcname=run.name + '/' + name, recursive=False)
            entry = tarfile.TarInfo('transfer-manifest.json')
            entry.size = len(payload)
            bundle.addfile(entry, io.BytesIO(payload))
        # Archive readback and source preservation: every selected identity must match.
        with tarfile.open(archive, 'r:gz') as bundle:
            names = bundle.getnames()
            expected = {run.name + '/' + name for name in files} | {'transfer-manifest.json'}
            if len(names) != len(expected) or set(names) != expected:
                raise RuntimeError('Unexpected/missing archived members')
            if bundle.extractfile('transfer-manifest.json').read() != payload:
                raise RuntimeError('Archived manifest differs')
            for name, expected_sha in files.items():
                with bundle.extractfile(run.name + '/' + name) as stream:
                    actual = hashlib.file_digest(stream, 'sha256').hexdigest()
                if actual != expected_sha or sha(run / name) != expected_sha:
                    raise RuntimeError('Archived/source identity differs: ' + name)
        record.update(status='passed', archive=str(archive), archive_sha256=sha(archive),
                      files_verified=len(files), command_logs_verified=len(report['commands']))
    except BaseException as error:
        record.update(status='failed', error=str(error))
        raise
    finally:
        receipt.write_text(json.dumps(record, indent=2) + '\n')
    print('ARCHIVE:', archive)
    print('SHA256:', record['archive_sha256'])
    print('FILES VERIFIED:', len(files))
    print('COMMAND LOGS VERIFIED:', record['command_logs_verified'])
    print('SIZE MiB:', round(archive.stat().st_size / 1048576, 2))


if __name__ == '__main__':
    main()
