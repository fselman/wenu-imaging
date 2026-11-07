"""New controller admission controls only; no observation I/O or native rebuild."""
import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
import tempfile
import unittest

p=argparse.ArgumentParser(description=__doc__);p.add_argument('--module',type=Path,required=True);p.add_argument('--qc',action='store_true');p.add_argument('--work',type=Path);args=p.parse_args()
spec=importlib.util.spec_from_file_location('sample_batch',args.module)
batch=importlib.util.module_from_spec(spec);spec.loader.exec_module(batch)


class SampleBatchControls(unittest.TestCase):
    def test_catalog_complete_identity_and_original65_reuse(self):
        entries=[dict(detector=f'ESO_CCD_#{n}',product=f'/CCD{n}/master.fits',qc_product=f'/CCD{n}/master.asdf',hdu=1) for n in range(65,97)]
        results=[dict(e,status='complete',native_exit_status=0,outputs={e['product']:dict(sha256='x'),e['qc_product']:dict(sha256='y')}) for e in entries[1:]]
        catalog=dict(status='candidate_signal_products',variance_state='unavailable',masters=entries)
        overall=dict(status='complete_for_owner_inspection',source_preservation=True,detectors_processed=31,preservation=dict(inputs=True),results=results)
        pilot=dict(status='complete_for_owner_inspection',preservation=dict(inputs=True),product=entries[0]['product'],qc_product=entries[0]['qc_product'],accepted_frames=10)
        execution=dict(status='complete',native_exit_status=0,qc_record_digest='frozen')
        admitted=batch.catalog_entries(catalog,overall,pilot,execution)
        self.assertEqual(len(admitted),32);self.assertEqual(admitted[0]['recipe']['qc_record_digest'],'frozen')
        for change in ('duplicate','wrong-path','wrong-hdu','failed','baseline'):
            c,b=copy.deepcopy(catalog),copy.deepcopy(overall)
            if change=='duplicate':c['masters'][-1]=c['masters'][0]
            if change=='wrong-path':c['masters'][1]['product']='/other.fits'
            if change=='wrong-hdu':c['masters'][1]['hdu']=2
            if change=='failed':b['preservation']['inputs']=False
            if change=='baseline':b['results'][0]['outputs']={}
            with self.assertRaises(RuntimeError):batch.catalog_entries(c,b,pilot,execution)
    def tables(self,work):
        points=[dict(detector='D',amplifier='L',configuration_detector=7,source_roi='R'+str(i),active_pixel=[i+1,1],raw_pixel=[i+51,5]) for i in range(2)]
        frames=[dict(asset='flat:8',index=8,hdu=17,pair='P'),dict(asset='flat:3',index=3,hdu=9,pair='P')]
        rows=[]
        for f in frames:
            for i,site in enumerate(points):
                rows.append(dict(zip(batch.SAMPLE_COLUMNS,map(str,[1,'D','L',7,site['source_roi'],i+1,1,i+51,5,f['asset'],f['index'],f['hdu'],f['pair'],2,
                    'admitted' if i==0 else 'not_admitted',-0.5 if i==0 else '', 'unavailable']))))
        def write_rows(values):
            (work/'samples.tsv').write_text('\t'.join(batch.SAMPLE_COLUMNS)+'\n'+''.join('\t'.join(r[k] for k in batch.SAMPLE_COLUMNS)+'\n' for r in values))
        write_rows(rows)
        (work/'population.tsv').write_text('\t'.join(batch.POP_COLUMNS)+'\n8\t6\t1\t0\t0\t0\t1\n3\t6\t1\t0\t0\t0\t1\n')
        (work/'command.complete').write_text('corrected_samples_complete_noise_unavailable\n')
        return points,dict(flat=frames),rows,write_rows
    def test_negative_signal_and_missing_preserved_with_original_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);points,selection,_,_=self.tables(work)
            result=batch.admit_tables(work,dict(detector='D'),selection,points,8)
            self.assertEqual(result,dict(rows=4,admitted=2,not_admitted=2,noise_state='unavailable'))
    def test_wrong_pixel_frame_missing_value_counts_and_columns_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);points,selection,rows,write=self.tables(work)
            for key,value in (('active_x','9'),('hdu','2'),('pair_id','OTHER'),('seconds','nan'),('signal_adu','nan'),('noise_state','identity')):
                altered=copy.deepcopy(rows);altered[0][key]=value;write(altered)
                with self.assertRaises(RuntimeError):batch.admit_tables(work,dict(detector='D'),selection,points,8)
            altered=copy.deepcopy(rows);altered[1]['signal_adu']='0';write(altered)
            with self.assertRaises(RuntimeError):batch.admit_tables(work,dict(detector='D'),selection,points,8)
            write(rows[::-1])
            with self.assertRaises(RuntimeError):batch.admit_tables(work,dict(detector='D'),selection,points,8)
            write(rows);(work/'population.tsv').write_text((work/'population.tsv').read_text().replace('8\t6','8\t5'))
            with self.assertRaises(RuntimeError):batch.admit_tables(work,dict(detector='D'),selection,points,8)
            (work/'samples.tsv').write_text('wrong\n')
            with self.assertRaises(RuntimeError):batch.admit_tables(work,dict(detector='D'),selection,points,8)
    def test_shared_images_two_passes_and_changed_source(self):
        paths=[Path('/flat'),Path('/master65')];expected={'/flat':'old','/master65':None};calls=[]
        def fingerprint(path):calls.append(str(path));return dict(sha256='old',stat=[1,2,3])
        self.assertEqual(batch.image_pass(paths,expected,fingerprint,'Before'),batch.image_pass(paths,expected,fingerprint,'After'))
        self.assertEqual(calls,['/flat','/master65']*2)
        with self.assertRaises(RuntimeError):batch.image_pass(paths,expected,lambda _:dict(sha256='changed'),'Changed')


