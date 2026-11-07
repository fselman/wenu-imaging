#!/usr/bin/env python3
"""One-use serial OCAM raw-pair batch, retaining shared verification and ASDF (#234)."""
import argparse
import copy
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_pair_qc as bridge


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load('single_pair_runner', ROOT/'tools/run-pair-measurements.py')
plotter = load('pair_plotter', ROOT/'tools/plot-pair-qc.py')
require = runner.require
NATIVE_REVISION = '512092fa3180653f165f744a1ba7d9991e251f03'
OUTPUTS = ('pairs.tsv', 'bias-ron.tsv', 'configuration.json', 'command.complete')


def write(path, value):
    # Atomic receipts: an interrupted write cannot masquerade as a completed JSON file.
    temporary = path.with_suffix(path.suffix+'.tmp')
    with temporary.open('x') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def digest(path):
    return bridge.sha(bridge.small(Path(path)))


def selection_text(selection):
    def lines(values):
        return ''.join(f'{k} = {json.dumps(v, ensure_ascii=True)}\n' for k, v in values.items())
    text = lines({k:v for k,v in selection.items() if k not in ('header_keys','flat','bias','bpm')})
    text += '\n[header_keys]\n'+lines(selection['header_keys'])
    for kind in ('flat', 'bias'):
        for item in selection[kind]:
            text += '\n[['+kind+']]\n'+lines(item)
    return text+'\n[bpm]\n'+lines(selection['bpm'])


def remap(selection, review, detector):
    """Use saved per-file identity maps, never a detector's native slot as its HDU."""
    result = copy.deepcopy(selection)
    result['detector'] = detector
    paths = [r['path'] for r in review['current_source_stats'][:30]]
    require(len(paths)==30 and len(set(paths))==30, 'Invalid reviewed raw sequence')
    for item in result['flat']:
        require(paths[item['index']]==item['path'], 'Flat acquisition index/path differs from review')
        item['hdu'] = review['headers']['raw_bindings'][str(item['index'])][detector]
    for index, item in enumerate(result['bias']):
        require(item['path']==paths[index], 'Approved bias pair differs from first two reviewed biases')
        item['hdu'] = review['headers']['raw_bindings'][str(index)][detector]
    result['bpm']['hdu'] = review['headers']['bpm_bindings'][detector]
    return result


def freeze(paths):
    return {str(Path(p).resolve(strict=True)):digest(p) for p in dict.fromkeys(map(str, paths))}


def unchanged(frozen):
    require(all(digest(p)==value for p,value in frozen.items()), 'Frozen metadata changed')


