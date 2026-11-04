"""Serialization/plotting controls; supplied tiny native transports, no pixel estimators (#233)."""
from copy import deepcopy
import csv
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge
qc=bridge.qc
WORK=Path(tempfile.gettempdir())


def row_text(columns,row):
    values=[]
    for key in columns:
        value=row[key]
        if value is None:value=''
        elif key in bridge.TEXT:
            value=str(value).replace('\\','\\\\').replace('\t','\\t').replace('\n','\\n').replace('\r','\\r')
        elif isinstance(value,float):value=format(value,'.17g')
        else:value=str(value)
        values.append(value)
    return '\t'.join(values)


def fixture(work):
    run=work/'measurement';(run/'native').mkdir(parents=True)
    refs=[]
    for i,pair in enumerate(('P0','P1','P1','P0')):
        refs.append(dict(path=str(work/f'F{i}.fits'),hdu=i%2+1,asset=f'F{i}.fits',index=10+i,pair=pair))
    biases=[dict(path=str(work/f'B{i}.fits'),hdu=i+1,asset=f'B{i}.fits') for i in range(2)]
    bpm=dict(path=str(work/'BPM.fits'),hdu=3,asset='BPM.fits',encoding='binary',good_value=1)
    selection=dict(selection_schema_version=1,detector='ESO_CCD_#65',readout_id='test:normal',bin_x=1,bin_y=1,
        raw_saturation_adu=65534,pair_time_tolerance_s=0,max_loaded_pixels=1000,max_rows=4,with_mad=True,
        reject_bits=255,exposure_hdu=0,header_keys=dict(identity='EXTNAME',amplifier='AMPID',bin_x='BINX',bin_y='BINY',exposure='EXPTIME'))
    text=''.join(f'{k}={json.dumps(v)}\n' for k,v in selection.items() if k!='header_keys')
    text+='[header_keys]\n'+''.join(f'{k}={json.dumps(v)}\n' for k,v in selection['header_keys'].items())
    for kind,items in (('flat',refs),('bias',biases)):
        for item in items:text+='\n[['+kind+']]\n'+''.join(f'{k}={json.dumps(v)}\n' for k,v in item.items())
    text+='\n[bpm]\n'+''.join(f'{k}={json.dumps(v)}\n' for k,v in bpm.items())
    (run/'selection.toml').write_text(text)
    rois=[dict(id='CCD65.R0',detector='ESO_CCD_#65',amplifier='L',xmin=1,xmax=2,ymin=1,ymax=2),
          dict(id='CCD65.R1',detector='ESO_CCD_#65',amplifier='L',xmin=3,xmax=4,ymin=1,ymax=2)]
    (run/'selected-rois.toml').write_text('roi_schema_version=1\n'+''.join('\n[[roi]]\n'+''.join(f'{k}={json.dumps(v)}\n' for k,v in r.items()) for r in rois))
    (run/'plan.tsv').write_text('schema\traw-pair-plan-v1\n')
    base=dict(schema_version=1,detector='ESO_CCD_#65',amplifier='L',configuration_detector=0,
        bias1_asset='B0.fits',bias1_hdu=1,bias2_asset='B1.fits',bias2_hdu=2,bpm_supplied=1,bpm_binary_supplied=1,
        reject_bits=255,saturation_raw_adu=65534.0,pair_time_tolerance_s=0.0,
        region_pixels=4,bpm_excluded=0,nonfinite_excluded=0,saturated=0,valid_pixels=4)
    def region(r):
        return dict(roi=r['id'],**{'active_'+k:r[k] for k in ('xmin','xmax','ymin','ymax')},
                    **{'raw_'+k:r[k]+5 for k in ('xmin','xmax','ymin','ymax')})
    pair_rows=[];bias_rows=[]
    for r in rois:
        bias_rows.append(dict(base,**region(r),level_available=1,difference_mean_adu=-0.0,
            difference_median_adu=-2.0,stdev_available=1,difference_stdev_adu=3.141592653589793,
            mad_available=1,difference_mad_adu=2.0,ron_available=1,ron_adu=2.221441469079183,
            ron_mad_available=1,ron_mad_adu=2.0967130275743506))
    for pair,first,second,seconds in [('P0',refs[0],refs[3],2.),('P1',refs[1],refs[2],5.)]:
        for r in rois:
            pair_rows.append(dict(base,**region(r),pair_id=pair,first_asset=first['asset'],first_input_index=first['index'],
                first_hdu=first['hdu'],first_seconds=seconds,second_asset=second['asset'],second_input_index=second['index'],
                second_hdu=second['hdu'],second_seconds=seconds,levels_available=1,flat1_mean_adu=1100.1234567890124,
                flat2_mean_adu=1102.1234567890124,bias1_mean_adu=100.,bias2_mean_adu=102.,signal_available=1,
                signal1_adu=999.1234567890124,signal2_adu=1001.1234567890124,mean_signal_adu=1000.1234567890124,
                variance_available=1,flat_difference_variance_adu2=410.,bias_difference_variance_adu2=10.,
                single_flat_variance_adu2=205.,single_bias_variance_adu2=5.,mismatch_available=1,
                fractional_mismatch=0.00199975311690079,matched_ron_available=1,matched_ron_adu=2.23606797749979,
                matched_ron_mad_available=1,matched_ron_mad_adu=2.0967130275743506,gain_state='arithmetic_available',
                point_gain_e_per_adu=5.000617283945062))
    for kind,rows,columns in [('pairs',pair_rows,bridge.PAIR_COLUMNS),('bias-ron',bias_rows,bridge.BIAS_COLUMNS)]:
        (run/'native'/(kind+'.tsv')).write_text('\t'.join(columns)+'\n'+'\n'.join(row_text(columns,r) for r in rows)+'\n')
    (run/'native/configuration.json').write_text('{"instrument":"transport_fixture"}\n')
    (run/'native/command.complete').write_text('raw_pair_tables_complete\n')
    outputs=[dict(path=str(p),size=p.stat().st_size,sha256=bridge.sha(p.read_bytes())) for p in sorted((run/'native').iterdir())]
    inputs=[dict(path=str(run/'selection.toml'),sha256=bridge.sha((run/'selection.toml').read_bytes()))]
    inputs += [dict(path=r['path'],sha256=str(i+1)*64,size=123,device=1,inode=i+1,mtime_ns=1,ctime_ns=1)
               for i,r in enumerate(refs+biases+[bpm])]
    receipt=dict(status='complete_for_owner_inspection',mode='raw_pair_measurements',native_exit_status=0,source_preservation=True,
        detectors_processed=1,detector='ESO_CCD_#65',amplifier='L',source_revision='1'*40,roi_count=2,
        output_rows={'pairs.tsv':4,'bias-ron.tsv':2},outputs=outputs,inputs=inputs)
    (run/'execution.json').write_text(json.dumps(receipt))
    return run,pair_rows,bias_rows


