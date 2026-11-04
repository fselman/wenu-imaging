/* Display-only OLS diagnostics. See docs/developer/design/linearity-residual-display-v1.md. */
(function (root) {
  'use strict';
  function sum(values) {
    let total=0, correction=0;
    for(const value of values){const y=value-correction,t=total+y;correction=(t-total)-y;total=t;}
    return total;
  }
  const finite=Number.isFinite;
  function analyze(samples, limits={}) {
    const minimum=limits.minimum??null,maximum=limits.maximum??null;
    const intervalValid=(minimum===null||finite(minimum))&&(maximum===null||finite(maximum))&&
      (minimum===null||maximum===null||minimum<=maximum);
    const configuration={method:'ordinary_unweighted_least_squares',free_intercept:true,
      minimum_signal_adu:finite(minimum)?minimum:null,maximum_signal_adu:finite(maximum)?maximum:null,
      interval_valid:intervalValid,default_population:'all_available_individual_exposures',
      residual_definition:'observed_minus_line',percentage_denominator:'positive_line_prediction',
      diagnostic_only:true,physical_shutter_fitted:false};
    const fits=[];
    const rows=samples.map(row=>({...row,fit_included:false,line_prediction_adu:null,
      residual_adu:null,residual_percent:null,count_rate_adu_per_s:
      finite(row.signal_adu)&&finite(row.exposure_seconds)&&row.exposure_seconds>0?
        row.signal_adu/row.exposure_seconds:null}));
    const rois=[...new Set(rows.map(r=>r.roi))];
    for(const roi of rois){
      const population=rows.filter(r=>r.roi===roi);
      const accepted=population.filter(r=>intervalValid&&finite(r.signal_adu)&&finite(r.exposure_seconds)&&
        (minimum===null||r.signal_adu>=minimum)&&(maximum===null||r.signal_adu<=maximum));
      const fit={roi,status:'unavailable',reason:null,n:accepted.length,intercept_adu:null,
        slope_adu_per_s:null,time_center_s:null,signal_center_adu:null,
        exposure_range_s:null,signal_range_adu:null};
      fits.push(fit);
      if(!intervalValid){fit.reason='invalid_fit_interval';continue;}
      for(const r of accepted)r.fit_included=true;
      if(accepted.length<2){fit.reason='fewer_than_two_points';continue;}
      const times=accepted.map(r=>r.exposure_seconds),signals=accepted.map(r=>r.signal_adu);
      const t0=times[0],s0=signals[0],tm=t0+sum(times.map(t=>(t-t0)/times.length)),
        sm=s0+sum(signals.map(s=>(s-s0)/signals.length));
      const sxx=sum(times.map(t=>(t-tm)**2)),sxy=sum(times.map((t,i)=>(t-tm)*(signals[i]-sm)));
      if(sxx===0){fit.reason='no_exposure_time_span';continue;}
      const b=sxy/sxx,a=sm-b*tm;
      if(![tm,sm,sxx,sxy,a,b].every(finite)||sxx<0){fit.reason='numerical_overflow';continue;}
      Object.assign(fit,{status:'available',intercept_adu:a,slope_adu_per_s:b,
        time_center_s:tm,signal_center_adu:sm,exposure_range_s:[Math.min(...times),Math.max(...times)],
        signal_range_adu:[Math.min(...signals),Math.max(...signals)]});
      for(const r of population){
        if(!finite(r.exposure_seconds)||!finite(r.signal_adu))continue;
        const predicted=sm+b*(r.exposure_seconds-tm),residual=r.signal_adu-predicted;
        if(!finite(predicted)||!finite(residual))continue;
        r.line_prediction_adu=predicted;r.residual_adu=residual;
        const percentage=predicted>0?100*(residual/predicted):null;
        r.residual_percent=finite(percentage)?percentage:null;
      }
    }
    for(const r of rows)if(!finite(r.count_rate_adu_per_s))r.count_rate_adu_per_s=null;
    return {configuration,fits,rows};
  }
  root.QcResiduals={analyze};
  if(typeof module!=='undefined'&&module.exports)module.exports=root.QcResiduals;
})(globalThis);
