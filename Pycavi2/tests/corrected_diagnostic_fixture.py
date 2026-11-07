"""Analytical saved-transport fixture, no native tool; remove images before use."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
from linearity_preparation_fixture import fixture,source_archive
import test_pair_qc as raw_fixture
import pycavi_linearity_preparation_qc as preparation


def tsv(path,columns,rows):
    path.write_text('\t'.join(columns)+'\n'+''.join(raw_fixture.row_text(columns,r)+'\n' for r in rows))


def make(work):
    s=fixture(work);source=source_archive(s)
    dummy=work/'raw-template';dummy.mkdir();_,templates,bias_templates=raw_fixture.fixture(dummy)
    native=work/'saved-native';native.mkdir()
    (native/'configuration.json').write_text(json.dumps(s['snapshot']))
    (native/'command.complete').write_text('linearity_preparation_complete_noise_unavailable\n')
    (native/'master-reference.tsv').write_text('path\thdu\tasset\n'+s['master']+'\t1\tmaster.fits\n')
    (native/'bias-traces.tsv').write_text('role\tinput_index\tmaster_accepted\traw_row\tcorrection_adu\n'+''.join(
        f"bias\t{b['index']}\t{b['accepted']}\t{y}\t{2+10*y}\n" for b in s['biases'] for y in range(1,5)))
    rois=s['resolved']['detectors'][0]['rois']
    def region(base,roi):
        r=deepcopy(base);r.update(roi=roi['id'],region_pixels=12,valid_pixels=12,bias1_asset='bias0.fits',bias2_asset='bias1.fits',
            bias1_hdu=0,bias2_hdu=0,bpm_supplied=1,bpm_binary_supplied=1,saturation_raw_adu=65534.)
        for key in ('xmin','xmax','ymin','ymax'):
            r['active_'+key]=roi[key];r['raw_'+key]=roi[key]+1
        return r
    for pair in range(10):
        group=native/f'pair-{pair:04d}';group.mkdir();members=[s['selection']['flat'][pair],s['selection']['flat'][19-pair]]
        rows=[];corrected=[];samples=[];bias=[]
        for i,roi in enumerate(rois):
            r=region(templates[0],roi);r['pair_id']=members[0]['pair']
            for prefix,member in zip(('first','second'),members):
                for target,origin in [('asset','asset'),('input_index','index'),('hdu','hdu')]:r[prefix+'_'+target]=member[origin]
                r[prefix+'_seconds']=float(2+pair)
            # Deliberately distinct raw diagnostic signals; never use them for corrected fits.
            r.update(signal1_adu=5000.+pair,signal2_adu=5002.+pair,mean_signal_adu=5001.+pair)
            rows.append(r);bias.append(region(bias_templates[0],roi))
            corrected.append(dict(schema_version=1,pair_row=i,valid_pixels=12,first_mean_adu=100.*(2+pair)+5.5,
                second_mean_adu=100.*(2+pair)+5.5,first_spatial_variance_adu2=13.,second_spatial_variance_adu2=13.,
                difference_mean_adu=0.,difference_variance_adu2=0.,half_difference_variance_adu2=0.))
        tsv(group/'pairs.tsv',preparation.pair.PAIR_COLUMNS,rows)
        tsv(group/'bias-ron.tsv',preparation.pair.BIAS_COLUMNS,bias)
        tsv(group/'corrected.tsv',preparation.FIELDS,corrected)
        for member in members:
            for i,site in enumerate(s['sites']):
                samples.append(dict(schema_version=1,detector='ESO_CCD_#65',amplifier='L',configuration_detector=0,
                    source_roi=site['source_roi'],active_x=i+1,active_y=1,raw_x=i+2,raw_y=2,
                    asset=member['asset'],input_index=member['index'],hdu=member['hdu'],pair_id=member['pair'],seconds=float(2+pair),
                    admission_state='admitted',signal_adu=100.*(2+pair)+i,noise_state='unavailable'))
        tsv(group/'samples.tsv',preparation.sample.COLUMNS,samples)
        columns='input_index outside_selected_sites bpm_excluded sample_excluded nonfinite saturated admitted'.split()
        tsv(group/'population.tsv',columns,[dict(zip(columns,[m['index'],7,0,0,0,0,5])) for m in members])
        (group/'flat-traces.tsv').write_text('role\tinput_index\tmaster_accepted\traw_row\tcorrection_adu\n'+''.join(
            f"flat\t{m['index']}\t-1\t{y}\t{2+10*y}\n" for m in members for y in range(1,5)))
    output=work/'preparation';output.mkdir()
    result=preparation.publish(native,source,output,resolved=s['resolved'],selection=s['selection'],biases=s['biases'],
        master_snapshot=s['snapshot'],assessment_id='prepared-fixture',created_at='2026-11-05T00:00:00Z',source_revision='b'*40)
    # No input image or native directory remains available to downstream readers.
    for p in work.glob('*.fits'):p.unlink()
    import shutil
    shutil.rmtree(native)
    detector=work/'display-detector.toml'
    detector.write_text(s['resolved']['sources']['detector_toml']['text']+'\nmosaic_column=1\nmosaic_row=1\namplifier_corner="lower-left"\n')
    processing=work/'display-processing.toml';processing.write_text(s['resolved']['sources']['processing_toml']['text'])
    return dict(state=s,source=Path(result['path']),detectors=detector,processing=processing)
