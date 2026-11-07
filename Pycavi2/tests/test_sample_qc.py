"""Corrected sample serialization controls only. Metadata fixtures, no FITS/native runs."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_sample_qc as bridge
qc=bridge.qc
WORK=Path(tempfile.gettempdir())


def fixture(work):
    batch=work/'native-batch';native=batch/'CCD65/native';native.mkdir(parents=True)
    masterdir=work/'original-master/QC';masterdir.mkdir(parents=True)
    detector='ESO_CCD_#65';slot=0
    def builder(name,kind,identity=None):
        return qc.QcRecipe(file=dict(id=identity or str(work/name),filename=name,location=str(work/name),kind=kind,
            sha256=None,observed_at=None,selectors=[dict(detector_id=detector,hdu_index=1,configuration_detector=slot)],
            context=dict(readout_id='OMEGACAM:normal:ordered:1x1',bin_x=1,bin_y=1)),assessment_id='master:'+name,
            created_at='2026-11-04T00:00:00Z',producer=dict(name='fixture',version='1',source_revision='old-native'),
            operation='cal.bias',configuration_id='fixture-config')
    leaves=[]
    for i in range(11):
        b=builder(f'bias{i}.fits' if i<10 else 'master-bpm.fits','raw' if i<10 else 'product');leaf=b.seal()
        qc.write_record(leaf,masterdir);leaves.append(leaf)
    b=builder('master.fits','product')
    for i,leaf in enumerate(leaves):b.add_input(leaf,qc_path=qc.qc_filename(leaf.as_dict()['file']['filename']),
        participation='rejected' if i==3 else 'used',reason='fixture_rejection' if i==3 else None)
    master=b.seal();masterpath=qc.write_record(master,masterdir)
    flat=[dict(path=str(work/f'flat{i}.fits'),asset=f'flat{i}.fits',hdu=1,index=10+i,pair=f'P{min(i,19-i)}') for i in range(20)]
    points=[dict(detector=detector,amplifier='L',configuration_detector=slot,source_roi=f'CCD65.R{i}',active_pixel=[i+1,1],raw_pixel=[i+51,5]) for i in range(5)]
    selection=dict(flat=flat,bpm=dict(path=str(work/'bpm.fits'),asset='bpm.fits',hdu=1),readout_id='OMEGACAM:normal:ordered:1x1',bin_x=1,bin_y=1)
    e=dict(detector=detector,configuration_detector=slot,population=points,selection=selection,active_pixels=12,directory=str(native.parent),
        master=dict(product=str(work/'master.fits'),qc_product=str(masterpath),hdu=1,recipe=dict(qc_record_digest=master.digest)))
    lines=['\t'.join(bridge.COLUMNS)]
    for f,frame in enumerate(flat):
        for i,point in enumerate(points):
            value='' if f==0 and i==0 else format(-.12345678901234568 if f==0 else 100.12345678901234*f+i,'.17g')
            lines.append('\t'.join(map(str,[1,detector,'L',slot,point['source_roi'],i+1,1,i+51,5,frame['asset'],frame['index'],1,frame['pair'],2,
                                            'admitted' if value else 'not_admitted',value,'unavailable'])))
    (native/'samples.tsv').write_text('\n'.join(lines)+'\n')
    columns='input_index outside_selected_sites bpm_excluded sample_excluded nonfinite saturated admitted'.split()
    (native/'population.tsv').write_text('\t'.join(columns)+'\n'+''.join(f'{10+i}\t7\t0\t0\t{int(i==0)}\t0\t{4 if i==0 else 5}\n' for i in range(20)))
    (native/'configuration.json').write_text('{}\n');(native/'command.complete').write_text('corrected_samples_complete_noise_unavailable\n')
    result=dict(detector=detector,rows=100,admitted=99,not_admitted=1,noise_state='unavailable',outputs={str(p):dict(sha256=bridge.sha(p.read_bytes())) for p in native.iterdir()})
    (batch/'run.py').write_bytes((ROOT/'Pycavi2/tools/run_ocam_linearity_samples.py').read_bytes())
    report=dict(metadata_inputs={str(p):dict(sha256=bridge.sha(p.read_bytes())) for p in masterdir.glob('*.asdf')})
    frozen={};state=bridge.admit_entry(batch,e,result,report,frozen)
    fingerprints={p:dict(sha256='1'*64,stat=[1,2,3,4,5,6]) for p in [*[r['path'] for r in flat],selection['bpm']['path'],e['master']['product']]}
    origin=dict(native_revision='f'*40,controller_revision='e'*40,image_fingerprints=fingerprints,sampling_policy=dict(status='fixture'),batch_receipt=dict(path=str(batch/'overall-execution.json'),sha256='2'*64,preservation={k:True for k in bridge.GUARDS}))
    return batch,state,result,report,frozen,origin


class SampleQcTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='sample-asdf-',dir=WORK))
        self.batch,self.state,self.result,self.report,self.frozen,self.origin=fixture(self.work)
        self.target=self.work/'saved';self.target.mkdir()
    def publish(self):
        return bridge.publish_entry(self.state,self.target,assessment_id='samples',created_at='2026-11-04T00:00:00Z',serializer_revision='a'*40,origin=self.origin)
    def test_exact_roundtrip_master_membership_and_relocation(self):
        result=self.publish();self.assertEqual(result['records'],34)
        table=bridge.read_product(result['path']);self.assertEqual(bridge.canonical(table),bridge.canonical(self.state['table']))
        self.assertIsNone(table['rows'][0]['signal_adu']);self.assertEqual(table['rows'][1]['signal_adu'],-.12345678901234568)
        master=qc.read_record(self.target/'master/master.asdf');self.assertEqual(master.digest,self.state['master_records'][0].digest)
        self.assertEqual(master.as_dict()['inputs'][3]['participation']['status'],'rejected')
        moved=self.work/'relocated';shutil.copytree(self.target,moved)
        self.assertEqual(bridge.canonical(bridge.read_product(moved/'samples.asdf')),bridge.canonical(table))
        self.assertTrue(all(bridge.small(p)==v for p,v in self.frozen.items()))
    def test_changed_transport_marker_or_master_refused(self):
        native=self.batch/'CCD65/native'
        for name in ('samples.tsv','command.complete'):
            p=native/name;old=p.read_bytes();p.write_bytes(old+b'changed')
            with self.assertRaises(qc.QcError):bridge.admit_entry(self.batch,self.state['entry'],self.result,self.report,{})
            p.write_bytes(old)
        master=Path(self.state['entry']['master']['qc_product']);old=master.read_bytes();master.write_bytes(b'broken')
        with self.assertRaises(ValueError):bridge.admit_entry(self.batch,self.state['entry'],self.result,self.report,{})
        master.write_bytes(old);self.assertFalse(list(self.target.iterdir()))
    def test_typed_units_origin_noise_and_measurement_tamper_refused(self):
        result=self.publish();tree=qc.read_record(result['path']).as_dict()
        for kind in ('typed','unit','measurement','noise','pixel','population'):
            altered=deepcopy(tree)
            if kind=='typed':altered['extensions']['corrected_sample_table']['rows'][1]['signal_adu']+=1
            if kind=='unit':altered['extensions']['corrected_sample_table']['units']['signal_adu']='electron'
            if kind=='measurement':altered['characterization']['detectors'][0]['measurements'][1]['value']+=1
            if kind=='noise':altered['extensions']['corrected_sample_origin']['noise_state']='identity'
            if kind=='population':altered['extensions']['corrected_sample_population']['rows'][0]['admitted']+=1
            if kind=='pixel':altered['extensions']['corrected_sample_origin']['entry']['population'][0]['raw_pixel'][0]+=1
            with self.assertRaises(qc.QcError):bridge.table_from_record(qc.QcRecord(qc.encoded(altered)))
    def test_failed_or_wrong_cohort_receipt_refused_before_publication(self):
        images={f'/recorded/{i}.fits':dict(sha256='1'*64) for i in range(53)}
        sampling=self.batch/'singleton-sites';sampling.mkdir();(sampling/'manifest.json').write_text('{}')
        plan=dict(controller_revision='e'*40,native_revision='f'*40,images=list(images),entries=[])
        (self.batch/'plan.json').write_text(json.dumps(plan))
        report=dict(status='complete_for_owner_inspection',source_preservation=True,preservation={k:True for k in bridge.GUARDS},
            detectors_processed=32,rows=3200,inputs=images,after_inputs=images,controller_revision='e'*40,native_revision='f'*40,
            results=[],metadata_inputs={str(p):dict(sha256=bridge.sha(p.read_bytes())) for p in
                (self.batch/'plan.json',self.batch/'run.py',sampling/'manifest.json')})
        for kind in ('failed','guard','source','cohort'):
            altered=deepcopy(report)
            if kind=='failed':altered['status']='failed'
            if kind=='guard':altered['preservation']['products']=False
            if kind=='source':altered['after_inputs']={}
            (self.batch/'overall-execution.json').write_text(json.dumps(altered))
            with self.assertRaises(qc.QcError):bridge.admit_batch(self.batch)
        self.assertFalse(list(self.target.iterdir()))
    def test_conflict_and_broken_frozen_link(self):
        result=self.publish();before={str(p):bridge.sha(p.read_bytes()) for p in self.target.rglob('*.asdf')}
        with self.assertRaises(qc.QcError):self.publish()
        self.assertEqual(before,{str(p):bridge.sha(p.read_bytes()) for p in self.target.rglob('*.asdf')})
        (self.target/'inputs/flat0.asdf').write_bytes(b'broken')
        with self.assertRaises(ValueError):bridge.read_product(result['path'])


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True);a=p.parse_args();WORK=a.work.resolve(strict=True)
    attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Network forbidden in sample ASDF fixture')
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('FITS access forbidden in sample ASDF fixture')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SampleQcTests))
    (WORK/'sample-qc-contract-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),network_attempts=attempts),indent=2)+'\n')
    sys.exit(0 if result.wasSuccessful() and not attempts else 1)
