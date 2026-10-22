"""MEF BPM association and preflight regressions; no native programs run."""
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
from astropy.io import fits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pycavi.pycavi import pycavi_associate_reduction as reduction


class Partition(SimpleNamespace):
    __hash__ = object.__hash__


class MefBpmTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.static = self.root / 'static'
        self.work = self.root / 'science'
        self.static.mkdir()
        self.work.mkdir()
        self.instrument = SimpleNamespace(
            bpm_prefix='OCAM_BPM', nextensions=2,
            valid_ext_names=['CCD_A', 'CCD_B'], bias_prefix='OCAM_MB',
            domeff_prefix='OCAM_DOMEFF', skyff_prefix='OCAM_SKYFF',
            mff_prefix='OCAM_MFF')
        self.source = self.static / 'OCAM_BPM_1x1.fits'
        self.local = self.work / self.source.name
        self.part = Partition(base_path=str(self.work), filter='r_SDSS')
        self.tree = reduction.PartitionsTree.__new__(reduction.PartitionsTree)
        self.tree.bpm_partitions = [SimpleNamespace(base_path=str(self.static))]

    def write_mask(self, names=('CCD_A', 'CCD_B'), dtype=np.uint8, shape=(3, 4)):
        fits.HDUList([fits.PrimaryHDU()] + [
            fits.ImageHDU(np.ones(shape, dtype=dtype), name=name)
            for name in names]).writeto(self.source, overwrite=True)

    def link(self):
        self.tree.link_bpm([self.part], self.instrument)

    def remove_group_cards(self, keys, compact=False):
        # Edit header cards directly: a FITS writer would restore mandatory
        # cards, hiding the legacy layout seen on chapman3.
        raw = bytearray(self.source.read_bytes())
        with fits.open(self.source, memmap=True) as hdus:
            for i, hdu in enumerate(hdus[1:], 1):
                start = hdus.fileinfo(i)['hdrLoc']
                if compact:
                    header = hdu.header.copy()
                    for key in keys:
                        del header[key]
                    block = header.tostring().encode('ascii')
                    raw[start:start+len(block)] = block
                    continue
                for j, card in enumerate(hdu.header.cards):
                    if card.keyword in keys:
                        raw[start + 80*j:start + 80*(j+1)] = b' ' * 80
        self.source.write_bytes(raw)

    def test_legacy_missing_group_cards_warn_without_changing_file(self):
        self.link()
        for keys in (('PCOUNT',), ('GCOUNT',), ('PCOUNT', 'GCOUNT')):
            with self.subTest(keys=keys):
                self.write_mask()
                self.remove_group_cards(keys)
                before = self.source.read_bytes()
                with fits.open(self.source) as hdus:
                    with self.assertRaises(fits.verify.VerifyError):
                        hdus.verify('exception')
                with self.assertLogs(level='WARNING') as captured:
                    self.assertTrue(reduction.check_mef_bpm(self.work, self.instrument))
                self.assertIn('legacy MEF BPM', captured.output[0])
                self.assertEqual(before, self.source.read_bytes())
                with fits.open(self.source) as hdus:
                    self.assertTrue(all(k not in hdus[1].header for k in keys))

        self.write_mask()
        self.remove_group_cards(('PCOUNT', 'GCOUNT'), compact=True)
        before = self.source.read_bytes()
        with self.assertLogs(level='WARNING'):
            self.assertTrue(reduction.check_mef_bpm(self.work, self.instrument))
        self.assertEqual(before, self.source.read_bytes())

    def test_legacy_tolerance_does_not_ignore_other_fits_errors(self):
        self.write_mask()
        self.link()
        self.remove_group_cards(('PCOUNT', 'GCOUNT'))
        with fits.open(self.source) as hdus:
            start = hdus.fileinfo(1)['hdrLoc']
            bitpix = start + 80 * hdus[1].header.index('BITPIX')
            name = start + 80 * hdus[1].header.index('EXTNAME')
        raw = bytearray(self.source.read_bytes())
        raw[bitpix:bitpix+80], raw[name:name+80] = raw[name:name+80], raw[bitpix:bitpix+80]
        self.source.write_bytes(raw)
        before = self.source.read_bytes()
        with self.assertRaisesRegex(ValueError, 'NAXIS1.*wrong place'):
            reduction.check_mef_bpm(self.work, self.instrument)
        self.assertEqual(before, self.source.read_bytes())

    def test_nonstandard_group_values_are_rejected(self):
        self.link()
        for key, value in (('PCOUNT', 1), ('GCOUNT', 2)):
            with self.subTest(key=key):
                self.write_mask()
                with fits.open(self.source) as hdus:
                    offset = hdus.fileinfo(1)['hdrLoc'] + 80 * hdus[1].header.index(key)
                raw = bytearray(self.source.read_bytes())
                raw[offset:offset+80] = fits.Card(key, value).image.encode('ascii')
                self.source.write_bytes(raw)
                with self.assertRaisesRegex(ValueError, key):
                    reduction.check_mef_bpm(self.work, self.instrument)

    def test_existing_source_creates_link_without_changing_mask(self):
        self.write_mask()
        before = self.source.read_bytes()
        self.link()
        self.assertTrue(self.local.is_symlink())
        self.assertEqual(self.local.resolve(), self.source)
        self.assertTrue(reduction.check_mef_bpm(self.work, self.instrument))
        self.assertEqual(before, self.source.read_bytes())

    def test_staging_link_is_preserved_but_fails_until_source_exists(self):
        self.link()
        target = os.readlink(self.local)
        self.link()
        self.assertEqual(os.readlink(self.local), target)
        with self.assertRaisesRegex(FileNotFoundError, 'broken link'):
            reduction.check_mef_bpm(self.work, self.instrument)
        self.write_mask()
        self.link()
        self.assertTrue(reduction.check_mef_bpm(self.work, self.instrument))

    def test_conflicting_file_or_link_is_not_replaced(self):
        for kind in ('file', 'link'):
            with self.subTest(kind=kind):
                if kind == 'file':
                    self.local.write_bytes(b'preserve this file')
                else:
                    self.local.symlink_to(self.root / 'different-mask.fits')
                with self.assertRaises(FileExistsError):
                    self.link()
                if kind == 'file':
                    self.assertEqual(self.local.read_bytes(), b'preserve this file')
                else:
                    self.assertEqual(os.readlink(self.local), str(self.root / 'different-mask.fits'))
                self.local.unlink()

    def test_missing_partition_and_missing_mask_fail_clearly(self):
        self.tree.bpm_partitions = []
        with self.assertRaisesRegex(ValueError, 'No BPM partition'):
            self.link()
        with self.assertRaises(FileNotFoundError):
            reduction.check_mef_bpm(self.work, self.instrument)

    def test_invalid_mef_layouts_are_rejected(self):
        self.link()
        cases = [
            (('CCD_A',), np.uint8, (3, 4)),
            (('CCD_A', 'CCD_A'), np.uint8, (3, 4)),
            (('CCD_A', 'UNKNOWN'), np.uint8, (3, 4)),
            (('', 'CCD_B'), np.uint8, (3, 4)),
            (('CCD_A', 'CCD_B'), np.float32, (3, 4)),
            (('CCD_A', 'CCD_B'), np.uint8, (3,)),
        ]
        for names, dtype, shape in cases:
            with self.subTest(names=names, dtype=dtype, shape=shape):
                self.write_mask(names, dtype, shape)
                with self.assertRaisesRegex(ValueError, 'Invalid MEF BPM'):
                    reduction.check_mef_bpm(self.work, self.instrument)
        self.source.write_text('not a FITS file')
        with self.assertRaisesRegex(ValueError, 'Invalid MEF BPM'):
            reduction.check_mef_bpm(self.work, self.instrument)

    def test_primary_image_and_table_extensions_are_rejected(self):
        self.link()
        for hdus in (
            [fits.PrimaryHDU(np.ones((3, 4), dtype=np.uint8)),
             fits.ImageHDU(np.ones((3, 4), dtype=np.uint8), name='CCD_A'),
             fits.ImageHDU(np.ones((3, 4), dtype=np.uint8), name='CCD_B')],
            [fits.PrimaryHDU(), fits.BinTableHDU(name='CCD_A'),
             fits.BinTableHDU(name='CCD_B')],
        ):
            with self.subTest(types=[type(h).__name__ for h in hdus]):
                fits.HDUList(hdus).writeto(self.source, overwrite=True)
                with self.assertRaises(ValueError):
                    reduction.check_mef_bpm(self.work, self.instrument)

    def test_all_reduction_stages_stop_before_launch_on_missing_mef(self):
        # Split files must not satisfy the MEF preflight.
        for i in (1, 2):
            fits.PrimaryHDU(np.ones((3, 4), dtype=np.uint8)).writeto(
                self.work / f'OCAM_BPM_{i:02d}.fits')
        (self.work / 'mefpp.paf').write_text('disposable test configuration')
        for stage in ('bias', 'dome', 'sky', 'science'):
            with self.subTest(stage=stage), patch.object(reduction, 'run_commands') as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(FileNotFoundError):
                        getattr(reduction, 'mefpp_reduce_' + stage)(
                            str(self.root), [self.part], self.instrument)
                run.assert_not_called()

    def test_all_stages_accept_mef_without_split_files(self):
        self.write_mask()
        self.link()
        (self.work / 'mefpp.paf').write_text('disposable test configuration')
        for name in ('bias.list', 'dome.list', 'sky.list', 'science.list',
                     'OCAM_DOMEFF_r_SDSS_1x1.fits', 'OCAM_MFF_r_SDSS_1x1.fits'):
            (self.work / name).touch()
        for stage in ('bias', 'dome', 'sky', 'science'):
            master = self.work / 'OCAM_MB_1x1.fits'
            if stage != 'bias':
                master.touch()
            dome = self.work / 'OCAM_DOMEFF_r_SDSS_1x1.fits'
            if stage == 'dome':
                dome.unlink()
            elif stage == 'sky':
                dome.touch()
            with self.subTest(stage=stage), patch.object(reduction, 'run_commands', return_value=0) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    getattr(reduction, 'mefpp_reduce_' + stage)(
                        str(self.root), [self.part], self.instrument)
                run.assert_called_once()


if __name__ == '__main__':
    unittest.main(verbosity=2)