def prepare(work, reference, pairs, bias, plots, review_path, preparation, command, revision):
    work = work.resolve(strict=True)
    require(not any(work.iterdir()), 'Fresh empty batch directory required')
    state = bridge.admit(reference)
    require(state['receipt']['source_revision']==NATIVE_REVISION, 'Reference native revision differs')
    lineage_path = reference.parent/'lineage.json'
    lineage = json.loads(bridge.small(lineage_path))
    review = json.loads(bridge.small(review_path))
    require(remap(state['selection'],review,'ESO_CCD_#65')==state['selection'], 'Reference HDUs differ from reviewed mappings')
    require(digest(review_path)==lineage['owner_approval']['review_sha256'], 'Header review differs from approved reference')
    prep = json.loads(bridge.small(preparation))
    require(prep['status']=='prepared_verified_copy' and all(prep[k] is True for k in
            ('source_preservation','payload_preservation','existing_cards_preservation')) and
            prep['detector_count']==32, 'Structural BPM preparation not verified')
    require(prep['copy']==state['selection']['bpm']['path'] and
            prep['copy_sha256']==lineage['derived_bpm_sha256'] and
            prep['original_sha256']==lineage['original_bpm_sha256'], 'BPM lineage differs')
    require(state['selection']['detector']=='ESO_CCD_#65' and len(state['selection']['flat'])==20 and
            state['selection']['raw_saturation_adu']==65534 and state['selection']['bpm']['good_value']==1,
            'Require approved CCD65 reference choices')
    command = command.resolve(strict=True)
    fingerprints = state['fingerprints']
    require(str(command)==state['receipt']['argv'][0] and str(command) in fingerprints and
            runner.fingerprint(command)['sha256']==fingerprints[str(command)]['sha256'], 'Qualified binary differs')
    frozen_paths = list(state['frozen'])+[lineage_path,review_path,preparation,command,Path(__file__),
        ROOT/'tools/run-pair-measurements.py', ROOT/'tools/detector-footprint.py',
        ROOT/'tools/plot-pair-qc.py', ROOT/'Pycavi2/pycavi/pycavi/pycavi_pair_qc.py',
        ROOT/'Pycavi2/pycavi/pycavi/pycavi_qc.py']
    for kind,path in (('pairs',pairs),('bias-ron',bias)):
        record = bridge.qc.read_record(path)
        table = bridge.table_from_record(record)
        require(bridge.canonical(table)==bridge.canonical(state['tables'][kind]), 'Reference ASDF/native mismatch')
        list(bridge.qc.traverse_records(path, qc_root=path.parent))
        frozen_paths.extend(path.parent.glob('*.asdf'))
    plot_report = json.loads(bridge.small(plots))
    require(plot_report['status']=='complete' and plot_report['source_sha256']==digest(pairs) and
            plot_report['qc_record_digest']==bridge.qc.read_record(pairs).digest, 'Reference plots differ')
    frozen_paths.append(plots)
    for output in plot_report['outputs']:
        require(digest(output['path'])==output['sha256'], 'Reference plot changed')
        frozen_paths.append(output['path'])
    detectors = ROOT/'config/detectors/omegacam-1x1.toml'
    processing = ROOT/'config/processing/omegacam-characterization.toml'
    paf = ROOT/'mefpp2/ins/mef/config/omegacam.paf'
    frozen_paths.extend((detectors,processing,paf))
    geometry,_,_ = runner.FOOTPRINT.load(detectors,processing)
    ids = [d['id'] for d in sorted(geometry['detector'],key=lambda d:d['native_paf_chip'])]
    require(len(ids)==32 and set(ids)=={f'ESO_CCD_#{n}' for n in range(65,97)}, 'Unexpected OCAM geometry')
    images = {r['path']:fingerprints[r['path']] for r in state['refs']}
    require(len(images)==23, 'Expected 23 shared image files')
    entries = []
    for detector in ids:
        if detector=='ESO_CCD_#65':continue
        directory = work/'detectors'/detector.replace('ESO_CCD_#','CCD')
        measurement = directory/'measurement'; measurement.mkdir(parents=True)
        selected = remap(state['selection'],review,detector)
        selection = measurement/'selection.toml'; selection.write_text(selection_text(selected))
        plan,rois,sources,nroi,identity = runner.prepare(detectors,processing,selection,paf)
        require(nroi==5 and selected['max_rows']==50 and selected['max_loaded_pixels']==206467604,
                'Reviewed ROI/resource limits differ')
        require(set(r['path'] for r in sources)==set(images), 'Batch image set differs')
        (measurement/'plan.tsv').write_text(plan)
        (measurement/'selected-rois.toml').write_text(rois)
        derived = dict(lineage,derived_selection_sha256=digest(selection))
        write(directory/'lineage.json',derived)
        frozen_paths.extend((selection,measurement/'plan.tsv',measurement/'selected-rois.toml',directory/'lineage.json'))
        entries.append(dict(detector=detector,amplifier=identity[1],roi_count=nroi,measurement=str(measurement),
            pair_count=10,native_slot=next(d['native_paf_chip']-1 for d in geometry['detector'] if d['id']==detector),
            flat_hdus=[r['hdu'] for r in selected['flat']],bias_hdus=[r['hdu'] for r in selected['bias']],
            bpm_hdu=selected['bpm']['hdu'],max_loaded_pixels=selected['max_loaded_pixels'],max_rows=selected['max_rows']))
    manifest = dict(schema_version=1,status='prepared_not_executed',source_revision=revision,
        native_revision=NATIVE_REVISION,command=str(command),native_paf=str(paf),entries=entries,
        images=images,frozen=freeze(frozen_paths),reference=dict(detector='ESO_CCD_#65',measurement=str(reference),
        pairs=str(pairs),bias_ron=str(bias),plots=str(plots)),created_at=now())
    write(work/'batch.json',manifest)
    write(work/'execution.json',dict(status='prepared_not_executed',manifest_sha256=digest(work/'batch.json'),
        detectors_processed=0,images_hashed=False))
    (work/'README.md').write_text('''# Serial OCAM raw-pair batch

Keep batch.json, execution.json, shared source verification, all detector native
transport, logs, ASDF records and plots together. CCD65 is reused, not remeasured.
Only execution.json establishes overall completion. Native pending receipts do
not assert final preservation. No fitted gain or near-saturation result is claimed.
Retain while any QC comparison or viewer depends on these records. Removal needs
owner review after required provenance has been retained; no automatic cleanup.
A failed/interrupted attempt is one-use: retain it, never silently resume/overwrite.
''')
    return manifest


