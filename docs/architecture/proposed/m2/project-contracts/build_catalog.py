"""Review catalog generator; no native defaults, discovery or execution."""
import json
from pathlib import Path


def scalar(kind, **kw):
    return dict(type=kind, **kw)


def obj(fields, optional=()):
    return dict(type='table', fields=fields, optional=list(optional))


def arr(items, minimum=0, maximum=256):
    return dict(type='array', items=items, minimum=minimum, maximum=maximum)


text = scalar('string')
positive = scalar('integer', minimum=1)
version = scalar('integer', enum=[1])
flag = scalar('boolean')

def choice(*values):
    return scalar('string', enum=list(values))


def domain(**fields):
    return obj(dict(schema_version=version, **fields))


region = obj(dict(x_min=positive, x_max=positive, y_min=positive, y_max=positive,
                  unit=choice('pixel'), convention=choice('fits-1-based-inclusive')),
             optional=('y_min', 'y_max'))
channel = obj(dict(id=text, physical_amplifier_id=text,
                   identity_status=choice('unknown', 'verified'),
                   active=flag, signal=region,
                   overscan=obj(dict(state=choice('absent', 'defined'),
                                     subtract=flag, region=region), optional=('region',))),
              optional=('physical_amplifier_id', 'signal'))
detector = obj(dict(id=text, legacy_ordinal=positive, physical_detector_id=text,
                    identity_status=choice('unknown', 'verified'),
                    channels=arr(channel, 1, 16)),
               optional=('legacy_ordinal', 'physical_detector_id'))
root = obj(dict(
    project_schema_version=version,
    project=domain(id=text, name=text, roots=obj({k: text for k in
        ('raw', 'calibration', 'output', 'work', 'logs')})),
    association=domain(mode=choice('explicit'), bindings=arr(obj(dict(
        group=text, role=choice('bias', 'bpm', 'linearity', 'dark', 'flat', 'fringe'),
        selection=choice('selected', 'omitted'), asset_id=text, asset_version=positive),
        optional=('asset_id', 'asset_version')))),
    reduction_profile=domain(id=text, purpose=choice('scientific', 'visual')),
    recipe=domain(id=text, steps=arr(obj(dict(id=text, operation=choice(
        'mef_cal_bias', 'mef_cal_bpm', 'mef_cal_linearity', 'mef_cal_dark',
        'mef_cal_domeff', 'mef_cal_skyff', 'mef_cal_mff', 'mef_cal_fringes',
        'mef_sci_pp'))), 1, 64)),
    execution=domain(activation=choice('disabled'), mode=choice('serial'),
                     workers=scalar('integer', enum=[1]),
                     numerical_threads=scalar('integer', enum=[1]),
                     niceness=scalar('integer', minimum=10, maximum=19)),
    quality=domain(policy=choice('record_only'), estimator_status=choice('not_qualified'),
                   thresholds=arr(text, maximum=0)),
    product_profile=domain(id=text, target=choice('legacy', 'ESO_Phase3'),
                           compliance=choice('not_validated'),
                           variance_contract=choice('pre_m6a_unavailable')),
    processing=domain(native_mode=choice('legacy_reference', 'unavailable'), native_configuration=text),
    readout=domain(id=text, authority=choice('configured', 'synthetic'),
                   metadata_policy=choice('explicit_review'),
                   header_evidence=arr(obj(dict(detector_id=text, asset_id=text,
                       asset_version=positive, hdu=scalar('integer', minimum=0), card_index=positive,
                       field=choice('amplifier_name', 'active_amplifier', 'overscan_region'),
                       raw_card=text, trust=choice('unverified'), disposition=choice('unresolved')))),
                   mapping_status=choice('unverified', 'verified'), inventory_status=choice('not_established'),
                   detectors=arr(detector, 1, 64)),
))
root['fields']['processing']['optional'] = ['native_configuration']
catalog = dict(notation='wenu-project-authoring-contract-1', version=1,
               status='validation-only', schema=root)
if __name__ == '__main__':
    Path(__file__).with_name('catalog.json').write_text(json.dumps(catalog, indent=2) + '\n')
