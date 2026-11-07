"""Pure diagnostic OLS, separate from ASDF storage and plotting."""
from copy import deepcopy
import math


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def analyze(samples, *, minimum=None, maximum=None):
    valid = ((minimum is None or finite(minimum)) and
             (maximum is None or finite(maximum)) and
             (minimum is None or maximum is None or minimum <= maximum))
    config = dict(method='ordinary_unweighted_least_squares', free_intercept=True,
        minimum_signal_adu=minimum if finite(minimum) else None,
        maximum_signal_adu=maximum if finite(maximum) else None,
        interval_valid=valid, default_population='all_available_individual_exposures',
        residual_definition='observed_minus_line', percentage_denominator='positive_line_prediction',
        diagnostic_only=True, physical_shutter_fitted=False,
        algorithm='centered_fsum_ols_v1')
    rows = deepcopy(samples)
    for row in rows:
        row.update(fit_included=False, line_prediction_adu=None, residual_adu=None,
                   residual_percent=None, count_rate_adu_per_s=None)
        t, s = row['exposure_seconds'], row['signal_adu']
        if finite(t) and finite(s) and t > 0:
            rate = s/t
            row['count_rate_adu_per_s'] = rate if finite(rate) else None
    fits = []
    for roi in dict.fromkeys(row['roi'] for row in rows):
        population = [r for r in rows if r['roi'] == roi]
        selected = [r for r in population if valid and finite(r['signal_adu'])
                    and finite(r['exposure_seconds'])
                    and (minimum is None or r['signal_adu'] >= minimum)
                    and (maximum is None or r['signal_adu'] <= maximum)]
        fit = dict(roi=roi, status='unavailable', reason=None, n=len(selected),
            intercept_adu=None, slope_adu_per_s=None, time_center_s=None,
            signal_center_adu=None, exposure_range_s=None, signal_range_adu=None)
        fits.append(fit)
        if not valid:
            fit['reason'] = 'invalid_fit_interval'; continue
        for row in selected:
            row['fit_included'] = True
        if len(selected) < 2:
            fit['reason'] = 'fewer_than_two_points'; continue
        times = [r['exposure_seconds'] for r in selected]
        signals = [r['signal_adu'] for r in selected]
        try:
            n = len(selected)
            tm = times[0] + math.fsum((t-times[0])/n for t in times)
            sm = signals[0] + math.fsum((s-signals[0])/n for s in signals)
            xx = math.fsum((t-tm)**2 for t in times)
            xy = math.fsum((t-tm)*(s-sm) for t,s in zip(times, signals))
            if xx == 0:
                fit['reason'] = 'no_exposure_time_span'; continue
            b = xy/xx; a = sm-b*tm
            if not all(map(finite, (tm,sm,xx,xy,a,b))):
                raise OverflowError()
        except (OverflowError, ValueError, ZeroDivisionError):
            fit['reason'] = 'numerical_overflow'; continue
        fit.update(status='available', intercept_adu=a, slope_adu_per_s=b,
            time_center_s=tm, signal_center_adu=sm,
            exposure_range_s=[min(times),max(times)], signal_range_adu=[min(signals),max(signals)])
        for row in population:
            t,s = row['exposure_seconds'],row['signal_adu']
            if not finite(t) or not finite(s): continue
            predicted = sm+b*(t-tm); residual = s-predicted
            if not finite(predicted) or not finite(residual): continue
            row.update(line_prediction_adu=predicted, residual_adu=residual)
            if predicted > 0:
                percent = 100*(residual/predicted)
                row['residual_percent'] = percent if finite(percent) else None
    return dict(configuration=config, fits=fits, rows=rows)
