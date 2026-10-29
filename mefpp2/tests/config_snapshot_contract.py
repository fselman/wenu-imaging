"""Private C90 snapshot checks against reviewed OCAM/WFI mapped state.

Uses real repository legacy headers, synthetic state, no PAF/FITS I/O or
scientific processing. A fresh work directory is always retained. This is not
an installed ABI test or proof of actual-constructor equivalence.
"""
import argparse
import ctypes
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import tempfile


def c_string(value):
    # UTF-8 octal bytes avoid source-encoding and hexadecimal escape ambiguity.
    return '"' + ''.join('\\%03o' % b for b in value.encode('utf-8')) + '"'


def fixture_source(baseline):
    lines = ['static char *fixture_string(const char *value) {',
             '    size_t n; char *p; n = strlen(value) + 1;',
             '    p = (malloc)(n); assert(p != NULL); memcpy(p, value, n); return p;',
             '}', 'static void fixture_init(mef_bb *source, const char *profile) {',
             '    memset(source, 0, sizeof(*source));']
    for instrument, data in baseline['profiles'].items():
        lines.append('    if (strcmp(profile, %s) == 0) {' % c_string(instrument))
        lines.append('        source->nchips = %d;' % data['nchips'])
        lines.append('        source->ccd = (calloc)((size_t)source->nchips, sizeof(*source->ccd));')
        lines.append('        assert(source->ccd != NULL);')
        for field in baseline['registry']:
            chips = range(1, data['nchips'] + 1) if '%d' in field['key_template'] else [None]
            for chip in chips:
                key = field['key_template'] % chip if chip else field['key_template']
                value = data['values'][key]['modeled_stored_value']
                target = field['legacy_target'].replace('bb->', 'source->')
                if chip:
                    target = target.replace('(ccd+i)->', 'source->ccd[%d].' % (chip - 1))
                expression = 'fixture_string(%s)' % c_string(value) if field['kind_code'] == 0 else repr(value)
                lines.append('        %s = %s;' % (target, expression))
        lines.extend(['        return;', '    }'])
    lines.extend(['    assert(0);', '}'])
    return '\n'.join(lines) + '\n'


