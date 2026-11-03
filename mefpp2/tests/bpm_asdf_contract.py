"""Qualified-ASDF child: common writer, frozen references and rejection checks."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import socket
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--module-root', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    sys.path.insert(0, str(a.module_root))
    import pycavi_bpm_qc as bpm
    import pycavi_qc as qc
    attempts = []

    def blocked(*args, **kwargs):
        attempts.append('network')
        raise RuntimeError('Network access forbidden in QC contract')

    socket.create_connection = blocked
    socket.socket.connect = blocked
    handoff = a.work/'handoff.json'
    directory = a.work/'qc'
    directory.mkdir()
    output = bpm.publish_handoff(handoff, directory,
        configuration_record=a.work/'configuration.json', assessment_id='synthetic-bpm-publication')
    t = json.loads(handoff.read_text())
    visited = list(qc.traverse_records(output, qc_root=directory))
    assert len(visited) == len(t['inputs'])+len(t['calibrations'])+1
    record = qc.read_record(output).as_dict()
    assert record['provenance']['operation'] == 'cal.bpm'
    assert record['file']['selectors'][0]['hdu_index'] == 0
    assert record['extensions']['bpm']['configuration_sha256']
    assert [i['participation']['status'] for i in record['inputs'][:len(t['inputs'])]] == [
        'used' if i['included'] else 'rejected' for i in t['inputs']]
    quantities = {m['name']: m['value'] for m in record['characterization']['detectors'][0]['measurements']}
    assert quantities['reasons.histogram'] == t['reason_histogram']
    assert quantities['fit.coverage_histogram'] == t['fit_histogram']
    assert output.read_bytes().startswith(b'#ASDF 1.0.0') and b'#ASDF_STANDARD 1.6.0' in output.read_bytes()[:120]
    assert all(not f.name.endswith('.fits.asdf') for f in directory.iterdir())
    before = {f.name: f.read_bytes() for f in directory.iterdir()}
    try:
        bpm.publish_handoff(handoff, directory, configuration_record=a.work/'configuration.json', assessment_id='again')
    except qc.QcError:
        pass
    else:
        raise AssertionError('Overwrite accepted')
    assert before == {f.name: f.read_bytes() for f in directory.iterdir()}
    # Modify only a private copy: a schema-valid changed leaf must break links.
    copy = a.work/'tampered-qc'
    shutil.copytree(directory, copy)
    leaf_name = record['inputs'][0]['qc']['path']
    leaf = qc.read_record(copy/leaf_name).as_dict()
    leaf['extensions']['deliberately_changed'] = True
    (copy/leaf_name).rename(copy/(leaf_name+'.original'))
    qc.write_record(qc.QcRecord(qc.encoded(leaf)), copy, qc_root=copy)
    try:
        list(qc.traverse_records(copy/output.name, qc_root=copy))
    except qc.QcError:
        pass
    else:
        raise AssertionError('Changed frozen leaf accepted')
    # Malformed transport/configuration fails before any ASDF file is written.
    changed = deepcopy(t)
    changed['fit_histogram'][0] += 1
    bad = a.work/'bad-handoff.json'
    bad.write_text(json.dumps(changed))
    empty = a.work/'rejected-qc'
    empty.mkdir()
    try:
        bpm.publish_handoff(bad, empty, configuration_record=a.work/'configuration.json', assessment_id='bad')
    except qc.QcError:
        pass
    else:
        raise AssertionError('Malformed histogram accepted')
    assert not list(empty.iterdir())
    wrong_config = a.work/'wrong-configuration.json'
    wrong_config.write_text('{}')
    try:
        bpm.publish_handoff(handoff, empty, configuration_record=wrong_config, assessment_id='bad-config')
    except qc.QcError:
        pass
    else:
        raise AssertionError('Changed configuration accepted')
    assert not list(empty.iterdir())
    assert not attempts
    print('PASS: common ASDF1.6 writer, every input/product, frozen links, no overwrite or network')


if __name__ == '__main__':
    main()
