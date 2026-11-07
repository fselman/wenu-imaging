"""Three serial-orchestration contracts; callbacks only, no FITS/native/ASDF."""
from copy import deepcopy
import os
from pathlib import Path
import runpy
import unittest
DRIVER=Path(os.environ.get('CORRECTED_ROI_BATCH_DRIVER',str(Path(__file__).resolve().parents[1]/'tools/run_ocam_corrected_roi_batch.py')))
run_remaining=runpy.run_path(str(DRIVER))['run_remaining']


def product(detector):
    return dict(detector=detector,path='/saved/'+detector+'/linearity-preparation.asdf',digest='a'*64,
                pairs=50,exposures=100,sites=100,trace_frames=30,noise_state='unavailable')


def plan():
    return dict(status='complete_dependency_plan',dependencies=[dict(selection=dict(detector=f'ESO_CCD_#{i}')) for i in range(65,97)])


def success(entry):
    return dict(status='complete_for_owner_inspection',source_preservation=True,fitted=False,
                product=product(entry['selection']['detector']))


class BatchTests(unittest.TestCase):
    def test_complete_coverage_reuses_CCD65_and_runs_serially(self):
        calls=[];snapshots=[];pilot=product('ESO_CCD_#65');original=deepcopy(pilot)
        def execute(entry):calls.append(entry['selection']['detector']);return success(entry)
        products=run_remaining(plan(),pilot,execute,snapshots.append)
        self.assertEqual(calls,[f'ESO_CCD_#{i}' for i in range(66,97)])
        self.assertEqual(len(products),32);self.assertEqual([len(s) for s in snapshots],list(range(2,33)))
        self.assertEqual(sum(p['reused'] for p in products),1)
        self.assertEqual(sum(p['exposures'] for p in products),3200)
        self.assertEqual(sum(p['pairs'] for p in products),1600)
        self.assertEqual(pilot,original)
    def test_invalid_cohort_fails_before_any_processing(self):
        for mode in ('missing','duplicate','wrong','failed','bad_pilot'):
            value=plan();pilot=product('ESO_CCD_#65');calls=[]
            if mode=='missing':value['dependencies'].pop()
            elif mode=='duplicate':value['dependencies'][-1]=deepcopy(value['dependencies'][0])
            elif mode=='wrong':value['dependencies'][-1]['selection']['detector']='OTHER'
            elif mode=='failed':value['status']='failed'
            else:pilot['detector']='OTHER'
            with self.assertRaises(RuntimeError):run_remaining(value,pilot,lambda e:calls.append(e))
            self.assertFalse(calls)
    def test_partial_failed_or_incomplete_result_stops_next_detector(self):
        for mode in ('exception','failed','images','fitted','count','noise','identity','path'):
            calls=[];snapshots=[]
            def execute(entry):
                calls.append(entry['selection']['detector']);result=success(entry)
                if len(calls)==2:
                    if mode=='exception':raise RuntimeError('synthetic processing failure')
                    if mode=='failed':result['status']='failed'
                    if mode=='images':result['source_preservation']=False
                    if mode=='fitted':result['fitted']=True
                    if mode=='count':result['product']['exposures']=99
                    if mode=='noise':result['product']['noise_state']='assumed'
                    if mode=='identity':result['product']['detector']='OTHER'
                    if mode=='path':result['product']['path']=product('ESO_CCD_#65')['path']
                return result
            with self.assertRaises((ValueError,RuntimeError)):
                run_remaining(plan(),product('ESO_CCD_#65'),execute,snapshots.append)
            self.assertEqual(calls,['ESO_CCD_#66','ESO_CCD_#67']);self.assertEqual(len(snapshots),1)
            self.assertEqual(len(snapshots[0]),2)


if __name__=='__main__':unittest.main()
