"""Python side of the isolated ASDF 1.6 C/Python interchange qualification."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

import asdf
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve(strict=True)
    assert asdf.__version__ == '6.0.0'
    assert importlib.metadata.version('asdf-standard') == '1.5.0'
    attempts = []
    def offline(event, arguments):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'):
            attempts.append(event)
            raise RuntimeError('Offline interchange attempted network: ' + event)
    sys.addaudithook(offline)
    checks = []
    def probe(*parts):
        subprocess.run([str(args.probe), *map(str, parts)], check=True, timeout=30)
    def standard(path):
        assert b'#ASDF_STANDARD 1.6.0' in path.read_bytes()[:150]
    expected = np.arange(6, dtype=np.float64).reshape(2, 3) - 2.5
    c_file = work / 'from-c.asdf'
    probe('write', c_file)
    standard(c_file)
    with asdf.open(c_file, lazy_load=False) as af:
        af.validate()
        assert af['measurement'] == dict(unit='ADU', value=12.5, unavailable=None)
        np.testing.assert_array_equal(af['profile'], expected)
    checks.append('C-to-Python: metadata/null/float64 shape and every value')
    for compression in (None, 'zlib'):
        path = work / ('from-python-' + str(compression) + '.asdf')
        with asdf.AsdfFile(dict(measurement=dict(unit='ADU', value=12.5, unavailable=None),
                               profile=expected), version='1.6.0') as af:
            af.write_to(path, all_array_compression=compression)
        standard(path)
        probe('read', path)
    checks.append('Python-to-C: uncompressed/zlib float64 shape and every value')
    # Exercise the actual common QC schema and linked raw/product records,
    # not another independently invented QC layout.
    import test_shared_qc as fixture
    fixture.WORK = work
    case = fixture.SharedQcTests(); case.setUp()
    first, second = case.leaf('input1.fits'), case.leaf('input2.fits')
    for leaf in (first, second): fixture.qc.write_record(leaf, case.records)
    record = case.parent(first, second)
    original = fixture.qc.write_record(record, case.records)
    c_copy = case.records / 'c-reemitted.asdf'
    probe('copy-qc', original, c_copy)
    standard(c_copy)
    assert fixture.qc.read_record(c_copy).digest == record.digest
    assert len(list(fixture.qc.traverse_records(c_copy, qc_root=case.records))) == 3
    checks.append('Shared QC: Python-to-C-to-Python schema/content and frozen links')
    assert not attempts
    report = dict(status='passed', standard='1.6.0', asdf=asdf.__version__,
                  asdf_standard=importlib.metadata.version('asdf-standard'),
                  numpy=np.__version__, checks=checks, network_attempts=attempts,
                  scope='synthetic interchange; not complete ASDF conformance or numerical QC')
    (work / 'interchange-results.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
