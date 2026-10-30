"""Focused read-only source/authoring contract checks; private synthetic writes.

No native compiler/build, FITS/Pycavi processing, installation or source edits.
Accepted native reference bytes are pinned, not independently requalified here.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import tomllib

from build_catalog import catalog
from build_examples import examples, render
from validate_project import ContractError, load, native_consistency, validate

BASE = Path(__file__).resolve().parent


def main():
    if sys.flags.optimize:
        raise RuntimeError('Run this contract check without Python optimization')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    work = Path(tempfile.mkdtemp(prefix='m2 project contracts ', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    # Catalog and checked-in examples must be reproducible, strict and complete.
    assert json.loads((BASE / 'catalog.json').read_text()) == catalog
    models = examples()
    snapshots = {}
    source_hashes = {}
    for name, model in models.items():
        source = BASE / 'examples' / (name + '.toml')
        raw = source.read_bytes()
        assert raw.decode() == render(model)
        source_hashes[str(source)] = hashlib.sha256(raw).hexdigest()
        snapshot = load(source)
        record = snapshot.as_dict()
        assert record['configuration'] == model
        assert record['validation_catalog_sha256'] == hashlib.sha256((BASE/'catalog.json').read_bytes()).hexdigest()
        assert record['execution_ready'] is False
        assert record['reference_validation'] == 'not_resolved'
        assert record['product_compliance'] == 'not_validated'
        assert record['wad_validation'] == 'review-crosswalk-only'
        snapshots[name] = snapshot
        # Every raw source/hash must describe exactly the retained bytes.
        for item in record['sources']:
            assert hashlib.sha256(item['text'].encode()).hexdigest() == item['sha256']
        # Read-only CLI must be independent of two unrelated caller directories.
        outputs = []
        for label in ('caller one', 'caller two'):
            cwd = work / label
            cwd.mkdir(exist_ok=True)
            call = subprocess.run([sys.executable, '-B', str(BASE / 'validate_project.py'), str(source)],
                                  cwd=cwd, capture_output=True, text=True)
            assert call.returncode == 0, call.stderr
            outputs.append(json.loads(call.stdout))
        assert outputs[0] == outputs[1] == record
    # Actual checked-in compatibility geometry, without inventing amplifier IDs.
    wfi = snapshots['wfi'].as_dict()['configuration']['readout']['detectors']
    assert [d['channels'][0]['overscan']['region']['x_min'] for d in wfi] == [2100]*4 + [5]*3 + [2100]
    assert [d['channels'][0]['overscan']['region']['x_max'] for d in wfi] == [2142]*4 + [48]*3 + [2142]
    ocam = snapshots['omegacam'].as_dict()['configuration']['readout']['detectors']
    assert len(ocam) == 32
    assert [d['channels'][0]['overscan']['region']['x_min'] for d in ocam] == ([2100]*8 + [5]*8)*2
    assert [d['channels'][0]['overscan']['region']['x_max'] for d in ocam] == ([2142]*8 + [48]*8)*2
    assert all(d['identity_status'] == 'unknown' for d in wfi + ocam)
    assert len(models['dual-active']['readout']['detectors'][0]['channels']) == 2
    alternate = models['alternative-selected']['readout']['detectors'][0]['channels']
    assert [c['active'] for c in alternate] == [False, True]
    assert alternate[1]['overscan']['region']['x_min'] == 1
    header_snapshot = snapshots['alternative-selected'].as_dict()
    assert header_snapshot['header_metadata_review'] == 'pending'
    assert header_snapshot['configuration']['readout']['header_evidence'][0]['raw_card'] == models['alternative-selected']['readout']['header_evidence'][0]['raw_card']
    assert header_snapshot['configuration']['readout']['mapping_status'] == 'unverified'
    assert header_snapshot['configuration']['readout']['detectors'][0]['channels'][1]['overscan']['region']['x_min'] == 1
    assert snapshots['wfi'].as_dict()['header_metadata_review'] == 'not_supplied'
    # Validated IDs are declarations, never evidence of physical verification.
    declared = copy.deepcopy(models['no-overscan'])
    declared['readout']['mapping_status'] = 'verified'
    declared['readout']['detectors'][0].update(identity_status='verified', physical_detector_id='synthetic-detector')
    declared['readout']['detectors'][0]['channels'][0].update(identity_status='verified', physical_amplifier_id='synthetic-amplifier')
    validate(declared)
    declared['reduction_profile']['purpose'] = 'visual'
    declared['product_profile']['target'] = 'ESO_Phase3'
    validate(declared)
    assert declared['product_profile']['compliance'] == 'not_validated'
    assert snapshots['no-overscan'].as_dict()['native_validation'] == 'unavailable'
    # Independent reference hashes from the accepted conversion evidence.
    evidence = json.loads((BASE.parent / 'examples/conversion-evidence.json').read_text())
    # Compare using recorded native file hashes, with no regeneration of values.
    for instrument in ('wfi', 'omegacam'):
        native = BASE.parent / 'examples' / instrument / 'full.toml'
        assert hashlib.sha256(native.read_bytes()).hexdigest() == evidence['instruments'][instrument]['example_sha256']['full.toml']
    print('PASS: 6 authoring examples, two caller directories, retained native hashes and per-chip geometry')

    # Frozen owned bytes outlive source edits/deletion and caller record mutation.
    private = work / 'private project.toml'
    private.write_text(render(models['no-overscan']))
    frozen = load(private)
    retained = frozen.encoded
    detached = frozen.as_dict()
    detached['configuration']['readout']['detectors'].clear()
    private.write_text('changed after loading')
    assert frozen.encoded == retained and frozen.as_dict()['configuration']['readout']['detectors']
    private.unlink()
    assert frozen.encoded == retained
    # A reference-bearing snapshot also owns native bytes after source edits.
    private_native = work/'native source.toml'
    native_original = (BASE.parent/'examples/wfi/full.toml').read_bytes()
    private_native.write_bytes(native_original)
    reference_model = copy.deepcopy(models['wfi'])
    reference_model['processing']['native_configuration'] = private_native.name
    private.write_text(render(reference_model))
    native_frozen = load(private)
    native_before = native_frozen.encoded
    private_native.write_text('changed native source after loading')
    assert native_frozen.encoded == native_before
    assert native_frozen.as_dict()['sources'][1]['text'].encode() == native_original
    private_native.unlink()
    private.unlink()
    assert native_frozen.encoded == native_before
    # Recipe order is preserved, not alphabetized or dependency-inferred.
    ordered = copy.deepcopy(models['no-overscan'])
    ordered['recipe']['steps'] = [dict(id='z-first',operation='mef_cal_bias'),dict(id='a-second',operation='mef_sci_pp')]
    private.write_text(render(ordered))
    assert load(private).as_dict()['configuration']['recipe']['steps'] == ordered['recipe']['steps']
    private.unlink()
    print('PASS: immutable project/native sources survive caller mutation, edits/deletion; recipe order retained')

    # Semantic/type/identity controls: reject then recover in the same process.
    rejects = []
    def reject(label, mutate, base='no-overscan'):
        data = copy.deepcopy(models[base])
        mutate(data)
        try:
            validate(data)
        except ContractError as exc:
            rejects.append(dict(case=label, diagnostic=str(exc)))
        else:
            raise AssertionError('accepted ' + label)
        validate(models[base])
    reject('unsupported root version', lambda d: d.update(project_schema_version=2))
    for domain in ('project', 'association', 'reduction_profile', 'recipe', 'execution', 'quality', 'product_profile', 'processing', 'readout'):
        reject('unsupported ' + domain, lambda d, k=domain: d[k].update(schema_version=2))
        reject('unknown key ' + domain, lambda d, k=domain: d[k].update(unknown={}))
    reject('unknown root', lambda d: d.update(unknown={}))
    reject('missing roots', lambda d: d['project'].pop('roots'))
    reject('bool is not integer', lambda d: d['execution'].update(workers=True))
    reject('no coercion', lambda d: d['execution'].update(workers='1'))
    reject('no activation', lambda d: d['execution'].update(activation='enabled'))
    reject('no parallel promise', lambda d: d['execution'].update(workers=2))
    reject('batch niceness', lambda d: d['execution'].update(niceness=0))
    reject('no compliance claim', lambda d: d['product_profile'].update(compliance='certified'))
    reject('no zero variance', lambda d: d['product_profile'].update(variance_contract='zero'))
    reject('no hidden thresholds', lambda d: d['quality'].update(thresholds=['new cut']))
    reject('separate profiles', lambda d: d['product_profile'].update(id=d['recipe']['id']))
    reject('unknown operation', lambda d: d['recipe']['steps'][0].update(operation='system'))
    reject('duplicate step identity', lambda d: d['recipe']['steps'].append(copy.deepcopy(d['recipe']['steps'][0])))
    reject('duplicate binding', lambda d: d['association']['bindings'].append(copy.deepcopy(d['association']['bindings'][0])))
    reject('selected exact version', lambda d: d['association']['bindings'][1].pop('asset_version'))
    reject('omitted forbids file identity', lambda d: d['association']['bindings'][0].update(asset_id='mask', asset_version=1))
    reject('unknown physical identity', lambda d: d['readout']['detectors'][0].update(physical_detector_id='invented'))
    reject('unsubstantiated verified mapping', lambda d: d['readout'].update(mapping_status='verified'))
    def c(d):
        return d['readout']['detectors'][0]['channels'][0]
    reject('absent cannot subtract', lambda d: c(d)['overscan'].update(subtract=True))
    reject('absent cannot define region', lambda d: c(d)['overscan'].update(region=dict(x_min=1,x_max=2,unit='pixel',convention='fits-1-based-inclusive')))
    reject('defined requires region', lambda d: c(d)['overscan'].pop('region'), 'defined-disabled')
    reject('inactive cannot subtract', lambda d: c(d).update(active=False), 'dual-active')
    reject('unknown amplifier ID', lambda d: c(d).update(physical_amplifier_id='invented'))
    reject('no active channels', lambda d: c(d).update(active=False))
    reject('duplicate channels', lambda d: d['readout']['detectors'][0]['channels'].append(copy.deepcopy(c(d))))
    reject('duplicate detectors', lambda d: d['readout']['detectors'].append(copy.deepcopy(d['readout']['detectors'][0])))
    reject('reversed scan', lambda d: c(d)['overscan']['region'].update(x_min=120), 'defined-disabled')
    reject('zero scan index', lambda d: c(d)['overscan']['region'].update(x_min=0), 'defined-disabled')
    reject('wrong scan unit', lambda d: c(d)['overscan']['region'].update(unit='mm'), 'defined-disabled')
    reject('wrong endpoint convention', lambda d: c(d)['overscan']['region'].update(convention='zero-based'), 'defined-disabled')
    reject('partial y interval', lambda d: c(d)['overscan']['region'].update(y_min=1), 'defined-disabled')
    reject('signal scan overlap', lambda d: c(d)['overscan']['region'].update(x_min=50), 'defined-disabled')
    reject('dual requires signal', lambda d: c(d).pop('signal'), 'dual-active')
    reject('dual signal overlap', lambda d: c(d)['signal'].update(x_max=150), 'dual-active')
    reject('native fallback forbidden', lambda d: d['processing'].update(native_configuration='fallback.toml'))
    reject('native missing ref', lambda d: d['processing'].update(native_mode='legacy_reference'))
    reject('no automatic header authority', lambda d: d['readout'].update(metadata_policy='trust_headers'))
    reject('no trusted header claim', lambda d: d['readout']['header_evidence'][0].update(trust='trusted'), 'alternative-selected')
    reject('no unresolved header selection', lambda d: d['readout']['header_evidence'][0].update(disposition='selected'), 'alternative-selected')
    reject('exact raw card preserved', lambda d: d['readout']['header_evidence'][0].update(raw_card='short'), 'alternative-selected')
    reject('header reference detector', lambda d: d['readout']['header_evidence'][0].update(detector_id='missing'), 'alternative-selected')
    reject('duplicate header occurrence', lambda d: d['readout']['header_evidence'].append(copy.deepcopy(d['readout']['header_evidence'][0])), 'alternative-selected')
    reject('control in roots', lambda d: d['project']['roots'].update(raw='a\x00b'))
    for label, mutate in (
        ('native geometry mismatch', lambda d: c(d)['overscan']['region'].update(x_min=2099)),
        ('native subtraction mismatch', lambda d: c(d)['overscan'].update(subtract=False)),
        ('native missing ordinal', lambda d: d['readout']['detectors'][0].pop('legacy_ordinal')),
        ('native dual active unsupported', lambda d: d['readout']['detectors'][0]['channels'].append(dict(c(d), id='second'))),
    ):
        data=copy.deepcopy(models['wfi']); mutate(data)
        native=tomllib.loads((BASE.parent/'examples/wfi/full.toml').read_text())
        try:
            native_consistency(data,native)
        except ContractError as exc:
            rejects.append(dict(case=label, diagnostic=str(exc)))
        else:
            raise AssertionError('accepted '+label)
        native_consistency(models['wfi'],native)
    print(f'PASS: {len(rejects)} rejection/same-process recovery cases')
    # Malformed input/CLI errors must fail without creating project directories.
    for text in ('invalid [', render(models['no-overscan']) + '\n[unknown]\nx=1\n'):
        private.write_text(text)
        call=subprocess.run([sys.executable,'-B',str(BASE/'validate_project.py'),str(private)],capture_output=True,text=True,cwd=work)
        assert call.returncode == 1 and call.stderr.startswith('INVALID:')
    assert not (BASE/'examples/review locations').exists()
    assert not (work/'review locations').exists()
    for path, expected in source_hashes.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected
    report=dict(check='project-authoring-contract', platform=platform.platform(),python=sys.version,
                examples=list(models),caller_directories=2, rejected=rejects,
                source_sha256=source_hashes,freeze='passed',native_execution=False,
                fits_access=False,installation=False,source_revision=os.environ.get('TASK_SOURCE_REVISION','unrecorded'))
    (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: malformed CLI inputs rejected; no project directories or source files changed')
    print('REPORT:',work/'run-provenance.json')


if __name__ == '__main__':
    main()
