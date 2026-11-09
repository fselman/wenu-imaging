"""Native final-product command and independent lossless QC mapping checks."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import subprocess
try:
    from . import pycavi_native_product_qc as native_qc
    from .pycavi_qc import require
except ImportError:
    import pycavi_native_product_qc as native_qc
    from pycavi_qc import require


def read_product(path):
    """Read a self-contained final QC container, without raw or detector files."""
    q = native_qc.read(path)
    require(q['extensions']['record_scope'] == 'one_final_MEF_product' and
            q['provenance']['operation'] == 'cal.bpm' and
            q['provenance']['producer']['name'] == 'mefpp_bpm_assemble', 'Expected assembled BPM QC')
    evidence = q['extensions']['native_evidence']
    children = [native_qc.read(io.BytesIO(e['text'].encode())) for e in evidence
                if e['format'] == 'product-qc-asdf/2.0.0']
    maps = [e['text'] for e in evidence if e['name'] == 'image-plane-map' and e['format'] == 'mef-bpm-plane-map/1']
    require(children and len(maps) == 1 and len(evidence) == len(children)+1, 'Incomplete assembly evidence')
    require(len(q['characterization']['detectors']) == len(children), 'Assembled detector count differs')
    seen, planes = set(), []
    for index, child in enumerate(children):
        detector = deepcopy(child['characterization']['detectors'][0])
        detector_id = detector['detector_id']
        require(detector_id not in seen and child['extensions']['record_scope'] == 'one_final_primary_image_product',
                'Duplicate or incompatible source detector')
        seen.add(detector_id)
        detector['output_hdu'] = index+1
        for metric in detector['measurements']:
            metric['sources'] = [q['file']['id'] if v == child['file']['id'] else v for v in metric['sources']]
        require(detector == q['characterization']['detectors'][index], 'Assembled product QC values or mapping differ')
        require(child['provenance']['configuration'] == q['provenance']['configuration'], 'Detector configuration differs')
    for name, field in [('inputs', 'participation_by_detector'), ('embedded_input_records', 'detectors'),
                        ('calibrations', 'detector_bindings')]:
        expected = deepcopy(children[0][name])
        for i, row in enumerate(expected):
            row[field] = []
            for child in children:
                source = child[name][i]
                require({k: v for k, v in source.items() if k != field} ==
                        {k: v for k, v in row.items() if k != field}, 'Common input/calibration metadata differ')
                row[field].extend(source[field])
        require(q[name] == expected and all(len(c[name]) == len(expected) for c in children),
                'Assembled input/calibration records differ')
    for line in maps[0].splitlines():
        detector, source_hdu, output_hdu, role = line.split('\t')
        planes.append(dict(detector_id=detector, source_hdu=int(source_hdu), output_hdu=int(output_hdu), role=role))
    expected = [(d['detector_id'], 0, 'BPM') for d in q['characterization']['detectors']]
    for detector in q['characterization']['detectors']:
        rows = [p for p in planes if p['detector_id'] == detector['detector_id'] and p['source_hdu']]
        roles = ['COVERAGE', 'NSAMPLE', 'NEWFLAGS', 'SELECTION']
        require(len(rows) in (4, 5) and [p['role'] for p in rows[:4]] == roles and
                (len(rows) == 4 or rows[-1]['role'] in ('PRIORSEL', 'PRIORFLAGS')), 'Invalid diagnostic plane map')
        expected += [(detector['detector_id'], i+1, row['role']) for i, row in enumerate(rows)]
    require([(p['detector_id'], p['source_hdu'], p['role']) for p in planes] == expected and
            [p['output_hdu'] for p in planes] == list(range(1, len(planes)+1)), 'Image plane order differs')
    return dict(qc=q, detector_products=children, image_planes=planes, FITS_integrity_rechecked=False)


def assemble_products(plan, report, controls):
    run = Path(plan['run'])
    policy = plan['assembly']
    fits = run/f'CMDP.{report["created_at"]}.001.fits'
    sidecar, log = fits.with_suffix('.asdf'), fits.with_suffix('.log')
    manifest = controls/'assembly.tsv'
    rows = []
    for member in report['detectors']:
        fields = [member['detector_id'], str(member['configuration_detector']), member['bpm']['fits'], member['bpm']['asdf']]
        require(all(not any(c in value for c in '\t\n\r\0') for value in fields), 'Invalid assembly transport')
        rows.append('\t'.join(fields)+'\n')
    with manifest.open('x') as stream:
        stream.write(''.join(rows))
    argv = [plan['native']['assembly'], str(manifest), str(fits), policy['reference_detector'], str(log),
            report['created_at'], plan['source_revision'], plan['recipe_path']]
    console = Path(plan['layout']['logs'])/run.name/'assembly.log'
    with console.open('x') as stream:
        subprocess.run(argv, cwd=plan['layout']['orchestration'], stdout=stream, stderr=subprocess.STDOUT, check=True)
    saved = read_product(sidecar)
    q = saved['qc']
    require(q['file']['location'] == str(fits) and q['provenance']['producer']['source_revision'] == policy['source_revision'] and
            q['provenance']['recipe_configuration']['snapshot'] == Path(plan['recipe_path']).read_text(), 'Final producer/recipe differs')
    require([c['characterization']['detectors'][0]['detector_id'] for c in saved['detector_products']] ==
            [m['detector_id'] for m in report['detectors']], 'Final catalogue order differs')
    for member, embedded in zip(report['detectors'], q['extensions']['native_evidence']):
        require(embedded['text'] == Path(member['bpm']['asdf']).read_text(), 'Original native QC evidence differs')
    return dict(fits=str(fits), asdf=str(sidecar), log=str(log),
                sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (fits, sidecar, log)})
