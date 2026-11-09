"""Serial detector-characterization coordinator; native services own all pixels/QC.

The manifest joins detector BPM candidates and linearity measurements. It does
not claim final MEF assembly, scientific acceptance or correction adoption.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
try:
    from . import pycavi_linearity_recipe as preparation
    from . import pycavi_bpm_linearity_native as native
except ImportError:
    import pycavi_linearity_recipe as preparation
    import pycavi_bpm_linearity_native as native
require = preparation.require


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata_unchanged(expected):
    require(all(digest(name) == value for name, value in expected.items()), 'Recipe/dependency metadata changed')


def stat_identity(path):
    s = Path(path).stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_mode]


class BatchInputs:
    """Hash shared images once at each batch boundary; stat-guard every stage."""
    def __init__(self, baseline, receipt):
        self.images = {name: preparation.image_fingerprint(name) for name in baseline}
        require(all(self.images[name]['sha256'] == value for name, value in baseline.items()),
                'Input differs from preserved scientific dependency')
        with receipt.open('x') as stream:
            stream.write(preparation.canonical(self.images)+'\n')
        self.reference = dict(path=str(receipt), sha256=digest(receipt))

    def observe(self, path):
        path = str(path)
        require(path in self.images and stat_identity(path) == self.images[path]['stat'],
                'Batch input changed: '+path)
        return self.images[path]

    def verify(self):
        require(all(preparation.image_fingerprint(name) == before for name, before in self.images.items()),
                'Batch input bytes or identity changed')
        require(digest(self.reference['path']) == self.reference['sha256'], 'Batch input receipt changed')


def execute(plan):
    run = Path(plan['run'])
    require(not any(run.iterdir()), 'Fresh empty combined run required')
    require(os.getpriority(os.PRIO_PROCESS, 0) >= 10, 'Execute the batch at niceness >=10')
    metadata_unchanged(plan['metadata'])
    metadata_stats = {name: stat_identity(name) for name in plan['metadata']}
    binaries = {name: digest(path) for name, path in plan['native'].items()}
    binary_stats = {path: stat_identity(path) for path in plan['native'].values()}
    # The current BPM interface represents one captured instant to whole seconds.
    started = datetime.now(timezone.utc).replace(microsecond=0).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    controls = Path(plan['layout']['orchestration'])/run.name
    controls.mkdir()
    with (controls/'request.json').open('x') as stream:
        json.dump(dict(created_at=started, native_source_revision=plan['source_revision'],
                       configuration_sources=plan['configuration_sources']), stream, indent=2)
        stream.write('\n')
    report = dict(schema_version=1, scope='detector_characterization', status='failed',
        scientific_acceptance=False, final_mef_state='not_assembled', linearity_correction='not_applied',
        created_at=started, native_source_revision=plan['source_revision'], product_root=str(run), directories=plan['layout'],
        configuration_sources=plan['configuration_sources'], coordinator_sources=plan['coordinator_sources'],
        binary_sha256=binaries, detectors=[])
    try:
        inputs = BatchInputs(plan['baseline'], run/'inputs.json')
        report['batch_inputs'] = inputs.reference
        for index, entry in enumerate(plan['entries']):
            detector = entry['detector']['detector_id']
            print(f'BPM_LINEARITY_DETECTOR {index+1}/{len(plan["entries"])} {detector}', flush=True)
            require(all(stat_identity(name) == value for name, value in metadata_stats.items()), 'Dependency metadata changed')
            require(all(stat_identity(name) == value for name, value in binary_stats.items()), 'Native producer changed')
            destination = run/f'detector-{index:03d}'
            destination.mkdir()
            prepared = destination/'preparation'
            prepared.mkdir()
            layout = dict(plan['layout'], run_key=entry['key']+'/preparation')
            result = preparation.prepare_detector(entry['dependencies'], plan['native']['preparation'], prepared,
                resolved=plan['resolved'], source_revision=plan['source_revision'], assessment_id=detector,
                created_at=started, layout=layout, configuration_sources=plan['configuration_sources'],
                publication='native', preservation=inputs)
            # Keep the admitted prior mask for both measurements and BPM fitting.
            # The new BPM is a candidate, never fed back into this population.
            bpm = native.characterize_bpm(plan, entry, destination, started, inputs)
            report['detectors'].append(dict(detector_id=detector,
                configuration_detector=entry['detector']['configuration_detector'],
                bpm_loaded_input_pixels=entry['bpm_loaded_pixels'], input_pixel_limit=entry['dependencies']['selection']['max_loaded_pixels'],
                preparation=result['product'], bpm=bpm))
        metadata_unchanged(plan['metadata'])
        require(all(digest(path) == binaries[name] for name, path in plan['native'].items()), 'Native producer changed')
        inputs.verify()
        report.update(status='detector_characterization_complete_for_owner_inspection', input_preservation=True)
        # The parent receipt resolves the children’s explicitly pending batch check.
        partial = run/'manifest.json.partial'
        with partial.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.link(partial, run/'manifest.json')
        partial.unlink()
        return report
    except Exception as error:
        report['status'] = 'failed'
        report['error'] = repr(error)
        raise
    finally:
        with (run/'execution.json').open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')


def read_manifest(path):
    """Verify the joined saved QC only; never open FITS or run an estimator."""
    try:
        from . import pycavi_linearity_native_archive as archive
    except ImportError:
        import pycavi_linearity_native_archive as archive
    path = Path(path).resolve(strict=True)
    report = json.loads(path.read_text())
    require(report['schema_version'] == 1 and report['scope'] == 'detector_characterization' and
            report['status'] == 'detector_characterization_complete_for_owner_inspection' and
            report['input_preservation'] is True and report['scientific_acceptance'] is False and
            report['linearity_correction'] == 'not_applied' and report['final_mef_state'] == 'not_assembled',
            'Incomplete or incompatible detector-characterization manifest')
    original = Path(report['product_root'])
    def local(name):
        member = (path.parent/Path(name).relative_to(original)).resolve(strict=True)
        require(member.is_relative_to(path.parent), 'Manifest member escapes product root')
        return member
    require(digest(local(report['batch_inputs']['path'])) == report['batch_inputs']['sha256'], 'Batch input receipt changed')
    saved, seen = [], set()
    for entry in report['detectors']:
        require(entry['detector_id'] not in seen, 'Duplicate detector manifest entry')
        seen.add(entry['detector_id'])
        prepared = entry['preparation']
        prep_path = local(prepared['path'])
        require(digest(prep_path) == prepared['sha256'], 'Saved preparation ASDF changed')
        value = archive.read_product(prep_path)
        bpm = entry['bpm']
        bpm_path = local(bpm['asdf'])
        require(digest(bpm_path) == bpm['sha256'][bpm['asdf']], 'Saved BPM ASDF changed')
        q = native.native_qc.read(bpm_path)
        detector = q['characterization']['detectors'][0]
        require(q['provenance']['operation'] == 'cal.bpm' and
                q['extensions']['record_scope'] == 'one_final_primary_image_product' and
                value['detector'] == detector['detector_id'] == entry['detector_id'] and
                detector['configuration_detector'] == entry['configuration_detector'] and
                q['provenance']['producer']['source_revision'] == report['native_source_revision'] and
                q['file']['location'] == bpm['fits'], 'Joined detector/product mapping differs')
        saved.append(dict(detector_id=entry['detector_id'], preparation=value, bpm=q))
    require(saved, 'Empty characterization manifest')
    return dict(manifest=report, detectors=saved, FITS_integrity_rechecked=False)