class PairQcTests(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='pair-qc-',dir=WORK))
        self.run,self.pairs,self.bias=fixture(self.work)
        self.records=self.work/'records';self.records.mkdir()
    def publish(self):
        return bridge.publish(self.run,self.records,assessment_id='test',created_at='2026-11-04T00:00:00Z',serializer_revision='2'*40)
    def replace_table(self,kind,rows):
        columns=bridge.KINDS[kind][0];path=self.run/'native'/(kind+'.tsv')
        path.write_text('\t'.join(columns)+'\n'+'\n'.join(row_text(columns,r) for r in rows)+'\n')
        receipt=json.loads((self.run/'execution.json').read_text())
        for output in receipt['outputs']:
            if output['path']==str(path):output.update(size=path.stat().st_size,sha256=bridge.sha(path.read_bytes()))
        (self.run/'execution.json').write_text(json.dumps(receipt))
    def test_exact_roundtrip_units_origins_and_no_raw_open(self):
        before={str(p):p.read_bytes() for p in self.run.rglob('*') if p.is_file()}
        report=self.publish();self.assertEqual(report['records'],9)
        self.assertTrue(report['roundtrip_exact']);self.assertFalse(report['raw_FITS_opened'])
        record=qc.read_record(self.records/'pairs.asdf');table=bridge.table_from_record(record)
        self.assertEqual(bridge.canonical(table['rows']),bridge.canonical(self.pairs))
        self.assertEqual(table['units']['single_flat_variance_adu2'],'ADU2')
        self.assertEqual(table['units']['point_gain_e_per_adu'],'electron/ADU')
        tree=record.as_dict();self.assertEqual(len(tree['inputs']),7)
        self.assertEqual(tree['file']['selectors'],[dict(detector_id='ESO_CCD_#65',table_name='pairs')])
        bias=qc.read_record(self.records/'bias-ron.asdf').as_dict()
        self.assertEqual(len(bias['inputs']),3)
        value=bridge.table_from_record(qc.read_record(self.records/'bias-ron.asdf'))['rows'][0]['difference_mean_adu']
        self.assertEqual(value.hex(),(-0.0).hex())
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.run.rglob('*') if p.is_file()})
        self.assertEqual(tree['provenance']['producer']['source_revision'],'1'*40)
        self.assertEqual(tree['extensions']['raw_pair_provenance']['serializer']['source_revision'],'2'*40)
    def test_unavailable_is_none_and_roundtrips(self):
        self.pairs[0]['gain_state']='nonpositive_variance';self.pairs[0]['point_gain_e_per_adu']=None
        self.replace_table('pairs',self.pairs);self.publish()
        record=qc.read_record(self.records/'pairs.asdf')
        self.assertIsNone(bridge.table_from_record(record)['rows'][0]['point_gain_e_per_adu'])
        metric=next(m for m in record.as_dict()['characterization']['detectors'][0]['measurements'] if m['name']=='pairs.0.point_gain_e_per_adu')
        self.assertEqual(metric['status'],'unavailable');self.assertEqual(metric['reason'],'nonpositive_variance')
    def test_failed_receipt_and_changed_table_refused(self):
        path=self.run/'execution.json';before=path.read_text();receipt=json.loads(before)
        receipt['status']='failed';path.write_text(json.dumps(receipt))
        with self.assertRaises(qc.QcError):self.publish()
        path.write_text(before);table=self.run/'native/pairs.tsv';table.write_bytes(table.read_bytes()+b'\n')
        with self.assertRaises(qc.QcError):self.publish()
        self.assertFalse(list(self.records.iterdir()))
    def test_unknown_columns_nonfinite_flags_and_counts_refused(self):
        original=(self.run/'native/pairs.tsv').read_bytes()
        with self.assertRaises(qc.QcError):bridge.parse_table(original.replace(b'point_gain_e_per_adu',b'unknown'),'pairs')
        for field,value in [('valid_pixels',5),('signal_available',2),('point_gain_e_per_adu',float('nan'))]:
            rows=deepcopy(self.pairs);rows[0][field]=value
            data=('\t'.join(bridge.PAIR_COLUMNS)+'\n'+'\n'.join(row_text(bridge.PAIR_COLUMNS,r) for r in rows)+'\n').encode()
            with self.assertRaises(qc.QcError):bridge.parse_table(data,'pairs')
    def test_binding_order_and_availability_mismatch_refused(self):
        for change in ('hdu','order','availability','roi'):
            rows=deepcopy(self.pairs)
            if change=='hdu':rows[0]['first_hdu']=99
            if change=='order':rows.reverse()
            if change=='availability':rows[0]['signal_available']=0
            if change=='roi':rows[0]['active_xmax']=99
            self.replace_table('pairs',rows)
            with self.assertRaises(qc.QcError):self.publish()
        self.assertFalse(list(self.records.iterdir()))
    def test_conflicts_frozen_links_and_relocation(self):
        self.publish();before={p.name:p.read_bytes() for p in self.records.iterdir()}
        with self.assertRaises(qc.QcError):self.publish()
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.records.iterdir()})
        moved=self.work/'moved';shutil.copytree(self.records,moved)
        self.assertEqual(len(list(qc.traverse_records(moved/'pairs.asdf',qc_root=moved))),8)
        self.assertEqual(len(list(qc.traverse_records(moved/'bias-ron.asdf',qc_root=moved))),4)
        (moved/'B0.asdf').unlink()
        with self.assertRaises(OSError):list(qc.traverse_records(moved/'pairs.asdf',qc_root=moved))
    def test_asdf_only_plot_and_typed_tamper_refusal(self):
        self.publish();path=self.records/'pairs.asdf';record=qc.read_record(path)
        bad=record.as_dict();bad['extensions']['raw_pair_table']['rows'][0]['mean_signal_adu']+=1
        with self.assertRaises(qc.QcError):bridge.table_from_record(qc.QcRecord(qc.encoded(bad)))
        spec=importlib.util.spec_from_file_location('pair_plot',ROOT/'tools/plot-pair-qc.py')
        plot=importlib.util.module_from_spec(spec);spec.loader.exec_module(plot)
        # Saved ASDF must be sufficient, even when original tables no longer exist there.
        shutil.move(self.run,self.work/'moved-native-evidence')
        output=self.work/'plots';output.mkdir();report=plot.render(path,output)
        self.assertFalse(report['native_TSV_opened']);self.assertFalse(report['raw_FITS_opened'])
        self.assertEqual(len(report['outputs']),3)
        for image in report['outputs']:
            self.assertTrue(Path(image['path']).read_bytes().startswith(b'\x89PNG'))
            self.assertEqual(image['signal_axis']['limits'],[0,65535])
            self.assertEqual(image['signal_axis']['ticks'],[0,10000,20000,30000,40000,50000,60000,65535])
            if image['kind']=='signal_time':
                series=image['series'][0]
                self.assertEqual(series['exposure_seconds'],[2.,2.,5.,5.])
                self.assertEqual(series['signal_adu'],[999.1234567890124,1001.1234567890124]*2)
                self.assertEqual([r['input_index'] for r in series['samples']],[10,13,11,12])
                self.assertEqual([r['pair_member'] for r in series['samples']],[1,2,1,2])
            if image['kind']=='gain':
                self.assertEqual(image['series'][0]['values'][0],5.000617283945062)
    def test_wrong_structural_bpm_lineage_refused(self):
        (self.run.parent/'lineage.json').write_text(json.dumps(dict(native_revision='1'*40,
            derived_selection_sha256='0'*64,derived_bpm_sha256='7'*64)))
        with self.assertRaises(qc.QcError):self.publish()
        self.assertFalse(list(self.records.iterdir()))

    def test_native_text_escapes_and_truncation(self):
        self.assertEqual(bridge.unescape(r'A\\B\tC\nD\rE\x23'), 'A\\B\tC\nD\rE#')
        for value in ('bad\\',r'bad\q'):
            with self.assertRaises(qc.QcError):bridge.unescape(value)
        data=(self.run/'native/pairs.tsv').read_bytes()
        with self.assertRaises(qc.QcError):bridge.parse_table(data[:-1],'pairs')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path,required=True)
    a=parser.parse_args();WORK=a.work.resolve(strict=True)
    attempts=[]
    def offline(event,args):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            attempts.append(event);raise RuntimeError('Offline ASDF test: '+event)
        if event=='open' and args and isinstance(args[0],(str,bytes)) and str(args[0]).lower().endswith('.fits'):
            raise RuntimeError('Raw FITS access forbidden in serialization test')
    sys.addaudithook(offline)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PairQcTests))
    (WORK/'pair-qc-contract-results.json').write_text(json.dumps(dict(tests=result.testsRun,successful=result.wasSuccessful(),
        failures=len(result.failures),errors=len(result.errors),network_attempts=attempts),indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() and not attempts else 1)
