"""New native/ASDF integration; synthetic FITS only, separate saved-value reader."""
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from linearity_preparation_fixture import fixture,native_argv,source_archive,recipe
import pycavi_linearity_preparation_qc as storage
WORK=Path(tempfile.gettempdir());COMMAND=None


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='preparation-asdf-',dir=WORK));self.s=fixture(self.work)
        self.native=self.work/'native';self.native.mkdir()
        r=subprocess.run(native_argv(self.s,COMMAND,self.native),capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.source=source_archive(self.s);self.target=self.work/'saved';self.target.mkdir()
    def publish(self,**changes):
        settings=dict(resolved=self.s['resolved'],selection=self.s['selection'],biases=self.s['biases'],
            master_snapshot=self.s['snapshot'],assessment_id='prepared',created_at='2026-11-05T00:00:00Z',source_revision='b'*40)
        settings.update(changes)
        return storage.publish(self.native,self.source,self.target,**settings)
    def test_exact_roundtrip_relocation_and_immutable_sources(self):
        before={str(p):p.read_bytes() for p in self.source.parent.rglob('*.asdf')}
        result=self.publish();self.assertEqual((result['pairs'],result['exposures'],result['sites'],result['trace_frames']),(50,100,100,30))
        value=storage.read_product(result['path'],expected_digest=result['digest'])
        self.assertEqual(len(value['rows']),50);self.assertEqual(value['scan_traces'][0]['correction_adu'],[12,22,32,42])
        self.assertEqual(sum(t['master_accepted'] is False or t['master_accepted']==0 for t in value['scan_traces']),1)
        moved=self.work/'relocated';shutil.move(str(self.target),moved);shutil.rmtree(self.native)
        self.assertEqual(storage.read_product(moved/'linearity-preparation.asdf'),value)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.source.parent.rglob('*.asdf')})
    def test_saved_reader_does_not_execute_native_and_model_noise_is_explicit(self):
        result=self.publish();old=subprocess.run
        try:
            subprocess.run=lambda *a,**k:(_ for _ in ()).throw(RuntimeError('Native execution forbidden'))
            self.assertEqual(len(storage.modelling_inputs(result['path'],require_noise=False)['pixel_observations']),100)
            with self.assertRaisesRegex(ValueError,'noise/covariance'):storage.modelling_inputs(result['path'])
        finally:subprocess.run=old
    def test_direct_replay_master_membership_and_config_conflicts_refused(self):
        for kind in ('membership','configuration','native-replay'):
            if kind=='membership':
                biases=deepcopy(self.s['biases']);biases[3]['accepted']=1
                with self.assertRaises(ValueError):self.publish(biases=biases)
            elif kind=='configuration':
                snapshot=deepcopy(self.s['snapshot']);snapshot['MEF.SCANREJ.MIN']['value']=1
                with self.assertRaises(ValueError):self.publish(master_snapshot=snapshot)
            else:
                p=self.native/'pair-0000/samples.tsv';old=p.read_bytes();p.write_bytes(old.replace(b'\t200\t',b'\t201\t',1))
                with self.assertRaises(ValueError):self.publish()
                p.write_bytes(old)
            self.assertFalse(list(self.target.iterdir()))
    def test_missing_trace_marker_and_overwrite_refused(self):
        p=self.native/'bias-traces.tsv';old=p.read_bytes();p.write_bytes(b'broken\n')
        with self.assertRaises(ValueError):self.publish()
        p.write_bytes(old);result=self.publish()
        with self.assertRaises(ValueError):self.publish()
        (self.target/'inputs/master/master.asdf').unlink()
        with self.assertRaises((ValueError,OSError)):storage.read_product(result['path'])
    def test_native_configuration_and_frozen_data_tamper_refused(self):
        resolved=deepcopy(self.s['resolved']);resolved['detectors'][0]['native_settings']['trim'][0]=3
        with self.assertRaises(ValueError):recipe.native_configuration(resolved,self.s['snapshot'])
        result=self.publish();tree=storage.qc.read_record(result['path']).as_dict()
        # Changing a saved native value without its immutable transport digest
        # cannot be legitimized by changing the surrounding common ASDF record.
        tree['extensions']['linearity_preparation']['native_transports']['pair-0000/corrected.tsv']['text']+='changed\n'
        bad=self.work/'bad';bad.mkdir();shutil.copytree(self.target/'inputs',bad/'inputs')
        path=storage.qc.write_record(storage.qc.QcRecord(storage.qc.encoded(tree)),bad,qc_root=bad)
        with self.assertRaises(ValueError):storage.read_product(path)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--native-command',required=True,type=Path);p.add_argument('--work',required=True,type=Path)
    a=p.parse_args();COMMAND=a.native_command.resolve(strict=True);WORK=a.work.resolve(strict=True)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PreparationTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite);raise SystemExit(not result.wasSuccessful())
