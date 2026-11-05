"""Only JSON receipt admission: actual pilot/batch schemas and refusal controls."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_linearity_recipe as recipe


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.directory=self.root/'CCD65';self.directory.mkdir()
        self.handoff=self.directory/'handoff.json';self.handoff.write_text('{}')
        self.master=dict(product=str(self.directory/'master.fits'),qc_product=str(self.directory/'master.asdf'),hdu=1)
        self.detector='ESO_CCD_#65';self.paths={str(self.root/f'bias{i}.fits') for i in range(10)}
        self.inputs={p:dict(sha256='a'*64,stat=[1,2,3,4,5,6]) for p in self.paths}
        self.pilot=dict(status='complete_for_owner_inspection',detector=self.detector,
            product=self.master['product'],qc_product=self.master['qc_product'],inputs=self.inputs,
            preservation={k:True for k in ('checkout','installed_files','exported_source','private_qc_runtime','inputs')})
        self.batch=dict(status='complete_for_owner_inspection',inputs=self.inputs,after_inputs=deepcopy(self.inputs),
            source_preservation=True,results=[dict(detector=self.detector,product=self.master['product'])],
            preservation={k:True for k in ('shared_inputs','products','checkout','installed_files','exported_source',
                                         'private_qc_runtime','reference_pilot','native_adapter')})
    def write(self,kind,value):
        path=self.directory/'outer-execution.json' if kind=='pilot' else self.root/'overall-execution.json'
        path.write_text(json.dumps(value));return path
    def admit(self):return recipe.bias_receipt_fingerprints(self.handoff,self.paths,self.master,self.detector)
    def check_directory_alias(self, path):
        alias=self.root/'directory-alias';alias.symlink_to(self.directory,target_is_directory=True)
        result=recipe.bias_receipt_fingerprints(alias/'handoff.json',self.paths,self.master,self.detector)
        self.assertEqual(result['path'],str(path.resolve(strict=True)))
        self.assertEqual(result['inputs'],{p:'a'*64 for p in self.paths})
    def test_actual_pilot_schema_without_source_preservation(self):
        path=self.write('pilot',self.pilot);before=path.read_bytes();result=self.admit()
        self.assertEqual(result['path'],str(path.resolve(strict=True)));self.assertEqual(result['inputs'],{p:'a'*64 for p in self.paths})
        self.assertEqual(result['sha256'],recipe.hashlib.sha256(before).hexdigest());self.assertEqual(path.read_bytes(),before)
        self.check_directory_alias(path)
    def test_actual_parent_batch_schema(self):
        path=self.write('batch',self.batch);self.assertEqual(self.admit()['path'],str(path.resolve(strict=True)))
        self.check_directory_alias(path)
    def test_failed_pilot_does_not_fall_back_to_good_batch(self):
        self.write('batch',self.batch)
        for key in self.pilot['preservation']:
            value=deepcopy(self.pilot);value['preservation'][key]=False;self.write('pilot',value)
            with self.assertRaises(ValueError):self.admit()
    def test_failed_or_missing_guard_refused(self):
        for kind,original in [('pilot',self.pilot),('batch',self.batch)]:
            for mode in ('status','missing','truthy'):
                value=deepcopy(original)
                if mode=='status':value['status']='failed'
                elif mode=='missing':value['preservation'].pop('checkout')
                else:value['preservation']['checkout']=1
                path=self.write(kind,value)
                with self.assertRaises(ValueError):self.admit()
                path.unlink()
    def test_wrong_master_or_detector_refused(self):
        for kind,original in [('pilot',self.pilot),('batch',self.batch)]:
            for key in ('product','detector'):
                value=deepcopy(original)
                (value if kind=='pilot' else value['results'][0])[key]='wrong'
                path=self.write(kind,value)
                with self.assertRaises(ValueError):self.admit()
                path.unlink()
    def test_changed_batch_inputs_or_false_source_preservation_refused(self):
        for mode in ('changed','false'):
            value=deepcopy(self.batch)
            if mode=='changed':value['after_inputs'][next(iter(self.paths))]['sha256']='b'*64
            else:value['source_preservation']=False
            self.write('batch',value)
            with self.assertRaises(ValueError):self.admit()
    def test_missing_and_invalid_digest_refused(self):
        for mode in ('missing','invalid'):
            value=deepcopy(self.pilot);name=next(iter(self.paths))
            if mode=='missing':del value['inputs'][name]
            else:value['inputs'][name]['sha256']='z'*64
            self.write('pilot',value)
            with self.assertRaises(ValueError):self.admit()
    def test_missing_or_ambiguous_batch_receipt_refused(self):
        with self.assertRaises(ValueError):self.admit()
        self.write('batch',self.batch)
        (self.directory/'overall-execution.json').write_text(json.dumps(self.batch))
        with self.assertRaises(ValueError):self.admit()


if __name__=='__main__':unittest.main()
