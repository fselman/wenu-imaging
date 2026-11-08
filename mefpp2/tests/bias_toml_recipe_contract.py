"""Five tiny actual recipe successes: all/subset, one extension and primary image.
Uses the existing synthetic numerical reference constructor, never observations.
"""
import argparse,json,os,subprocess,sys,tomllib
from pathlib import Path
import numpy as np
from astropy.io import fits
import bias_recipe_contract as old

PRIMARY=['MJD-OBS','DATE-OBS','EXPTIME','PRODCATG','TELESCOP','TIMESYS','EXTEND','NEXTEND','NOTTHERE']
DETECTOR=['EXTNAME','EXTVER','ESO DET CHIP ID','NOTTHERE']
p=argparse.ArgumentParser()
for key in ('work','recipe','adapter','asdf-python'):
    p.add_argument('--'+key,type=Path,required=True)
p.add_argument('--revision',required=True)
p.add_argument('--reuse-fixture',type=Path,help='Retain and reuse a prior tiny synthetic fixture without rerunning adapters')
a=p.parse_args();a.work=a.work.resolve();a.work.mkdir()
a.recipe=a.recipe.resolve(strict=True);a.adapter=a.adapter.resolve(strict=True)
a.asdf_python=old.interpreter_path(a.asdf_python)
old.ARGS=a;old.ARGS.reuse_omissions=False;old.WORK=a.work
if a.reuse_fixture is None:
    old.RecipeTests.setUpClass()  # Existing small F1 fixture and native reference pixels/QC.
else:
    # Read retained synthetic inputs/references; freeze every previous evidence file.
    previous=a.reuse_fixture.resolve(strict=True)
    assert previous != a.work
    cls=old.RecipeTests
    cls.raw=previous/'raw';cls.orchestration=previous/'orchestration'
    assert cls.raw.is_dir() and cls.orchestration.is_dir() and not list(cls.orchestration.iterdir())
    cls.products=a.work/'products';cls.products.mkdir()
    cls.paf=previous/'bias.paf';cls.toml=previous/'bias.toml'
    cls.listing=previous/'bias.list';cls.bpm=previous/'mask.fits';cls.bad_bpm=previous/'bad-mask.fits'
    cls.members=[Path(v) for v in cls.listing.read_text().splitlines() if v.strip()]
    assert len(cls.members)==4 and all(v.is_file() for v in cls.members)
    cls.references={mode:[previous/f'reference-{mode}-{d}'/'bias.fits' for d in range(2)]
                    for mode in ('masked','omitted','renamed')}
    cls.reference_qc={mode:[json.loads(v.with_name('qc.json').read_text()) for v in paths]
                      for mode,paths in cls.references.items()}
    cls.configuration=json.loads((previous/'reference-masked-0/config.json').read_text())

    # The frozen adapter predates median-policy provenance. The retained TOML
    # explicitly selects historical lower mode; keep the full expected snapshot
    # identical to normal fixture setup rather than dropping that comparison (#294).

    assert tomllib.loads(cls.toml.read_text())['native']['MEF.BIAS.MEDIAN.EVEN.HANDLING']=='lower'
    cls.configuration['MEF.BIAS.MEDIAN.EVEN.HANDLING']={'type':'string','value':'lower'}
    cls.frozen={str(v):old.digest(v) for v in previous.rglob('*') if v.is_file()}

case=old.RecipeTests('test_explicit_omissions_and_toml')
recipe_specs={}
def config(label,entries,selection=None):
    text='bias_recipe_schema_version=1\nsettings="bias.toml"\n[bias]\nmad=false\nreadout_id="synthetic-readout"\nbin_x=1\nbin_y=1\ninput_bpm="omitted"\namplifier_id="explicit-whole-detector"\n'
    if a.reuse_fixture is not None:
        text=text.replace('settings="bias.toml"','settings='+json.dumps(str(case.toml)))
    if selection is not None:text+='detectors='+json.dumps(selection)+'\n'
    text+='[provenance]\nprimary='+json.dumps(PRIMARY)+'\ndetector='+json.dumps(DETECTOR)+'\n'
    for identity,index,hdu in entries:
        text+='[[detector]]\nid='+json.dumps(identity)+'\nconfiguration_detector='+str(index)+'\nhdus=['+str(hdu)+']\n'
    path=a.work/(label+'.toml');path.write_text(text);return path
both=[('F1_CCD_A',0,1),('F1_CCD_B',1,2)]
def expected_card(header,key,hdu,identity):
    matches=[c for c in header.cards if c.keyword==key]
    assert len(matches)<=1
    if not matches:
        return dict(keyword=key,role='primary' if identity is None else 'detector',
                    hdu=hdu,detector_id=identity,status='missing',value_type='missing',
                    value=None,comment=None,card=None)
    card=matches[0];value=card.value
    if value is fits.card.UNDEFINED:value=None
    kind='undefined' if value is None else 'boolean' if isinstance(value,bool) else 'integer' if isinstance(value,int) else 'real' if isinstance(value,float) else 'string'
    return dict(keyword=key,role='primary' if identity is None else 'detector',
                hdu=hdu,detector_id=identity,status='present',value_type=kind,
                value=value,comment=card.comment,card=card.image)
