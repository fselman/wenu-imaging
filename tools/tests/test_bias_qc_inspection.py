"""Projection/cache/HTML controls; real ASDF opening is a separate Mac gate."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('bias_view', ROOT/'tools/view-bias-qc.py')
view = importlib.util.module_from_spec(spec)
spec.loader.exec_module(view)


def measurement(name, value, unit='ADU'):
    return dict(name=name, value=value, unit=unit,
                status='unavailable' if value is None else 'measured',
                reason='not_requested' if value is None else None,
                sources=['raw-000000'], definition=dict(stage='raw_pair_difference_before_any_correction',
                method='sample_stdev_raw_difference_div_sqrt2', sample_count=9,
                region=dict(bounds=[1, 9, 1, 9], coordinates='FITS-1-based-inclusive',
                            detector_bpm='applied', mask_record_id='bpm-0',
                            clipping='none', nonfinite='excluded')))


def record(name, subset=False):
    ids = ['CCD_A'] if subset else ['CCD_A', 'CCD_B']
    detectors = [dict(detector_id=d, output_hdu=i+1, configuration_detector=i,
                     measurements=[measurement('read_noise', 2.1+i*.2),
                                   measurement('variance', None, 'ADU2'),
                                   measurement('zero', 0, 'count'),
                                   measurement('pixels.hot.x', [3, 8], 'pixel')])
                 for i, d in enumerate(ids)]
    inputs = [dict(record_id='raw-%06d'%i, original_index=i,
                   file=dict(location='/never-open/raw%d.fits'%i),
                   detectors=[dict(detector_id=d, source_hdu=j+1,
                     measurements=[measurement('input.stat.%03d'%k, i+k*.01)
                                   for k in range(45)]) for j,d in enumerate(ids)])
              for i in range(2)]
    return dict(file=dict(filename=name+'.fits', location='/products/'+name+'.fits'),
                record=dict(created_at='2026-11-07T13:35:31.698Z'),
                provenance=dict(operation='cal.bias', fits_headers=[],
                                recipe_configuration=dict(snapshot='literal </script><script>bad()</script>')),
                calibrations=[], inputs=[], embedded_input_records=inputs,
                characterization=dict(detectors=detectors))


def sample_data(directory):
    products = []
    for name,subset in [('master-old',False),('master-recovered',False),('master-new',True)]:
        q = record(name,subset)
        for d in q['characterization']['detectors']:
            for metric,value,unit in [('read_noise.mad',2.0967,'ADU'),('master.mean',-.2,'ADU'),
                                      ('master.median',-.18,'ADU'),('master.stdev',.8,'ADU'),('pixels.hot',4,'count')]:
                d['measurements'].append(measurement(metric,value,unit))
            if name=='master-new':
                clipped=measurement('read_noise.clipped',1.99)
                clipped['definition']['method']='clipped_sample_stdev_raw_difference_div_sqrt2'
                clipped['definition']['region']['clipping']='median_centered_monotone_sigma'
                d['measurements'].append(clipped)
        for i,entry in enumerate(q['embedded_input_records']):
            for d in entry['detectors']:
                d['measurements'][0]['name']='raw_active.mean'
            q['inputs'].append(dict(record_id=entry['record_id'],participation_by_detector=[
                dict(detector_id=d['detector_id'],status='used' if i==0 else 'rejected',reason=None if i==0 else 'native_frame_mean_rejection')
                for d in entry['detectors']]))
        products.append(view.extract(directory/(name+'.asdf'),q))
    return dict(schema_version=1, directory=str(directory), products=products,
                errors=[dict(path='bad.asdf', error='Invalid schema <test>')],
                generated_at='2026-11-07', observation_epoch_policy='not_selected')


class InspectionTests(unittest.TestCase):
    def test_detached_scalars_arrays_and_no_epoch(self):
        q = record('master')
        p = view.extract(Path('/products/master.asdf'), q)
        rows = p['rows']
        self.assertEqual(len(rows), 186)
        self.assertEqual(len(p['array_measurements']), 2)
        self.assertTrue(any(r['measurement']['value'] == 0 for r in rows))
        missing = next(r for r in rows if r['measurement']['name'] == 'variance')
        self.assertIsNone(missing['measurement']['value'])
        self.assertEqual(missing['measurement']['status'], 'unavailable')
        q['characterization']['detectors'][0]['measurements'][0]['value'] = 99
        self.assertEqual(rows[0]['measurement']['value'], 2.1)
        self.assertNotIn('jd', p)

    def test_read_once_and_visible_bad_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name in ('a', 'b', 'broken'):
                (directory/(name+'.asdf')).write_bytes(b'synthetic placeholder')
            calls = []
            def reader(path, schema):
                calls.append(path.name)
                if path.stem == 'broken':
                    raise ValueError('bad fixture')
                return view.extract(path, record(path.stem))
            data = view.collect(directory, b'not used by projection reader', reader)
            self.assertEqual(calls, ['a.asdf','b.asdf','broken.asdf'])
            self.assertEqual(data['read_attempts'], 3)
            self.assertEqual(len(data['errors']), 1)
            self.assertEqual(data['products'][0]['raw_sequence'], data['products'][1]['raw_sequence'])
            page = view.render(data)
            self.assertNotIn('__BIAS_QC_', page)
            self.assertNotIn('literal </script><script>bad()', page)
            self.assertIn(r'\u003c/script>', page)
            self.assertEqual(calls, ['a.asdf','b.asdf','broken.asdf'])

    def test_changed_source_nonfinite_duplicate_and_stem_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp);p=directory/'a.asdf';p.write_bytes(b'a')
            def reader(path, schema):
                path.write_bytes(b'changed')
                return view.extract(path, record('a'))
            with self.assertRaisesRegex(ValueError, 'changed'):
                view.collect(directory, b'', reader)
        q = record('a')
        with self.assertRaisesRegex(ValueError,'stem mismatch'):
            view.extract(Path('/b.asdf'), q)
        q['characterization']['detectors'][0]['measurements'][0]['value'] = float('nan')
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            view.extract(Path('/a.asdf'), q)
        q = record('a');q['characterization']['detectors'][0]['measurements'] *= 2
        with self.assertRaisesRegex(ValueError, 'Duplicate measurement'):
            view.extract(Path('/a.asdf'), q)


if __name__ == '__main__':
    unittest.main()
