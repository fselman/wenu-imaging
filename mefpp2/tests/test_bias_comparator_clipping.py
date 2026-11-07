"""Comparator control checks; no Astropy, ASDF runtime or image files needed."""
import importlib.util
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[2] / 'tools/compare-bias-products.py'
spec = importlib.util.spec_from_file_location('compare_bias_products', path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ComparatorTests(unittest.TestCase):
    def setUp(self):
        self.old = {key: 'old.fits' for key in m.IDENTITY_KEYS}
        self.old['ESO MPP QC RON STD'] = 2.3
        self.old['ESO MPP QC FRAME001 RAW MEAN'] = 270.5
        self.new = dict(self.old)
        self.new.update({key: 'new.fits' for key in m.IDENTITY_KEYS})
        self.added = {'ESO MPP QC ' + group: 1 for group in m.ADDITION_GROUPS}

    def test_strict_default_and_own_identities(self):
        self.assertEqual(m.compare_headers(self.new, self.old, False), (2, 0))
        with self.assertRaises(AssertionError):
            m.compare_headers(self.new | self.added, self.old, False)

    def test_documented_additions_only(self):
        self.assertEqual(m.compare_headers(self.new | self.added, self.old, True), (2, 16))
        for key in ('ESO MPP QC UNKNOWN', 'ESO MPP QC RCL STDERR', 'ESO MPP QC RON CLIPPER'):
            with self.assertRaises(AssertionError):
                m.compare_headers(self.new | self.added | {key: 9}, self.old, True)
        with self.assertRaises(AssertionError):
            m.compare_headers(self.new, self.old, True)

    def test_existing_science_and_input_context_stay_strict(self):
        for key in ('ESO MPP QC RON STD', 'ESO MPP QC FRAME001 RAW MEAN'):
            for action in ('change', 'remove'):
                changed = self.new | self.added
                if action == 'change':
                    changed[key] += 0.1
                else:
                    del changed[key]
                with self.assertRaises(AssertionError):
                    m.compare_headers(changed, self.old, True)

    def test_asdf_reader_compiles_and_explicit_names(self):
        compile(m.ASDF_READER, '<independent-asdf-reader>', 'exec')
        self.assertEqual(len(m.CLIPPED_ADDITIONS), 16)
        self.assertNotIn('read_noise', m.CLIPPED_ADDITIONS)
        self.assertNotIn('bpm.good_value', m.CLIPPED_ADDITIONS)


if __name__ == '__main__':
    unittest.main()
