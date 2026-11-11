"""Project saved native characterization onto the existing QC display contract.

The saved reader verifies the manifest and original evidence. This adapter only
selects stored values; it never opens images, runs commands or fits a model.
"""
from copy import deepcopy
import json
from pathlib import Path

import pycavi_bpm_linearity_recipe as recipe
import pycavi_measurement_display as measurements

require = recipe.require


class ManifestReader:
    def __init__(self, path, progress=print):
        self.path = Path(path).resolve(strict=True)
        progress('Validating saved BPM/linearity manifest and ASDF evidence')
        saved = recipe.read_manifest(self.path)
        self.manifest = saved['manifest']
        self.inputs = {str(self.path): recipe.digest(self.path)}
        self.records = {}
        self.bpm = {}
        self.identities = {}
        for member, decoded in zip(self.manifest['detectors'], saved['detectors']):
            path = self.local(member['preparation']['path'])
            self.inputs[str(path)] = member['preparation']['sha256']
            bpm_path = None
            if member['bpm'].get('state') not in ('skipped_input_bpm','skipped_measurement_only'):
                bpm_path = self.local(member['bpm']['asdf'])
                self.inputs[str(bpm_path)] = member['bpm']['sha256'][member['bpm']['asdf']]
            value = decoded['preparation']
            bias = value['raw_bias_diagnostics'][0]['table']['rows'] if value['raw_bias_diagnostics'] else []
            require(all(d['table']['rows'] == bias for d in value['raw_bias_diagnostics']),
                    'Raw bias diagnostics differ across pairs')
            q = decoded['bpm']
            identity = dict(digest=None, sha256=self.inputs[str(path)])
            self.identities[path] = identity
            self.records[path] = dict(kind='preparation', stage=measurements.CORRECTED,
                identity=identity, signals=measurements.preparation_rows(value),
                pairs=[deepcopy(row['raw']) for row in value['rows']], bias=deepcopy(bias),
                provenance=dict(measurement_stage=value['measurement_stage'],
                    raw_diagnostic_stage=measurements.RAW,
                    selection=('Input BPM explicitly omitted; historical archive unchanged'
                        if value.get('input_bpm_policy')=='omitted' else
                        'Preserved native ASDF populations; admitted prior mask retained'),
                    native_receipt=dict(operation='linearity.prepare', path=str(path)),
                    serializer=dict(source_revision=self.manifest['native_source_revision'])))
            if q is None:
                self.bpm[member['detector_id']] = dict(state='skipped_input_bpm',
                    supplied_mask=member['bpm']['input'], output_mode='SUPPLIED',
                    selection_note=('BPM creation disabled for measurement-only linearity.' if member['bpm'].get('state')=='skipped_measurement_only' else 'BPM creation skipped because an input BPM was supplied.'),
                    zero_meaning='Input mask retains its declared encoding and polarity')
                continue
            metrics = q['characterization']['detectors'][0]['measurements']
            context = json.loads(q['extensions']['operation_context']['snapshot'])
            require(context['output_mode'] in (1, 2), 'Unknown BPM output mode')
            self.bpm[member['detector_id']] = dict(
                output_mode='NEW' if context['output_mode'] == 1 else 'COMBINED',
                measurements=deepcopy(metrics), parameters=context['parameters'],
                acquisition_coverage=context['coverage'],
                prior_mask=context['calibrations'], source=str(bpm_path),
                selection_count=None,
                selection_note=('Selection also applies the prior mask.' if any(
                    c['role']=='bpm' for c in context['calibrations']) else
                    'No input BPM supplied; selection requires a usable fit and accepted reason bits.')+
                    ' Inspect the saved SELECTION plane for its count.',
                zero_meaning='No detected reasons; not certification',
                reason_codes={'0': 'No detected reasons', '4': 'Low normalized response',
                              '8': 'High normalized response'},
                fit_states=['unavailable', 'fit', 'legacy_ls_fallback'])
        if saved['bpm_product'] is not None:
            product = self.manifest['bpm_product']
            path = self.local(product['asdf'])
            self.inputs[str(path)] = product['sha256'][product['asdf']]
            for detector, value in self.bpm.items():
                value['image_planes'] = [p for p in saved['bpm_product']['image_planes']
                                         if p['detector_id'] == detector]
        progress(f'Validated {len(self.records)} detector preparation products')

    def local(self, name):
        path = (self.path.parent/Path(name).relative_to(self.manifest['product_root'])).resolve(strict=True)
        require(path.is_relative_to(self.path.parent), 'Manifest member escapes product root')
        return path

    def preparation(self, path, expected=None):
        return self.records[Path(path).resolve(strict=True)]

    def configuration(self, path):
        path = Path(path).resolve(strict=True)
        expected = self.manifest['configuration_sources'].get(str(path))
        require(expected is not None and recipe.digest(path) == expected,
                'Viewer geometry/processing differs from the executed recipe')
        self.inputs[str(path)] = expected
        return path
