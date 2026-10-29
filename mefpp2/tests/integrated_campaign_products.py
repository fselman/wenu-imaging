"""Exact integrated output oracle; generated provenance IDs are mapped by product role."""
import hashlib,json
from pathlib import Path
import numpy as np
from astropy.io import fits

CATEGORIES = {'CALIB.MASTER_BIAS':'bias','CALIB.BPM':'bpm',
              'CALIB.MASTER_DOME_FLAT':'flat','CALIB.MASTER_SKY_FLAT':'flat',
              'CALIB.MASTER_FLAT':'flat','SCIENCE.MEFIMAGE':'science'}


def file_hash(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def verify(root, inputs, detectors, tiny, extension_names=None):
    # Input preservation and complete expected product set.
    for name,h in inputs.items():
        if file_hash(root/name)!=h:
            raise RuntimeError('Staged input changed: '+name)
    products=[p for p in sorted(root.glob('*.fits')) if p.name not in inputs]
    if len(products)!=6:raise RuntimeError('Expected exactly six integrated FITS products; found '+str(len(products)))
    found={};ids={};details={}
    for path in products:
        with fits.open(path,memmap=False) as hdus:
            category=hdus[0].header.get('PRODCATG')
            if category not in CATEGORIES or category in found:
                raise RuntimeError('Missing/duplicate/unexpected category: '+str(category))
            if len(hdus)!=detectors+1 or hdus[0].data is not None:
                raise RuntimeError('Unexpected output primary/extension count: '+path.name)
            orig=hdus[0].header.get('ORIGFILE')
            if not isinstance(orig,str) or not orig or orig in ids:
                raise RuntimeError('Missing/duplicate generated product identity')
            ids[orig]=category;found[category]=path.name
            details[category]=dict(name=path.name,extension_names=[],pixels=[],headers=[])
            for xt,hdu in enumerate(hdus):
                # The recipe publishes ORIGFILE on primaries; only BPM repeats it
                # in extensions. Preserve other extension cards exactly as written.
                if category=='CALIB.BPM' and hdu.header.get('ORIGFILE')!=orig:
                    raise RuntimeError('BPM generated identity differs between HDUs')
                if xt:
                    data=hdu.data
                    if data is None or data.ndim!=2:raise RuntimeError('Missing two-dimensional product array')
                    kind=CATEGORIES[category]
                    if tiny:
                        expected=np.load(root/('expected-%s-%d.npy'%(kind,xt)))
                        if data.shape!=(9,9) or not np.array_equal(data,expected):
                            raise RuntimeError('Known-answer array differs: '+category+' extension '+str(xt))
                    if category=='CALIB.BPM' and (hdu.header['BITPIX']!=8 or not np.isin(data,[0,1]).all()):
                        raise RuntimeError('Mask storage/polarity changed')
                    physical=np.asarray(data,dtype='>f8')
                    # NaN/inf positions are retained, not replaced or silently removed.
                    details[category]['pixels'].append(dict(shape=list(data.shape),bitpix=hdu.header['BITPIX'],
                        sha256=hashlib.sha256(physical.tobytes()).hexdigest(),nonfinite=int((~np.isfinite(physical)).sum())))
                    details[category]['extension_names'].append(hdu.header.get('EXTNAME'))
                details[category]['headers'].append([(c.keyword,c.value,c.comment,c.image) for c in hdu.header.cards])
    if extension_names is not None:
        for category,item in details.items():
            if item['extension_names']!=extension_names:
                raise RuntimeError('Detector order differs: '+category)
    if set(found)!=set(CATEGORIES):raise RuntimeError('Incomplete integrated output categories')
    # Only generated product IDs are canonicalized, consistently across all references.
    # All unaffected cards remain byte-exact, including ordering and commentary.
    for category,item in details.items():
        canonical=[]
        for cards in item['headers']:
            current=[]
            for keyword,value,comment,raw in cards:
                if isinstance(value,str) and value in ids:
                    current.append(fits.Card(keyword,'@GENERATED:'+ids[value],comment).image)
                else:current.append(raw)
            canonical.append(current)
        item['canonical_headers_sha256']=hashlib.sha256(json.dumps(canonical,ensure_ascii=True).encode()).hexdigest()
        del item['headers']
    return details
