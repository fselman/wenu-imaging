"""Execute the actual qualifier dispatch block with controlled command results.

No Mac admission, ASDF runtime, observations, networking or installed files used.
"""
import ast
import json
from pathlib import Path
import tempfile
import sys
import unittest

SOURCE=Path(__file__).with_name('qualify_residual_viewer_mac.py')

class DispatchTests(unittest.TestCase):
    def dispatch(self,result):
        tree=ast.parse(SOURCE.read_text())
        loops=[node for node in ast.walk(tree) if isinstance(node,ast.For)
               and isinstance(node.target,ast.Tuple)
               and [getattr(v,'id',None) for v in node.target.elts]==['name','script','filename','count']]
        self.assertEqual(len(loops),1)
        expected=ast.literal_eval(loops[0].iter)
        self.assertTrue(all(isinstance(row,tuple) and len(row)==4 for row in expected))
        code=compile(ast.fix_missing_locations(ast.Module(body=loops,type_ignores=[])),str(SOURCE),'exec')
        with tempfile.TemporaryDirectory(prefix='qualifier-dispatch-') as directory:
            work=Path(directory);source=work/'source';calls=[]
            def command(name,argv):
                calls.append((name,argv))
                filename=next(spec[2] for spec in expected if spec[0]==name)
                value=dict(result)
                if value['tests'] is None:value['tests']=next(spec[3] for spec in expected if spec[0]==name)
                (work/name/filename).write_text(json.dumps(value))
                log=work/'test.log';log.write_text('controlled test result')
                return log
            def require(ok,message):
                if not ok:raise RuntimeError(message)
            namespace=dict(work=work,source=source,PRIVATE=work/'runtime',
                           command=command,require=require,json=json)
            exec(code,namespace)
            self.assertEqual(len(calls),len(expected))
            for call,spec in zip(calls,expected):
                self.assertEqual(call[0],spec[0])
                self.assertEqual(call[1][2],source/'Pycavi2/tests'/spec[1])
                self.assertEqual(call[1][3:],['--work',work/spec[0]])
    def test_exact_single_dispatch(self):
        self.dispatch(dict(tests=None,successful=True,network_attempts=[]))
    def test_dispatch_counts_match_declared_test_methods(self):
        tree=ast.parse(SOURCE.read_text())
        loop=next(node for node in ast.walk(tree) if isinstance(node,ast.For)
            and isinstance(node.target,ast.Tuple)
            and [getattr(v,'id',None) for v in node.target.elts]==['name','script','filename','count'])
        for _,script,_,count in ast.literal_eval(loop.iter):
            tests=ast.parse(SOURCE.with_name(script).read_text())
            actual=sum(isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_')
                for cls in tests.body if isinstance(cls,ast.ClassDef) for node in cls.body)
            self.assertEqual(count,actual,script)
    def test_incomplete_failed_and_network_results_refused(self):
        for result in (dict(tests=7,successful=True,network_attempts=[]),
                       dict(tests=8,successful=False,network_attempts=[]),
                       dict(tests=8,successful=True,network_attempts=['blocked'])):
            with self.subTest(result=result),self.assertRaises(RuntimeError):self.dispatch(result)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--qualifier',type=Path,default=SOURCE)
    args,remaining=parser.parse_known_args();SOURCE=args.qualifier
    unittest.main(argv=[sys.argv[0],*remaining],verbosity=2)
