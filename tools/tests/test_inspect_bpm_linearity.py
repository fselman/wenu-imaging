"""Saved inspection rejects altered image payloads and incomplete receipt bindings."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('inspection', Path(__file__).parents[1]/'inspect-bpm-linearity.py')
inspection = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inspection)

class Plane:
    def fileinfo(self):
        return {'datLoc': 2, 'datSpan': 4}

class SavedInspectionTests(unittest.TestCase):
    def test_pixel_and_padding_bytes_are_exact(self):
        inspection.equal_payload(Plane(), Plane(), io.BytesIO(b'XXabcd'), io.BytesIO(b'YYabcd'))
        for changed in (b'YYabce', b'YYabc'):
            with self.assertRaises(AssertionError):
                inspection.equal_payload(Plane(), Plane(), io.BytesIO(b'XXabcd'), io.BytesIO(changed))

    def test_native_receipt_covers_all_published_members(self):
        document = {'native_recipe_receipt_schema_version': 1,
                    'fits': 'final.fits', 'fits_sha256': 'a',
                    'asdf': 'final.asdf', 'asdf_sha256': 'b',
                    'detectors': [{'fits': 'det.fits', 'fits_sha256': 'c',
                                   'asdf': 'det.asdf', 'asdf_sha256': 'd',
                                   'prepared': 'measurement.asdf', 'prepared_sha256': 'e'}]}
        self.assertEqual(inspection.receipt_fingerprints(document),
                         {'final.fits': 'a', 'final.asdf': 'b', 'det.fits': 'c',
                          'det.asdf': 'd', 'measurement.asdf': 'e'})
        del document['detectors'][0]['fits_sha256']
        with self.assertRaises(AssertionError):
            inspection.receipt_fingerprints(document)

    def test_native_and_legacy_completion_formats(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, text in [('native.toml', 'status = "complete"'),
                               ('legacy.json', '{"status": "complete"}')]:
                p = Path(directory)/name
                p.write_text(text)
                self.assertEqual(inspection.completion_document(p), {'status': 'complete'})

if __name__ == '__main__':
    unittest.main()
