"""Source-only migration ledger builder; lexical evidence, not runtime tracing."""
import configparser
import hashlib
import json
import re
from pathlib import Path

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source-root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).parent
src = args.source_root.resolve()
out = args.output.resolve().parent
names = ['mefpp2/ins/mef/recipes/mefpp.c', 'mefpp2/ins/mef/common/mefp_lib.c', 'Pycavi2/pycavi/pycavi/pycavi_instrument.py', 'Pycavi2/pycavi/pycavi/pycavi_associate_reduction.py', 'Pycavi2/pycavi/pycavi/pycavi_tools.py', 'Pycavi2/pycavi/pycavi/pycavi_metadata.py', 'Pycavi2/pycavi/config/omegacam.cfg', 'Pycavi2/pycavi/config/wfi.cfg', 'Pycavi2/pycavi/config/omegacam.paf', 'Pycavi2/pycavi/config/wfi.paf', 'Pycavi2/pycavi/config/pycavi.cfg', 'Pycavi2/pycavi/config/mefpp.cfg']
files = sorted(src/p for p in names)
identities = {str(p.relative_to(src)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
native = (src/'mefpp2/ins/mef/common/mefp_lib.c').read_text().splitlines()
key = None
getters = []
for n, line in enumerate(native, 1):
    match = re.search(r'sprintf\(buffer,\s*"([^"]+)"', line)
    if match:
        key = match.group(1)
    match = re.search(r'mef_paf_value\(cfgfile, buffer, (\d), &value\)', line)
    if match:
        stop = min(n+12, len(native))
        dest = next((s.strip() for s in native[n:stop] if re.search(r'(?:bb->|\(ccd\+i\)->)[^;]*\s=\s', s)), 'manual review')
        getters.append({'key_template': key, 'kind_code': int(match.group(1)), 'line': n, 'nearby_assignment': dest})

cfg = []
for p in files:
    if p.suffix != '.cfg' or p.name == 'mefpp.cfg':
        continue
    parser = configparser.ConfigParser(inline_comment_prefixes=('#',), interpolation=None)
    parser.read(p)
    for section in parser.sections():
        for name, value in parser.items(section):
            family = re.sub(r'ext_\d+_', 'ext_{n}_', name)
            cfg.append({'file': str(p.relative_to(src)), 'section': section, 'option': name, 'family': family, 'literal_value': value})

cli_source = (src/'mefpp2/ins/mef/recipes/mefpp.c').read_text()
cli = []
for match in re.finditer(r'\{"([^"]+)",\s*([01]),\s*0,\s*(OPT_\w+)\}', cli_source):
    token = match.group(3)
    blocks = re.findall(r'case '+token+r':(.*?)(?=\n\s*case |\n\s*default:)', cli_source, re.S)
    assignments = []
    for block in blocks:
        assignments += sorted(set(re.findall(r'bb->(\w+)', block)))
    cli.append({'option': '--'+match.group(1), 'argument': bool(int(match.group(2))), 'token': token,
                'line': cli_source[:match.start()].count('\n')+1, 'referenced_context_fields': sorted(set(assignments))})

paf = []
for ins in ('omegacam', 'wfi'):
    p = src/f'Pycavi2/pycavi/config/{ins}.paf'
    for n, line in enumerate(p.read_text().splitlines(), 1):
        m = re.match(r'((?:MEF|PHASE3)\.\S+)\s+(.*)', line)
        if m:
            paf.append({'instrument': ins, 'line': n, 'key': m.group(1), 'literal_value': m.group(2)})

ledger = {'source_revision': '0fa9eaf157359a93f2a9196f6fff05dc3e96e220', 'scope': 'lexical source snapshot; no runtime-use/effective-value claim',
          'source_sha256': identities, 'native_getters': getters, 'paf_entries': paf, 'cfg_entries': cfg, 'long_options': cli,
          'short_options': {'L':'license', 'd':'dump effective settings; legacy may continue', 'h':'help', 'x:':'extension selector'},
          'positional': 'first remaining argument overrides output master-flat name after option processing',
          'defaults': [{'location':'mefpp.c:mef_bb_load','value':'mefpp.paf','meaning':'PAF filename unless --pafname'},
                       {'location':'PartitionsTree association calls','value':'science/std bias 10 days; sky science/std 30 days; bias for sky/dome 30 days; dome for sky 30 days','meaning':'preserve per-call policy, not a universal flat rule'},
                       {'location':'copy_paf_to_dir','value':'existing partition PAF; project instrument PAF; engine-prefix instrument PAF','meaning':'existing partition file retained before fallbacks'}],
          'unresolved': ['actual partition-local PAF bytes/effective CLI invocation must be imported from retained pilot records',
                         'native getter conversion/constructor defaults require field-by-field runtime comparison in M1/M2',
                         'Python dynamically selected extension CFG keys require detector-order/identity review in M4',
                         'active executable configuration is user-local, not config/mefpp.cfg; import actual pinned host record',
                         'final TOML property names, override allowlist and parser compatibility remain review decisions']}
args.output.write_text(json.dumps(ledger, indent=2)+'\n')
print(json.dumps({k: len(ledger[k]) for k in ('native_getters','paf_entries','cfg_entries','long_options','source_sha256')}))