def expected_values(baseline, instrument):
    result = {}
    data = baseline['profiles'][instrument]
    for field in baseline['registry']:
        chips = range(1, data['nchips'] + 1) if '%d' in field['key_template'] else [None]
        for chip in chips:
            key = field['key_template'] % chip if chip else field['key_template']
            value = data['values'][key]['modeled_stored_value']
            ctype = field['legacy_storage_type'].split('[')[0]
            if ctype in ('float', 'double'):
                tag, fmt = ('float32-bits', '>f') if ctype == 'float' else ('float64-bits', '>d')
                value = struct.pack(fmt, value).hex()
            else:
                tag = 'string' if ctype == 'char *' else 'int'
            result[key] = {'type': tag, 'value': value}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True, help='monorepo root')
    parser.add_argument('--cc', type=Path, required=True, help='explicit compiler executable')
    parser.add_argument('--work-parent', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true', help='ASan/UBSan, only where supported')
    parser.add_argument('--sysroot', type=Path, help='explicit SDK root when required by compiler')
    parser.add_argument('--c-standard', choices=('90', '17'), default='90')
    parser.add_argument('--paf-probe', type=Path, help='optional source-built config_paf_snapshot executable')
    args = parser.parse_args()
    if not args.cc.is_absolute():
        raise SystemExit('Supply an absolute compiler path')
    root, compiler = args.source_root.resolve(), args.cc.resolve(strict=True)
    if not os.access(compiler, os.X_OK):
        raise SystemExit('Compiler must be executable')
    baseline_path = root / 'docs/architecture/proposed/m1/effective-settings-baseline.json'
    baseline = json.loads(baseline_path.read_text())
    synthetic = copy.deepcopy(baseline)
    edge = copy.deepcopy(baseline['profiles']['wfi'])
    for field in baseline['registry']:
        key = field['key_template']
        if '%d' in key:
            continue
        if field['legacy_storage_type'] == 'char *':
            edge['values'][key]['modeled_stored_value'] = 'space "quote" \\ slash\n\t\r café'
        elif field['legacy_storage_type'] in ('float', 'double'):
            edge['values'][key]['modeled_stored_value'] = -0.0
    edge['values']['MEF.CCD.GAIN.CHIP1']['modeled_stored_value'] = -0.0
    synthetic['profiles']['edge'] = edge
    parent = args.work_parent.resolve(strict=True)
    work = Path(tempfile.mkdtemp(prefix='m1-config-', dir=parent))
    print('WORK DIRECTORY:', work, flush=True)
    # Header-only legacy dependencies need dimensions, not the full build system.
    sizes = {'CHAR': ctypes.c_char, 'SHORT': ctypes.c_short, 'INT': ctypes.c_int,
             'LONG': ctypes.c_long, 'FLOAT': ctypes.c_float, 'DOUBLE': ctypes.c_double}
    config = '#include <limits.h>\n' + ''.join('#define SIZEOF_%s %d\n' % (k, ctypes.sizeof(v)) for k, v in sizes.items())
    if platform.system() not in ('Linux', 'Darwin'):
        raise SystemExit('Only Linux/Darwin are in scope')
    config += '#define OS_%s 1\n' % ('LINUX' if platform.system() == 'Linux' else 'DARWIN')
    if struct.pack('=I', 1)[0] == 0:
        config += '#define WORDS_BIGENDIAN 1\n'
    for name in ('mefpp_platform_config.h', 'qfits_platform_config.h'):
        (work / name).write_text(config)
    (work / 'config_snapshot_fixture.h').write_text(fixture_source(synthetic))
    common = root / 'mefpp2/ins/mef/common'
    executable = work / 'config_snapshot'
    command = [str(compiler), '-std=c' + args.c_standard, '-pedantic-errors', '-Wall', '-Wextra', '-Werror',
               '-UNDEBUG', '-D_DEFAULT_SOURCE=1', '-D_DARWIN_C_SOURCE=1',
               '-I' + str(work), '-I' + str(common),
               '-I' + str(root / 'mefpp2/src/include'),
               '-I' + str(root / 'mefpp2/qfits5/include'),
               str(common / 'mef_config.c'), str(root / 'mefpp2/tests/config_snapshot.c'),
               '-o', str(executable)]
    if args.sanitize:
        command[1:1] = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
    if args.sysroot:
        command[1:1] = ['-isysroot', str(args.sysroot.resolve(strict=True))]
    commands = []
    def run(argv, label):
        with (work / (label + '.log')).open('w') as log:
            completed = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT,
                                       cwd=work, timeout=120, check=False)
        commands.append({'argv': argv, 'exit_status': completed.returncode, 'log': label + '.log'})
        if completed.returncode:
            raise RuntimeError('STOP: %s; inspect %s' % (label, work / (label + '.log')))
    run([str(compiler), '--version'], 'compiler')
    run(command, 'compile')
    for instrument in synthetic['profiles']:
        output = work / (instrument + '.json')
        run([str(executable), instrument, str(output)], instrument)
        actual = json.loads(output.read_text())
        expected = expected_values(synthetic, instrument)
        if actual != expected:
            differing = sorted(k for k in actual.keys() | expected.keys() if actual.get(k) != expected.get(k))
            raise RuntimeError('Snapshot mismatch: ' + repr(differing))
        print('PASS:', instrument, len(actual), 'exact mapped values', flush=True)
    if args.paf_probe:
        probe = args.paf_probe.resolve(strict=True)
        for instrument, profile in baseline['profiles'].items():
            paf = root / ('mefpp2/ins/mef/config/' + instrument + '.paf')
            if hashlib.sha256(paf.read_bytes()).hexdigest() != profile['project_paf_sha256']:
                raise RuntimeError('PAF changed from reviewed baseline: ' + str(paf))
            output = work / (instrument + '-paf.json')
            run([str(probe), str(paf), str(output)], instrument + '-paf')
            if json.loads(output.read_text()) != expected_values(baseline, instrument):
                raise RuntimeError('Actual PAF constructor mismatch: ' + instrument)
            print('PASS:', instrument, 'actual PAF constructor snapshot', flush=True)
    # Include generated fixture/header and exact implementation hashes for audit.
    inputs = [baseline_path, common / 'mef_config.c', common / 'mef_config.h',
              common / 'mef_config_fields.def', common / 'mef_config_members.h',
              common / 'mefp_lib.h', root / 'mefpp2/tests/config_snapshot.c', Path(__file__).resolve()]
    if args.paf_probe:
        inputs.extend([probe, root / 'mefpp2/ins/mef/config/omegacam.paf',
                       root / 'mefpp2/ins/mef/config/wfi.paf'])
    report = {'status': 'synthetic-config-snapshot-passed', 'host': platform.node(),
              'platform': platform.platform(), 'compiler': str(compiler), 'sanitize': args.sanitize, 'c_standard': args.c_standard,
              'commands': commands, 'diagnostic_environment': {k: os.environ.get(k) for k in ('ASAN_OPTIONS', 'UBSAN_OPTIONS', 'LSAN_OPTIONS')},
              'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
              'paf_constructor_checked': bool(args.paf_probe),
              'scope': 'configuration only; no FITS, recipe execution, installation or scientific acceptance'}
    (work / 'run-provenance.json').write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT:', work / 'run-provenance.json')


if __name__ == '__main__':
    main()
