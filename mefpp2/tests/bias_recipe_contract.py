"""Actual standalone native recipe on the established tiny synthetic FITS fixture.

No observations, installation, Pycavi import or broad previous-gate replay.
Run from a separate empty orchestration directory. Raw fixtures freeze after setup.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unittest
import numpy as np
from astropy.io import fits
from prepare_integrated_campaign_fixture import prepare
from config_toml_contract import render_snapshot

ROOT=Path(__file__).resolve().parents[2]
ARGS=WORK=None
RECIPE_CALLS=ASDF_CHECKS=0
IDS=['F1_CCD_A','F1_CCD_B']

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def interpreter_path(path):
    # Venv identity depends on the invoked path, not its symlink target (#255).
    path=path.absolute()
    if not path.is_file() or not os.access(path,os.X_OK):raise ValueError('Missing selected interpreter')
    return path

class RecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ARGS.reuse_omissions:
            cls.restore_omission_fixture()
            return
        cls.raw=WORK/'raw';cls.orchestration=WORK/'orchestration';cls.orchestration.mkdir()
        cls.products=WORK/'products';cls.products.mkdir()
        fixture=prepare(cls.raw,ROOT)
        text=(ROOT/'mefpp2/ins/mef/config/omegacam.paf').read_text()
        for key,value in dict(fixture['synthetic_paf_overrides'],**{'MEF.BIAS.KAPPA1':1.2}).items():
            text,count=re.subn(r'^'+re.escape(key)+r'\s+[^;\n]*;',key+' '+str(value)+';',text,flags=re.M)
            assert count==1,key
        cls.paf=WORK/'bias.paf';cls.paf.write_text(text)
        with fits.open(cls.raw/'bias0.fits',memmap=False) as h:
            h[1].data[:,:9]+=100;h[2].data[:,:9]+=100;h.writeto(cls.raw/'outlier.fits')
        cls.members=[cls.raw/n for n in ('bias0.fits','outlier.fits','bias1.fits','bias2.fits')]
        for index,path in enumerate(cls.members):
            with fits.open(path,mode='update',memmap=False) as h:
                for d in range(2):h[d+1].data[:,:9]+=7*d+np.arange(9,dtype=np.float32)[None,:]*(index+1)/4
        cls.listing=WORK/'bias.list';cls.listing.write_text('\n'.join(map(str,cls.members))+'\n')
        mask=np.ones((9,9),np.uint8);mask[1,2]=mask[6,7]=0
        cls.bpm=WORK/'mask.fits'
        fits.HDUList([fits.PrimaryHDU(),fits.ImageHDU(mask,name='MASK_A'),fits.ImageHDU(mask[:,::-1],name='MASK_B')]).writeto(cls.bpm)
        cls.bad_bpm=WORK/'bad-mask.fits'
        with fits.open(cls.bpm,memmap=False) as h:h[1].data[0,0]=2;h.writeto(cls.bad_bpm)
        cls.swapped=cls.raw/'swapped-outlier.fits'
        with fits.open(cls.members[1],memmap=False) as h:fits.HDUList([h[0].copy(),h[2].copy(),h[1].copy()]).writeto(cls.swapped)
        cls.swapped_members=[cls.members[0],cls.swapped,*cls.members[2:]]
        cls.swapped_list=WORK/'swapped.list';cls.swapped_list.write_text('\n'.join(map(str,cls.swapped_members))+'\n')
        normalized=WORK/'reference-inputs';normalized.mkdir()
        renamed=normalized/'swapped-outlier.fits'
        renamed.write_bytes(cls.members[1].read_bytes())
        named_members=[cls.members[0],renamed,*cls.members[2:]]
        named_list=WORK/'reference-renamed.list';named_list.write_text('\n'.join(map(str,named_members))+'\n')
        cls.references={};cls.reference_qc={}
        # References match actual mask/measurement policy AND input basenames.
        # The reordered case keeps logical pixels in normal HDU order here;
        # the candidate alone must follow the explicitly reordered input HDUs.
        for mode in ('masked','omitted','renamed'):
            cls.references[mode]=[];cls.reference_qc[mode]=[]
            for d in range(2):
                ref=WORK/f'reference-{mode}-{d}';ref.mkdir()
                listing=named_list if mode=='renamed' else cls.listing
                selected=mode!='omitted'
                argv=[str(ARGS.adapter),'cal','bias','--pafname',str(cls.paf),'--bias',str(listing),
                    '--detector-id',IDS[d],'--hdu',str(d+1),'--config-detector',str(d),
                    '--readout-id','synthetic-readout','--bin-x','1','--bin-y','1',
                    '--input-bpm',str(cls.bpm) if selected else 'omitted',
                    '--output',str(ref/'bias.fits'),'--work-dir',str(ref),
                    '--log-path',str(ref/'native.log'),'--config-record',str(ref/'config.json'),
                    '--qc-record',str(ref/'qc.json'),'--expected-extname',IDS[d],
                    '--measurements','yes','--mad','yes' if selected else 'no']
                if selected:argv+=['--ron-first','0','--ron-second','3','--high-sigma','5',
                    '--bpm-hdu',str(d+1),'--bpm-good-value','1','--bpm-coordinates','active',
                    '--bpm-expected-extname','MASK_A' if d==0 else 'MASK_B']
                with (ref/'command.log').open('x') as log:
                    subprocess.run(argv,cwd=cls.orchestration,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
                cls.references[mode].append(ref/'bias.fits')
                cls.reference_qc[mode].append(json.loads((ref/'qc.json').read_text()))
        cls.configuration=json.loads((WORK/'reference-masked-0/config.json').read_text())
        cls.toml=WORK/'bias.toml';cls.toml.write_text(render_snapshot(cls.configuration))
        frozen=[*cls.members,cls.swapped,cls.bpm,cls.bad_bpm,cls.paf,cls.toml,cls.listing,cls.swapped_list,renamed,named_list,*[p for rows in cls.references.values() for p in rows]]
        cls.frozen={str(p):digest(p) for p in frozen}
        assert not list(cls.orchestration.iterdir())

    @classmethod
    def restore_omission_fixture(cls):
        # Reuse only the owner's retained tiny synthetic fixture and references.
        # Preserve its failed output, previous logs, and seven passed groups.
        previous=json.loads((WORK/'bias-recipe-results.json').read_text())
        assert previous['tests']==8 and not previous['successful']
        assert previous['asdf_checks']==2 and not previous['observations_opened']
        assert not (WORK/'bias-recipe-omissions-retry-results.json').exists()
        assert not (WORK/'toml-omissions-memory-readback.console.log').exists()
        cls.raw=WORK/'raw';cls.orchestration=WORK/'orchestration'
        cls.products=WORK/'products';cls.paf=WORK/'bias.paf';cls.toml=WORK/'bias.toml'
        cls.listing=WORK/'bias.list';cls.bpm=WORK/'mask.fits'
        assert cls.orchestration.is_dir() and not list(cls.orchestration.iterdir())
        assert cls.products.is_dir() and cls.toml.is_file()
        cls.members=[Path(s) for s in cls.listing.read_text().splitlines() if s.strip()]
        assert len(cls.members)==4 and all(p.is_file() for p in cls.members)
        refs=[WORK/f'reference-omitted-{d}' for d in range(2)]
        cls.references={'omitted':[p/'bias.fits' for p in refs]}
        cls.reference_qc={'omitted':[json.loads((p/'qc.json').read_text()) for p in refs]}
        cls.configuration=json.loads((WORK/'reference-masked-0/config.json').read_text())
        # These are existing small synthetic fixtures/products, not observations
        # or a source/runtime ancestry audit. No old file may be changed.
        cls.frozen={str(p):digest(p) for p in WORK.rglob('*') if p.is_file()}

    def destination(self,name):
        p=self.products/name;p.mkdir(parents=True);return p

    def command(self,destination,*,complete=False,swapped=False,measured=True,bad_mask=False,toml=False):
        argv=[str(ARGS.recipe),'cal','bias','--config' if toml else '--pafname',str(self.toml if toml else self.paf),
            '--bias',str(self.swapped_list if swapped else self.listing),
            '--output' if complete else '--output-dir',str(destination),
            '--reference-detector',IDS[1],'--mad','yes' if measured else 'no']
        if measured:argv+=['--ron-first','0','--ron-second','3','--high-sigma','5']
        for d in range(2):
            argv+=['--detector-id',IDS[d],'--config-detector',str(d),'--readout-id','synthetic-readout',
                '--bin-x','1','--bin-y','1','--amplifier-id','explicit-whole-detector',
                '--input-bpm',str(self.bad_bpm if bad_mask else self.bpm) if measured else 'omitted']
            hdus=([d+1,2-d,d+1,d+1] if swapped else [d+1])
            for hdu in hdus:argv+=['--hdu',str(hdu)]
            if measured:argv+=['--bpm-hdu',str(d+1),'--bpm-good-value','1','--bpm-coordinates','active',
                '--bpm-expected-extname','MASK_A' if d==0 else 'MASK_B']
        return argv

    def run_recipe(self,argv,label,success):
        global RECIPE_CALLS
        RECIPE_CALLS+=1
        log=WORK/(label+'.console.log')
        with log.open('x') as stream:
            result=subprocess.run(argv,cwd=self.orchestration,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
        text=log.read_text();self.assertGreaterEqual(result.returncode,0,text)
        self.assertEqual(result.returncode==0,success,text)
        self.assertEqual('BIAS_RECIPE_COMPLETE' in text,success,text)
        self.assertEqual(self.frozen,{p:digest(Path(p)) for p in self.frozen})
        self.assertEqual(list(self.orchestration.iterdir()),[])
        return text

    def verify(self,product,*,swapped=False,measured=True):
        global ASDF_CHECKS
        self.assertTrue(product.with_suffix('.log').is_file())
        self.assertIn('OUTPUTS_WRITTEN',product.with_suffix('.log').read_text())
        self.assertEqual(sorted(p.suffix for p in product.parent.iterdir()),['.asdf','.fits','.log'])
        mode='renamed' if swapped else 'masked' if measured else 'omitted'
        references=self.references[mode]
        from bias_qc_fits_contract import is_addition
        fits_qc_headers=[]
        # Strict card assertions retained, with policy/provenance-matched references.
        with fits.open(product,memmap=False) as h:
            h.verify('exception');self.assertEqual(len(h),3)
            self.assertEqual(h[0].header['NEXTEND'],2)
            cards=lambda hd:[c.image for c in hd.header.cards if c.keyword not in ('ORIGFILE','CHECKSUM','NEXTEND','DATE') and not is_addition(c.keyword)]
            with fits.open(references[1],memmap=False) as ref:self.assertEqual(cards(h[0]),cards(ref[0]))
            for d in range(2):
                with fits.open(references[d],memmap=False) as ref:
                    self.assertEqual(h[d+1].data.dtype,ref[1].data.dtype)
                    self.assertEqual(h[d+1].data.tobytes(),ref[1].data.tobytes())
                    self.assertEqual(cards(h[d+1]),cards(ref[1]))
                self.assertEqual(h[d+1].header['ORIGFILE'],product.name)
                addition_cards=[c.keyword for c in h[d+1].header.cards if is_addition(c.keyword)]
                self.assertEqual(len(addition_cards),len(set(addition_cards)))
                fits_qc_headers.append({key:h[d+1].header[key] for key in addition_cards})
        expected=dict(fits_qc_headers=fits_qc_headers,fits=str(product),raw=list(map(str,self.swapped_members if swapped else self.members)),
            hdus=[[d+1,2-d,d+1,d+1] if swapped else [d+1]*4 for d in range(2)],
            measured=measured,configuration=self.configuration,reference_qc=self.reference_qc[mode])
        name=product.parent.relative_to(self.products).as_posix().replace('/','_')
        expected_path=WORK/(name+'-expected.json')
        with expected_path.open('x') as stream:json.dump(expected,stream)
        # Independent actual ASDF6 schema/exact native QC check; no Pycavi.
        r=subprocess.run([str(ARGS.asdf_python),'-B',str(ROOT/'mefpp2/tests/bias_recipe_verify.py'),
            '--file',str(product.with_suffix('.asdf')),'--schema',str(ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'),
            '--expected',str(expected_path)],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        ASDF_CHECKS+=1

    def test_output_dir_complete_native_recipe_and_qc(self):
        out=self.destination('bias');argv=self.command(out)
        argv[argv.index('--output-dir')+1]=os.path.relpath(out,self.orchestration)
        self.run_recipe(argv,'output-dir',True)
        products=list(out.glob('*.fits'));self.assertEqual(len(products),1)
        self.assertRegex(products[0].name,r'^CMDP\.\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\.001\.fits$')
        self.verify(products[0])

    def test_complete_output_and_per_input_hdu_mapping(self):
        out=self.destination('cal/bias')/'user.named.product.fits'
        argv=self.command(out,complete=True,swapped=True)
        argv[argv.index('--output')+1]=os.path.relpath(out,self.orchestration)
        self.run_recipe(argv,'complete-output',True)
        self.assertTrue(out.is_file());self.verify(out,swapped=True)

    def test_explicit_omissions_and_toml(self):
        name='toml-no-mad-memory-readback' if ARGS.reuse_omissions else 'toml-no-mad'
        label='toml-omissions-memory-readback' if ARGS.reuse_omissions else 'toml-omissions'
        out=self.destination(name);self.run_recipe(self.command(out,measured=False,toml=True),label,True)
        self.verify(next(out.glob('*.fits')),measured=False)

    def test_conflicting_or_missing_destination_refused(self):
        out=self.destination('conflict')
        for mode in ('both','neither'):
            argv=self.command(out)
            if mode=='both':argv+=['--output',str(out/'explicit.fits')]
            else:
                i=argv.index('--output-dir');del argv[i:i+2]
            self.run_recipe(argv,'destination-'+mode,False);self.assertEqual(list(out.iterdir()),[])

    def test_occupied_files_and_dangling_links_preserved(self):
        for suffix in ('.fits','.asdf','.log','link'):
            out=self.destination('occupied-'+suffix.replace('.',''))/'existing.fits'
            protected=out if suffix=='link' else out.with_suffix(suffix)
            if suffix=='link':protected.symlink_to(out.parent/'missing')
            else:protected.write_bytes(b'protected earlier product')
            self.run_recipe(self.command(out,complete=True),'occupied-'+suffix.replace('.',''),False)
            if suffix=='link':self.assertTrue(protected.is_symlink())
            else:self.assertEqual(protected.read_bytes(),b'protected earlier product')
            self.assertEqual(len(list(out.parent.iterdir())),1)

    def test_bad_mapping_and_reference_refused(self):
        for mode in ('hdu','reference','duplicate'):
            out=self.destination('bad-'+mode);argv=self.command(out)
            if mode=='hdu':argv[argv.index('--hdu')+1]='99'
            elif mode=='reference':argv[argv.index('--reference-detector')+1]='unknown'
            else:
                i=len(argv)-1-argv[::-1].index('--detector-id');argv[i+1]=IDS[0]
            self.run_recipe(argv,'bad-'+mode,False);self.assertEqual(list(out.iterdir()),[])

    def test_invalid_bpm_content_reports_incomplete(self):
        out=self.destination('bad-mask');self.run_recipe(self.command(out,bad_mask=True),'bad-mask',False)
        self.assertEqual(list(out.glob('*.fits')),[]);self.assertEqual(list(out.glob('*.asdf')),[])
        self.assertIn('FAILED',next(out.glob('*.log')).read_text())
        self.assertEqual(len(list(out.glob('.mefpp-bias-*'))),1)

    def test_invalid_ron_pair_refused(self):
        for mode in ('same','range'):
            out=self.destination('ron-'+mode);argv=self.command(out)
            argv[argv.index('--ron-second')+1]='0' if mode=='same' else '4'
            self.run_recipe(argv,'ron-'+mode,False);self.assertEqual(list(out.iterdir()),[])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,required=True)
    p.add_argument('--recipe',type=Path,required=True);p.add_argument('--adapter',type=Path,required=True)
    p.add_argument('--asdf-python',type=Path,required=True)
    p.add_argument('--reuse-omissions',action='store_true',
        help='Retry only the timed-out omission group using retained synthetic fixtures')
    ARGS=p.parse_args()
    WORK=ARGS.work.resolve(strict=True)
    for key in ('recipe','adapter'):setattr(ARGS,key,getattr(ARGS,key).resolve(strict=True))
    ARGS.asdf_python=interpreter_path(ARGS.asdf_python)
    os.environ.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1')
    suite=unittest.TestSuite([RecipeTests('test_explicit_omissions_and_toml')]) if ARGS.reuse_omissions else unittest.defaultTestLoader.loadTestsFromTestCase(RecipeTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    receipt='bias-recipe-omissions-retry-results.json' if ARGS.reuse_omissions else 'bias-recipe-results.json'
    (WORK/receipt).write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),
        actual_bias_recipe_exercised=RECIPE_CALLS>0,recipe_calls=RECIPE_CALLS,
        real_asdf_exercised=ASDF_CHECKS>0,asdf_checks=ASDF_CHECKS,
        reused_passed_groups=7 if ARGS.reuse_omissions else 0,
        observations_opened=False,pycavi_used=False))+'\n')
    raise SystemExit(not result.wasSuccessful())
