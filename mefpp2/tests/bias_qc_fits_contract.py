"""Independent FITS/ASDF scalar and definition comparison, bias-scalar/1.

The X-macro file is the versioned registry, not an executable parser dependency.
This module needs only Python's standard library; FITS reading stays with the
normal Astropy interpreter and ASDF reading with the retained ASDF interpreter.
"""
import ast
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / 'ins/mef/common/mef_bias_qc_fits.def'


def registry():
    result = {name: [] for name in 'GMQC'}
    for line in REGISTRY.read_text().splitlines():
        if len(line) > 2 and line[0] in result and line[1] == '(':
            result[line[0]].append(ast.literal_eval(line[1:]))
    return result


def is_addition(keyword):
    if not keyword.startswith('ESO MPP QC '):
        return False
    tail = keyword[len('ESO MPP QC '):]
    if tail in ('FRMEDIAN', 'FRSTDEV'):
        return False
    pieces = tail.split()
    return not (len(pieces) == 3 and pieces[0].startswith('FRAME')
                and pieces[1:] in (['SCAN', 'MEDIAN'], ['SCAN', 'STDEV']))


def verify(header, product, detector):
    reg = registry()
    codes = {(kind, text): value for kind, text, value in reg['C']}
    expected = {}

    def put(key, value):
        full = 'ESO MPP QC ' + key
        assert full not in expected, full
        expected[full] = value

    def context(key, m):
        definition = m['definition']
        region = definition['region']
        put(key + ' STG', codes['stage', definition['stage']])
        put(key + ' MASK', codes['mask', region['detector_bpm']])
        put(key + ' COORD', codes['coord', region['coordinates']])
        assert region['clipping'] in ('none', 'median_centered_monotone_sigma')
        if region['clipping'] != 'none':
            put(key + ' CLIP', 'MEDSIG')
        assert region['nonfinite'] == 'excluded'
        if region['mask_record_id'] is not None:
            put(key + ' BPMID', region['mask_record_id'])
        for suffix, value in zip(('X1', 'X2', 'Y1', 'Y2'), region['bounds']):
            put(key + ' ' + suffix, value)
        for index, source in enumerate(m['sources'], 1):
            put(f'{key} SRC{index}', Path(source).name)

    def measurement(key, m, own_context):
        definition = m['definition']
        put(key + ' NSAMP', definition['sample_count'])
        if own_context:
            context(key, m)
        if definition['method'] is not None:
            put(key + ' METHOD', codes['method', definition['method']])
        put(key + ' UNIT', m['unit'])
        put(key + ' S', m['status'])
        if m['status'] == 'measured':
            assert m['reason'] is None and m['value'] is not None
            put(key, m['value'])
        else:
            assert m['status'] == 'unavailable' and m['value'] is None
            put(key + ' R', codes['reason', m['reason']])

    def samples(scope, prefix, values):
        ms = {m['name']: m for m in values}
        mapped = set()
        for group_scope, source, name in reg['G']:
            if scope != group_scope:
                continue
            key = prefix + name
            context(key, ms[source + '.mean'])
            for suffix, fits_suffix in reg['M']:
                identifier = source + '.' + suffix
                measurement(key + ' ' + fits_suffix, ms[identifier], False)
                mapped.add(identifier)
        for scalar_scope, source, name in reg['Q']:
            if scope == scalar_scope and source in ms:
                measurement(prefix + name, ms[source], True)
                mapped.add(source)
        # Every remaining scalar must be explicitly legacy-backed. Coordinate
        # arrays (including empty/unavailable coordinate sets) remain ASDF-only.
        legacy = {
            'legacy.frame_mean_average', 'legacy.frame_mean_sigma',
            'legacy.rejection_low', 'legacy.rejection_high',
            'legacy.product_median', 'legacy.product_stdev',
        } if scope == 0 else {'scan_correction.median', 'scan_correction.stdev'}
        assert set(ms) - mapped == legacy | (
            {'pixels.hot.x', 'pixels.hot.y'} if scope == 0 else set()
        ), set(ms) - mapped
        return ms

    if product['extensions'].get('bpm_registry') is not None:
        put('BPM REG', product['extensions']['bpm_registry'])
    if detector.get('median_even_handling') is not None:
        assert detector['median_even_handling'] in ('average', 'lower')
        put('MED EVEN', detector['median_even_handling'])
    put('MAPVER', 'bias-scalar/1')
    put('ASDF', Path(product['file']['location']).with_suffix('.asdf').name)
    put('PROD', product['file']['filename'])
    for fits_name, asdf_name in (
        ('CONFIG', 'configuration_detector'), ('BINX', 'bin_x'),
        ('BINY', 'bin_y'), ('READID', 'readout_id'), ('AMP', 'amplifier'),
    ):
        put(fits_name, detector[asdf_name])
    ms = samples(0, '', detector['measurements'])
    inputs = {r['record_id']: r for r in product['embedded_input_records']}
    for index, source in enumerate(ms['read_noise']['sources'], 1):
        if source in inputs:
            put(f'RON I{index}', inputs[source]['original_index'])
    membership = {
        item['record_id']: next(d for d in item['participation_by_detector']
                                if d['detector_id'] == detector['detector_id'])
        for item in product['inputs']
    }
    for item in product['embedded_input_records']:
        binding = next(d for d in item['detectors']
                       if d['detector_id'] == detector['detector_id'])
        prefix = f"FRAME{item['original_index'] + 1:03d}"
        put(prefix + ' ID', item['record_id'])
        put(prefix + ' HDU', binding['source_hdu'])
        use = membership[item['record_id']]
        put(prefix + ' USE', use['status'])
        if use['status'] == 'rejected':
            put(prefix + ' WHY', codes['reason', use['reason']])
        samples(1, prefix + ' ', binding['measurements'])

    actual = {k: v for k, v in header.items() if is_addition(k)}
    assert set(actual) == set(expected), (
        'keyword coverage', sorted(set(expected) - set(actual)),
        sorted(set(actual) - set(expected)),
    )
    for key, value in expected.items():
        assert actual[key] == value, (key, actual[key], value)
        if isinstance(value, (int, float)):
            assert isinstance(actual[key], (int, float)), (key, type(actual[key]))
    return len(expected)
