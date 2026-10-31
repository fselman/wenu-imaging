"""Reproduce inherited dependency defects with original units; no actual OOM."""
from pathlib import Path
import subprocess, shlex, json, hashlib, resource, os
root=Path('/workspace/scratch/555b377cf948/eclipse-allocation-failures')
build=root.parent/'eclipse-oom-c90'
work=root.parent/'eclipse-oom-baseline'; work.mkdir(exist_ok=False)
base='e2460fb72bdbe69f92c7da8994a81d21928569b5'
report={'baseline':base,'status':'running','purpose':'Original source NULL-return and borrowed-owner reproductions; no real OOM','commands':[]}
def save(): (work/'run-provenance.json').write_text(json.dumps(report,indent=2)+'\n')
def command(argv,cwd,log,check=True,preexec_fn=None):
    with (work/log).open('wb') as out:
        run=subprocess.run(argv,cwd=cwd,stdout=out,stderr=subprocess.STDOUT,preexec_fn=preexec_fn)
    report['commands'].append({'argv':list(map(str,argv)),'cwd':str(cwd),'status':run.returncode,'log':log})
    save()
    if check: assert run.returncode==0,log
    return run.returncode
try:
    flags={}
    for line in (build/'CMakeFiles/eclipse_allocation_units.dir/flags.make').read_text().splitlines():
        if line.startswith(('C_DEFINES =','C_INCLUDES =','C_FLAGS =')):
            key,value=line.split('=',1); flags[key.strip()]=shlex.split(value)
    link=shlex.split((build/'CMakeFiles/eclipse_allocation_probe.dir/link.txt').read_text())
    for rel in ('src/iproc/image_handling.c','src/iproc/cube_handling.c','src/iproc/cube2image.c','ins/mef/common/mefp_lib.c'):
        original=subprocess.check_output(['git','show',base+':mefpp2/'+rel],cwd=root)
        source=work/Path(rel).name; source.write_bytes(original)
        obj=source.with_suffix('.o')
        report.setdefault('source_sha256',{})[rel]=hashlib.sha256(original).hexdigest()
        # Compile unchanged original units with the same test-only NULL seam.
        command(['/usr/bin/gcc',*flags['C_DEFINES'],*flags['C_INCLUDES'],*flags['C_FLAGS'],'-c',str(source),'-o',str(obj)],build,source.stem+'-compile.log')
        link[link.index('CMakeFiles/eclipse_allocation_units.dir/'+rel+'.o')]=str(obj)
    probe=work/'baseline-probe'; link[link.index('-o')+1]=str(probe)
    command(link,build,'link.log')
    def no_core(): resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    for name in ('image-structure','image-pixels','median-structure','median-pixels','median-timeline','reject-structure','reject-planes','overscan-owner'):
        # Expected failing originals run individually, with core dumps disabled.
        status=command([str(probe),'--site='+name],work,name+'.log',False,no_core)
        assert status!=0, 'Original unexpectedly passed '+name
        print(name,status,flush=True)
    report['status']='passed-original-defects-reproduced'
except BaseException as exc:
    report.update(status='failed',error=repr(exc)); raise
finally: save()
