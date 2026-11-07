"""Batch orchestration controls; supplied transports, no native numerical claim (#234)."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import test_pair_qc as fixture
batch=fixture.bridge  # Load actual orchestration using its supported module entry points.
import importlib.util
spec=importlib.util.spec_from_file_location('ocam_batch',ROOT/'tools/run-ocam-pair-batch.py')
batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)
WORK=Path(tempfile.gettempdir())


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='ocam-batch-',dir=WORK))
        self.revision='2'*40
        reference=self.work/'reference';reference.mkdir()
        self.reference,self.pairs,self.bias=fixture.fixture(reference)
        selection=json.loads(json.dumps(batch.tomllib.loads((self.reference/'selection.toml').read_text())))
        self.images={}
        for ref in selection['flat']+selection['bias']+[selection['bpm']]:
            Path(ref['path']).write_bytes(b'tiny transport source, not FITS pixels')
            self.images[ref['path']]=batch.runner.fingerprint(ref['path'])
        self.work_batch=self.work/'batch';self.work_batch.mkdir()
        self.entries=[];self.transports={}
        for number in (66,67,68):
            parent=self.work_batch/'detectors'/f'CCD{number}';parent.mkdir(parents=True)
            run,_,_=fixture.fixture(parent)
            for name in ('pairs.tsv','bias-ron.tsv'):
                path=run/'native'/name
                path.write_text(path.read_text().replace('ESO_CCD_#65',f'ESO_CCD_#{number}').replace('CCD65.',f'CCD{number}.'))
            text=(run/'selection.toml').read_text().replace('ESO_CCD_#65',f'ESO_CCD_#{number}')
            # All children share the same raw file paths, but retain their own HDU bindings.
            text=text.replace(str(parent),str(reference))
            (run/'selection.toml').write_text(text)
            path=run/'selected-rois.toml';path.write_text(path.read_text().replace('ESO_CCD_#65',f'ESO_CCD_#{number}').replace('CCD65.',f'CCD{number}.'))
            (run/'execution.json').unlink()
            self.transports[number]={p.name:p.read_bytes() for p in (run/'native').iterdir()}
            shutil.rmtree(run/'native')
            self.entries.append(dict(detector=f'ESO_CCD_#{number}',amplifier='L',roi_count=2,pair_count=2,measurement=str(run)))
        self.manifest=dict(source_revision=self.revision,native_revision='1'*40,command='qualified-native',native_paf='qualified-paf',
            entries=self.entries,images=self.images,frozen=batch.freeze([Path(e['measurement'])/name for e in self.entries
                for name in ('selection.toml','selected-rois.toml','plan.tsv')]),created_at='2026-11-04T00:00:00Z')
        batch.write(self.work_batch/'batch.json',self.manifest)
        batch.write(self.work_batch/'execution.json',dict(status='prepared_not_executed',manifest_sha256=batch.digest(self.work_batch/'batch.json')))
        self.launched=[];self.published=[]
    def launch(self,argv,log):
        number=int(Path(argv[-1]).parent.parent.name[3:]);self.launched.append(number)
        self.assertFalse(self.published)
        for name,data in self.transports[number].items():(Path(argv[-1])/name).write_bytes(data)
        log.write_text('supplied transport; no native numerical qualification\n')
        return 0
    def publish(self,entry,revision,created):
        self.assertEqual(self.launched,[66,67,68])
        self.assertTrue((self.work_batch/'shared-verification.json').is_file())
        self.assertTrue(all(json.loads((Path(e['measurement'])/'execution.json').read_text())['source_preservation'] for e in self.entries))
        self.published.append(entry['detector'])
        records=Path(entry['measurement']).parent/'asdf';records.mkdir()
        return batch.bridge.publish(Path(entry['measurement']),records,assessment_id=entry['detector'],
            created_at=created,serializer_revision=revision)
    def execute(self,launcher=None,publisher=None):
        with patch.object(batch,'launch',launcher or self.launch),patch.object(batch,'publish',publisher or self.publish):
            return batch.execute(self.work_batch,self.revision)
    def test_serial_shared_hashes_and_real_asdf(self):
        counts={p:0 for p in self.images};original=batch.runner.fingerprint
        def fingerprint(path):
            if str(path) in counts:counts[str(path)]+=1
            return original(path)
        with patch.object(batch.runner,'fingerprint',fingerprint):report=self.execute()
        self.assertEqual(set(counts.values()),{2});self.assertEqual(report['detectors_processed'],3)
        self.assertEqual(len(self.published),3)
        with self.assertRaisesRegex(ValueError,'one-use'):self.execute()
    def test_first_native_failure_stops_and_no_asdf(self):
        def fail(argv,log):self.launched.append(66);return 1
        with self.assertRaisesRegex(ValueError,'Native command failed'):self.execute(fail)
        self.assertEqual(self.launched,[66]);self.assertFalse(self.published)
        report=json.loads((self.work_batch/'execution.json').read_text())
        self.assertEqual(report['status'],'failed');self.assertTrue(report['source_preservation'])
    def test_missing_marker_stops(self):
        def missing(argv,log):
            self.launch(argv,log);(Path(argv[-1])/'command.complete').unlink();return 0
        with self.assertRaises(FileNotFoundError):self.execute(missing)
        self.assertEqual(self.launched,[66]);self.assertFalse(self.published)
    def test_changed_source_after_native_blocks_publication(self):
        def changed(argv,log):
            code=self.launch(argv,log)
            if len(self.launched)==3:Path(next(iter(self.images))).write_bytes(b'changed')
            return code
        with self.assertRaisesRegex(ValueError,'Shared image differs'):self.execute(changed)
        self.assertFalse(self.published)
        self.assertFalse(json.loads((self.work_batch/'execution.json').read_text())['source_preservation'])
    def test_changed_initial_source_prevents_children(self):
        Path(next(iter(self.images))).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Shared image differs'):self.execute()
        self.assertFalse(self.launched);self.assertFalse(self.published)
    def test_metadata_tamper_and_wrong_revision_prevent_children(self):
        with self.assertRaisesRegex(ValueError,'revision differs'):batch.execute(self.work_batch,'3'*40)
        (Path(self.entries[0]['measurement'])/'plan.tsv').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Frozen metadata changed'):self.execute()
        self.assertFalse(self.launched)
    def test_bad_table_stops(self):
        def bad(argv,log):
            self.launch(argv,log);(Path(argv[-1])/'pairs.tsv').write_text('bad\n');return 0
        with self.assertRaises(Exception):self.execute(bad)
        self.assertEqual(self.launched,[66]);self.assertFalse(self.published)
    def test_asdf_failure_keeps_native_proof_and_parent_failed(self):
        def fail(entry,revision,created):raise RuntimeError('publication failed')
        with self.assertRaisesRegex(RuntimeError,'publication failed'):self.execute(publisher=fail)
        report=json.loads((self.work_batch/'execution.json').read_text())
        self.assertEqual(report['status'],'failed');self.assertTrue(report['source_preservation'])
        for entry in self.entries:
            self.assertEqual(json.loads((Path(entry['measurement'])/'execution.json').read_text())['status'],'complete_for_owner_inspection')
    def test_independent_mapping_and_selection_preservation(self):
        selection=batch.tomllib.loads((self.reference/'selection.toml').read_text())
        paths=['unused'+str(i) for i in range(30)]
        paths[:2]=[r['path'] for r in selection['bias']]
        for r in selection['flat']:paths[r['index']]=r['path']
        review=dict(current_source_stats=[dict(path=p) for p in paths],headers=dict(
            raw_bindings={str(i):{'ESO_CCD_#66':32-i} for i in range(30)},bpm_bindings={'ESO_CCD_#66':17}))
        original=copy.deepcopy(selection);mapped=batch.remap(selection,review,'ESO_CCD_#66')
        self.assertEqual(selection,original)
        self.assertEqual([r['hdu'] for r in mapped['flat']],[22,21,20,19])
        self.assertEqual([r['hdu'] for r in mapped['bias']],[32,31]);self.assertEqual(mapped['bpm']['hdu'],17)
        self.assertEqual(batch.tomllib.loads(batch.selection_text(mapped)),mapped)
        for key in original:
            if key not in ('detector','flat','bias','bpm'):self.assertEqual(mapped[key],original[key])
        self.assertEqual([r['index'] for r in mapped['flat']],[10,11,12,13])

    def test_stat_change_with_identical_bytes_blocks_publication(self):
        import os
        def touched(argv,log):
            code=self.launch(argv,log)
            if len(self.launched)==3:
                path=Path(next(iter(self.images)));stat=path.stat()
                os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns+1000000000))
            return code
        with self.assertRaisesRegex(ValueError,'stat/hash changed'):self.execute(touched)
        self.assertFalse(self.published)
    def test_missing_independent_mapping_refused(self):
        selection=batch.tomllib.loads((self.reference/'selection.toml').read_text())
        review=dict(current_source_stats=[dict(path=str(i)) for i in range(30)],headers=dict(raw_bindings={},bpm_bindings={}))
        with self.assertRaises(ValueError):batch.remap(selection,review,'ESO_CCD_#66')
    def test_prepare_all31_without_image_hash_or_pixels(self):
        state=batch.bridge.admit(self.reference)
        records=self.work/'reference-asdf';records.mkdir()
        batch.bridge.publish(self.reference,records,assessment_id='reference',created_at='2026-11-04T00:00:00Z',serializer_revision=self.revision)
        selection=state['selection']
        selection.update(max_loaded_pixels=206467604,max_rows=50)
        selection['flat']=[]
        for i in range(20):
            path=self.work/f'flat{i}.fits';path.write_bytes(b'not a pixel array')
            selection['flat'].append(dict(path=str(path),asset=path.name,index=10+i,pair='P'+str(i%10),hdu=1))
        state['refs']=selection['flat']+selection['bias']+[selection['bpm']]
        for ref in state['refs']:state['fingerprints'][ref['path']]=batch.runner.fingerprint(ref['path'])
        paths=[r['path'] for r in selection['bias']]+['unused'+str(i) for i in range(8)]+[r['path'] for r in selection['flat']]
        ids=[f'ESO_CCD_#{n}' for n in range(65,97)]
        bindings={str(i):{d:(n%32)+1 for n,d in enumerate(ids)} for i in range(30)}
        # Match the original tiny reference's independently selected bias HDUs.
        for i,ref in enumerate(selection['bias']):bindings[str(i)]['ESO_CCD_#65']=ref['hdu']
        masks={d:i+1 for i,d in enumerate(ids)};masks['ESO_CCD_#65']=selection['bpm']['hdu']
        review=self.work/'review.json';batch.write(review,dict(current_source_stats=[dict(path=p) for p in paths],headers=dict(raw_bindings=bindings,bpm_bindings=masks)))
        binary=self.work/'native-command';binary.write_bytes(b'qualified native identity fixture')
        state['receipt'].update(source_revision=batch.NATIVE_REVISION,argv=[str(binary)])
        state['fingerprints'][str(binary)]=batch.runner.fingerprint(binary)
        lineage=dict(native_revision=batch.NATIVE_REVISION,owner_approval=dict(review_sha256=batch.digest(review)),
            derived_bpm_sha256=state['fingerprints'][selection['bpm']['path']]['sha256'],original_bpm_sha256='a'*64)
        batch.write(self.reference.parent/'lineage.json',lineage)
        preparation=self.work/'preparation.json';batch.write(preparation,dict(status='prepared_verified_copy',
            source_preservation=True,payload_preservation=True,existing_cards_preservation=True,detector_count=32,
            copy=selection['bpm']['path'],copy_sha256=lineage['derived_bpm_sha256'],original_sha256='a'*64))
        png=self.work/'gain.png';png.write_bytes(b'plot transport fixture')
        plots=self.work/'plots.json';batch.write(plots,dict(status='complete',source_sha256=batch.digest(records/'pairs.asdf'),
            qc_record_digest=batch.bridge.qc.read_record(records/'pairs.asdf').digest,
            outputs=[dict(path=str(png),sha256=batch.digest(png))]))
        fresh=self.work/'prepared';fresh.mkdir()
        original=batch.runner.fingerprint
        def fingerprint(path):
            self.assertNotIn(str(path),{r['path'] for r in state['refs']},'Preparation hashed an observation')
            return original(path)
        with patch.object(batch.bridge,'admit',return_value=state),patch.object(batch.runner,'fingerprint',fingerprint):
            manifest=batch.prepare(fresh,self.reference,records/'pairs.asdf',records/'bias-ron.asdf',plots,review,preparation,binary,self.revision)
        self.assertEqual(len(manifest['entries']),31);self.assertEqual(len(manifest['images']),23)
        self.assertNotIn('ESO_CCD_#65',[e['detector'] for e in manifest['entries']])
        self.assertFalse(list(fresh.rglob('native')))
        for entry in manifest['entries']:
            selected=batch.tomllib.loads((Path(entry['measurement'])/'selection.toml').read_text())
            self.assertEqual([r['index'] for r in selected['flat']],list(range(10,30)))
            self.assertEqual(selected['max_loaded_pixels'],206467604)
            self.assertEqual(entry['roi_count'],5)


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();WORK=args.work.resolve(strict=True)
    attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline batch controls')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BatchTests))
    batch.write(WORK/'ocam-batch-results.json',dict(tests=result.testsRun,successful=result.wasSuccessful(),network_attempts=attempts))
    raise SystemExit(0 if result.wasSuccessful() and not attempts else 1)
