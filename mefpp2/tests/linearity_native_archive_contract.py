"""Synthetic preparation publication: exact saved values and lossless transports.

--metadata-only uses a test-only writer boundary, never asserts ASDF coverage.
Without it, the actual command writes ASDF and an independent reader checks it.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'Pycavi2/tests'))
from linearity_preparation_fixture import fixture, native_argv


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def verify(asdf_path, schema, output):
    import asdf
    schema_bytes = schema.read_bytes()
    schema_id = json.loads(schema_bytes)['id']
    with asdf.config_context() as configuration:
        configuration.add_resource_mapping({schema_id: schema_bytes})
        with asdf.open(asdf_path, custom_schema=schema_id) as archive:
            tree = dict(archive.tree)
            archive.validate()
            q = tree['qc']
            assert q['extensions']['record_scope'] == 'one_final_table_product'
            assert q['extensions']['table_name'] == 'linearity_preparation'
            assert 'output_hdu' not in q['characterization']['detectors'][0]
            assert len(q['embedded_input_records']) == 30
            output.write_text(json.dumps(q))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--command', type=Path)
    parser.add_argument('--work-parent', type=Path)
    parser.add_argument('--metadata-only', action='store_true')
    parser.add_argument('--asdf-python', type=Path)
    parser.add_argument('--verify', type=Path)
    parser.add_argument('--schema', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.verify:
        verify(args.verify, args.schema, args.output)
        return
    command = args.command.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='linearity-native-archive-', dir=args.work_parent)).resolve()
    state = fixture(work, separated=True)
    os.chdir(state['work'])
    raw = state['raw']
    inputs = [*raw.glob('*.fits'), Path(state['master']), Path(state['selection']['bpm']['path'])]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    for path in inputs:
        path.chmod(0o444)
    raw.chmod(0o555)
    reduced = state['reduced']
    native = reduced/'native'
    native.mkdir()
    destination = reduced/'linearity-preparation.asdf'
    log = reduced/'native.log'
    argv = native_argv(state, command, native) + ['--native-asdf', str(destination),
                                                '2026-11-09T19:00:00.000Z', str(log)]
    with log.open('x') as stream:
        result = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT)
    assert result.returncode == 0, log.read_text()
    saved = rows(destination.with_suffix('.tsv'))
    assert len(saved) == 100
    expected_sources = state['selection']['flat']
    assert [r['asset'] for r in saved] == [r['asset'] for r in expected_sources for _ in range(5)]
    for row in saved:
        assert float(row['signal_adu']) == 100*float(row['exposure_seconds'])+5.5
        assert abs(float(row['spatial_variance_adu2'])-13) < 6e-15
        assert int(row['valid_pixels']) == 12
    if args.metadata_only:
        assert not destination.exists(), 'Test boundary must not masquerade as ASDF'
        metrics = rows(Path(str(destination)+'.metadata.tsv'))
        evidence_root = Path(str(destination)+'.evidence')
        evidence = {str(p.relative_to(evidence_root)): p.read_text()
                    for p in evidence_root.rglob('*') if p.is_file()}
        for i, row in enumerate(saved):
            for offset, field in enumerate(('signal_adu', 'spatial_variance_adu2')):
                m = metrics[2*i+offset]
                assert m['name'] == f'exposure.{i}.{field}'
                assert m['state'] == '1' and float(m['value']) == float(row[field])
                assert m['source'] == row['asset'] and int(m['count']) == 12
        assert metrics[-1]['name'] == 'absolute_noise_covariance' and metrics[-1]['state'] == '2'
    else:
        decoded = reduced/'independent-readback.json'
        subprocess.run([str(args.asdf_python), '-B', str(Path(__file__).resolve()),
                        '--verify', str(destination), '--schema',
                        str(ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'),
                        '--output', str(decoded)], check=True)
        q = json.loads(decoded.read_text())
        assert q['file']['location'] == str(destination.with_suffix('.tsv'))
        detector = q['characterization']['detectors'][0]
        metrics = detector['measurements']
        assert len(metrics) == 201 and metrics[-1]['status'] == 'unavailable'
        assert q['provenance']['operation'] == 'linearity.prepare'
        assert 'fit_state=not_performed' in q['extensions']['operation_context']['snapshot']
        for i, row in enumerate(saved):
            for offset, field in enumerate(('signal_adu', 'spatial_variance_adu2')):
                m = metrics[2*i+offset]
                assert m['name'] == f'exposure.{i}.{field}' and m['value'] == float(row[field])
                assert m['status'] == 'measured' and m['sources'] == [row['asset']]
        evidence = {item['name']: item['text'] for item in q['extensions']['native_evidence']}
        source_records = q['embedded_input_records']
        assert [r['file']['id'] for r in source_records] == [r['asset'] for r in expected_sources] + [r['asset'] for r in state['biases']]
        assert [r['detectors'][0]['source_hdu'] for r in source_records] == [r['hdu'] for r in expected_sources] + [r['hdu'] for r in state['biases']]
    assert len(evidence) == 71
    for path in native.rglob('*'):
        if path.is_file():
            assert evidence[str(path.relative_to(native))] == path.read_text()
    for name in ('native.toml', 'rois.toml', 'sites.toml', 'plan.tsv', 'biases.tsv'):
        assert evidence[name] == (state['work']/name).read_text()
    assert 'bias\t3\t' in evidence['source-bindings.tsv']
    assert '\t0\t' in evidence['bias-traces.tsv']
    frozen = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in reduced.rglob('*') if p.is_file()}
    repeated = subprocess.run(argv, capture_output=True, text=True)
    assert repeated.returncode != 0
    assert frozen == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in reduced.rglob('*') if p.is_file()}
    assert before == {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before}
    assert Path.cwd() == state['work'] and not list(state['work'].glob('*.fits'))
    print('RETAINED NATIVE PREPARATION:', work)
    print('PASS: 100 corrected exposures, 201 typed QC records, 71 lossless evidence snapshots; no fit/noise claim')
    print('PASS: original source order/HDU, trace membership, immutable inputs/output, orchestration/raw/reduced separation')
    print('COVERAGE:', 'typed metadata boundary only; ASDF not exercised' if args.metadata_only else 'real native ASDF, independent schema/value reader')


if __name__ == '__main__':
    main()
