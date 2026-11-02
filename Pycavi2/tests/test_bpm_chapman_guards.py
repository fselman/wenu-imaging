"""Read-only guard preparation; never claims a Chapman execution."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('qualify_bpm_chapman.py'))
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class Guards(unittest.TestCase):
    def test_wrong_host_before_environment_or_writes(self):
        with patch.object(runner.platform,'node',return_value='some-other-host'):
            with self.assertRaisesRegex(RuntimeError,'Chapman4 only'):
                runner.main()

    def test_exact_inventory(self):
        good={'tests':[{'name':n} for n in runner.TESTS]}
        runner.test_inventory(good)
        for changed in ({'tests':good['tests'][:-1]}, {'tests':good['tests']+[{'name':'shared_qc_asdf'}]},
                        {'tests':good['tests']+[good['tests'][0]]}):
            with self.assertRaises(RuntimeError):
                runner.test_inventory(changed)

    def test_reuse_needs_passed_protected_receipt(self):
        good=dict(status='passed',revision=runner.PREVIOUS,actual_glibc='2.17',
            private_python=str(runner.PRIVATE/'bin/python'),interchange={'status':'passed'},
            shared_qc=dict(successful=True,tests=10,network_attempts=[]),
            preservation={k:True for k in ('checkout','installed_files','production_packages',
                'retained_python_environment','exported_source','external_prefix_after_install')})
        runner.prior_receipt(good)
        for key,value in [('status','failed'),('revision','0'*40),('actual_glibc','2.28')]:
            with self.assertRaises(RuntimeError):
                runner.prior_receipt(dict(good,**{key:value}))
        changed=json.loads(json.dumps(good));changed['preservation']['checkout']=False
        with self.assertRaises(RuntimeError):
            runner.prior_receipt(changed)


if __name__=='__main__':
    unittest.main(verbosity=2)
