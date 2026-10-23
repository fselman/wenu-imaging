"""Metadata boundary regressions; no native engines or observational data."""
import hashlib
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import numpy as np
from astropy.io import fits
from astropy.time import Time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Pycavi2'))
from pycavi.pycavi.pycavi_metadata import (
    science_exposure_header, detector_science_header,
    copy_science_metadata, coadd_observation_metadata,
)


class ScienceMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)

    def primary(self, start=57823.093557795, exposure=80.):
        return fits.Header({'DATE-OBS': '2017-03-11T02:14:43.393',
                            'MJD-OBS': start, 'MJD-END': 57823.09375,
                            'EXPTIME': exposure, 'BUNIT': 'e-/s',
                            'SATLEVEL': 1759.4343046875, 'ONEADU': .02684765625,
                            'OBJECT': 'CN Ori', 'FILTER': 'r_SDSS', 'ORIGIN': 'ESO-PARANAL'})

    def make_mef(self, path, start=57823.093557795, exposure=80., unsigned=False):
        hdus = [fits.PrimaryHDU(header=self.primary(start, exposure))]
        for i, name in enumerate(('CCD_B', 'CCD_A')):
            header = fits.Header({'EXTNAME': name, 'DATE-OBS': '2017-03-13T23:14:56.158',
                                  'MJD-OBS': 57825.968705542, 'GAIN': 2. + i,
                                  'CTYPE1': 'RA---TAN', 'CTYPE2': 'DEC--TAN',
                                  'CRVAL1': 88., 'CRVAL2': -5., 'CRPIX1': 2., 'CRPIX2': 2.,
                                  'CD1_1': -.0001, 'CD2_2': .0001})
            data = np.arange(20).reshape(4, 5).astype(np.uint16 if unsigned else np.float32)
            hdus.append(fits.ImageHDU(data=data+i, header=header))
        fits.HDUList(hdus).writeto(path, checksum=True)
        return path

    def test_double_precision_endpoint_preserves_short_exposure(self):
        for exposure in (.948, 80., 480.):
            primary = self.primary(exposure=exposure)
            updated = science_exposure_header(primary)
            self.assertLess(abs((updated['MJD-END']-updated['MJD-OBS'])*86400-exposure), 1e-6)
            self.assertEqual(primary['MJD-END'], 57823.09375)
        for value in (float('nan'), float('inf'), 0., -1.):
            with self.assertRaises(ValueError):
                science_exposure_header(self.primary(exposure=value))

    def test_utc_endpoint_handles_leap_second(self):
        start = Time('2016-12-31T23:59:59', scale='utc')
        header = self.primary(start=float(start.mjd), exposure=3.)
        header['DATE-OBS'] = start.isot
        result = science_exposure_header(header)
        end = Time(result['MJD-END'], format='mjd', scale='utc')
        self.assertLess(abs((end-start).sec-3.), 1e-6)

    def test_detector_overlay_keeps_wcs_identity_and_detector_gain(self):
        detector = fits.Header({'EXTNAME': 'CCD_A', 'CRVAL1': 42., 'GAIN': 2.1,
                                'MJD-OBS': 57825.9687, 'DATE-OBS': 'flat date'})
        result = detector_science_header(detector, self.primary())
        self.assertEqual(result['EXTNAME'], 'CCD_A')
        self.assertEqual(result['CRVAL1'], 42.)
        self.assertEqual(result['GAIN'], 2.1)
        for key in ('MJD-OBS', 'DATE-OBS', 'EXPTIME', 'BUNIT', 'SATLEVEL', 'ONEADU'):
            self.assertEqual(result[key], self.primary()[key])
        self.assertEqual(detector['DATE-OBS'], 'flat date')

    def test_fresh_copy_preserves_pixels_storage_wcs_and_input(self):
        for unsigned in (False, True):
            source = self.make_mef(self.work / ('in%d.fits' % unsigned), unsigned=unsigned)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            destination = self.work / ('out%d.fits' % unsigned)
            copy_science_metadata(source, destination)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)
            with fits.open(source, do_not_scale_image_data=True) as a, fits.open(destination, do_not_scale_image_data=True, checksum=True) as b:
                for i in range(1, 3):
                    np.testing.assert_array_equal(a[i].data, b[i].data)
                    self.assertEqual(a[i].data.dtype, b[i].data.dtype)
                    for key in ('EXTNAME', 'GAIN', 'CRVAL1', 'CD1_1', 'BZERO', 'BSCALE'):
                        self.assertEqual(a[i].header.get(key), b[i].header.get(key))
                    self.assertEqual(b[i].header['EXPTIME'], 80.)
                    self.assertEqual(b[i].header['BUNIT'], 'e-/s')
                    self.assertEqual(b[i].header['MJD-OBS'], b[0].header['MJD-OBS'])
                for hdu in b:
                    self.assertEqual(hdu.verify_checksum(), 1)
            existing = destination.read_bytes()
            with self.assertRaises(FileExistsError):
                copy_science_metadata(source, destination)
            self.assertEqual(destination.read_bytes(), existing)

    def test_invalid_input_does_not_publish_partial_copy(self):
        source = self.make_mef(self.work / 'input.fits')
        with fits.open(source, mode='update') as hdus:
            hdus[0].header['EXPTIME'] = -1.
        output = self.work / 'output.fits'
        with self.assertRaises(ValueError):
            copy_science_metadata(source, output)
        self.assertFalse(output.exists())
        self.assertFalse(list(self.work.glob('.pycavi-metadata-*')))

    def test_coadd_uses_all_exposures_not_detector_count_or_order(self):
        a = self.make_mef(self.work / 'a.fits')
        b = self.make_mef(self.work / 'b.fits', start=57823.1, exposure=120.)
        result = coadd_observation_metadata([b, a])
        self.assertEqual(result['TEXPTIME'], 200.)
        self.assertEqual(result['NCOMBINE'], 2)
        self.assertEqual(result['MJD-OBS'], self.primary()['MJD-OBS'])
        self.assertAlmostEqual(result['MJD-END'], 57823.1 + 120./86400, places=10)
        self.assertNotIn('EXPTIME', result)
        self.assertNotIn('GAIN', result)
        for paths in ([], [a, a]):
            with self.assertRaises(ValueError):
                coadd_observation_metadata(paths)
        with fits.open(b, mode='update') as hdus:
            hdus[0].header['FILTER'] = 'NB_659'
        with self.assertRaisesRegex(ValueError, 'FILTER'):
            coadd_observation_metadata([a, b])

    def test_coadd_update_keeps_native_equivalent_exposure_gain_and_weight_units(self):
        from pycavi.pycavi import pycavi_astromatic_tools as tools
        inputs = [self.make_mef(self.work / 'a.fits'),
                  self.make_mef(self.work / 'b.fits', start=57823.1)]
        for weight in (False, True):
            output = self.work / ('weight.fits' if weight else 'science.fits')
            fits.writeto(output, np.ones((3, 4), dtype=np.float32),
                         fits.Header({'EXPTIME': 160., 'GAIN': 1.59,
                                      'CRVAL1': 88., 'CRVAL2': -5.}), checksum=True)
            tools.update_headers(output, inputs[0], inputs, weight_map=weight)
            with fits.open(output, checksum=True) as hdus:
                header = hdus[0].header
                self.assertEqual(header['EXPTIME'], 160.)
                self.assertEqual(header['GAIN'], 1.59)
                self.assertEqual(header['TEXPTIME'], 160.)
                self.assertEqual(header['NCOMBINE'], 2)
                self.assertEqual('BUNIT' in header, not weight)
                self.assertEqual(hdus[0].verify_checksum(), 1)
                np.testing.assert_array_equal(hdus[0].data, np.ones((3, 4)))

    def test_swarp_runner_uses_entire_list_including_last_line_without_newline(self):
        from pycavi.pycavi import pycavi_astromatic_tools as tools
        inputs = [self.make_mef(self.work / 'a.fits'),
                  self.make_mef(self.work / 'b.fits', start=57823.1)]
        (self.work / 'frames.list').write_text('\n'.join(map(str, inputs)))
        config = {'IMAGEOUT_NAME': 'coadd.fits', 'WEIGHTOUT_NAME': 'weight.fits'}
        wrapper = Mock(config=config)
        def native(*args, **kwargs):
            for name in config.values():
                fits.writeto(name, np.ones((2, 2)),
                             fits.Header({'CRVAL1': 88., 'CRVAL2': -5., 'EXPTIME': 160.}))
        wrapper.run.side_effect = native
        previous = Path.cwd()
        try:
            with patch.object(tools, 'SWarp', return_value=wrapper):
                tools.run_swarp(str(self.work), 'frames.list', path='/native/swarp')
        finally:
            os.chdir(previous)
        for name in config.values():
            self.assertEqual(fits.getheader(self.work / name)['NCOMBINE'], 2)
            self.assertEqual(fits.getheader(self.work / name)['TEXPTIME'], 160.)
        wrapper.run.assert_called_once_with('@frames.list', updateconfig=True,
                                            clean=False, path='/native/swarp')

    def test_invalid_coadd_does_not_launch_native_or_modify_output(self):
        from pycavi.pycavi import pycavi_astromatic_tools as tools
        (self.work / 'frames.list').write_text('missing.fits\n')
        output = self.work / 'old.fits'
        output.write_bytes(b'existing output')
        wrapper = Mock()
        previous = Path.cwd()
        try:
            with patch.object(tools, 'SWarp', return_value=wrapper):
                with self.assertRaises(FileNotFoundError):
                    tools.run_swarp(str(self.work), 'frames.list')
        finally:
            os.chdir(previous)
        wrapper.run.assert_not_called()
        self.assertEqual(output.read_bytes(), b'existing output')

    def test_extraction_and_assembly_reuse_metadata_without_solver(self):
        from pycavi.pycavi import pycavi_solve as solve
        source = self.make_mef(self.work / 'science.fits')
        instrument = SimpleNamespace(valid_ext_names=['CCD_A', 'CCD_B'])
        pool = Mock()
        with patch.object(solve.multiprocessing, 'Pool', return_value=pool):
            solve.run_solve_field(str(source.with_suffix('')), instrument, cpu_count=1)
        for name in instrument.valid_ext_names:
            directory = source.with_suffix('') / (name+'_solve_field')
            detector = directory / (name+'.fits')
            self.assertEqual(fits.getheader(detector)['EXPTIME'], 80.)
            self.assertEqual(fits.getheader(detector)['MJD-OBS'], self.primary()['MJD-OBS'])
            (directory / (name+'.wcs')).touch()
            # Simulate an existing solved file with a changed WCS, never call solve-field.
            with fits.open(detector) as hdus:
                hdus[0].header['CRVAL1'] = 89.
                hdus.writeto(directory / (name+'_newwcs.fits'))
        previous = Path.cwd()
        try:
            os.chdir(self.work)
            solve.create_wcs_frame(str(source), instrument)
        finally:
            os.chdir(previous)
        with fits.open(source.with_suffix('') / 'science_wcs.fits', checksum=True) as assembled:
            self.assertTrue(all(hdu.verify_checksum() == 1 for hdu in assembled))
            self.assertEqual([h.name for h in assembled[1:]], ['CCD_A', 'CCD_B'])
            for hdu in assembled[1:]:
                self.assertEqual(hdu.header['CRVAL1'], 89.)
                self.assertEqual(hdu.header['EXPTIME'], 80.)
                self.assertEqual(hdu.header['BUNIT'], 'e-/s')
                np.testing.assert_array_equal(hdu.data, fits.getdata(source, extname=hdu.name))


if __name__ == '__main__':
    unittest.main()
