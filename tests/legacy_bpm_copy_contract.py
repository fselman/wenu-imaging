"""Independent stored-byte and refusal controls for the explicit BPM derivative (#232)."""
import hashlib
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bpm_copy', ROOT/'tools/prepare-legacy-bpm-copy.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def header(cards):
    text = ''.join((f'{key:<8}= {value:>20}').ljust(80) for key,value in cards)+'END'.ljust(80)
    return text.encode('ascii').ljust(((len(text)+2879)//2880)*2880,b' ')


def fixture(path, *, conflict=False, duplicate=False, full=False):
    content = header([('SIMPLE','T'),('BITPIX','8'),('NAXIS','0'),('EXTEND','T')])
    for identity in ('ESO_CCD_#65','ESO_CCD_#66'):
        cards = [('XTENSION',"'IMAGE   '"),('BITPIX','8'),('NAXIS','2'),
                 ('NAXIS1','3'),('NAXIS2','2')]
        if conflict or full:
            cards += [('PCOUNT','1' if conflict else '0'),('GCOUNT','1')]
        cards += [('EXTNAME',repr(identity)),('ORIGFILE',"'legacy.fits'"),('DATASUM',"'opaque'")]
        if duplicate:
            cards += [('EXTNAME',repr(identity))]
        # Deliberately nonzero padding: prove exact stored bytes, not only pixel equality.
        content += header(cards)+struct.pack('6B',0,1,1,0,1,0)+b'P'*(2880-6)
    path.write_bytes(content)


class CopyContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.source = self.directory/'source.fits'
        self.output = self.directory/'copy.fits'
        self.expected = {'ESO_CCD_#65':[3,2],'ESO_CCD_#66':[3,2]}

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_cards_exact_bytes_and_metadata(self):
        from astropy.io import fits
        fixture(self.source)
        frozen = self.source.read_bytes()
        result = module.prepare(self.source,self.output,self.expected)
        self.assertEqual(result['added_card_count'],4)
        self.assertEqual(self.source.read_bytes(),frozen)
        self.assertTrue(result['payload_preservation'] and result['existing_cards_preservation'])
        with fits.open(self.output) as hdus:
            hdus.verify('exception')
            for i,hdu in enumerate(hdus[1:],1):
                self.assertEqual(hdu.header['PCOUNT'],0)
                self.assertEqual(hdu.header['GCOUNT'],1)
                info = hdu.fileinfo()
                raw = self.output.read_bytes()[info['datLoc']:info['datLoc']+info['datSpan']]
                self.assertEqual(raw,frozen[(2*i)*2880:(2*i+1)*2880])
        self.assertEqual(result['original_sha256'],hashlib.sha256(frozen).hexdigest())

    def test_standard_headers_preserved(self):
        fixture(self.source,full=True)
        result = module.prepare(self.source,self.output,self.expected)
        self.assertEqual(result['added_card_count'],0)
        self.assertEqual(self.source.read_bytes(),self.output.read_bytes())

    def test_conflicting_existing_card_refused(self):
        fixture(self.source,conflict=True)
        frozen = self.source.read_bytes()
        with self.assertRaises((ValueError,OSError)):
            module.prepare(self.source,self.output,self.expected)
        self.assertEqual(self.source.read_bytes(),frozen)
        self.assertFalse(self.output.exists())

    def test_duplicate_identity_card_refused(self):
        fixture(self.source,duplicate=True)
        with self.assertRaises(ValueError):
            module.prepare(self.source,self.output,self.expected)
        self.assertFalse(self.output.exists())

    def test_incorrect_detector_set_refused(self):
        fixture(self.source)
        with self.assertRaises(ValueError):
            module.prepare(self.source,self.output,{'unknown':[3,2],'ESO_CCD_#66':[3,2]})
        self.assertFalse(self.output.exists())

    def test_recorded_source_hash_required_to_match(self):
        fixture(self.source)
        with self.assertRaises(ValueError):
            module.prepare(self.source,self.output,self.expected,'0'*64)
        self.assertFalse(self.output.exists())

    def test_existing_output_preserved(self):
        fixture(self.source)
        self.output.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            module.prepare(self.source,self.output,self.expected)
        self.assertEqual(self.output.read_bytes(),b'keep')


if __name__ == '__main__':
    unittest.main()