def launch(argv, log):
    with log.open('x') as stream:
        process = subprocess.Popen(argv,stdout=stream,stderr=subprocess.STDOUT)
        while True:
            try:return process.wait(timeout=30)
            except subprocess.TimeoutExpired:print('Still measuring:',Path(argv[-1]).parent.parent.name,flush=True)


def verify_outputs(measurement, entry):
    require((measurement/'native/command.complete').read_bytes()==b'raw_pair_tables_complete\n', 'Missing/invalid native marker')
    require({p.name for p in (measurement/'native').iterdir()}==set(OUTPUTS), 'Unexpected native output set')
    rows = {kind:len(bridge.parse_table(bridge.small(measurement/'native'/(kind+'.tsv')),kind)['rows'])
            for kind in ('pairs','bias-ron')}
    require(rows=={'pairs':entry['roi_count']*entry['pair_count'],'bias-ron':entry['roi_count']}, 'Native row count differs')
    json.loads(bridge.small(measurement/'native/configuration.json'))
    return {k+'.tsv':v for k,v in rows.items()}


def image_pass(images, label):
    result=[]
    for i,(path,expected) in enumerate(images.items(),1):
        print(f'{label} shared image {i}/{len(images)}',flush=True)
        value = runner.fingerprint(path)
        require(value['sha256']==expected['sha256'] and value['size']==expected['size'], 'Shared image differs from CCD65: '+path)
        result.append(value)
    return result


def publish(entry, revision, created):
    measurement=Path(entry['measurement']); directory=measurement.parent
    records=directory/'asdf'; records.mkdir()
    persistence=bridge.publish(measurement,records,assessment_id='ocam-batch:'+directory.name+':'+created,
        created_at=created,serializer_revision=revision)
    write(directory/'persistence.json',persistence)
    plots=directory/'plots'; plots.mkdir()
    plotter.render(records/'pairs.asdf',plots)
    return persistence


