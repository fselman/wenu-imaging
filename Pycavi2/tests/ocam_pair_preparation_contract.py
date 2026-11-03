"""Preparation-policy checks with injected header records; no FITS parser substitute."""
import contextlib
import hashlib
import io
from pathlib import Path
import runpy
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
API=runpy.run_path(str(ROOT/'Pycavi2/tools/prepare_ocam_pair_measurements.py'))


class PreparationTests(unittest.TestCase):
    def test_declared_nonconsecutive_pairs(self):
        rows=API['selected_sequence'](Path('/raw'))
        self.assertEqual(len(rows),30)
        self.assertEqual(len({r['path'] for r in rows}),30)
        self.assertEqual([r['expected_seconds'] for r in rows[10:]],
                         [2,70,40,5,10,30,20,50,60,7,7,60,50,20,30,10,5,40,70,2])
        pairs={}
        for row in rows:
            self.assertEqual(row['expected_obs_id'],574184)
            if row['pair_id']:pairs.setdefault(row['pair_id'],[]).append(row['index'])
        self.assertEqual(len(pairs),10)
        self.assertTrue(all(len(v)==2 for v in pairs.values()))
        self.assertEqual(pairs['flat-02s'],[10,29])
        self.assertEqual(pairs['flat-07s'],[19,20])

    def test_saved_inventory_unresolved_choices_and_identity_mapping(self):
        config=API['configuration'](ROOT)
        ids=[d['detector_id'] for d in config['configured_detectors']]
        self.assertEqual(len(ids),32)
        self.assertEqual(ids[17],'ESO_CCD_#69')
        self.assertEqual(ids[21],'ESO_CCD_#77')
        with tempfile.TemporaryDirectory(prefix='ocam-preparation-') as temporary:
            parent=Path(temporary);raw=parent/'raw';raw.mkdir();out=parent/'inventory'
            rows=API['selected_sequence'](raw)
            bypath={r['path']:r for r in rows}
            for row in rows:Path(row['path']).write_bytes(b'Frozen source placeholder, no arrays')
            before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()}
            def inspector(path):
                row=bypath[str(path)]
                values={'INSTRUME':'OMEGACAM','EXPTIME':row['expected_seconds'],
                        'ESO DPR TYPE':row['expected_type'],'ESO INS FILT1 NAME':row['expected_filter'],
                        'ESO OBS ID':574184}
                primary=dict(hdu=0,dimensions=[],cards=[dict(key=k,value=v) for k,v in values.items()])
                # Alternate HDU order: identities must follow EXTNAME independently.
                ordered=ids if row['index']%2==0 else list(reversed(ids))
                hdus=[primary]+[dict(hdu=i+1,dimensions=[2144,4200],cards=[dict(key='EXTNAME',value=name)])
                                for i,name in enumerate(ordered)]
                return dict(asset=dict(path=str(path),hdus=hdus),diagnostics=[dict(code='fits_warning',message='retained')])
            with contextlib.redirect_stdout(io.StringIO()):
                report=API['prepare'](ROOT,raw,out,inspector)
            self.assertEqual(report['status'],'prepared_for_selection_review')
            self.assertFalse(report['ready_for_measurement'])
            self.assertFalse(report['measurement_executed'])
            self.assertEqual(len(report['unresolved']),5)
            self.assertTrue(report['source_stat_preservation']['passed'])
            self.assertEqual(report['detector_bindings'][0]['observed'][0]['hdu'],1)
            self.assertEqual(report['detector_bindings'][0]['observed'][1]['hdu'],32)
            self.assertEqual(sum(b['history_review'] for b in report['detector_bindings']),2)
            self.assertTrue((out/'inventory.json').is_file() and (out/'sequence.tsv').is_file() and (out/'pairs.json').is_file())
            self.assertEqual(before,{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()})
            with self.assertRaises(ValueError):API['prepare'](ROOT,raw,out,inspector)

    def test_conflicting_metadata_is_not_rounded_or_accepted(self):
        row=API['selected_sequence'](Path('/raw'))[10]
        primary=dict(hdu=0,dimensions=[],cards=[dict(key=k,value=v) for k,v in
             [('INSTRUME','OMEGACAM'),('EXPTIME',2.001),('ESO DPR TYPE','FLAT,DOME'),
              ('ESO INS FILT1 NAME','v_STRM'),('ESO OBS ID',999)]])
        result=dict(asset=dict(hdus=[primary]),diagnostics=[])
        errors=API['assess'](row,result,{'ESO_CCD_#96':{}})
        self.assertTrue(any('EXPTIME' in e for e in errors))
        self.assertTrue(any('DPR TYPE' in e for e in errors))
        self.assertTrue(any('OBS ID' in e for e in errors))
        self.assertTrue(any('coverage' in e for e in errors))
        primary['cards'].append(dict(key='EXPTIME',value=2))
        self.assertIsNone(API['single'](primary,'EXPTIME'))


if __name__=='__main__':unittest.main(verbosity=2)
