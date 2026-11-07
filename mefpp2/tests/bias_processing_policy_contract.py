"""Shared processing TOML/clone controls; no observations, FITS or ASDF I/O."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
from config_toml_contract import render_snapshot
from config_toml_domains_contract import render_domains


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probe', type=Path, required=True)
    p.add_argument('--settings', type=Path, required=True)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    a = p.parse_args()
    a.work.mkdir(parents=True, exist_ok=False)
    initial = a.work / 'initial.json'
    loaded = subprocess.run([str(a.probe), str(a.settings), str(initial)], capture_output=True, text=True)
    (a.work / 'initial.log').write_text(loaded.stdout + loaded.stderr)
    assert loaded.returncode == 0, loaded.stderr
    base = render_snapshot(json.loads(initial.read_text()))
    count = 0

    def run(name, text, okay=True):
        nonlocal count
        f = a.work / (name + '.toml')
        f.write_text(text)
        output = f.with_suffix('.json')
        r = subprocess.run([str(a.probe), str(f), str(output)], capture_output=True, text=True)
        f.with_suffix('.log').write_text(r.stdout + r.stderr)
        assert (r.returncode == 0) == okay, (name, r.returncode, r.stderr)
        count += 1
        return json.loads(output.read_text()) if okay else None

    legacy = run('legacy', base)
    binary = '\n"BPM.ENCODING" = "binary"\n"BPM.BAD_WHEN" = "zero"\n'
    zero = binary.replace('"zero"', '"nonzero"')
    reason = '\n"BPM.ENCODING" = "reason8"\n"BPM.BAD_WHEN" = "nonzero"\n"BPM.REJECT_BITS" = 255\n"BPM.REGISTRY" = "WENU_BPM_V1"\n'
    clip = '\n"QC.RON.CLIP.ENABLED" = 1\n"QC.RON.CLIP.LOW" = 5.0\n"QC.RON.CLIP.HIGH" = 5.0\n"QC.RON.CLIP.MAX_ITERATIONS" = 10\n'
    for name, extra in [('binary', binary), ('zero-good', zero), ('reason', reason),
                        ('clip', clip), ('combined', reason + clip), ('disabled', clip.replace(' = 1\n', ' = 0\n'))]:
        actual = run(name, base + extra)
        assert all(actual[k] == v for k, v in legacy.items())
        expected = dict(legacy)
        import tomllib
        for key, value in tomllib.loads(base + extra)['native'].items():
            if key in legacy:
                continue
            if isinstance(value, str):
                expected[key] = {'type': 'string', 'value': value}
            elif isinstance(value, int):
                expected[key] = {'type': 'int', 'value': value}
            else:
                expected[key] = {'type': 'float64-bits', 'value': struct.pack('>d', value).hex()}
        assert actual == expected
        catalog = json.loads((a.source_root / 'docs/architecture/proposed/m2/typed-field-catalog.json').read_text())
        domain = render_domains(actual, catalog)
        assert run(name + '-domain', domain) == actual
    bad = [binary.replace('"zero"', '"guess"'), binary.replace('"binary"', '"guess"'),
           binary + '"BPM.REJECT_BITS" = 255\n', reason.replace(' = 255', ' = 256'),
           reason.replace(' = 255', ' = -1'), reason.replace('"nonzero"', '"zero"'),
           reason.replace('"WENU_BPM_V1"', '"bad registry"'), reason.replace('"WENU_BPM_V1"', '"' + 'A'*33 + '"'),
           clip.replace(' = 5.0', ' = 0.0'), clip.replace(' = 5.0', ' = 5'),
           clip.replace(' = 10', ' = 0'), clip.replace(' = 10', ' = 1001'),
           clip.replace(' = 1\n', ' = 2\n')]
    for extra in [binary, reason, clip]:
        lines = extra.strip().splitlines()
        bad.extend('\n' + '\n'.join(lines[:i] + lines[i+1:]) + '\n' for i in range(len(lines)))
    for i, extra in enumerate(bad):
        run(f'refuse-{i:02d}', base + extra, False)
    (a.work / 'results.json').write_text(json.dumps({'successful': True, 'cases': count,
        'legacy_fields': len(legacy), 'raw_files_read': False}, indent=2) + '\n')
    print(f'PASS: {count} shared processing policy cases, exact legacy fields, native/domain equivalence, clone/owner failure checks')


if __name__ == '__main__':
    main()
