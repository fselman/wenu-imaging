"""Assemble a retained synthetic coordinator case; never rerun characterization.

Checks actual native ASDF joining and every stored FITS payload byte against
completed source products, then exercises the self-contained relocated reader.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'Pycavi2/pycavi/pycavi'), str(ROOT/'mefpp2/tests')]
import pycavi_bpm_linearity_assembly as assembly
import pycavi_native_product_qc as native_qc
from mef_assembly_contract import card, hdus


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mapping_fixture(member, folder):
    """Second detector identity exercises cross-document joins without a rerun.

    Its pixels are copied from the completed native product. Python writes only
    this explicitly labelled synthetic input metadata; final publication is C.
    """
    original_id = member['detector_id']
    detector_id = 'SYNTHETIC_MAPPING_DETECTOR'
    output = folder/'mapping-fixture.fits'
    sidecar = output.with_suffix('.asdf')
    q = deepcopy(native_qc.read(member['bpm']['asdf']))
    old_path = q['file']['id']
    slot = member['configuration_detector']+100
    def remap(value):
        if isinstance(value, dict):
            return {k: slot if k == 'configuration_detector' else remap(v) for k, v in value.items()}
        if isinstance(value, list):
            return [remap(v) for v in value]
        if isinstance(value, str):
            return detector_id if value == original_id else str(output) if value == old_path else value
        return value
    q = remap(q)
    q['file']['filename'] = output.name
    q['provenance']['producer']['name'] = 'synthetic_mapping_fixture_from_retained_native_product'
    data = bytearray(Path(member['bpm']['fits']).read_bytes())
    for offset in range(0, len(data), 80):
        if data[offset:offset+8] == b'DETID   ':
            data[offset:offset+80] = card('DETID', repr(detector_id))
            break
        assert data[offset:offset+8] != b'END     ', 'Native primary DETID missing'
    output.write_bytes(data)
    native_qc.qc._asdf().AsdfFile(dict(qc=q)).write_to(sidecar)
    for path in (output, sidecar):
        path.chmod(0o444)
    return dict(detector_id=detector_id, configuration_detector=slot,
                bpm=dict(fits=str(output), asdf=str(sidecar)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--command', type=Path, required=True)
    parser.add_argument('--assembly-source-revision', required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    parent = args.case.resolve(strict=True)
    source_manifest = parent/'reduced/cal/bpm-linearity/combined/manifest.json'
    report = json.loads(source_manifest.read_text())
    assert report['status'] == 'detector_characterization_complete_for_owner_inspection' and report['input_preservation']
    members = deepcopy(report['detectors'])
    work = Path(tempfile.mkdtemp(prefix='native-bpm-assembly-', dir=args.work_parent)).resolve()
    controls, reduced = work/'orchestration', work/'reduced'
    for path in (work/'raw', controls, reduced):
        path.mkdir()
    os.chdir(controls)
    priority = os.getpriority(os.PRIO_PROCESS, 0)
    if priority < 10:
        os.nice(10-priority)
    recipe = controls/'bpm-linearity.toml'
    recipe.write_bytes((parent/'orchestration/bpm-linearity.toml').read_bytes())
    paths = [Path(m['bpm'][key]) for m in members for key in ('fits', 'asdf', 'log')]
    for member in members:
        for name, digest in member['bpm']['sha256'].items():
            assert sha(Path(name)) == digest
    frozen = {p: sha(p) for p in paths}
    fixture_folder = reduced/'cal'
    fixture_folder.mkdir()
    members.append(mapping_fixture(members[0], fixture_folder))
    manifest = controls/'assembly.tsv'
    manifest.write_text(''.join('\t'.join([m['detector_id'], str(m['configuration_detector']),
        m['bpm']['fits'], m['bpm']['asdf']])+'\n' for m in members))
    output = reduced/f'CMDP.{report["created_at"]}.001.fits'
    log = output.with_suffix('.log')
    argv = [str(args.command.resolve(strict=True)), str(manifest), str(output), members[-1]['detector_id'], str(log),
            report['created_at'], report['native_source_revision'], str(recipe)]
    result = subprocess.run(argv, capture_output=True, text=True)
    with (reduced/'native-invocation.json').open('x') as stream:
        json.dump(dict(argv=argv, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr), stream, indent=2)
    assert result.returncode == 0, f'Native exit {result.returncode}; case {work}\n'+result.stdout+result.stderr
    assert output.with_suffix('.asdf').read_bytes().splitlines()[1] == b'#ASDF_STANDARD 1.6.0'
    saved = assembly.read_product(output.with_suffix('.asdf'))
    q = saved['qc']
    assert q['provenance']['producer']['source_revision'] == args.assembly_source_revision
    assert q['provenance']['recipe_configuration']['snapshot'] == recipe.read_text()
    assert saved['detector_products'] == [native_qc.read(m['bpm']['asdf']) for m in members]
    actual = hdus(output)
    assert actual[0][1]['NAXIS'] == '0' and actual[0][1]['DETID'] == members[-1]['detector_id']
    assert int(actual[0][1]['NEXTEND']) == len(actual)-1 == len(saved['image_planes'])
    by_id = {m['detector_id']: hdus(Path(m['bpm']['fits'])) for m in members}
    for plane in saved['image_planes']:
        cards, header, data = actual[plane['output_hdu']]
        source = by_id[plane['detector_id']][plane['source_hdu']]
        assert data == source[2] and header['BITPIX'] == source[1]['BITPIX']
        assert header['DETID'] == plane['detector_id'] and header['ORIGFILE'] == output.name
        assert header['EXTNAME'] == (plane['role'] if plane['source_hdu'] else plane['detector_id'])
        slot = next(m['configuration_detector'] for m in members if m['detector_id'] == plane['detector_id'])
        assert int(header['EXTVER']) == slot+1
    completed = {p: sha(p) for p in reduced.iterdir() if p.is_file()}
    assert subprocess.run(argv, capture_output=True).returncode != 0
    assert completed == {p: sha(p) for p in completed}
    relocated = reduced/'relocated'
    relocated.mkdir()
    copied = relocated/output.with_suffix('.asdf').name
    shutil.copyfile(output.with_suffix('.asdf'), copied)
    native_run = subprocess.run
    try:
        subprocess.run = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Saved reader invoked native command'))
        assert assembly.read_product(copied) == saved
    finally:
        subprocess.run = native_run
    tampered = deepcopy(q)
    tampered['characterization']['detectors'][0]['measurements'][0]['value'][0] += 1
    bad = reduced/'tampered.asdf'
    native_qc.qc._asdf().AsdfFile(dict(qc=tampered)).write_to(bad)
    try:
        assembly.read_product(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('Changed joined measurement escaped original-record comparison')
    assert frozen == {p: sha(p) for p in paths}
    print('PASS: native final MEF/ASDF; every padded pixel payload and all stored QC values/mappings preserved')
    print('PASS: original detector provenance, recipe snapshot, exclusive publication and self-contained relocated reader')
    print('COVERAGE: real native ASDF assembly across retained native QC and an explicit synthetic detector-mapping fixture')
    print('No characterization or raw-image read repeated')
    print('RETAINED NATIVE BPM ASSEMBLY:', work)


if __name__ == '__main__':
    main()
