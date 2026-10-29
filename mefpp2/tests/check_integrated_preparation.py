"""Python-only positive/negative controls for the integrated fixture/product reader.

Constructed products check the reader, not native numerical or memory acceptance.
"""
from pathlib import Path
import tempfile
import numpy as np
from astropy.io import fits
from prepare_integrated_campaign_fixture import prepare
from integrated_campaign_products import verify,CATEGORIES
from qualify_integrated_campaign_mac import comparable


def main():
    repo=Path(__file__).resolve().parents[2]
    with tempfile.TemporaryDirectory(prefix='integrated-reader-controls-') as temp:
        root=Path(temp)/'fixture'
        # Fixture contract: seventeen preserved raw inputs and independent expectations.
        record=prepare(root,repo)
        assert sum(record['frame_counts'].values())==17
        for p in root.glob('*[0-9].fits'):
            with fits.open(p) as hdus:
                assert hdus[0].header['ORIGFILE']==p.name
                assert len(hdus)==3
        ids={cat:'CONTROL.%d.fits'%i for i,cat in enumerate(CATEGORIES)}
        def write_products(prefix):
            for i,(cat,kind) in enumerate(CATEGORIES.items()):
                primary=fits.Header({'PRODCATG':cat,'ORIGFILE':prefix+ids[cat]})
                primary['MBIAS']=prefix+ids['CALIB.MASTER_BIAS']
                hdus=[fits.PrimaryHDU(header=primary)]
                for xt in (1,2):
                    header=fits.Header({'EXTNAME':'F1_CCD_A' if xt==1 else 'F1_CCD_B'})
                    if cat=='CALIB.BPM':header['ORIGFILE']=prefix+ids[cat]
                    hdus.append(fits.ImageHDU(np.load(root/f'expected-{kind}-{xt}.npy'),header))
                fits.HDUList(hdus).writeto(root/f'product-{i}.fits',overwrite=True)
        # Positive controls: exact products, detector order, generated IDs/references only.
        write_products('A.')
        original=verify(root,record['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
        write_products('B.')
        changed_ids=verify(root,record['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
        assert comparable(original)==comparable(changed_ids)
        # Negative controls: a changed scientific card must remain visible to comparison.
        with fits.open(root/'product-0.fits',mode='update') as hdus:hdus[1].header['FILTER']='CHANGED'
        changed=verify(root,record['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
        assert comparable(original)!=comparable(changed)
        # Negative control: changed pixel must fail the independent known-answer check.
        with fits.open(root/'product-0.fits',mode='update') as hdus:hdus[1].data[0,0]=7
        try:verify(root,record['input_sha256'],2,True)
        except RuntimeError as error:assert 'Known-answer' in str(error)
        else:raise AssertionError('Pixel corruption accepted')
        write_products('C.')
        # Negative control: swapped detector labels must fail even with matching arrays.
        try:verify(root,record['input_sha256'],2,True,['F1_CCD_B','F1_CCD_A'])
        except RuntimeError as error:assert 'Detector order' in str(error)
        else:raise AssertionError('Detector swap accepted')
    print('Preparation controls passed; native engine launches: 0')


if __name__=='__main__':main()
