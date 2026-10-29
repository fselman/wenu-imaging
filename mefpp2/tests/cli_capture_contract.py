"""Compare the unchanged CLI loader with its owned compatibility capture.

Uses synthetic filenames/lists and existing PAFs only; never runs the engine.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--work-parent', type=Path, required=True)
    args = parser.parse_args()
    root = args.source_root.resolve(strict=True)
    probe = args.probe.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='m1-cli-', dir=args.work_parent.resolve(strict=True)))
    print('WORK DIRECTORY:', work, flush=True)
    baseline_path = root / 'docs/architecture/proposed/m1/effective-settings-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    old = root / 'mefpp2/tests/config_snapshot_contract.py'
    spec = importlib.util.spec_from_file_location('snapshot_contract', old)
    contract = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(contract)
    finally:
        sys.dont_write_bytecode = previous
    aliases = {'name_paf': 'paf_path', 'name_bias': 'bias_path', 'name_bpm': 'bpm_path',
               'name_dome': 'dome_path', 'name_sky': 'sky_path', 'name_mf': 'mff_path',
               'name_mf_o': 'mff_output', 'science_name_i': 'science_path', 'name_split': 'split_path',
               'noverify': 'noverify', 'xtnum': 'xtnum', 'bias_subtract': 'bias_subtract',
               'bias_save': 'bias_save', 'dome_save': 'dome_save', 'sky_save': 'sky_save',
               'sat_check': 'sat_check'}
    cases = []
    for i, part in enumerate(baseline['partitions']):
        argv = shlex.split(part['retained_command'])
        if argv[0] == 'nohup':
            argv = argv[1:]
        cases.append({'label': 'retained-%02d' % i, 'instrument': part['instrument'],
                      'argv': argv, 'bindings': part['cli_field_overrides']})
    for instrument in baseline['profiles']:
        prefix = instrument + '-'
        cases.append({'label': prefix + 'defaults', 'instrument': instrument, 'argv': ['mefpp']})
        full = ['mefpp', '--pafname', 'missing-first.paf', '--pafname', 'configs/custom with spaces.paf',
                '--noverify', '-x', '3', '--bias', 'bias "escaped".list', '--bpm', 'bad pixels.list',
                '--dome', 'dome.list', '--sky', 'sky.list', '--mff', 'existing flat.fits',
                '--mffsave', 'explicit_MFF', '--science', 'science ñ.list', '--split', 'split.list',
                '--biassub', '--biassave', '--domesave', '--skysave', '--nosat',
                '--biaskappa1', '0.123456789012345', '--domethr', '0.234567890123456 1.23456789012345',
                '--domemin', '6', '--skythr', '0.345678901234567 1.34567890123456', '--skymin', '7',
                '--scanrej', '2 3', '--pixrej', '3.123456789012345 4.123456789012345',
                '--medianreg', '2 8 3 11', '--satlevel', '55001.23456789012',
                '--satmax', '0.123456789012345', 'positional "MFF"']
        cases.append({'label': prefix + 'full-overrides', 'instrument': instrument, 'argv': full,
                      'bindings': {'name_paf': 'configs/custom with spaces.paf', 'name_bias': 'bias "escaped".list',
                          'name_bpm': 'bad pixels.list', 'name_dome': 'dome.list', 'name_sky': 'sky.list',
                          'name_mf': 'existing flat.fits', 'name_mf_o': 'positional "MFF"',
                          'science_name_i': 'science ñ.list', 'name_split': 'split.list', 'noverify': 1,
                          'xtnum': 3, 'bias_subtract': 1, 'bias_save': 1, 'dome_save': 1, 'sky_save': 1, 'sat_check': 0},
                      'settings': {'bias_kappa1': 0.123456789012345,
                          'dome_framethr_lo': 0.234567890123456, 'dome_framethr_hi': 1.23456789012345,
                          'dome_minframe': 6, 'sky_framethr_lo': 0.345678901234567,
                          'sky_framethr_hi': 1.34567890123456, 'sky_minframe': 7,
                          'scanrej[0]': 2, 'scanrej[1]': 3, 'pixrej_lo': 3.123456789012345,
                          'pixrej_hi': 4.123456789012345, 'median_reg[0]': 2, 'median_reg[1]': 8,
                          'median_reg[2]': 3, 'median_reg[3]': 11, 'sat_level': 55001.23456789012,
                          'sat_max': 0.123456789012345}})
        cases.append({'label': prefix + 'repeated', 'instrument': instrument,
                      'argv': ['mefpp', '--bias', 'first', '--bias', 'last', '--biaskappa1', '1',
                               '--biaskappa1', '2.125suffix', '--xtnum', '-3'],
                      'bindings': {'name_bias': 'last', 'xtnum': -3}, 'settings': {'bias_kappa1': 2.125}})
        cases.append({'label': prefix + 'partial', 'instrument': instrument,
                      'argv': ['mefpp', '--medianreg', '4 9', '--scanrej', '5', '--domethr', '0.25',
                               '--pixrej', '4', '--xtnum', 'nonnumeric'],
                      'settings': {'median_reg[0]': 4, 'median_reg[1]': 9,
                                   'scanrej[0]': 5, 'dome_framethr_lo': 0.25, 'pixrej_lo': 4.0}})
        cases.append({'label': prefix + 'empty-binding', 'instrument': instrument,
                      'argv': ['mefpp', '--science', ''], 'bindings': {'science_name_i': ''}})
        cases.append({'label': prefix + 'display', 'instrument': instrument, 'argv': ['mefpp', '-d']})
        for label, selector in [('first', 1), ('last', baseline['profiles'][instrument]['nchips']),
                                ('negative', -3), ('excessive', baseline['profiles'][instrument]['nchips'] + 1)]:
            cases.append({'label': prefix + 'display-' + label, 'instrument': instrument,
                          'argv': ['mefpp', '-d', '-x', str(selector)], 'bindings': {'xtnum': selector}})
        rejected = [['--ksize', '5'], ['--unknown'], ['--satmax', '1.0'], ['--satmax', 'nan'],
                    ['--satmax', '0'], ['--pafname', 'missing.paf'], ['--bias']]
        for i, options in enumerate(rejected):
            cases.append({'label': prefix + 'rejected-%d' % i, 'instrument': instrument,
                          'argv': ['mefpp'] + options, 'status': 1, 'capture': False})
    for option in ['--help', '-h', '--version', '--license', '-L']:
        cases.append({'label': 'information-' + option.lstrip('-'), 'instrument': 'wfi',
                      'argv': ['mefpp', '--pafname', 'missing.paf', option], 'capture': False, 'no_default_paf': True})
    initial_cwd = Path.cwd()
    report = {'status': 'running', 'host': platform.node(), 'platform': platform.platform(),
              'python': sys.executable, 'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
              'cases': [], 'scope': 'existing CLI loader/capture only; no engine or FITS processing',
              'source_revision': 'see exported-source/target build provenance'}
    source_paths = [baseline_path, old, Path(__file__).resolve(),
                    root / 'mefpp2/tests/cli_capture_probe.c', root / 'mefpp2/ins/mef/recipes/mefpp.c']
    source_paths += sorted((root / 'mefpp2/ins/mef/common').glob('mef_cli*'))
    before_source = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    report['input_sha256'] = before_source
    try:
        for case in cases:
            folder = work / case['label']; folder.mkdir()
            paf = root / ('mefpp2/ins/mef/config/' + case['instrument'] + '.paf')
            data = paf.read_bytes()
            if hashlib.sha256(data).hexdigest() != baseline['profiles'][case['instrument']]['project_paf_sha256']:
                raise RuntimeError('PAF differs from reviewed profile')
            if not case.get('no_default_paf'):
                (folder / 'mefpp.paf').write_bytes(data)
            (folder / 'configs').mkdir()
            (folder / 'configs/custom with spaces.paf').write_bytes(data)
            # These are text sentinels, not real frames; no list expansion is authorized.
            for name in ['science.list', 'bias.list', 'dome.list', 'sky.list', 'split.list']:
                (folder / name).write_text('frame-z.fits\nframe-a with spaces.fits\nframe-z.fits\n')
            protected = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}
            capture = folder / 'request.json'; config = folder / 'config.json'
            command = [str(probe), str(capture), str(config), str(folder)] + case['argv']
            with (folder / 'probe.log').open('w') as log:
                result = subprocess.run(command, cwd=folder, stdout=log, stderr=subprocess.STDOUT, timeout=90)
            if result.returncode != case.get('status', 0):
                raise RuntimeError('Unexpected exit: ' + case['label'])
            if protected != {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in protected}:
                raise RuntimeError('Input changed: ' + case['label'])
            if case.get('capture', True):
                actual_config = json.loads(config.read_text())
                reference = json.loads(Path(str(config) + '.reference').read_text())
                model = copy.deepcopy(baseline)
                for field in model['registry']:
                    name = field['legacy_target'].removeprefix('bb->')
                    values = {**case.get('bindings', {}), **case.get('settings', {})}
                    if name in values:
                        model['profiles'][case['instrument']]['values'][field['key_template']]['modeled_stored_value'] = values[name]
                expected_config = contract.expected_values(model, case['instrument'])
                if actual_config != reference or actual_config != expected_config:
                    differing = sorted(k for k in actual_config.keys() | expected_config.keys() if actual_config.get(k) != expected_config.get(k))
                    raise RuntimeError('Effective config mismatch: ' + case['label'] + ' ' + repr(differing))
                actual = json.loads(capture.read_text())
                expected = {aliases[k]: None for k in ['name_paf', 'name_bias', 'name_bpm', 'name_dome',
                            'name_sky', 'name_mf', 'name_mf_o', 'science_name_i', 'name_split']}
                expected.update({'base_dir': str(folder), 'argc': len(case['argv']), 'argv': case['argv'],
                                 'paf_path': 'mefpp.paf', 'noverify': 0, 'xtnum': 0, 'bias_subtract': 0,
                                 'bias_save': 0, 'dome_save': 0, 'sky_save': 0, 'sat_check': 1})
                # BPM and output-MFF names also come from constructor defaults;
                # preserve their effective values in both legacy views.
                for field in baseline['registry']:
                    name = field['legacy_target'].removeprefix('bb->')
                    if name in aliases:
                        expected[aliases[name]] = baseline['profiles'][case['instrument']]['values'][field['key_template']]['modeled_stored_value']
                for name, value in case.get('bindings', {}).items(): expected[aliases[name]] = value
                region = {}
                for field in model['registry']:
                    if field['legacy_target'].startswith('bb->median_reg['):
                        region[field['legacy_target']] = model['profiles'][case['instrument']]['values'][field['key_template']]['modeled_stored_value']
                expected['median_surface'] = (region['bb->median_reg[1]'] - region['bb->median_reg[0]'] + 1) * (region['bb->median_reg[3]'] - region['bb->median_reg[2]'] + 1)
                if actual != expected:
                    raise RuntimeError('Bindings/argv mismatch: ' + case['label'] + ' ' + repr(actual))
                if '-d' in case['argv']:
                    log_text = (folder / 'probe.log').read_text()
                    selector = expected['xtnum']
                    if selector > baseline['profiles'][case['instrument']]['nchips']:
                        if 'Cannot display detector selector' not in log_text or 'ReadoutNoise' in log_text:
                            raise RuntimeError('Missing bounded display diagnostic')
                    else:
                        chip = selector if selector > 0 else 1
                        ron = baseline['profiles'][case['instrument']]['values']['MEF.CCD.RON.CHIP%d' % chip]['modeled_stored_value']
                        match = re.search(r'ReadoutNoise\s*=\s*(\S+)', log_text)
                        # The legacy diagnostic uses %g (six significant digits);
                        # configuration equality above is checked at full stored bits.
                        if not match or match.group(1) != format(ron, '.6g'):
                            raise RuntimeError('Display RON selector mismatch')
            elif capture.exists() or config.exists():
                raise RuntimeError('Unexpected capture for rejected/informational command')
            report['cases'].append({'label': case['label'], 'instrument': case['instrument'],
                                    'argv': command, 'exit_status': result.returncode,
                                    'captured': case.get('capture', True), 'inputs_unchanged': True})
            print('PASS:', case['label'], flush=True)
        report['status'] = 'CLI-capture-passed'
    except Exception as error:
        report['status'] = 'stopped'; report['error'] = str(error)
        raise
    finally:
        report['cwd_unchanged'] = Path.cwd() == initial_cwd
        report['source_unchanged'] = before_source == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
        if not report['cwd_unchanged'] or not report['source_unchanged']:
            report['status'] = 'stopped-preservation'
        (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
        print('REPORT:', work / 'run-provenance.json', flush=True)
    if report['status'] != 'CLI-capture-passed': raise SystemExit('STOP: preservation failed')
    print('PASS:', len(cases), 'CLI cases; no reduction executed', flush=True)


if __name__ == '__main__':
    main()
