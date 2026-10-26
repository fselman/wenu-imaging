"""Compile-only GCC symbol/call inventory; not a production build or runtime coverage test."""
import argparse
from collections import defaultdict
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile


def main():
    # Isolation/provenance: unpack tracked native sources and lower analysis priority.
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--records-parent', type=Path, required=True)
    args = p.parse_args()
    source = args.source.resolve()
    work = Path(tempfile.mkdtemp(prefix='native-symbol-analysis-', dir=args.records_parent))
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        os.nice(10 - os.getpriority(os.PRIO_PROCESS, 0))
    def git(*argv):
        return subprocess.check_output(['git', *argv], cwd=source)
    archive = git('archive', 'HEAD', 'mefpp2', 'qfits52')
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(work, filter='data')
    trees = {name: git('rev-parse', 'HEAD:' + name).decode().strip()
             for name in ('mefpp2', 'qfits52')}
    originals = {str(f.relative_to(work)): hashlib.sha256(f.read_bytes()).hexdigest()
                 for package in trees for f in (work/package).rglob('*') if f.is_file()}

    # Host header generation: configure only copies, with explicit qfits source path.
    config_results = []
    for package, flags in (
        ('qfits52', ['--with-cc', '--prefix=' + str(work/'unused-prefix')]),
        ('mefpp2', ['--with-cc', '--qfits=' + str(work/'qfits52'),
                    '--prefix=' + str(work/'unused-prefix')]),
    ):
        result = subprocess.run(['/bin/sh', './configure', *flags], cwd=work/package,
                                text=True, capture_output=True, timeout=30)
        (work/(package+'-configure.log')).write_text(result.stdout+result.stderr)
        assert result.returncode == 0 and (work/package/'config.make').exists()
        config_results.append({'package':package, 'returncode':result.returncode})

    # Build-list inventory: select the actual Eclipse/qfits archive translation units.
    def listed_sources(makefile):
        text = makefile.read_text().replace('\\\n', ' ')
        value = re.search(r'^SRCS\s*=\s*(.+)$', text, re.M).group(1)
        return [makefile.parent/name for name in value.split()]
    eclipse = listed_sources(work/'mefpp2/src/Makefile')
    qfits = listed_sources(work/'qfits52/Makefile')
    roots = [work/'mefpp2/ins/mef/recipes/mefpp.c',
             work/'mefpp2/ins/mef/common/mefp_lib.c']
    groups = [('mefpp', f) for f in roots] + [('eclipse',f) for f in eclipse] + [
        ('qfits',f) for f in qfits]
    objects = work/'objects'
    objects.mkdir()
    units = []
    for index, (group, f) in enumerate(groups):
        # Compile-only analysis: retain warnings and initial GCC call graph; no link/run.
        obj = objects/(str(index).zfill(3)+'_'+f.stem+'.o')
        command = ['/usr/bin/gcc', '-O0', '-g', '-fdump-ipa-cgraph',
                   '-I'+str(work/'mefpp2/src/include'),
                   '-I'+str(work/'mefpp2/ins/mef/common'),
                   '-I'+str(work/'qfits52/include'), '-D_ECLIPSE_',
                   '-c', str(f), '-o', str(obj)]
        result = subprocess.run(command, cwd=objects, text=True, capture_output=True, timeout=60)
        log = work/(obj.stem+'.log')
        log.write_text(result.stdout+result.stderr)
        unit = dict(group=group, source=str(f.relative_to(work)), object=str(obj),
                    returncode=result.returncode, log=str(log), command=command)
        if result.returncode == 0:
            # Object symbols: distinguish exported definitions from unresolved references.
            for key, nmflags in [('defined',['-g','--defined-only']),('undefined',['-u'])]:
                output = subprocess.check_output(['/usr/bin/nm','--format=posix',*nmflags,str(obj)],text=True)
                unit[key] = sorted({line.split()[0] for line in output.splitlines() if line.strip()})
            graph = obj.with_suffix('.c.000i.cgraph')
            if not graph.exists():
                candidates = list(objects.glob(obj.stem+'*.cgraph'))
                assert len(candidates)==1,(obj,candidates)
                graph = candidates[0]
            text = graph.read_text().split('Initial Symbol table:',1)[1].split('Removing unused symbols:',1)[0]
            nodes = {}
            for block in re.split(r'(?m)(?=^[\w.$]+/\d+ \()',text):
                header = re.match(r'^([\w.$]+)/\d+ \(',block)
                if not header or 'Type: function definition' not in block:
                    continue
                calls = re.search(r'^  Calls:(.*)$',block,re.M)
                refs = re.search(r'^  References:(.*)$',block,re.M)
                nodes[header.group(1)] = dict(
                    calls=sorted(set(re.findall(r'([\w.$]+)/\d+',calls.group(1) if calls else ''))),
                    references=sorted(set(re.findall(r'([\w.$]+)/\d+',refs.group(1) if refs else ''))),
                    indirect_call_present='Indirect call' in block,
                )
            unit['functions']=nodes
        units.append(unit)
    failures = [u for u in units if u['returncode']]
    assert not failures,[(u['source'],u['log']) for u in failures]

    # Archive-object closure: conservatively select translation units demanded by roots.
    definitions = defaultdict(list)
    for i,u in enumerate(units):
        for name in u['defined']:
            definitions[name].append(i)
    needed = {0,1}
    direct = set()
    for i in (0,1):
        for name in units[i]['undefined']:
            direct.update(definitions.get(name,[]))
    while True:
        new = set(needed)
        for i in needed:
            for name in units[i]['undefined']:
                new.update(definitions.get(name,[]))
        if new == needed:
            break
        needed = new

    # Function-call closure: resolve local definitions first, then exported definitions.
    def resolve(i,name):
        if name in units[i]['functions']:
            return [(i,name)]
        return [(j,name) for j in definitions.get(name,[]) if name in units[j]['functions']]
    reachable = {(0,'main')}
    queue = list(reachable)
    unresolved_calls = set()
    while queue:
        i,name = queue.pop()
        node = units[i]['functions'][name]
        for called in node['calls'] + node['references']:
            targets = resolve(i,called)
            if not targets:
                unresolved_calls.add(called)
            for target in targets:
                if target not in reachable:
                    reachable.add(target)
                    queue.append(target)
    for i,u in enumerate(units):
        u['direct_object_dependency'] = i in direct
        u['in_object_closure'] = i in needed
        u['potentially_reachable_functions'] = sorted(name for j,name in reachable if j==i)
    counts = {}
    for group in ('mefpp','eclipse','qfits'):
        subset=[u for u in units if u['group']==group]
        counts[group] = dict(translation_units=len(subset),
                            direct_objects=sum(u['direct_object_dependency'] for u in subset),
                            object_closure=sum(u['in_object_closure'] for u in subset),
                            function_reachable_units=sum(bool(u['potentially_reachable_functions']) for u in subset),
                            defined_functions=sum(len(u['functions']) for u in subset),
                            potentially_reachable_functions=sum(len(u['potentially_reachable_functions']) for u in subset))

    # Preservation/provenance: verify all non-generated source bytes and retain full results.
    generated={'mefpp2/src/include/config.h','qfits52/src/config.h'}
    for name,want in originals.items():
        if name not in generated:
            assert hashlib.sha256((work/name).read_bytes()).hexdigest()==want,name
    report=dict(source_checkout=str(source),source_commit=git('rev-parse','HEAD').decode().strip(),
                native_trees=trees,work=str(work),compiler=subprocess.check_output(['/usr/bin/gcc','--version'],text=True).splitlines()[0],
                configuration=config_results,counts=counts,units=units,
                unresolved_symbol_references=sorted(unresolved_calls),
                duplicate_exported_symbols={k:[units[i]['source'] for i in v] for k,v in definitions.items() if len(v)>1},
                scope='GCC O0 Linux static potential-call and conservative object inventory; no target build/link/runtime coverage; indirect callbacks and other configurations require separate review')
    (work/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'work':str(work),'counts':counts,'duplicate_exported_symbols':report['duplicate_exported_symbols']},indent=2))


if __name__=='__main__':
    main()
