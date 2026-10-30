"""M2 native compatibility checks; text/configuration only, no FITS or recipe.

The emitter is a test helper, not a replacement PAF decoder or public migration
command. Its input is the actual C PAF constructor's full-precision M1 dump.
"""
import argparse
import copy
import hashlib
import json
import platform
import struct
import subprocess
import tempfile
import tomllib
from pathlib import Path

from config_snapshot_contract import expected_values


def render_snapshot(snapshot):
    lines = ['# Native compatibility envelope; not the final M2 domain schema.',
             'schema_version = 1', '', '[native]']
    for key, entry in snapshot.items():
        tag, value = entry['type'], entry['value']
        if tag == 'string':
            text = json.dumps(value, ensure_ascii=False)
        elif tag == 'int':
            text = str(value)
        elif tag in ('float32-bits', 'float64-bits'):
            number, = struct.unpack('>f' if tag == 'float32-bits' else '>d', bytes.fromhex(value))
            text = repr(number)
        else:
            raise ValueError('Unknown stored type: ' + tag)
        lines.append(json.dumps(key) + ' = ' + text)
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--toml-probe', type=Path, required=True)
    parser.add_argument('--paf-probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    toml_probe, paf_probe = (p.resolve(strict=True) for p in (args.toml_probe, args.paf_probe))
    work = Path(tempfile.mkdtemp(prefix='m2 native config ', dir=args.work_parent.resolve(strict=True)))
    other = work / 'unrelated cwd'; other.mkdir()
    print('WORK DIRECTORY:', work, flush=True)
    commands = []

    def run(argv, label):
        log = work / (label + '.log')
        with log.open('w') as stream:
            result = subprocess.run([str(x) for x in argv], cwd=other, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=90, check=False)
        commands.append({'argv': [str(x) for x in argv], 'exit_status': result.returncode, 'log': log.name})
        if result.returncode:
            raise RuntimeError('STOP: ' + label + '; inspect ' + str(log))

    baseline_path = root / 'docs/architecture/proposed/m1/effective-settings-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    references = {}
    inputs = [baseline_path, toml_probe, paf_probe, Path(__file__).resolve()]
    # Actual PAF constructor: compare native stored types/bits with reviewed M1.
    for instrument, profile in baseline['profiles'].items():
        paf = root / ('mefpp2/ins/mef/config/' + instrument + '.paf')
        original = paf.read_bytes(); inputs.append(paf)
        if hashlib.sha256(original).hexdigest() != profile['project_paf_sha256']:
            raise RuntimeError('PAF source differs from accepted input lock')
        output = work / (instrument + '-paf.json')
        run([paf_probe, paf, output], instrument + '-paf')
        actual = json.loads(output.read_text())
        if actual != expected_values(baseline, instrument):
            raise RuntimeError('Actual PAF constructor disagrees with M1 baseline')
        references[instrument] = actual
        # Conversion evidence retains original bytes/text, including duplicate
        # occurrences and unconsumed keys; none are silently migrated/deleted.
        (work / (instrument + '-source.paf')).write_bytes(original)
        (work / (instrument + '-conversion.json')).write_text(json.dumps({
            'source_sha256': hashlib.sha256(original).hexdigest(),
            'original_text': original.decode(), 'effective_dump': output.name,
            'method': 'actual PAF constructor -> M1 snapshot -> TOML test emitter',
            'limits': 'original PAF decoder and duplicate policy unchanged; not a public importer',
        }, indent=2) + '\n')

    # Native TOML roundtrip: all stored values, clone/source lifetime and every
    # returned-snapshot allocation failure; Python tomllib checks shared syntax.
    edge = copy.deepcopy(references['wfi'])
    for entry in edge.values():
        if entry['type'] == 'string':
            entry['value'] = 'space "quote" \\ slash\n\t\r\b\f café # literal'
        elif entry['type'] == 'float32-bits':
            entry['value'] = '80000000'
        elif entry['type'] == 'float64-bits':
            entry['value'] = '8000000000000000'
    references['edge'] = edge
    for name, expected in references.items():
        path = work / (name + ' config.toml')
        text = render_snapshot(expected); path.write_text(text)
        tomllib.loads(text)
        output = work / (name + '-toml.json')
        run([toml_probe, path, output], name + '-toml')
        if json.loads(output.read_text()) != expected:
            raise RuntimeError('TOML stored-value mismatch: ' + name)
        print('PASS:', name, len(expected), 'exact native settings; ownership/failure controls', flush=True)

    # Rejection/recovery: each bad input is rejected, leaves NULL output, then
    # valid WFI config is read in the same process and compared in full.
    good = work / 'wfi config.toml'
    text = good.read_text()
    def replace(key, value):
        prefix = json.dumps(key) + ' = '
        return '\n'.join(prefix + value if line.startswith(prefix) else line for line in text.splitlines()) + '\n'
    def remove(key):
        prefix = json.dumps(key) + ' = '
        return '\n'.join(line for line in text.splitlines() if not line.startswith(prefix)) + '\n'
    cases = {
        'missing-global': remove('MEF.INSTRUMENT'),
        'missing-detector': remove('MEF.CCD.GAIN.CHIP8'),
        'unknown-key': text + '"MEF.UNKNOWN" = 1\n',
        'unknown-table': text + '\n[unknown]\nx = 1\n',
        'wrong-version': text.replace('schema_version = 1', 'schema_version = 4'),
        'bool-version': text.replace('schema_version = 1', 'schema_version = true'),
        'missing-version': text.replace('schema_version = 1', ''),
        'nul-root-key': text.replace('schema_version = 1', '"schema_version\\u0000ignored" = 1'),
        'duplicate-version': text.replace('schema_version = 1', 'schema_version = 1\nschema_version = 1'),
        'duplicate-same': text + '"MEF.NCHIPS" = 8\n',
        'duplicate-conflict': text + '"MEF.NCHIPS" = 7\n',
        'integer-real': replace('MEF.NCHIPS', '8.0'),
        'integer-bool': replace('MEF.NCHIPS', 'true'),
        'integer-string': replace('MEF.NCHIPS', '"8"'),
        'integer-overflow': replace('MEF.SCANREJ.MIN', '2147483648'),
        'integer-underflow': replace('MEF.SCANREJ.MIN', '-2147483649'),
        'zero-detectors': replace('MEF.NCHIPS', '0'),
        'negative-detectors': replace('MEF.NCHIPS', '-1'),
        'oversized-detectors': replace('MEF.NCHIPS', '2147483647'),
        'extra-detectors': replace('MEF.NCHIPS', '7'),
        'float-integer': replace('MEF.CCD.GAIN.CHIP1', '2'),
        'float-bool': replace('MEF.CCD.GAIN.CHIP1', 'true'),
        'float-string': replace('MEF.CCD.GAIN.CHIP1', '"2.0"'),
        'float-overflow': replace('MEF.CCD.GAIN.CHIP1', '1e100'),
        'double-integer': replace('MEF.BIAS.KAPPA1', '2'),
        'nan': replace('MEF.BIAS.KAPPA1', 'nan'),
        'infinity': replace('MEF.BIAS.KAPPA1', 'inf'),
        'negative-infinity': replace('MEF.BIAS.KAPPA1', '-inf'),
        'string-integer': replace('MEF.INSTRUMENT', '1'),
        'string-array': replace('MEF.INSTRUMENT', '["WFI"]'),
        'string-table': replace('MEF.INSTRUMENT', '{name="WFI"}'),
        'string-date': replace('MEF.INSTRUMENT', '2026-10-30'),
        'nul-string': replace('MEF.INSTRUMENT', '"WFI\\u0000ignored"'),
        'nul-key': text + '"ignored\\u0000key" = 1\n',
        'toml11-escape-e': replace('MEF.INSTRUMENT', '"\\e"'),
        'toml11-escape-x': replace('MEF.INSTRUMENT', '"\\x57FI"'),
        'multiline-string': replace('MEF.INSTRUMENT', '"""WFI"""'),
        'malformed': text + 'broken = [\n',
    }
    bad_inputs = []
    for name, bad_text in cases.items():
        path = work / (name + '.toml'); path.write_text(bad_text); bad_inputs.append((name, path))
    invalid_utf8 = work / 'invalid-utf8.toml'
    invalid_utf8.write_bytes(text.encode().replace(b'WFI', b'W\xffI', 1))
    bad_inputs.append(('invalid-utf8', invalid_utf8))
    bad_inputs.append(('missing-file', work / 'does-not-exist.toml'))
    oversized = work / 'oversized.toml'; oversized.write_bytes(b'#' + b' ' * (4 * 1024 * 1024))
    bad_inputs.append(('oversized-file', oversized))
    for name, path in bad_inputs:
        output = work / (name + '-recovery.json')
        run([toml_probe, good, output, path], name)
        if json.loads(output.read_text()) != references['wfi']:
            raise RuntimeError('Recovery changed valid settings: ' + name)
    print('PASS:', len(bad_inputs), 'rejection/same-process recovery cases', flush=True)

    # Source evidence: exact new code/dependency/probe identities; no installed
    # programs, science inputs or production configuration are modified/read.
    inputs += list((root / 'mefpp2/ins/mef/common').glob('mef*toml*.[ch]'))
    inputs.append(root / 'mefpp2/ins/mef/common/mef_toml_override_keys.def')
    inputs += [root / 'third_party/tomlc17' / name for name in ('tomlc17.c', 'tomlc17.h', 'upstream.json')]
    inputs += [root / 'mefpp2/tests/config_toml_snapshot.c', root / 'mefpp2/ins/mef/common/mef_config.c']
    report = {'status': 'native-toml-compatibility-passed', 'host': platform.node(),
              'platform': platform.platform(), 'commands': commands,
              'exact_value_counts': {name: len(data) for name, data in references.items()},
              'rejection_cases': [name for name, _ in bad_inputs],
              'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'scope': 'native compatibility envelope only; no subset composition, overrides, FITS, recipe or scientific validation'}
    report_path = work / 'run-provenance.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT:', report_path, flush=True)


if __name__ == '__main__':
    main()
