"""Linearity preparation orchestration and native configuration transport.

Detector and processing TOMLs are authoritative. The completed master's typed
snapshot carries unused legacy/header fields through the existing native TOML
reader; all active numerical settings must agree with the resolved TOMLs.
No independently edited PAF, pixel estimator, model or plotting implementation.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import struct
try:
    from . import pycavi_linearity_config as configuration
except ImportError:
    import pycavi_linearity_config as configuration


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))


def native_configuration(resolved, master_snapshot):
    """Generate the native compatibility TOML from validated, agreeing settings.

    Reject a master made with different scan/trim/stack settings. Non-operation
    header/legacy fields retain exact typed values from its frozen snapshot.
    This function never opens the historical PAF or supplies scientific defaults.
    """
    require(isinstance(master_snapshot, dict), 'Explicit master configuration snapshot required')
    snapshot = deepcopy(master_snapshot)
    decoded = {}
    for key, item in snapshot.items():
        require(type(key) is str and isinstance(item, dict) and set(item) == {'type','value'},
                'Malformed typed native snapshot')
        kind, value = item['type'], item['value']
        if kind == 'string':
            require(type(value) is str and '\0' not in value, 'Invalid native string')
        elif kind == 'int':
            require(type(value) is int, 'Invalid native integer')
        else:
            require(kind in ('float32-bits','float64-bits') and type(value) is str and
                    len(value) == (8 if kind == 'float32-bits' else 16), 'Invalid native float bits')
            value, = struct.unpack('>f' if kind == 'float32-bits' else '>d', bytes.fromhex(value))
            require(math.isfinite(value), 'Nonfinite native snapshot setting')
        decoded[key] = value
    controls = resolved['controls']; detectors = resolved['detectors']
    require(decoded.get('MEF.NCHIPS') == len(detectors), 'Master/native detector count differs')
    # These are the legacy bias service's fixed frame-admission bounds, already
    # used by the preserved masters. A different policy needs a reviewed backend.
    require(controls['bias_mean_min_adu'] == 0 and controls['bias_mean_max_adu'] == 1000,
            'Legacy master builder does not implement different admission bounds')
    desired = {'MEF.USE.PRESCAN': detectors[0]['native_settings']['use_prescan'],
               'MEF.USE.OVERSCAN': detectors[0]['native_settings']['use_overscan'],
               'MEF.SCANREJ.MIN': detectors[0]['native_settings']['rejection'][0],
               'MEF.SCANREJ.MAX': detectors[0]['native_settings']['rejection'][1],
               'MEF.BIAS.FRAMENUM.MIN': controls['bias_min_frames'],
               'MEF.BIAS.KAPPA1': controls['bias_stack_kappa']}
    for d in detectors:
        g = d['native_settings']; chip = d['configuration_detector']+1
        for key in ('use_prescan','use_overscan','rejection'):
            require(g[key] == detectors[0]['native_settings'][key], 'Inconsistent global native scan settings')
        for band in ('prescan','overscan'):
            for part,value in zip(('MIN','MAX'),g[band]):
                desired[f'MEF.{band.upper()}.X.{part}.CHIP{chip}'] = value
        for part,value in zip(('X.MIN','X.MAX','Y.MIN','Y.MAX'),g['trim']):
            desired[f'MEF.CROP.{part}.CHIP{chip}'] = value
    for key,value in desired.items():
        require(key in decoded and type(decoded[key]) is type(value) or
                key in decoded and type(decoded[key]) in (int,float) and type(value) in (int,float),
                'Missing/incompatible native setting: '+key)
        require(decoded[key] == value, 'Master configuration conflicts with TOML: '+key)
        decoded[key] = value
    lines = ['# Generated transport: detector/processing TOMLs select active settings.',
             'schema_version = 1', '', '[native]']
    for key,value in decoded.items():
        # Native compatibility fields have exact declared types. Preserve real
        # notation even when the matching TOML scientific value was an integer.
        kind = snapshot[key]['type']
        text = json.dumps(value, ensure_ascii=True) if kind == 'string' else (
            repr(float(value)) if kind.startswith('float') else str(value))
        lines.append(json.dumps(key)+' = '+text)
    return '\n'.join(lines)+'\n'


def region_toml(regions):
    require(bool(regions), 'Explicit regions required')
    return 'roi_schema_version = 1\n'+''.join('\n[[roi]]\n'+''.join(
        json.dumps(k)+' = '+json.dumps(v)+'\n' for k,v in region.items()) for region in regions)


def native_plan(resolved, selection, sites):
    """Explicit dataset binding -> native transport; no pixel/EXPTIME reads."""
    s = deepcopy(selection); c = resolved['controls']
    ds = [d for d in resolved['detectors'] if d['detector_id'] == s['detector']]
    require(len(ds)==1, 'Unknown selected detector'); d=ds[0]
    require([s['bin_x'],s['bin_y']] == resolved['binning'], 'Binning conflict')
    for old,new in [('raw_saturation_adu','raw_saturation_adu'),('pair_time_tolerance_s','pair_time_tolerance_s'),
                    ('with_mad','with_mad'),('reject_bits','reject_bits')]:
        require(s[old] == c[new], 'Archived selection conflicts with processing TOML: '+old)
    bpm = s['bpm']; require(bpm['encoding']==c['mask_encoding'], 'BPM encoding conflict')
    if bpm['encoding']=='binary':require(bpm['good_value']==c['binary_good_value'], 'BPM polarity conflict')
    require(len(s['bias'])==2 and 2<=len(s['flat'])<=64 and len(s['flat'])%2==0, 'Explicit flat pairs/two raw RON biases required')
    require(type(s['max_loaded_pixels']) is int and s['max_loaded_pixels']>0 and
            type(s['max_rows']) is int and s['max_rows']>=len(d['rois'])*len(s['flat'])//2,
            'Insufficient explicit resource limits')
    refs = s['flat']+s['bias']+([] if bpm['encoding']=='omitted' else [bpm])
    require(len({r['asset'] for r in refs})==len(refs), 'Duplicate dataset asset')
    require(len({(r['path'],r['hdu']) for r in refs})==len(refs), 'Duplicate dataset path/HDU')
    require(len({r['index'] for r in s['flat']})==len(s['flat']), 'Duplicate original input index')
    for r in refs:
        require(type(r['hdu']) is int and 0<=r['hdu']<128 and Path(r['path']).is_absolute(), 'Invalid explicit path/HDU')
    ids = [r['pair'] for r in s['flat']]
    require(all(ids.count(v)==2 for v in ids), 'Invalid pair multiplicity')
    require(len(sites)>0 and len({tuple(p['active_pixel']) for p in sites})==len(sites), 'Duplicate/empty direct sites')
    points=[]; crop=d['retained']
    for p in sites:
        require(p['detector']==d['detector_id'] and p['amplifier']==d['amplifier_id'] and
                p['configuration_detector']==d['configuration_detector'], 'Direct site identity/slot conflict')
        x,y=p['active_pixel'];require(p['raw_pixel']==[x+crop[0]-1,y+crop[2]-1], 'Direct site raw/active mapping conflict')
        require(any(r['id']==p['source_roi'] and r['xmin']<=x<=r['xmax'] and r['ymin']<=y<=r['ymax'] for r in d['rois']),
                'Direct site not inside its named ROI')
        points.append(dict(id=p['source_roi'],detector=d['detector_id'],amplifier=d['amplifier_id'],xmin=x,xmax=x,ymin=y,ymax=y))
    keys=s['header_keys']; w,h=d['raw_size']
    settings=dict(detector=d['detector_id'],amplifier=d['amplifier_id'],slot=d['configuration_detector'],
        readout=s['readout_id'],identity_key=keys['identity'],amplifier_key=keys['amplifier'],bin_x_key=keys['bin_x'],
        bin_y_key=keys['bin_y'],bin_x=s['bin_x'],bin_y=s['bin_y'],mask_encoding=bpm['encoding'],
        good_value=c['binary_good_value'] if bpm['encoding']=='binary' else 0,mask_registry=bpm.get('registry','-'),
        reject_bits=c['reject_bits'],saturation=c['raw_saturation_adu'],tolerance=c['pair_time_tolerance_s'],
        max_pixels=s['max_loaded_pixels'],max_rows=s['max_rows'],exposure_key=keys['exposure'],exposure_hdu=s['exposure_hdu'],
        with_mad=int(c['with_mad']),schema='raw-pair-plan-v1',crop=','.join(map(str,crop)),raw_width=w,raw_height=h)
    def line(values):
        values=list(map(str,values));require(all(v and not any(ch in v for ch in '\t\n\r\0') for v in values), 'Invalid native transport cell')
        return '\t'.join(values)+'\n'
    text=''.join(line((k,v)) for k,v in settings.items())
    text+=''.join(line(('flat',r['path'],r['hdu'],r['asset'],r['index'],r['pair'])) for r in s['flat'])
    text+=''.join(line(('bias',r['path'],r['hdu'],r['asset'])) for r in s['bias'])
    if bpm['encoding']!='omitted':text+=line(('bpm',bpm['path'],bpm['hdu'],bpm['asset']))
    return dict(plan=text,rois=region_toml(d['rois']),sites=region_toml(points),detector=d)


def preparation_dependencies(source_samples, handoff_path, resolved):
    """Admit preserved inputs without opening FITS or rebuilding a calibration."""
    try:
        from . import pycavi_linearity_preparation_qc as archive
    except ImportError:
        import pycavi_linearity_preparation_qc as archive
    qc, sample, pair = archive.qc, archive.sample, archive.pair
    source_samples = Path(source_samples).resolve(strict=True)
    frozen = archive.graph(source_samples)
    table = sample.read_product(source_samples)
    record = qc.read_record(source_samples)
    origin = record.as_dict()['extensions']['corrected_sample_origin']
    entry = origin['entry']; selection = deepcopy(entry['selection'])
    selection['detector'] = entry['detector']
    handoff_path = Path(handoff_path).resolve(strict=True)
    handoff_bytes = pair.small(handoff_path); handoff = json.loads(handoff_bytes)
    config_path = Path(handoff['configuration_record']).resolve(strict=True)
    config_bytes = pair.small(config_path); snapshot = json.loads(config_bytes)
    require(snapshot == handoff['configuration'] == origin['native_configuration'],
            'Master, extraction and handoff configurations differ')
    native = native_configuration(resolved, snapshot)
    transport = native_plan(resolved, selection, entry['population'])
    master = entry['master']
    require(handoff['detector_id'] == entry['detector'] and
            handoff['configuration_detector'] == entry['configuration_detector'] and
            handoff['output'] == master['product'] and handoff['output_hdu'] == master['hdu'] and
            handoff['readout_id'] == selection['readout_id'] and
            [handoff['bin_x'], handoff['bin_y']] == [selection['bin_x'], selection['bin_y']],
            'Master handoff identity/readout differs')
    records = list(qc.traverse_records(source_samples, qc_root=source_samples.parent))
    masters = [r for r in records if r.digest == origin['master_qc_digest']]
    require(len(masters) == 1, 'Preserved master QC missing')
    mt = masters[0].as_dict()
    require(mt['file']['location'] == master['product'] and
            mt['provenance']['configuration_id'] == 'sha256:'+pair.sha(canonical(snapshot).encode()) and
            mt['provenance']['producer'] == handoff['producer'], 'Master QC configuration/producer mismatch')
    members = handoff['inputs']
    require(len(members) >= resolved['controls']['bias_min_frames'] and
            len(mt['inputs']) == len(members)+1, 'Incomplete master memberships')
    biases = []
    baseline = {master['product']: origin['master_fingerprint']['sha256']}
    leaves = {r.digest:r.as_dict() for r in records}
    for i, (member, link) in enumerate(zip(members, mt['inputs'])):
        require(type(member['accepted']) is int and member['accepted'] in (0,1) and
                link['file_id'] == member['path'] and
                link['participation']['status'] == ('used' if member['accepted'] else 'rejected'),
                'Master membership differs')
        # The original sequence indexes its biases before its flat exposures.
        biases.append(dict(index=i, path=member['path'], asset=Path(member['path']).name,
                           hdu=handoff['input_hdu'], accepted=member['accepted']))
    require(sum(b['accepted'] for b in biases) >= resolved['controls']['bias_min_frames'],
            'Insufficient accepted master inputs')
    # Bias QC intentionally predates image digests. Recover those fingerprints
    # from the completed bias run's preserved outer receipt when needed.
    bias_baseline = {}
    bias_paths = {b['path'] for b in biases}
    if any(not any(r['file']['location']==path and r['file']['sha256'] is not None
                   for r in leaves.values()) for path in bias_paths):
        receipts = [p for p in (handoff_path.parent/'overall-execution.json',
                               handoff_path.parent.parent/'overall-execution.json') if p.is_file()]
        matches = []
        for receipt_path in receipts:
            payload = pair.small(receipt_path); receipt = json.loads(payload)
            inputs = receipt.get('inputs', {})
            if (receipt.get('status') == 'complete_for_owner_inspection' and
                receipt.get('source_preservation') is True and receipt.get('preservation') and
                all(receipt['preservation'].values()) and isinstance(inputs,dict) and
                bias_paths.issubset(inputs)):
                matches.append((receipt_path,payload,inputs))
        require(len(matches)==1,'Require one completed preserved bias receipt with input digests')
        receipt_path,payload,inputs=matches[0]
        frozen[str(receipt_path)] = pair.sha(payload)
        bias_baseline={path:inputs[path]['sha256'] for path in bias_paths}
    for path in [r['path'] for r in selection['flat']]+[selection['bpm']['path']]+[b['path'] for b in biases]:
        matches = [r['file']['sha256'] for r in leaves.values()
                   if r['file']['location']==path and r['file']['sha256'] is not None]
        if path in bias_baseline:matches.append(bias_baseline[path])
        require(bool(matches) and len(set(matches))==1,
                'Missing/conflicting preserved image fingerprint: '+path)
        baseline[path] = matches[0]
    require(all(b['index'] not in {r['index'] for r in selection['flat']} for b in biases),
            'Original bias/flat indices overlap')
    frozen[str(handoff_path)] = pair.sha(handoff_bytes)
    frozen[str(config_path)] = pair.sha(config_bytes)
    require(all(Path(p).is_absolute() and type(d) is str and len(d)==64 for p,d in baseline.items()),
            'Invalid preserved image baseline')
    return dict(source_samples=str(source_samples), handoff_path=str(handoff_path), selection=selection, biases=biases,
                master=master, master_snapshot=snapshot, configuration=native, transport=transport,
                baseline=baseline, metadata_sha256={str(p):d for p,d in frozen.items()},
                expected_samples=table, handoff=handoff)


def image_fingerprint(path):
    """Stream immutable input bytes; retain inode/size/time as well as digest."""
    path = Path(path); before = path.stat(); h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024), b''):h.update(block)
    after = path.stat()
    def stat(s):return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_mode]
    require(stat(before)==stat(after), 'Image changed while fingerprinting: '+str(path))
    return dict(sha256=h.hexdigest(), stat=stat(after))


def prepare_detector(dependencies, executable, directory, *, resolved, source_revision,
                     assessment_id, created_at):
    """Run the native preparation and publish one immutable ASDF product.

    Dependencies are the result of preparation_dependencies. The command reads
    all supplied biases for traces and paired flats for new ROI measurements.
    Existing masters are reused. No master construction, physical fit or plot.
    """
    import subprocess
    try:
        from . import pycavi_linearity_preparation_qc as archive
    except ImportError:
        import pycavi_linearity_preparation_qc as archive
    directory = Path(directory).resolve(strict=True)
    require(not any(directory.iterdir()), 'Fresh empty preparation directory required')
    executable = Path(executable).resolve(strict=True)
    d = dependencies
    # Re-admit all caller-owned metadata rather than trusting a stale dictionary.
    admitted = preparation_dependencies(d['source_samples'], d['handoff_path'], resolved)
    require(canonical(d)==canonical(admitted),
            'Preparation dependencies changed after admission')
    before = {}; report = dict(status='failed', fitted=False, scientific_acceptance=False)
    binary_digest = archive.pair.sha(executable.read_bytes())
    def metadata_preserved():
        return all(archive.pair.sha(archive.pair.small(Path(p)))==digest
                   for p,digest in d['metadata_sha256'].items())
    try:
        require(metadata_preserved(), 'Preparation metadata changed')
        for path, digest in d['baseline'].items():
            before[path] = image_fingerprint(path)
            require(before[path]['sha256']==digest, 'Input differs from preserved archive: '+path)
        for name, text in [('native.toml',d['configuration']), ('plan.tsv',d['transport']['plan']),
                           ('rois.toml',d['transport']['rois']), ('sites.toml',d['transport']['sites'])]:
            (directory/name).write_text(text)
        bias_text='input_index\thdu\tasset\tpath\taccepted\n'
        for b in d['biases']:
            cells=[str(b[k]) for k in ('index','hdu','asset','path','accepted')]
            require(all(not any(c in v for c in '\t\r\n\0') for v in cells), 'Invalid bias transport cell')
            bias_text+='\t'.join(cells)+'\n'
        (directory/'biases.tsv').write_text(bias_text)
        native = directory/'native';native.mkdir()
        argv = [str(executable),*[str(directory/n) for n in ('native.toml','rois.toml','sites.toml','plan.tsv')],
                d['master']['product'],str(d['master']['hdu']),d['master']['product'],
                str(directory/'biases.tsv'),str(native)]
        report['argv']=argv;report['native_binary_sha256']=binary_digest
        with (directory/'native.log').open('x') as log:
            subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=True)
        after = {p:image_fingerprint(p) for p in before}
        require(before==after and metadata_preserved() and
                archive.pair.sha(executable.read_bytes())==binary_digest, 'Preparation source preservation failed')
        output = directory/'asdf';output.mkdir()
        product = archive.publish(native,d['source_samples'],output,resolved=resolved,
            selection=d['selection'],biases=d['biases'],master_snapshot=d['master_snapshot'],
            assessment_id=assessment_id,created_at=created_at,source_revision=source_revision,
            dependency_evidence=dict(handoff=d['handoff'],metadata_sha256=d['metadata_sha256'],
                                     images=before,native_binary_sha256=binary_digest))
        require(metadata_preserved(), 'Metadata changed during publication')
        report.update(status='complete_for_owner_inspection',product=product,
                      inputs=before,after_inputs=after,source_preservation=True)
        return report
    except Exception as error:
        report['error']=repr(error);raise
    finally:
        (directory/'execution.json').write_text(json.dumps(report,indent=2)+'\n')
