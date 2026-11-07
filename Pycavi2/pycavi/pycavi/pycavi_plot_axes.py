"""Shared presentation-only signal axes for static plots."""
import json
import math


def load(path):
    value=json.loads(path.read_text())
    if value['schema_version']!=1:raise ValueError('Unknown plot-axis specification')
    return value


def signal_axes(axis,which,spec,values):
    from matplotlib.ticker import FixedLocator,StrMethodFormatter
    finite=[v for v in values if v is not None and math.isfinite(v)]
    step=spec['signal_major_step_adu']
    lower=min(spec['signal_minimum_adu'],math.floor(min(finite,default=0)/step)*step)
    maximum=max(finite,default=0)
    upper=spec['signal_maximum_adu'] if maximum<=spec['signal_maximum_adu'] else math.ceil(maximum/step)*step
    ticks=sorted({*spec['signal_ticks_adu'],*range(lower,upper+1,step)})
    target=getattr(axis,which+'axis')
    target.set_major_locator(FixedLocator([v for v in ticks if lower<=v<=upper]))
    target.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    getattr(axis,'set_'+which+'lim')(lower,upper)
    return dict(limits=[lower,upper],ticks=[v for v in ticks if lower<=v<=upper])
