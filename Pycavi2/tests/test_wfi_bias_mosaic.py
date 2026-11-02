"""Packaging/link checks only; no native reduction or installed environment."""
import argparse
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
from astropy.io import fits

SOURCE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(SOURCE/'Pycavi2/pycavi/pycavi'))
import pycavi_qc as qc
spec=importlib.util.spec_from_file_location('mosaic',SOURCE/'Pycavi2/tools/run_wfi_bias_mosaic.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class MosaicTests(unittest.TestCase):
    def test_pixel_preservation_order_checksums_and_links(self):
        work=Path(tempfile.mkdtemp(prefix='wfi-mosaic-',dir=WORK))
        root=work/'QC';root.mkdir()
        products=[];leaves=[]
        for i,name in enumerate(m.DETECTORS):
            product=work/('slot'+str(i+1)+'.fits')
            data=np.array([[i,-i,0.125],[1.25,1000,float('nan')]],dtype=np.float32)
            header=fits.Header();header['EXTNAME']=name
            fits.HDUList([fits.PrimaryHDU(),fits.ImageHDU(data,header=header)]).writeto(product,checksum=True)
            folder=root/('slot'+str(i+1));folder.mkdir()
            b=qc.QcRecipe(file=dict(id=str(product),filename=product.name,location=str(product),kind='product',
                sha256=m.digest(product),observed_at=None,context={},
                selectors=[dict(detector_id=name,hdu_index=1,configuration_detector=i)]),
                assessment_id='synthetic:'+name,created_at='2026-11-02T00:00:00Z',
                producer=dict(name='synthetic',version='1',source_revision='fixture'),
                operation='cal.bias',configuration_id='fixture')
            leaves.append(qc.write_record(b.seal(),folder));products.append(product)
        before=[m.digest(p) for p in products]
        destination=work/'WFI_MB_1x1.fits'
        m.assemble(products,destination,m.DETECTORS,shape=(2,3))
        self.assertEqual(before,[m.digest(p) for p in products])
        final=m.digest(destination)
        with self.assertRaises(OSError):m.assemble(products,destination,m.DETECTORS,shape=(2,3))
        self.assertEqual(final,m.digest(destination))
        with self.assertRaises(RuntimeError):m.assemble(products,work/'wrong.fits',list(reversed(m.DETECTORS)),shape=(2,3))
        self.assertFalse((work/'wrong.fits').exists())
        parent=m.publish_collection(destination,root,leaves,m.DETECTORS,'fixture:assembly')
        records=list(qc.traverse_records(parent,qc_root=root,max_records=9))
        self.assertEqual(len(records),9)
        tree=qc.read_record(parent).as_dict()
        self.assertEqual([s['detector_id'] for s in tree['file']['selectors']],m.DETECTORS)
        self.assertEqual(tree['file']['sha256'],final)
        self.assertEqual([b['source_hdu'] for b in tree['extensions']['detector_assembly']['bindings']],[1]*8)
        self.assertEqual([b['output_hdu'] for b in tree['extensions']['detector_assembly']['bindings']],list(range(1,9)))
        print('RETAINED PACKAGING TEST:',work,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args();WORK=args.work.resolve(strict=True)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MosaicTests))
    raise SystemExit(0 if result.wasSuccessful() else 1)
