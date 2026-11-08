"""Tiny actual native products; independent temporal median and ASDF/QC oracle.
Astropy is a verifier only. The selected native C recipe creates every product.
"""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from astropy.io import fits
import bias_recipe_contract as old
p=argparse.ArgumentParser(description=__doc__)
for k in ('work','recipe','adapter','asdf-python'):p.add_argument('--'+k,type=Path,required=True)
p.add_argument('--revision',required=True)
p.add_argument('--reuse-fixture',type=Path)
a=p.parse_args();a.work=a.work.resolve();a.work.mkdir();a.asdf_python=old.interpreter_path(a.asdf_python)
a.reuse_omissions=False;old.ARGS=a;old.WORK=a.work
if a.reuse_fixture is None:
    old.RecipeTests.setUpClass()
else:
    previous=a.reuse_fixture.resolve(strict=True);assert previous!=a.work
    cls=old.RecipeTests
    cls.raw=previous/'raw';cls.orchestration=a.work/'orchestration';cls.orchestration.mkdir()
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
    cls.configuration['MEF.BIAS.MEDIAN.EVEN.HANDLING']={'type':'string','value':'lower'}
    cls.frozen={str(v):old.digest(v) for v in previous.rglob('*') if v.is_file()}
case=old.RecipeTests('test_explicit_omissions_and_toml')
# First retain the exact historical oracle against the frozen reference adapter.
out=case.destination('legacy-reference');case.run_recipe(case.command(out,toml=False),'legacy-reference',True)
case.verify(next(out.glob('*.fits')))
configuration=dict(case.configuration);configuration.pop('MEF.BIAS.MEDIAN.EVEN.HANDLING')
configuration['MEF.BIAS.KAPPA1']={'type':'float64-bits','value':__import__('struct').pack('>d',100).hex()}
settings=a.work/'average-settings.toml';settings.write_text(old.render_snapshot(configuration))
products={};corrected=[];headers={}
def run(label,listing,mode=None,pair=False,policy=None,success=True):
    cfg=a.work/(label+'.toml');text='bias_recipe_schema_version=1\nsettings='+json.dumps(str(policy or settings))+'\n[bias]\nmad=true\ninput_bpm="omitted"\nreadout_id="synthetic-readout"\nbin_x=1\nbin_y=1\namplifier_id="whole"\n'
    if mode is not None:text+='median_even_handling='+json.dumps(mode)+'\n'
    if pair:text+='ron_pair=[0,3]\n'
    for i,identity in enumerate(old.IDS):text+='[[detector]]\nid='+json.dumps(identity)+f'\nconfiguration_detector={i}\nhdus=[{i+1}]\n'
    cfg.write_text(text);out=case.destination(label)
    case.run_recipe([str(a.recipe),'cal','bias','--config',str(cfg),'--bias',str(listing),'--output-dir',str(out)],label,success)
    if not success:
        assert not list(out.glob('*.fits'));return
    product=next(out.glob('*.fits'));products[label]=str(product)
    with fits.open(product,memmap=False) as h:
        h.verify('exception');arrays=[v.data.astype(np.float32).copy() for v in h[1:]]
        headers[label]=[{k:v.header[k] for k in v.header if k.startswith('ESO MPP QC ')} for v in h[1:]]
        for v in h[1:]:assert v.header['ESO MPP QC MED EVEN']==(mode or 'average')
    return arrays
def bracket_values(data,zone,delta):
    """Exactly representable active-only offset; scan pixels remain unchanged."""
    x1,x2,y1,y2=zone;result=data.astype(np.float32).copy()
    active=result[y1-1:y2,x1-1:x2];before=active.copy()
    active+=np.float32(delta)
    assert np.all(active.astype(np.float64)-before.astype(np.float64)==delta)
    outside=np.ones(result.shape,dtype=bool);outside[y1-1:y2,x1-1:x2]=False
    assert np.array_equal(result[outside],data[outside])
    return result
def bracket_triplet(source,directory):
    """Distinct synthetic files at offsets -1, 0, +1: central plane unchanged."""
    directory.mkdir();members=[];saved=old.digest(source)
    with fits.open(source,memmap=False) as original:
        for index,delta in enumerate((-1,0,1)):
            hdus=fits.HDUList([v.copy() for v in original])
            for d in range(2):
                zone=[configuration[f'MEF.CROP.{axis}.{bound}.CHIP{d+1}']['value']
                      for axis,bound in [('X','MIN'),('X','MAX'),('Y','MIN'),('Y','MAX')]]
                assert configuration[f'MEF.OVERSCAN.X.MIN.CHIP{d+1}']['value']>zone[1]
                hdus[d+1].data=bracket_values(hdus[d+1].data,zone,delta)
            destination=directory/f'bracket-{index}-{source.name}';hdus.writeto(destination)
            hdus.close();members.append(destination.resolve(strict=True))
    assert len(set(members))==3 and old.digest(source)==saved
    return members
# Retain the real recipe's duplicate-identity refusal as an explicit check.
duplicate=a.work/'duplicate.list';duplicate.write_text((str(case.members[0])+'\n')*3)
run('duplicate-refused',duplicate,success=False)
# Symmetric active-only offsets preserve the central corrected plane and
# avoid the inherited zero-spread strict frame-rejection interval.
raw_oracle=a.work/'raw-bracketed';raw_oracle.mkdir()
for i,path in enumerate(case.members):
    copies=bracket_triplet(path,raw_oracle/f'plane-{i}')
    case.frozen.update({str(v):old.digest(v) for v in copies})
    listing=a.work/f'single-{i}.list';listing.write_text('\n'.join(map(str,copies))+'\n')
    corrected.append(run('single-'+str(i),listing))
expected=np.stack(corrected)
values={};master={}
for label,mode in [('default',None),('average','average'),('lower','lower')]:
    actual=run(label,case.listing,mode,True);values[label]=actual
    oracle=np.sort(expected,axis=0)[1] if mode=='lower' else np.median(expected,axis=0)
    master[label]=[]
    for plane in oracle:
        v=plane.astype(np.float64).ravel();med=float(np.median(v))
        master[label].append(dict(mean=float(np.mean(v)),median=med,stdev=float(np.std(v,ddof=1)),scaled_mad=float(np.median(np.abs(v-med)))*1.4826))
    for d in range(2):assert actual[d].tobytes()==oracle[d].astype(np.float32).tobytes(),(label,d)
assert any(np.any(values['default'][d]!=values['lower'][d]) for d in range(2))
for value in ('upper','AVERAGE'):run('refuse-'+value,case.listing,value,success=False)
conflict=a.work/'conflict-settings.toml';conflict.write_text(settings.read_text()+'\n"MEF.BIAS.MEDIAN.EVEN.HANDLING"="lower"\n')
run('conflict',case.listing,'average',policy=conflict,success=False)
expected_path=a.work/'median-expected.json';expected_path.write_text(json.dumps(dict(products=products,headers=headers,master=master,revision=a.revision)))
with (a.work/'asdf-verify.log').open('x') as log:
    subprocess.run([str(a.asdf_python),'-B',str(old.ROOT/'mefpp2/tests/bias_median_asdf_verify.py'),'--expected',str(expected_path),'--schema',str(old.ROOT/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json')],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
(a.work/'results.json').write_text(json.dumps(dict(successful=True,products=products,legacy_exact=True,raw_observations_accessed=False),indent=2)+'\n')
print('PASS: exact historical lower, default/explicit average temporal oracle, native FITS/ASDF mode and QC, input/RON invariance and four refusals')
