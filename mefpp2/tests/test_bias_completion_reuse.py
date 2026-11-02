"""Synthetic reuse guards: reject changed code, binary, tools or failed evidence.

No native execution, observations, installation or network. The fixture archive
and reports are independent small stand-ins for the accepted target evidence.
"""
import hashlib
import io
import json
from pathlib import Path
import runpy
import tarfile
import tempfile
import unittest

api=runpy.run_path(str(Path(__file__).with_name('qualify_bias_files_mac.py')))


class ReuseTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='bias-completion-reuse-'))
        self.old=self.root/'old';self.source=self.root/'candidate'
        self.old.mkdir();self.source.mkdir()
        self.files={'CMakeLists.txt':b'project(test LANGUAGES C)\n','mefpp2/test.c':b'int main(void) { return 0; }\n'}
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w') as bundle:
            for name,data in self.files.items():
                item=tarfile.TarInfo(name);item.size=len(data);bundle.addfile(item,io.BytesIO(data))
                for base in (self.source,self.old/'source'):
                    path=base/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        self.archive=buffer.getvalue()
        self.adapter=self.old/'build-c17/mefpp2/mefpp_m5'
        self.adapter.parent.mkdir(parents=True);self.adapter.write_bytes(b'fixture executable bytes\n');self.adapter.chmod(0o700)
        log=self.old/'tests-c17.log';log.write_text('six contracts passed\n')
        self.tools={'compiler':{'path':'/explicit/compiler','sha256':'a'*64}}
        self.report=dict(revision=api['QUALIFIED_BIAS'],status='passed',
            preservation=dict(installed_files=True,checkout=True,exported_source=True,retained_qc_controls=True),
            tool_sha256=self.tools,commands=[dict(label='configure-c17',exit=0,argv=['-DMEFPP_C_STANDARD=17']),
                dict(label='tests-c17',exit=0,log=str(log),sha256=api['sha'](log))],
            archive_sha256=hashlib.sha256(self.archive).hexdigest(),
            source_sha256={n:hashlib.sha256(b).hexdigest() for n,b in self.files.items()})
        self.save()
        proof=self.old/'build-c17/mefpp2/test-work/m5-bias-proof/qualification.json';proof.parent.mkdir(parents=True)
        proof.write_text(json.dumps(dict(status='passed',source_revision=api['QUALIFIED_BIAS'],
            adapter_sha256=api['sha'](self.adapter),commands=[dict(argv=[str(self.adapter)],exit_status=0)])))
    def save(self):
        (self.old/'qualification.json').write_text(json.dumps(self.report))
    def call(self):
        def git(*argv):
            self.assertEqual(argv,('archive','--format=tar',api['QUALIFIED_BIAS']))
            return self.archive
        return api['reuse_bias_adapter'](self.old,self.source,git,self.tools)
    def test_passed_identical_lane(self):
        adapter,proof=self.call();self.assertEqual(adapter,self.adapter)
        self.assertEqual(proof['native_source_files'],2)
    def test_changed_native_source(self):
        (self.source/'mefpp2/test.c').write_text('changed\n')
        with self.assertRaises(RuntimeError):self.call()
    def test_added_native_source(self):
        (self.source/'mefpp2/new.c').write_text('new\n')
        with self.assertRaises(RuntimeError):self.call()
    def test_changed_binary(self):
        self.adapter.write_bytes(b'changed binary\n')
        with self.assertRaises(RuntimeError):self.call()
    def test_failed_prior_gate(self):
        self.report['status']='failed';self.save()
        with self.assertRaises(RuntimeError):self.call()
    def test_changed_tools(self):
        self.report['tool_sha256']={};self.save()
        with self.assertRaises(RuntimeError):self.call()
    def test_changed_test_log(self):
        (self.old/'tests-c17.log').write_text('changed\n')
        with self.assertRaises(RuntimeError):self.call()


if __name__=='__main__':unittest.main(verbosity=2)
