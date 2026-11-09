"""Synthetic FITS -> native preparation -> immutable shared ASDF.

Explicit binaries via environment; no observational paths or installed products.
"""
from copy import deepcopy
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'Pycavi2/pycavi/pycavi'),str(ROOT/'mefpp2/tests'),str(ROOT/'Pycavi2/tests')]
import pycavi_linearity_recipe as recipe
import pycavi_linearity_preparation_qc as archive
from linearity_files_contract import plane
import test_sample_qc as saved_fixture
qc=archive.qc


class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from linearity_preparation_fixture import fixture, native_argv, source_archive
        cls.work=Path(tempfile.mkdtemp(prefix='linearity-recipe-'))
        cls.state=fixture(cls.work)
        cls.resolved=cls.state['resolved'];cls.snapshot=cls.state['snapshot']
        cls.selection=cls.state['selection'];cls.biases=cls.state['biases'];cls.points=cls.state['sites']
        cls.native=cls.work/'native';cls.native.mkdir()
        cls.argv=native_argv(cls.state,os.environ['LINEARITY_PREPARE_BINARY'],cls.native)
        run=subprocess.run(cls.argv,capture_output=True,text=True)
        if run.returncode:raise RuntimeError(run.stdout+run.stderr)
        cls.source=source_archive(cls.state);cls.expected=archive.sample.read_product(cls.source)
        cls.master_reference=dict(product=cls.state['master'],hdu=1)

    def test_analytical_native_roi_and_ordered_traces(self):
        value=archive.collect(self.native,self.resolved,self.selection,self.biases,self.expected,self.snapshot,master_reference=self.master_reference)
        self.assertEqual(len(value['exposure_rows']),100)
        self.assertEqual(len(value['scan_traces']),30)
        self.assertEqual(value['scan_traces'][0]['correction_adu'],[12.,22.,32.,42.])
        self.assertEqual(value['scan_traces'][10]['correction_adu'],[12.,22.,32.,42.])
        self.assertFalse(value['scan_traces'][3]['master_accepted'])
        self.assertEqual(value['exposure_rows'][0]['signal_adu'],205.5)
        self.assertAlmostEqual(value['exposure_rows'][0]['spatial_variance_adu2'],13.)

    def test_asdf_roundtrip_and_relocation_without_native_files(self):
        target=self.work/'saved';target.mkdir()
        result=archive.publish(self.native,self.source,target,resolved=self.resolved,selection=self.selection,biases=self.biases,
            master_snapshot=self.snapshot,assessment_id='prepare',created_at='2026-11-05T00:00:00Z',source_revision='b'*40)
        self.assertEqual(result['exposures'],100)
        moved=self.work/'relocated';shutil.copytree(target,moved)
        hidden=self.work/'hidden-native';self.native.rename(hidden)
        try:
            value=archive.read_product(moved/'linearity-preparation.asdf',expected_digest=result['digest'])
            self.assertEqual(value['direct_site_replay'],self.expected['rows'])
            with self.assertRaises(ValueError):archive.modelling_inputs(moved/'linearity-preparation.asdf')
        finally:hidden.rename(self.native)
        with self.assertRaises(ValueError):archive.publish(self.native,self.source,target,resolved=self.resolved,selection=self.selection,biases=self.biases,
            master_snapshot=self.snapshot,assessment_id='again',created_at='2026-11-05T00:00:00Z',source_revision='b'*40)

    def test_conflicting_master_settings_and_sites_refused(self):
        changed=deepcopy(self.snapshot);changed['MEF.CROP.Y.MIN.CHIP1']['value']=1
        with self.assertRaises(ValueError):recipe.native_configuration(self.resolved,changed)
        points=deepcopy(self.points);points[0]['raw_pixel'][1]+=1
        with self.assertRaises(ValueError):recipe.native_plan(self.resolved,self.selection,points)

    def test_changed_replay_and_trace_coverage_refused(self):
        expected=deepcopy(self.expected);expected['rows'][0]['signal_adu']+=1
        with self.assertRaises(ValueError):archive.collect(self.native,self.resolved,self.selection,self.biases,expected,self.snapshot,master_reference=self.master_reference)
        path=self.native/'bias-traces.tsv';data=path.read_bytes()
        try:
            path.write_bytes(data.rsplit(b'\n',2)[0]+b'\n')
            with self.assertRaises(ValueError):archive.collect(self.native,self.resolved,self.selection,self.biases,self.expected,self.snapshot,master_reference=self.master_reference)
        finally:path.write_bytes(data)

    def test_native_rejects_alias_and_preserves_partial_evidence(self):
        target=self.work/'alias';target.mkdir();argv=list(self.argv);argv[-1]=str(target);argv[7]='flat0.fits'
        run=subprocess.run(argv,capture_output=True)
        self.assertNotEqual(run.returncode,0);self.assertFalse((target/'command.complete').exists())

    def test_recipe_file_directory_contract(self):
        from linearity_preparation_fixture import fixture, source_archive
        state = fixture(self.work/'separated', separated=True)
        controls, reduced, raw = state['work'], state['reduced'], state['raw']
        source = source_archive(state)
        for name, item in state['resolved']['sources'].items():
            (controls/(name+'.toml')).write_text(item['text'])
        inputs = [*raw.glob('*.fits'), Path(state['master']), Path(state['selection']['bpm']['path'])]
        before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
        for path in inputs:
            path.chmod(0o444)
        raw.chmod(0o555)
        run = reduced/'cal/bpm-linearity/run-001'
        run.mkdir(parents=True)
        envelope = dict(linearity_recipe_schema_version=1,
            paths=dict(raw=str(raw), orchestration='.', reduced=str(reduced)),
            preparation=dict(detector_toml='detector_toml.toml', processing_toml='processing_toml.toml',
                source_samples=str(source), handoff=str(state['handoff_path']),
                native=str(Path(os.environ['LINEARITY_PREPARE_BINARY']).resolve()),
                run=str(run), source_revision='b'*40))
        text = 'linearity_recipe_schema_version = 1\n'
        for table in ('paths', 'preparation'):
            text += '\n['+table+']\n'
            text += ''.join(key+' = '+json.dumps(value)+'\n' for key, value in envelope[table].items())
        path = controls/'bpm-linearity.toml'
        path.write_text(text)
        command = [sys.executable, str(ROOT/'tools/prepare-linearity.py'), '--config', str(path), '--execute']
        result = subprocess.run(command, cwd=controls, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        receipt = json.loads((run/'execution.json').read_text())
        self.assertEqual(receipt['status'], 'complete_for_owner_inspection')
        self.assertEqual(receipt['directories']['orchestration'], str(controls))
        self.assertTrue((controls/'run-001/native.toml').is_file())
        self.assertFalse((run/'native.toml').exists())
        self.assertTrue((run/'native.log').is_file())
        product = archive.read_product(receipt['product']['path'])
        self.assertEqual(len(product['exposure_rows']), 100)
        self.assertEqual(product['exposure_rows'][0]['signal_adu'], 205.5)
        repeated = subprocess.run(command, cwd=controls, capture_output=True, text=True)
        self.assertNotEqual(repeated.returncode, 0)
        self.assertEqual(before, {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
        dependencies = recipe.preparation_dependencies(source, state['handoff_path'], state['resolved'])
        with self.assertRaises(ValueError):
            recipe.preparation_layout(dependencies, run, raw=raw, orchestration=controls, reduced=raw)
        self.assertEqual(len(list(raw.iterdir())), 30)
        self.assertFalse(list(controls.glob('*.fits')))

    def test_dependency_admission_and_complete_recipe(self):
        dependencies=recipe.preparation_dependencies(self.source,self.work/'handoff.json',self.resolved)
        self.assertEqual(len(dependencies['biases']),10)
        target=self.work/'recipe-execution';target.mkdir()
        result=recipe.prepare_detector(dependencies,os.environ['LINEARITY_PREPARE_BINARY'],target,
            resolved=self.resolved,source_revision='b'*40,assessment_id='recipe',created_at='2026-11-05T00:00:00Z')
        self.assertEqual(result['status'],'complete_for_owner_inspection')
        self.assertTrue(result['source_preservation'])
        self.assertEqual(result['product']['exposures'],100)
        changed=deepcopy(dependencies);changed['biases'][0]['accepted']=0
        fresh=self.work/'bad-dependencies';fresh.mkdir()
        with self.assertRaises(ValueError):recipe.prepare_detector(changed,os.environ['LINEARITY_PREPARE_BINARY'],fresh,
            resolved=self.resolved,source_revision='b'*40,assessment_id='bad',created_at='2026-11-05T00:00:00Z')
        self.assertFalse(list(fresh.iterdir()))

if __name__=='__main__':unittest.main()
