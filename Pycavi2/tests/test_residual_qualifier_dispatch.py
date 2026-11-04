"""Execute the actual qualifier dispatch block with controlled command results.

No Mac admission, ASDF runtime, observations, networking or installed files used.
"""
import ast
import json
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).with_name('qualify_residual_viewer_mac.py')

class DispatchTests(unittest.TestCase):
    def dispatch(self,result):
        tree=ast.parse(SOURCE.read_text())
        loops=[node for node in ast.walk(tree) if isinstance(node,ast.For)
               and isinstance(node.target,ast.Tuple)
               and [getattr(v,'id',None) for v in node.target.elts]==['name','script','filename','count']]
        self.assertEqual(len(loops),1)
        code=compile(ast.fix_missing_locations(ast.Module(body=loops,type_ignores=[])),str(SOURCE),'exec')
        with tempfile.TemporaryDirectory(prefix='qualifier-dispatch-') as directory:
            work=Path(directory);source=work/'source';calls=[]
            def command(name,argv):
                calls.append((name,argv))
                (work/name/'pair-viewer-results.json').write_text(json.dumps(result))
                log=work/'test.log';log.write_text('controlled test result')
                return log
            def require(ok,message):
                if not ok:raise RuntimeError(message)
            namespace=dict(work=work,source=source,PRIVATE=work/'runtime',
                           command=command,require=require,json=json)
            exec(code,namespace)
            self.assertEqual(len(calls),1)
            self.assertEqual(calls[0][0],'signal-time-viewer')
            self.assertEqual(calls[0][1][2],source/'Pycavi2/tests/test_pair_qc_viewer.py')
            self.assertEqual(calls[0][1][3:],[ '--work',work/'signal-time-viewer'])
    def test_exact_single_dispatch(self):
        self.dispatch(dict(tests=8,successful=True,network_attempts=[]))
    def test_incomplete_failed_and_network_results_refused(self):
        for result in (dict(tests=7,successful=True,network_attempts=[]),
                       dict(tests=8,successful=False,network_attempts=[]),
                       dict(tests=8,successful=True,network_attempts=['blocked'])):
            with self.subTest(result=result),self.assertRaises(RuntimeError):self.dispatch(result)

if __name__=='__main__':unittest.main(verbosity=2)
