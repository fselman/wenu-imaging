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
a=p.parse_args();a.work=a.work.resolve();a.work.mkdir();a.asdf_python=old.interpreter_path(a.asdf_python)
a.reuse_omissions=False;old.ARGS=a;old.WORK=a.work
old.RecipeTests.setUpClass();case=old.RecipeTests('test_explicit_omissions_and_toml')
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
# Identical triplets expose the scan-corrected plane without temporal ambiguity.
for i,path in enumerate(case.members):
    listing=a.work/f'single-{i}.list';listing.write_text((str(path)+'\n')*3)
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
print('PASS: exact historical lower, default/explicit average temporal oracle, native FITS/ASDF mode and QC, input/RON invariance and three refusals')