def execute(work, revision):
    work=work.resolve(strict=True)
    manifest=json.loads(bridge.small(work/'batch.json'))
    report=json.loads(bridge.small(work/'execution.json'))
    require(report['status']=='prepared_not_executed' and not (work/'started.json').exists(), 'Batch is one-use; retain previous attempt')
    require(manifest['source_revision']==revision and report['manifest_sha256']==digest(work/'batch.json'), 'Prepared manifest/revision differs')
    # Exclusive claim survives interruption before any child or source read.
    with (work/'started.json').open('x') as stream:json.dump(dict(started_at=now()),stream)
    report.update(status='running',entries=[],detectors_processed=0,source_preservation=False)
    write(work/'execution.json',report)
    before=None;after=None;error=None;receipts=[]
    try:
        unchanged(manifest['frozen'])
        before=image_pass(manifest['images'],'Before')
        write(work/'shared-before.json',before)
        for entry in manifest['entries']:
            unchanged(manifest['frozen'])
            measurement=Path(entry['measurement']); (measurement/'native').mkdir()
            argv=[manifest['command'],manifest['native_paf'],str(measurement/'selected-rois.toml'),str(measurement/'plan.tsv'),str(measurement/'native')]
            receipt=dict(status='running',mode='raw_pair_measurements',source_revision=manifest['native_revision'],
                detector=entry['detector'],amplifier=entry['amplifier'],roi_count=entry['roi_count'],
                source_preservation=False,detectors_processed=0,argv=argv,
                inputs=before+[runner.fingerprint(measurement/'selection.toml')],
                batch_manifest_sha256=report['manifest_sha256'])
            receipts.append((measurement,receipt));write(measurement/'execution.json',receipt)
            print('Measuring:',entry['detector'],flush=True)
            receipt['native_exit_status']=launch(argv,measurement/'command.log')
            require(receipt['native_exit_status']==0, 'Native command failed: '+entry['detector'])
            receipt['output_rows']=verify_outputs(measurement,entry)
            receipt['outputs']=[runner.fingerprint(measurement/'native'/name) for name in OUTPUTS]
            receipt['status']='native_complete_pending_batch_verification'
            write(measurement/'execution.json',receipt)
            report['entries'].append(dict(detector=entry['detector'],status=receipt['status']))
            write(work/'execution.json',report)
    except Exception as exc:
        error=exc
    # Always attempt final source verification once after a successful initial pass,
    # including native failure. No ASDF publication until the entire native phase passes.
    if before is not None:
        try:
            after=image_pass(manifest['images'],'After')
            write(work/'shared-after.json',after)
            require(before==after,'Shared source stat/hash changed during native batch')
            unchanged(manifest['frozen'])
            report['source_preservation']=True
        except Exception as exc:
            if error is None:error=exc
            else:report['verification_error']=repr(exc)
    try:
        if error is not None:raise error
        verification=dict(status='passed',before_sha256=digest(work/'shared-before.json'),
            after_sha256=digest(work/'shared-after.json'),images=len(before),hash_passes_per_image=2,
            scope='native_measurement_interval; metadata-only ASDF/plot stage follows')
        write(work/'shared-verification.json',verification)
        # Complete all native receipts before touching ASDF. Bridge validates every
        # table binding/ROI/setting before publication, using the shared frozen hashes.
        for measurement,receipt in receipts:
            receipt.update(status='complete_for_owner_inspection',source_preservation=True,detectors_processed=1,
                batch_verification=dict(path=str(work/'shared-verification.json'),sha256=digest(work/'shared-verification.json')))
            write(measurement/'execution.json',receipt)
            try:bridge.admit(measurement)
            except Exception:
                receipt['status']='failed';write(measurement/'execution.json',receipt);raise
        for entry in manifest['entries']:
            print('Persisting ASDF and plots:',entry['detector'],flush=True)
            result=publish(entry,revision,manifest['created_at'])
            require(result['status']=='complete' and result['roundtrip_exact'] and result['metadata_preservation'], 'ASDF completion failed')
            report['entries'][report['detectors_processed']]['status']='complete_for_owner_inspection'
            report['detectors_processed']+=1
            write(work/'execution.json',report)
        unchanged(manifest['frozen'])
        for item in after:
            stat=Path(item['path']).stat()
            require((stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)==tuple(item[k] for k in
                    ('device','inode','size','mtime_ns','ctime_ns')), 'Source changed during metadata-only stage')
        report.update(status='complete_for_owner_inspection',hash_passes_per_image=2,
            raw_FITS_opened_by_persistence=False,reference_detector_reused=True,completed_at=now())
    except Exception as exc:
        report.update(status='failed',error=repr(exc))
        for measurement,receipt in receipts:
            if receipt['status']!='complete_for_owner_inspection':
                receipt.update(status='failed',error=repr(exc));write(measurement/'execution.json',receipt)
        raise
    finally:
        write(work/'execution.json',report)
        print('BATCH STATUS:',report['status'],flush=True)
        print('RETAINED BATCH:',work,flush=True)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--source-revision',required=True)
    parser.add_argument('--execute-prepared',action='store_true')
    for name in ('reference','pairs','bias','plots','review','preparation','command'):
        parser.add_argument('--'+name,type=Path)
    args=parser.parse_args()
    require(len(args.source_revision)==40 and all(c in '0123456789abcdef' for c in args.source_revision),'Exact source revision required')
    require(os.getpriority(os.PRIO_PROCESS,0)>=10,'Run batch with niceness >=10')
    def offline(event, arguments):
        if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo','socket.sendto'):
            raise RuntimeError('Network disabled during batch: '+event)
    sys.addaudithook(offline)
    if args.execute_prepared:execute(args.run,args.source_revision)
    else:
        require(all(getattr(args,name) for name in ('reference','pairs','bias','plots','review','preparation','command')), 'Preparation paths required')
        manifest=prepare(args.run,args.reference,args.pairs,args.bias,args.plots,args.review,args.preparation,args.command,args.source_revision)
        print(json.dumps(dict(status=manifest['status'],detectors=len(manifest['entries']),shared_images=len(manifest['images']),
            entries=manifest['entries']),indent=2))


if __name__=='__main__':main()
