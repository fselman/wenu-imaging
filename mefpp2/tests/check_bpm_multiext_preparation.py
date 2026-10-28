"""Python-only two-extension preparation. Constructed products are not native acceptance."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from astropy.io import fits
from bpm_multiext_cases import prepare, verify, expected_mask, canonical_headers
from qualify_mac_leaks import digest, save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    work = args.work.resolve()
    work.mkdir(exist_ok=False)
    fixture = repo / 'mefpp2/tests/fixtures/bpm-cleanup'
    # Provenance: retain constructed products and each rejected mutation.
    record = dict(purpose=__doc__, status='running', native_execution=False,
                  created_utc=datetime.now(timezone.utc).isoformat(), python=sys.executable,
                  tested_source=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(), dirty=True),
                  source_sha256={str(p.relative_to(repo)): digest(p) for p in sorted((repo/'mefpp2/tests').glob('*multiext*')) if p.is_file()},
                  cases=[], rejected=[], retention_roles=['preparation_evidence'])
    save(work/'run-provenance.json', record)
    protected = json.loads((fixture/'manifest.json').read_text())['files']
    declared = json.loads((repo/'mefpp2/tests/fixtures/bpm-multiext/manifest.json').read_text())
    reference = json.loads((repo/'docs/developer/fixtures/mac-bpm-cleanup-2026-10-27/run-provenance.json').read_text())
    reference = {c['case']: c for c in reference['cases']}
    metadata = json.loads((repo/'docs/developer/fixtures/mac-stage2-bpm-metadata-2026-10-27/run-provenance.json').read_text())
    cases = {c['case']: c for c in metadata['cases']}
    try:
        # Input readback: exact parent anchoring, PAF, science transform, overscan and padding.
        if any(digest(fixture/n) != h for n,h in protected.items()):
            raise RuntimeError('Immutable source fixture differs')
        for instrument in ('omegacam', 'wfi'):
            for kind in ('retained', 'known-response'):
                for flag in (0,1):
                    label = '%s-%s-flag%d' % (instrument,kind,flag)
                    root = work/label
                    root.mkdir()
                    save(root/'run-provenance.json',dict(purpose='Constructed oracle controls only', status='running', parent=str(work/'run-provenance.json')))
                    inputs = prepare(root,fixture,kind,instrument)
                    if inputs != declared['cases'][instrument+'-'+kind]['inputs_sha256']:
                        raise RuntimeError('Declared input identity differs')
                    if (root/'mefpp.paf').read_bytes() != (repo/('mefpp2/ins/mef/config/'+instrument+'.paf')).read_bytes():
                        raise RuntimeError('Instrument PAF differs')
                    for i in range(3):
                        name = 'frame%d.fits' % i
                        raw = (root/name).read_bytes()
                        parent = (fixture/kind/name).read_bytes()
                        with fits.open(root/name, memmap=False) as hdus, fits.open(fixture/kind/name,memmap=False) as original:
                            if len(hdus)!=3 or raw[5760:8640]!=parent[5760:8640] or raw[12168:]!=parent[6408:]:
                                raise RuntimeError('Parent payload/padding differs')
                            for xt in (1,2):
                                expected = original[1].data.copy()
                                if xt==2: expected[:,:9]=expected[:,:9][:,::-1]
                                if not np.array_equal(hdus[xt].data,expected) or hdus[xt].header['EXTNAME']!=('S2_CCD_A' if xt==1 else 'S2_CCD_B'):
                                    raise RuntimeError('Input detector science/order differs')
                    ref = reference['c90-%s-flag%d' % (kind,flag)]
                    previous=cases['c90-leaks-%s-flag%d' % (kind,flag)]['roles']['ordinary']['outputs']
                    mask=expected_mask(fixture,kind,ref)
                    # Constructed output control: accepted masks and declared ordered metadata.
                    chunks=[]
                    for index,cards in enumerate(canonical_headers(previous,instrument)):
                        header=fits.Header([fits.Card.fromstring(c) for c in cards])
                        header.append(('ORIGFILE','PREPARATION_ONLY'))
                        chunks.append(header.tostring().encode('ascii'))
                        if index: chunks.append((mask if index==1 else mask[:,::-1]).tobytes().ljust(2880,b'\0'))
                    product=root/(('WFI_BPM' if instrument=='wfi' else 'OCAM_BPM')+'.fits')
                    product.write_bytes(b''.join(chunks))
                    for xt in (1,2): fits.PrimaryHDU(mask if xt==1 else mask[:,::-1]).writeto(root/('returned-%02d.fits'%xt))
                    check=lambda:verify(root,inputs,ref,flag,previous,instrument,fixture,kind)
                    check()
                    # Negative controls: wrong extension pixels, first-frame metadata and order.
                    good=product.read_bytes()
                    for mutation in ('pixels','metadata','order'):
                        if mutation=='pixels':
                            damaged=bytearray(good); damaged[sum(map(len,chunks[:4]))]^=1; damaged=bytes(damaged)
                        elif mutation=='metadata':
                            damaged=good.replace(b'ESO S2 METADATA 0',b'ESO S2 METADATA 1',1)
                        else:
                            damaged=chunks[0]+chunks[3]+chunks[4]+chunks[1]+chunks[2]
                        if damaged==good: raise RuntimeError('Mutation not applied')
                        product.write_bytes(damaged)
                        try: check()
                        except RuntimeError: record['rejected'].append(label+':'+mutation)
                        else: raise RuntimeError('Oracle accepted '+mutation)
                        (work/(label+'-rejected-'+mutation+'.bin')).write_bytes(damaged)
                        product.write_bytes(good)
                    check()
                    record['cases'].append(label)
                    save(root/'run-provenance.json',dict(purpose='Constructed oracle controls only', status='passed', parent=str(work/'run-provenance.json')))
        record['status']='passed'
    except BaseException as error:
        record.update(status='failed',error=str(error)); raise
    finally:
        # Preservation: immutable fixture identities and final retained status.
        record['immutable_fixtures_unchanged']=all(digest(fixture/n)==h for n,h in protected.items())
        if not record['immutable_fixtures_unchanged']: record['status']='failed'
        record['completed_utc']=datetime.now(timezone.utc).isoformat()
        save(work/'run-provenance.json',record)
    print('PREPARATION:',record['status'],'constructed cases:',len(record['cases']), 'rejections:',len(record['rejected']), 'native execution: false')
    print('REPORT:',work/'run-provenance.json')


if __name__=='__main__': main()
