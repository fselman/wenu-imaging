"""Original format/newline controls; no actual exhaustion or external display."""
from pathlib import Path
import subprocess,shlex,json,hashlib,resource,os
root=Path('/workspace/scratch/555b377cf948/eclipse-allocation-failures'); parent=root.parent
build=parent/'eclipse-oom-asan'; work=parent/'format-batch-baseline'; work.mkdir(exist_ok=False)
base='2699aa97228baa22956be30d7e8a68e826ea7c93'
record=dict(status='running',repository=str(root),branch='fix/eclipse-allocation-failures',commit=base,dirty=True,purpose=__doc__,retention='Preserve original expected failures; mixed private probe/link environment',commands=[],source_sha256={})
def sha(data): return hashlib.sha256(data).hexdigest()
def save(): (work/'run-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
for rel in ['src/unix/comm.c','src/unix/t_iso8601.c','qfits5/src/qerror.c','qfits5/src/fits_h.c']:
 data=subprocess.check_output(['git','show',base+':mefpp2/'+rel],cwd=root)
 p=work/(rel.replace('/','_'));p.write_bytes(data);record['source_sha256'][rel]=sha(data)
flags={}
for line in (build/'CMakeFiles/format_safety_probe.dir/flags.make').read_text().splitlines():
 if line.startswith(('C_DEFINES =','C_INCLUDES =','C_FLAGS =')):
  key,value=line.split('=',1);flags[key.strip()]=shlex.split(value)
clock='''#include <time.h>\n#include <sys/time.h>\nstatic time_t ft(time_t *p){if(p)*p=(time_t)253402300800.0;return (time_t)253402300800.0;}\nstatic int fg(struct timeval*p,void*z){(void)z;p->tv_sec=(time_t)253402300800.0;p->tv_usec=0;return 0;}\n#define time ft\n#define gettimeofday fg\n'''
programs={
'comm-long':'#include "src_unix_comm.c"\nint main(void){char s[6000];memset(s,\'x\',5999);s[5999]=0;e_error("%s",s);return 0;}\n',
'comm-newlines':'#include "src_unix_comm.c"\nint main(void){e_error("\\n\\n");return 0;}\n',
'qfits-long':'#include "qfits5_src_qerror.c"\nint main(void){char s[6000];memset(s,\'x\',5999);s[5999]=0;qfits_err_statset(1);qfits_error("%s",s);return 0;}\n',
'date-year':clock+'#include "src_unix_t_iso8601.c"\nint main(void){puts(get_datetime_iso8601());return 0;}\n',
'header-percent':'#include "qfits5_src_fits_h.c"\nint main(void){qfits_header*h=qfits_header_default();FILE*f=tmpfile();char s[4096];size_t n;qfits_header_add(h,"OBJECT","100%%","literal",NULL);qfits_header_dump_hdr(h,f);rewind(f);n=fread(s,1,sizeof(s)-1,f);s[n]=0;return strstr(s,"100%%")==NULL?23:0;}\n'}
def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
try:
 for name,content in programs.items():
  source=work/(name+'.c');source.write_text(content);exe=work/name
  argv=['/usr/bin/gcc',*flags['C_DEFINES'],*flags['C_INCLUDES'],*flags['C_FLAGS'],str(source),'-o',str(exe),str(build/'libmefpp_common.a'),str(build/'libeclipse.a'),str(build/'libqfits.a'),'-lm','-fsanitize=address,undefined','-no-pie']
  with (work/(name+'-compile.log')).open('w') as stream:r=subprocess.run(argv,stdout=stream,stderr=subprocess.STDOUT)
  record['commands'].append(dict(argv=argv,status=r.returncode));save();assert r.returncode==0,name
  with (work/(name+'.log')).open('w') as stream:
   r=subprocess.run([str(exe)],cwd=work,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1','TZ':'UTC','TERM':'dumb'},stdout=stream,stderr=subprocess.STDOUT,preexec_fn=no_core)
  text=(work/(name+'.log')).read_text(errors='replace')
  assert r.returncode!=0,name+' unexpectedly passed'
  assert ('AddressSanitizer' in text or 'runtime error:' in text) if name!='header-percent' else r.returncode==23,name
  record['commands'].append(dict(argv=[str(exe)],status=r.returncode,log_sha256=sha((work/(name+'.log')).read_bytes())));save();print(name,r.returncode,flush=True)
 record['status']='passed-original-failures-reproduced'
except BaseException as exc:record.update(status='failed',error=repr(exc));raise
finally:save()