def run(label,entries,listing,selector=None,legacy_check=False):
    cfg=config(label,entries)
    out=case.destination(label)
    command=[str(a.recipe),'cal','bias','--config',str(cfg),'--bias',str(listing),'--output-dir',str(out)]
    if selector is not None:command+=['--detectors',selector]
    case.run_recipe(command,label,True)
    product=next(out.glob('*.fits'))
    selected=entries if selector in (None,'all') else [v for v in entries if v[0] in selector.split(',')]
    cards=[]
    with fits.open(product,memmap=False) as hdus:
        hdus.verify('exception');assert len(hdus)==len(selected)+1
        cards.extend(expected_card(hdus[0].header,k,0,None) for k in PRIMARY)
        for output,(identity,index,hdu) in enumerate(selected,1):
            assert hdus[output].header['EXTNAME']==identity
            with fits.open(case.references['omitted'][index],memmap=False) as ref:
                assert hdus[output].data.tobytes()==ref[1].data.tobytes()
            cards.extend(expected_card(hdus[output].header,k,output,identity) for k in DETECTOR)
    for card in cards:card["source_file"]=str(product)
    if legacy_check:case.verify(product,measured=False,reference_index=0)
    expected=dict(revision=a.revision,recipe_path=str(cfg),recipe_text=cfg.read_text(),
                  cards=cards,detectors=[v[0] for v in selected],
                  configuration_indices=[v[1] for v in selected],source_hdus=[v[2] for v in selected])
    expected_path=a.work/(label+'-headers.json');expected_path.write_text(json.dumps(expected))
    with (a.work/(label+'-asdf.log')).open('x') as stream:
        subprocess.run([str(a.asdf_python),'-B',str(old.ROOT/'mefpp2/tests/bias_header_asdf_verify.py'),
            '--file',str(product.with_suffix('.asdf')),'--schema',str(old.ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'),
            '--expected',str(expected_path)],stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=60)
    assert 'xmem:' not in (a.work/(label+'.console.log')).read_text()
    return product
products=[]
products.append(run('default-all',both,case.listing,legacy_check=True))
products.append(run('explicit-all',both,case.listing,'all',legacy_check=True))
products.append(run('subset',both,case.listing,'F1_CCD_B'))
for mode,hdu in (('one-extension',1),('primary-image',0)):
    raw=a.work/mode;raw.mkdir();members=[]
    for i,path in enumerate(case.members):
        target=raw/f'bias{i}.fits'
        with fits.open(path,memmap=False) as source:
            if hdu:
                result=fits.HDUList([source[0].copy(),source[1].copy()])
            else:
                header=source[0].header.copy()
                for card in source[1].header.cards:
                    if card.keyword not in ('XTENSION','BITPIX','NAXIS','NAXIS1','NAXIS2','PCOUNT','GCOUNT','EXTNAME','EXTVER'):
                        header[card.keyword]=(card.value,card.comment)
                result=fits.HDUList([fits.PrimaryHDU(source[1].data.copy(),header)])
            result.writeto(target)
        members.append(target)
    listing=a.work/(mode+'.list');listing.write_text('\n'.join(map(str,members))+'\n')
    saved={str(v):old.digest(v) for v in [*members,listing]}
    products.append(run(mode,[('F1_CCD_A',0,hdu)],listing))
    assert saved=={str(v):old.digest(v) for v in [*members,listing]}
# Two declared logical detectors cannot select the same physical raw HDU.
cfg=config('duplicate-plane',[('F1_CCD_A',0,1),('F1_CCD_B',1,1)])
out=case.destination('duplicate-plane')
case.run_recipe([str(a.recipe),'cal','bias','--config',str(cfg),'--bias',str(case.listing),
                 '--output-dir',str(out)],'duplicate-plane',False)
assert not list(out.iterdir())
# New selection/mixed-authority errors must refuse before creating products/logs.
cfg=config('refusals',both)
for label,extra in (('unknown',['--detectors','ABSENT']),('duplicate',['--detectors','F1_CCD_A,F1_CCD_A']),
                    ('mixed',['--mad','yes'])):
    out=case.destination(label)
    case.run_recipe([str(a.recipe),'cal','bias','--config',str(cfg),'--bias',str(case.listing),
                     '--output-dir',str(out),*extra],label,False)
    assert not list(out.iterdir())
receipt=dict(successful=True,successful_products=5,selection_refusals=4,
             source_revision=a.revision,observations_opened=False,pycavi_used=False,
             products=list(map(str,products)))
(a.work/'bias-toml-results.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: five actual native recipe products, independent ASDF/header checks and four selection refusals')
