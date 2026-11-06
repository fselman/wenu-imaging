"""Synthetic FITS tests of the actual native qfits-backed assembler; no recipe.

Build only qfits and the assembler/probe directly. Do not install anything.
The generated platform header uses the same fields as the CMake template and
the running host ABI; the assembler requires the selected LP64 representation.
Optional --astropy-python adds independent real Astropy FITS verification.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORK = PROBE = ARGS = None
ASTROPY_CHECKS = 0

def card(key, value=None):
    return ((key.ljust(8) + '= ' + str(value)) if value is not None else key).ljust(80).encode('ascii')

def header(cards):
    b = b''.join(cards + [card('END')])
    return b + b' ' * (-len(b) % 2880)

def fixture(path, index, bitpix=-32, width=3, height=2, scale=1, zero=0, extra_cards=0):
    primary = header([card('SIMPLE', 'T'), card('BITPIX', 8), card('NAXIS', 0),
        card('EXTEND', 'T'), card('NEXTEND', 1), card('ORIGFILE', "'temporary.fits'"),
        card('INSTRUME', "'TESTCAM'"), card('RDNOISE', str(index + 0.25)),
        card('GAIN', str(index + 1.5)), card('DATASUM', "'0'"), card('CHECKSUM', "'stale-fixture'"), card('HISTORY synthetic primary')])
    ext_cards = [card('XTENSION', "'IMAGE   '"), card('BITPIX', bitpix), card('NAXIS', 2),
        card('NAXIS1', width), card('NAXIS2', height), card('PCOUNT', 0), card('GCOUNT', 1),
        card('EXTNAME', f"'CCD-{index:02d}'"), card('EXTVER', index + 100),
        card('BSCALE', scale), card('BZERO', zero), card('BUNIT', "'ADU'"),
        card('RDNOISE', str(index + 0.25)), card('GAIN', str(index + 1.5)),
        card('ORIGFILE', "'temporary.fits'"), card('CHECKSUM', "'stale-fixture'"),
        card('HISTORY synthetic extension')]
    # Exact stored bytes, including negative zero and a NaN payload. No estimator.
    patterns = {-32: bytes.fromhex('800000007fc123453f800000bf80000041200000c1200000'),
                -64: struct.pack('>6Q', 0x8000000000000000, 0x7ff8123456789abc, 0, 1, 2, 3),
                16: struct.pack('>6h', -32768, -17, 0, 1, 42, 32767)}
    data = patterns[bitpix]
    assert width * height == 6
    padded = data + b'\0' * (-len(data) % 2880)
    checksum = sum(struct.unpack('>'+str(len(padded)//4)+'I', padded))
    while checksum >> 32: checksum = (checksum & 0xffffffff) + (checksum >> 32)
    ext = header(ext_cards + [card('DATASUM', f"'{checksum}'")] +
                 [card(f'HIERARCH TEST QC V{i:05d}', i) for i in range(extra_cards)])
    path.write_bytes(primary + ext + padded)
    return [str(path), f'CCD-{index:02d}', str(index * 3 + 2), str(index + 1),
            str(width), str(height), str(bitpix), str(scale), str(zero)]

def hdus(path):
    """Small independent test-fixture reader; not production FITS ingestion."""
    raw = path.read_bytes(); pos = 0; result = []
    while pos < len(raw):
        cards = []; values = {}; start = pos
        while True:
            c = raw[pos:pos+80]; assert len(c) == 80; pos += 80
            key = c[:8].decode().strip()
            if key == 'END': break
            cards.append(c)
            if c[8:10] == b'= ':
                value = c[10:].decode().split('/')[0].strip()
                values[key] = value.strip("'").strip()
        pos = start + ((pos-start+2879)//2880)*2880
        size = 0
        if int(values['NAXIS']):
            size = abs(int(values['BITPIX']))//8
            for i in range(1, int(values['NAXIS'])+1): size *= int(values[f'NAXIS{i}'])
        padded = ((size+2879)//2880)*2880
        assert pos+padded <= len(raw)
        result.append((cards, values, raw[pos:pos+padded])); pos += padded
    assert pos == len(raw)
    return result

class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='assembly-', dir=WORK)
        self.addCleanup(self.temp.cleanup); self.base = Path(self.temp.name).resolve()
        self.output = self.base/'CMDP.2026-11-06T16:00:00.123Z.001.fits'
        self.members = [fixture(self.base/f'detector-{i}.fits', i) for i in range(2)]

    def execute(self, members=None, reference='CCD-01', output=None):
        members = self.members if members is None else members
        frozen = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in self.base.glob('detector-*.fits')}
        argv = [str(PROBE), str(output or self.output), reference] + [v for row in members for v in row]
        r = subprocess.run(argv, capture_output=True, text=True)
        self.assertEqual(frozen, {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in frozen})
        self.assertFalse(list(self.base.glob('*.assembling-*')))
        return r

    def verify(self, members, reference=1):
        global ASTROPY_CHECKS
        out = hdus(self.output); self.assertEqual(len(out), len(members)+1)
        self.assertEqual(out[0][1]['NEXTEND'], str(len(members)))
        source = hdus(Path(members[reference][0]))[0]
        self.assertEqual(out[0][1]['RDNOISE'], source[1]['RDNOISE'])
        self.assertEqual(out[0][1]['GAIN'], source[1]['GAIN'])
        for i, row in enumerate(members, 1):
            original = hdus(Path(row[0]))[1]
            self.assertEqual(out[i][2], original[2])
            self.assertEqual(out[i][1]['EXTNAME'], row[1])
            # Every unedited card retains exact original bytes and ordering.
            kept = lambda cards: [c for c in cards if c[:8].strip() not in (b'ORIGFILE', b'CHECKSUM', b'NEXTEND')]
            self.assertEqual(kept(out[i][0]), kept(original[0]))
        for _, values, _ in out:
            self.assertEqual(values['ORIGFILE'], self.output.name)
            self.assertNotIn('CHECKSUM', values)
        if ARGS.astropy_python:
            # Real independent FITS structural/value read, with scaling disabled.
            code = '''from astropy.io import fits
import numpy as np, sys
with fits.open(sys.argv[1], mode='readonly', do_not_scale_image_data=True, memmap=False) as out:
 out.verify('exception')
 assert len(out)==len(sys.argv)-1
 assert out[0].verify_datasum()==1
 for i,path in enumerate(sys.argv[2:],1):
  with fits.open(path, mode='readonly', do_not_scale_image_data=True, memmap=False) as src:
   src.verify('exception')
   assert out[i].verify_datasum()==1 and src[1].verify_datasum()==1
   assert out[i].data.dtype==src[1].data.dtype
   assert out[i].data.tobytes()==src[1].data.tobytes()
   assert out[i].header['EXTNAME']==src[1].header['EXTNAME']
'''
            r = subprocess.run([str(ARGS.astropy_python), '-B', '-c', code, str(self.output)] +
                               [row[0] for row in members], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout+r.stderr); ASTROPY_CHECKS += 1

    def test_exact_pixels_headers_reference_and_cwd(self):
        before = Path.cwd(); r = self.execute(); self.assertEqual(r.returncode, 0, r.stderr)
        self.verify(self.members); self.assertEqual(Path.cwd(), before)

    def test_all_32_detectors(self):
        members = [fixture(self.base/f'detector-{i}.fits', i) for i in range(32)]
        r = self.execute(members); self.assertEqual(r.returncode, 0, r.stderr); self.verify(members)

    def test_expanded_headers_32_exceed_old_aggregate_limit(self):
        members = [fixture(self.base/f'detector-{i}.fits', i, extra_cards=2880)
                   for i in range(32)]
        header_bytes = sum(len(Path(row[0]).read_bytes())-2880-2880 for row in members)
        self.assertGreater(header_bytes, 7_000_000)
        self.assertLess(len(Path(members[0][0]).read_bytes())-2880, 1048576)
        r = self.execute(members)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.verify(members)

    def test_individual_header_bound_remains_enforced(self):
        self.members[0] = fixture(Path(self.members[0][0]), 0, extra_cards=14000)
        r = self.execute()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertFalse(self.output.exists())

    def test_integer_scaling_double_pixels_and_unequal_shapes(self):
        self.members[0] = fixture(Path(self.members[0][0]), 0, 16, 2, 3, 2, 32768)
        self.members[1] = fixture(Path(self.members[1][0]), 1, -64, 6, 1)
        r = self.execute(); self.assertEqual(r.returncode, 0, r.stderr); self.verify(self.members)

    def test_bad_manifest_and_detector_contracts(self):
        cases = [(0,1,'CCD-99'), (1,1,'CCD-00'), (1,2,self.members[0][2]),
                 (1,3,'1'), (0,4,'4'), (0,5,'0'), (0,6,'-64'), (0,7,'2'), (0,8,'1'),
                 (0,4,'2147483647'), (0,7,'nan')]
        for i,j,value in cases:
            with self.subTest(field=j,value=value):
                members = [list(x) for x in self.members]; members[i][j] = value
                r = self.execute(members); self.assertEqual(r.returncode, 1, r.stderr)
                self.assertFalse(self.output.exists())
        r = self.execute(reference='unknown'); self.assertEqual(r.returncode, 1)

    def test_missing_member_and_truncated_data(self):
        p = Path(self.members[0][0]); saved = p.read_bytes(); p.unlink()
        r = self.execute(); self.assertEqual(r.returncode, 1); self.assertFalse(self.output.exists())
        p.write_bytes(saved[:-1])
        r = self.execute(); self.assertEqual(r.returncode, 1); self.assertFalse(self.output.exists())

    def test_extra_extension_and_primary_pixels_refused(self):
        p = Path(self.members[0][0]); saved = p.read_bytes()
        p.write_bytes(saved+saved[2880:])
        r = self.execute(); self.assertEqual(r.returncode, 1); self.assertFalse(self.output.exists())
        p.write_bytes(saved.replace(card('NAXIS',0), card('NAXIS',1), 1))
        r = self.execute(); self.assertEqual(r.returncode, 1); self.assertFalse(self.output.exists())

    def test_existing_file_and_dangling_link_preserved(self):
        self.output.write_bytes(b'protected product')
        r = self.execute(); self.assertEqual(r.returncode, 1)
        self.assertEqual(self.output.read_bytes(), b'protected product'); self.output.unlink()
        self.output.symlink_to(self.base/'missing')
        r = self.execute(); self.assertEqual(r.returncode, 1); self.assertTrue(self.output.is_symlink())

    def test_missing_parent_and_unrepresentable_basename(self):
        for output in (self.base/'absent'/'product.fits', self.base/('x'*70+'.fits')):
            r = self.execute(output=output); self.assertEqual(r.returncode, 1); self.assertFalse(output.exists())

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--work', type=Path, required=True)
    p.add_argument('--cc', type=Path); p.add_argument('--probe', type=Path);
    p.add_argument('--expanded-only', action='store_true'); p.add_argument('--sdkroot', type=Path)
    p.add_argument('--astropy-python', type=Path); ARGS = p.parse_args()
    WORK = ARGS.work.resolve(strict=True); PROBE = WORK/'mef-assembly-probe'
    if not ARGS.probe and not ARGS.cc: p.error('Select existing --probe or explicit --cc')
    if not ARGS.probe and sys.platform == 'darwin' and not ARGS.sdkroot: p.error('Darwin requires explicit --sdkroot')
    argv = None
    if ARGS.probe:
        PROBE = ARGS.probe.resolve(strict=True)
    else:
        common = ROOT/'mefpp2/ins/mef/common'; qfits = ROOT/'mefpp2/qfits5'
        # Generate only the existing platform fields from the selected host ABI.
        names = ('char','short','int','long','float','double')
        config = '#ifndef QFITS_PLATFORM_CONFIG_H\n#define QFITS_PLATFORM_CONFIG_H\n'
        config += ''.join(f'#define SIZEOF_{n.upper()} {ctypes.sizeof(getattr(ctypes,"c_"+n))}\n' for n in names)
        config += '#define OS_DARWIN 1\n' if sys.platform == 'darwin' else '#define OS_LINUX 1\n'
        if sys.byteorder == 'big': config += '#define WORDS_BIGENDIAN 1\n'
        (WORK/'qfits_platform_config.h').write_text(config+'#endif\n')
        flags = ['-std=c17','-Wall','-Wextra','-D_DEFAULT_SOURCE=1','-D_DARWIN_C_SOURCE=1',
                 '-I'+str(common),'-I'+str(qfits/'include'),'-I'+str(WORK)]
        if ARGS.sdkroot: flags += ['-isysroot',str(ARGS.sdkroot.resolve(strict=True))]
        # Strict new-code inspection, then link actual in-tree qfits (no mock library).
        new = [str(common/'mef_mef_assemble.c'),str(ROOT/'mefpp2/tests/mef_assembly_probe.c')]
        subprocess.run([str(ARGS.cc),*flags,'-Werror','-pedantic-errors','-fsyntax-only',*new],check=True)
        sources = re.findall(r'qfits5/src/[\w-]+\.c', (ROOT/'mefpp2/cmake/QfitsSources.cmake').read_text())
        argv = [str(ARGS.cc),*flags,'-DXMEMORY_MODE=2','-DXMEMORY_MAXPTRS=2000000',*new,
                *[str(ROOT/'mefpp2'/s) for s in sources],'-lm','-o',str(PROBE)]
        print('BUILD:', json.dumps(argv), flush=True); subprocess.run(argv,check=True)
    # Actual assembler: known-answer FITS copy, identity/coverage/header/refusal controls.
    suite = unittest.TestSuite(AssemblyTests(name) for name in (
        'test_expanded_headers_32_exceed_old_aggregate_limit',
        'test_individual_header_bound_remains_enforced',
    )) if ARGS.expanded_only else unittest.defaultTestLoader.loadTestsFromTestCase(AssemblyTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (WORK/'mef-assembly-results.json').write_text(json.dumps(dict(tests=result.testsRun,
        successful=result.wasSuccessful(),astropy_checks=ASTROPY_CHECKS,build_argv=argv,probe=str(PROBE),
        observations_opened=False,bias_recipe_executed=False,pycavi_used=False))+'\n')
    raise SystemExit(not result.wasSuccessful())
