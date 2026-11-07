"""Pure same-exposure ROI ratio diagnostic; no fitting, I/O or plotting."""
from copy import deepcopy
import math
from pycavi_residuals import finite

KEYS=('input_index','asset','hdu','pair_id','pair_member')


def compute(samples,*,numerator_roi,denominator_roi,minimum=15000.,maximum=35000.):
    if numerator_roi==denominator_roi:raise ValueError('Distinct ratio ROIs required')
    if not finite(minimum) or not finite(maximum) or minimum>maximum:
        raise ValueError('Finite ordered ratio-reference limits required')
    def collect(roi):
        result={}
        for row in samples:
            if row['roi']!=roi:continue
            key=tuple(row[k] for k in KEYS)
            if key in result:raise ValueError('Duplicate ROI exposure')
            result[key]=row
        return result
    numerator,denominator=collect(numerator_roi),collect(denominator_roi)
    if not numerator or set(numerator)!=set(denominator):
        raise ValueError('Ratio ROI exposure populations differ')
    result=[]
    for key in sorted(numerator,key=lambda k:(k[0],k[1:])):
        n,d=numerator[key],denominator[key]
        if n['exposure_seconds']!=d['exposure_seconds'] or n['detector']!=d['detector']:
            raise ValueError('Ratio exposure metadata differs')
        ns,ds=n['signal_adu'],d['signal_adu']
        valid=finite(ns) and finite(ds) and ns>0 and ds>0
        ratio=ns/ds if valid else None
        if ratio is not None and not finite(ratio):ratio=None
        result.append(dict(roi='ratio',detector=n['detector'],amplifier=n['amplifier'],
            **{k:n[k] for k in KEYS},exposure_seconds=n['exposure_seconds'],
            signal_adu=ns,numerator_signal_adu=ns,denominator_signal_adu=ds,
            numerator=deepcopy(n),denominator=deepcopy(d),raw_ratio=ratio,
            normalized_ratio=None,ratio_departure_percent=None,
            reference_included=bool(ratio is not None and minimum<=ns<=maximum and minimum<=ds<=maximum),
            state='available' if ratio is not None else 'unavailable',
            reason=None if ratio is not None else 'missing_nonpositive_or_nonfinite_signal'))
    refs=[r for r in result if r['reference_included']]
    reference=math.fsum(r['raw_ratio']/len(refs) for r in refs) if refs else None
    if not finite(reference) or reference<=0:reference=None
    for row in result:
        if row['raw_ratio'] is not None and reference is not None:
            value=row['raw_ratio']/reference;delta=100*(value-1)
            if finite(value) and finite(delta):
                row.update(normalized_ratio=value,ratio_departure_percent=delta)
    return dict(configuration=dict(method='same_exposure_ratio_v1',numerator_roi=numerator_roi,
        denominator_roi=denominator_roi,reference_method='arithmetic_mean_of_individual_ratios',
        reference_signal_min_adu=minimum,reference_signal_max_adu=maximum,
        reference_population='both_roi_signals_in_inclusive_interval',
        uncertainty_state='unavailable',physical_correction_fitted=False),
        normalization=dict(reference_ratio=reference,count=len(refs),
            members=[{k:r[k] for k in KEYS} for r in refs],
            status='available' if reference is not None else 'unavailable',
            reason=None if reference is not None else 'no_usable_reference_samples'),rows=result)
