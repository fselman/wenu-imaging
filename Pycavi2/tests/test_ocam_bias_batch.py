"""Metadata/serial batch controls only; no native or ASDF numerical qualification."""
import argparse
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--module',type=Path,required=True)
args=parser.parse_args()
spec=importlib.util.spec_from_file_location('bias_batch_controls',args.module)
batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)


class BiasBatchControls(unittest.TestCase):
    def fixture(self):
        template=['cal','bias','--detector-id','ESO_CCD_#65','--expected-extname','ESO_CCD_#65',
            '--hdu','1','--config-detector','0','--bpm-hdu','1','--bpm-expected-extname','ESO_CCD_#65',
            '--output','/reference/master.fits','--work-dir','/reference','--log-path','/reference/native.log',
            '--config-record','/reference/configuration.json','--qc-record','/reference/handoff.json',
            '--pafname','/reference/omegacam.paf','--bias','/reference/bias.list',
            '--readout-id','OMEGACAM:normal:ordered:1x1','--bpm-good-value','1',
            '--ron-first','0','--ron-second','1','--high-sigma','5','--mad','yes']
        geometry={'id':'ESO_CCD_#69','native_paf_chip':17}
        review={'headers':{'raw_bindings':{str(i):{'ESO_CCD_#69':23} for i in range(10)},
                           'bpm_bindings':{'ESO_CCD_#69':9}}}
        return template,geometry,review,[Path('/synthetic')/str(i) for i in range(10)]
    def test_independent_hdu_maps_preserve_recipe_choices(self):
        template,geometry,review,members=self.fixture();saved=copy.deepcopy(template)
        entry=batch.detector_plan(template,geometry,review,members,Path('/new/CCD69'))
        self.assertEqual((entry['hdu'],entry['bpm_hdu'],entry['configuration_detector']),(23,9,16))
        self.assertEqual(template,saved)
        new=batch.options(entry['native']);old=batch.options(template)
        for key in ('--pafname','--bias','--readout-id','--bpm-good-value','--ron-first','--ron-second','--high-sigma','--mad'):
            self.assertEqual(new[key],old[key])
        self.assertEqual(new['--expected-extname'],'ESO_CCD_#69')
    def test_mixed_hdu_binding_and_duplicate_options_refused(self):
        template,geometry,review,members=self.fixture()
        review['headers']['raw_bindings']['5']['ESO_CCD_#69']=24
        with self.assertRaises(RuntimeError):batch.detector_plan(template,geometry,review,members,Path('/new/CCD69'))
        with self.assertRaises(RuntimeError):batch.options(template+['--hdu','2'])
    def test_serial_completion_before_next_detector(self):
        entries=[dict(detector='CCD'+str(i)) for i in (66,67,68)]
        completed=[];saved=[]
        def command(entry):
            self.assertEqual(len(completed),len(saved));completed.append(entry['detector'])
            return dict(status='complete',native_exit_status=0,detector=entry['detector'])
        result=batch.serial(entries,command,lambda values:saved.append(len(values)))
        self.assertEqual(completed,['CCD66','CCD67','CCD68']);self.assertEqual(saved,[1,2,3]);self.assertEqual(len(result),3)
    def test_stop_on_first_failure_or_wrong_identity(self):
        entries=[dict(detector='CCD66'),dict(detector='CCD67')]
        for result in (dict(status='failed',native_exit_status=1,detector='CCD66'),
                       dict(status='complete',native_exit_status=0,detector='CCD77')):
            launched=[];saved=[]
            def command(entry):launched.append(entry['detector']);return result
            with self.assertRaises(RuntimeError):batch.serial(entries,command,lambda values:saved.append(values))
            self.assertEqual(launched,['CCD66']);self.assertFalse(saved)
    def test_two_shared_hash_passes_and_source_change(self):
        paths=[Path('/synthetic')/str(i) for i in range(3)]
        expected={str(p):dict(sha256=str(i),stat=[1,i,4,5,6,7]) for i,p in enumerate(paths)}
        counts={str(p):0 for p in paths}
        def fingerprint(path):counts[str(path)]+=1;return copy.deepcopy(expected[str(path)])
        first=batch.image_pass(paths,expected,fingerprint,'Before')
        last=batch.image_pass(paths,expected,fingerprint,'After')
        self.assertEqual(first,last);self.assertEqual(set(counts.values()),{2})
        def changed(path):return dict(sha256='changed',stat=[])
        with self.assertRaises(RuntimeError):batch.image_pass(paths,expected,changed,'Changed')


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BiasBatchControls))
    sys.exit(0 if result.wasSuccessful() else 1)
