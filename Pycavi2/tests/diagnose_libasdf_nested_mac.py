"""Isolate libasdf scalar versus nested-path writes; no installation or ASDF files."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys

C_SOURCE = r'''
#include <asdf.h>
#include <stdio.h>
#include <string.h>

#define SHOW(call) do { int rc = (call); printf("%s => %d\n", #call, rc); } while (0)
int main(int argc, char **argv) {
    asdf_file_t *f;
    asdf_mapping_t *m;
    double value = -999.0;
    if (argc != 2) return 2;
    setbuf(stdout, NULL);
    printf("OK=%d OOM=%d NOT_FOUND=%d TYPE_MISMATCH=%d\n",
        ASDF_VALUE_OK, ASDF_VALUE_ERR_OOM, ASDF_VALUE_ERR_NOT_FOUND,
        ASDF_VALUE_ERR_TYPE_MISMATCH);
    f = asdf_open(NULL);
    if (!f) return 3;
    if (!strcmp(argv[1], "flat")) {
        SHOW(asdf_set_string0(f, "unit", "ADU"));
        SHOW(asdf_set_double(f, "value", 12.5));
        SHOW(asdf_get_double(f, "value", &value));
    } else if (!strcmp(argv[1], "nested")) {
        SHOW(asdf_set_string0(f, "measurement/unit", "ADU"));
        SHOW(asdf_set_double(f, "measurement/value", 12.5));
        SHOW(asdf_get_double(f, "measurement/value", &value));
    } else if (!strcmp(argv[1], "mapping")) {
        m = asdf_mapping_create(f);
        if (!m) { asdf_close(f); return 4; }
        SHOW(asdf_mapping_set_string0(m, "unit", "ADU"));
        SHOW(asdf_mapping_set_double(m, "value", 12.5));
        SHOW(asdf_mapping_set_null(m, "unavailable"));
        /* asdf_set_mapping consumes the mapping wrapper. */
        SHOW(asdf_set_mapping(f, "measurement", m));
        SHOW(asdf_get_double(f, "measurement/value", &value));
    } else { asdf_close(f); return 2; }
    printf("readback=%.17g\n", value);
    asdf_close(f);
    return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    if (platform.system(), platform.machine(), platform.node().split('.')[0]) != ('Darwin', 'x86_64', 'MC02VV0HPHTDG'):
        raise RuntimeError('Intel Mac only')
    if Path(sys.prefix) != Path('/Users/fselman/anaconda3/envs/wenu-imaging'):
        raise RuntimeError('Unexpected guard interpreter')
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        raise RuntimeError('Require niceness >=10')
    work = args.work.resolve(strict=True)
    if args.work.is_symlink() or work.parent != Path('/Users/fselman/Software/build/wenu-imaging') or {p.name for p in work.iterdir()} != {'diagnose.py'}:
        raise RuntimeError('Require fresh diagnostic directory')
    repo = Path('/Users/fselman/Developer/wenu-imaging')
    def git(*parts):
        return subprocess.check_output(['/usr/bin/git', '-C', str(repo), *parts])
    before = [git(*parts) for parts in [('rev-parse', 'HEAD'), ('branch', '--show-current'),
        ('rev-parse', '--abbrev-ref', '@{upstream}'), ('status', '--porcelain=v1', '--untracked-files=all')]]
    if before != [b'47123eedaaa31b4464238ffaaf1b690f7d2cde40\n', b'main\n', b'origin/main\n', b'']:
        raise RuntimeError('Expected unchanged clean main')
    old = work.parent / 'mac-asdf16-external-dFpUmHsz'
    report = json.loads((old / 'libasdf-qualification.json').read_text())
    helper_path = old / 'source/Pycavi2/tests/qualify_libasdf_mac.py'
    if helper_path.read_bytes() != git('show', '33f165559eef59d7fb1479f6dd1520b6fd7248c5:Pycavi2/tests/qualify_libasdf_mac.py'):
        raise RuntimeError('Retained protection helper mismatch')
    helper = runpy.run_path(str(helper_path))
    if not report['reused_prefix_preserved']:
        raise RuntimeError('Prior prefix preservation failed')
    prefix = helper['retained_prefix'](work.parent / 'mac-asdf16-streams-o8KPDcUm', work)
    identity = helper['prefix_identity'](prefix)
    manifest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    if manifest != report['reused_prefix_manifest_sha256']:
        raise RuntimeError('Retained prefix changed since interchange failure')
    source = work / 'nested-path.c'; source.write_text(C_SOURCE)
    probe = work / 'nested-path'
    command = next(c for c in report['commands'] if c['label'] == 'compile-c17')
    if command['exit_status'] != 0:
        raise RuntimeError('Original compilation was not successful')
    argv = command['argv'][:]
    argv[argv.index(str(old / 'source/Pycavi2/tests/asdf16_interop.c'))] = str(source)
    argv[argv.index('-o') + 1] = str(probe)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    for key in ('PYTHONPATH', 'DYLD_LIBRARY_PATH', 'LD_LIBRARY_PATH'):
        env.pop(key, None)
    commands = []
    result = dict(status='failed', scope='in-memory API diagnosis, not interchange qualification', commands=commands)
    try:
        helper['run_logged']('compile-diagnostic', argv, work=work, env=env, commands=commands)
        for case in ('flat', 'nested', 'mapping'):
            # Separate processes preserve evidence even if a specific API path crashes.
            try:
                output = helper['run_logged'](case, [probe, case], work=work, env=env,
                    commands=commands, capture=True, timeout=60)
                print(output, flush=True)
            except RuntimeError as error:
                print(str(error), flush=True)
        result['status'] = 'diagnostic-completed'
    finally:
        result['prefix_preserved'] = identity == helper['prefix_identity'](prefix)
        result['checkout_preserved'] = before == [git(*parts) for parts in [('rev-parse', 'HEAD'),
            ('branch', '--show-current'), ('rev-parse', '--abbrev-ref', '@{upstream}'),
            ('status', '--porcelain=v1', '--untracked-files=all')]]
        (work / 'diagnostic-results.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2), flush=True)
        if not result['prefix_preserved'] or not result['checkout_preserved']:
            raise RuntimeError('Preservation failure')


if __name__ == '__main__':
    main()