class MasterQcAdmission(unittest.TestCase):
    def test_real_asdf_membership_selectors_frozen_links_and_no_FITS_open(self):
        source=Path(__file__).resolve().parents[2]
        if not (source/'Pycavi2/pycavi/pycavi').is_dir():
            source=batch.QC_QUALIFICATION/'source'
        sys.path.insert(0,str(source/'Pycavi2/pycavi/pycavi'))
        import pycavi_bias_qc as bridge
        import pycavi_qc as qc
        work=Path(tempfile.mkdtemp(prefix='master-qc-admission-',dir=args.work))
        print('RETAINED MASTER QC FIXTURE:',work,flush=True)
        def audit(event,values):
            if event=='open' and isinstance(values[0],(str,bytes)) and str(values[0]).lower().endswith('.fits'):
                raise RuntimeError('Unexpected FITS open in metadata admission')
        sys.addaudithook(audit)
        def sample(mask=0,empty=False):
            return dict(region_pixels=0 if empty else 4,bpm_excluded=0,nonfinite_excluded=0,
                valid_pixels=0 if empty else 4,zone=[0]*4 if empty else [1,2,1,2],bpm_supplied=mask,
                level_available=int(not empty),stdev_available=int(not empty),mad_available=int(not empty),
                mean=0,median=0,stdev=0,mad=0)
        product=work/'master.fits';config=work/'configuration.json';config.write_text('{}')
        members=[dict(path=str(work/f'bias{i}.fits'),accepted=int(i!=3),raw_active=sample(1),
            corrected_active=sample(1),prescan=sample(empty=True),overscan=sample(),
            scan_correction=dict(rows=2,median=0,stdev=0,prescan_used=0,overscan_used=1,rejection=[0,0])) for i in range(10)]
        handoff=dict(status='complete',handoff_version=1,configuration={},configuration_record=str(config),
            detector_id='D',configuration_detector=7,readout_id='OMEGACAM:normal:ordered:1x1',bin_x=1,bin_y=1,
            input_hdu=17,output_hdu=1,output=str(product),producer=dict(name='fixture',version='1',source_revision='fixture'),
            inputs=members,bpm=dict(selected=1,path=str(work/'bpm.fits'),hdu=9,good_value=1,active_only=1),
            master=sample(1),master_unmasked=sample(),raw_difference=sample(empty=True),
            ron=dict(pair_set=0,first=0,second=1,stdev_available=0,mad_available=0,stdev_adu=0,mad_adu=0),
            high_offset=dict(available=1,degenerate=0,count=0,locations=[],sigma=5,threshold=0))
        handoff_path=work/'handoff.json';handoff_path.write_text(json.dumps(handoff))
        records=work/'QC';records.mkdir()
        saved=bridge.publish_handoff(handoff_path,records,assessment_id='fixture',created_at='2026-11-04T00:00:00Z')
        entry=dict(detector='D',configuration_detector=7,product=str(product),hdu=1,handoff=str(handoff_path),
            qc_product=str(saved),expected_input_hdu=17,expected_bias_paths=[m['path'] for m in members],
            expected_bpm=handoff['bpm'],recipe=dict(producer=handoff['producer'],qc_record_digest=qc.read_record(saved).digest,accepted_frames=9))
        manifest=work/'masters.json';manifest.write_text(json.dumps([entry]))
        # Guard the ASDF runtime against this fixture's actual Python prefix only.
        original=batch.PRIVATE;batch.PRIVATE=Path(sys.prefix)
        try:
            batch.validate_qc(manifest,work/'valid.json')
            self.assertEqual(batch.read(work/'valid.json')['masters'][0]['accepted_frames'],9)
            bad=copy.deepcopy(entry);bad['recipe']['qc_record_digest']='0'*64;manifest.write_text(json.dumps([bad]))
            with self.assertRaises(RuntimeError):batch.validate_qc(manifest,work/'bad.json')
            manifest.write_text(json.dumps([entry]));handoff['inputs'][3]['accepted']=1;handoff_path.write_text(json.dumps(handoff))
            with self.assertRaises(RuntimeError):batch.validate_qc(manifest,work/'bad-membership.json')
            handoff['inputs'][3]['accepted']=0;handoff_path.write_text(json.dumps(handoff))
            (records/'bias0.asdf').write_bytes(b'broken frozen leaf')
            with self.assertRaises(ValueError):batch.validate_qc(manifest,work/'bad-link.json')
        finally:batch.PRIVATE=original


if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(MasterQcAdmission if args.qc else SampleBatchControls)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
