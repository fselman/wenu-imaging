"""Saved-header policy and explicit proposal tests; no FITS parser/numerical substitute."""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import runpy
import tomllib
import unittest
ROOT=Path(__file__).resolve().parents[2]
API=runpy.run_path(str(ROOT/'tools/prepare-ocam-pair-review.py'))

class ReviewTests(unittest.TestCase):
    def fixture(self):
        geometry=tomllib.loads((ROOT/'config/detectors/omegacam-1x1.toml').read_text())
        processing=tomllib.loads((ROOT/'config/processing/omegacam-characterization.toml').read_text())
        def hdu(index,dimensions,values):return dict(hdu=index,dimensions=dimensions,cards=[dict(key=k,value=v) for k,v in values.items()])
        rows=[]
        for wanted in API['API']['selected_sequence'](Path('/raw')):
            values={'INSTRUME':'OMEGACAM','ESO OBS ID':574184,'EXPTIME':wanted['expected_seconds'],
                'ESO DPR TYPE':wanted['expected_type'],'ESO INS FILT1 NAME':wanted['expected_filter'],
                'ESO DET READ MODE':'normal','ESO DET READ SPEED':'normal','ESO DET READ CLOCK':'mosaic read (ordered)',
                'ESO DET WIN1 BINX':1,'ESO DET WIN1 BINY':1,'ESO DET OUTPUTS':32,
                'ESO TPL ID':wanted['role'],'ESO TPL START':'saved-template-start'}
            hdus=[hdu(0,[],values)]
            # Reordering on alternate files proves independent identity binding.
            order=geometry['detector'] if not wanted['index']%2 else list(reversed(geometry['detector']))
            for index,d in enumerate(order,1):
                hdus.append(hdu(index,d['raw_size'],{'EXTNAME':d['id'],'ESO DET CHIP ID':d['id'],
                    'ESO DET OUT1 ID':'L','ESO DET OUT1 NX':2048,'ESO DET OUT1 NY':4100,
                    'ESO DET OUT1 PRSCX':48,'ESO DET OUT1 OVSCX':48,'BITPIX':16,'BSCALE':1,'BZERO':32768}))
            rows.append(dict(**wanted,errors=[],inspection=dict(asset=dict(hdus=hdus),diagnostics=[])))
        mask=[hdu(0,[],{})]+[hdu(i+1,[2044,4091],{'EXTNAME':d['id'],'BITPIX':8}) for i,d in enumerate(geometry['detector'])]
        inventory=dict(raw_root='/raw',selected=rows,candidates=[dict(path='/raw/OCAM_BPM_1x1.fits',inspection=dict(asset=dict(hdus=mask)))],
                       errors=[],source_stat_preservation=dict(passed=True))
        return inventory,geometry,processing

    def test_complete_headers_and_proposal_preserve_order(self):
        inventory,geometry,processing=self.fixture();report=API['review'](inventory,geometry['detector'])
        text,proposal=API['proposed_selection'](inventory,geometry,report,processing)
        selection=tomllib.loads(text)
        self.assertEqual(selection['detector'],'ESO_CCD_#65')
        self.assertEqual([b['hdu'] for b in selection['bias']],[1,32])
        self.assertEqual([f['index'] for f in selection['flat']],list(range(10,30)))
        self.assertEqual([f['pair'] for f in selection['flat'] if f['pair']=='flat-02s'],['flat-02s','flat-02s'])
        self.assertEqual(selection['max_loaded_pixels'],206467604)
        self.assertEqual(selection['max_rows'],50)
        self.assertEqual(selection['bpm']['good_value'],1)
        self.assertEqual(selection['raw_saturation_adu'],65534)
        self.assertEqual(proposal['status'],'proposal_not_executed')
        self.assertEqual(report['history_review'],['ESO_CCD_#69','ESO_CCD_#77'])

    def test_complete_helper_against_canonical_configuration(self):
        inventory,_,_=self.fixture()
        with tempfile.TemporaryDirectory(prefix='ocam-review-policy-') as temporary:
            parent=Path(temporary);raw=parent/'raw';raw.mkdir()
            inventory['raw_root']=str(raw)
            for row in inventory['selected']+inventory['candidates']:
                path=raw/Path(row['path']).name;path.write_bytes(b'Injected header evidence fixture, not a FITS payload')
                row['path']=str(path);row['stat_before']=API['stat_identity'](path)
            source=parent/'inventory.json';source.write_text(json.dumps(inventory))
            prior=parent/'prior.json';prior.write_text('{}')
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()}
            out=parent/'review';out.mkdir()
            command=[sys.executable,'-B',str(ROOT/'tools/prepare-ocam-pair-review.py'),
                     '--inventory',str(source),'--bpm-review',str(prior),'--output',str(out)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            receipt=json.loads((out/'review.json').read_text())
            self.assertEqual(receipt['status'],'prepared_for_owner_choices')
            self.assertFalse(receipt['measurement_executed'])
            self.assertTrue((out/'README.md').is_file())
            self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()})
            with (raw/Path(inventory['selected'][0]['path']).name).open('ab') as stream:stream.write(b'changed')
            failed=parent/'failed';failed.mkdir();command[-1]=str(failed)
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads((failed/'review.json').read_text())['status'],'failed')
            self.assertFalse((failed/'selection-proposed.toml').exists())

    def test_refuse_changed_output_amplifier_clock_or_duplicate_card(self):
        for case in ('amplifier','clock','duplicate','coverage'):
            inventory,geometry,_=self.fixture()
            hdus=inventory['selected'][12]['inspection']['asset']['hdus']
            if case=='clock':
                next(c for c in hdus[0]['cards'] if c['key']=='ESO DET READ CLOCK')['value']='different'
            elif case=='coverage':hdus.pop()
            else:
                card=next(c for c in hdus[20]['cards'] if c['key']=='ESO DET OUT1 ID')
                if case=='duplicate':hdus[20]['cards'].append(dict(card))
                else:card['value']='R'
            with self.assertRaises(ValueError):API['review'](inventory,geometry['detector'])

    def test_refuse_sequence_and_bpm_conflicts(self):
        for case in ('order','time','bpm'):
            inventory,geometry,_=self.fixture()
            if case=='order':inventory['selected'][0],inventory['selected'][1]=inventory['selected'][1],inventory['selected'][0]
            elif case=='time':
                next(c for c in inventory['selected'][10]['inspection']['asset']['hdus'][0]['cards'] if c['key']=='EXPTIME')['value']=2.01
            else:inventory['candidates'][0]['inspection']['asset']['hdus'][1]['dimensions']=[2044,4090]
            with self.assertRaises(ValueError):API['review'](inventory,geometry['detector'])

if __name__=='__main__':unittest.main()
