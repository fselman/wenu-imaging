// Independent analytical checks for the actual dependency-free diagnostic module.
const assert=require('node:assert/strict');
const {analyze}=require('../pair-qc-residuals.js');
const point=(t,s,roi='R0')=>({roi,exposure_seconds:t,signal_adu:s,asset:'saved.fits'});
const close=(a,b,tol=1e-12)=>assert.ok(Math.abs(a-b)<=tol,`${a} != ${b}`);
let checks=0;
// Exact offset line: slope/intercept recovered, constant shutter offset removed.
let input=[1,2,10].map(t=>point(t,10*(t+0.2))),frozen=JSON.stringify(input);
let out=analyze(input);close(out.fits[0].slope_adu_per_s,10);close(out.fits[0].intercept_adu,2);
out.rows.forEach(r=>close(r.residual_adu,0));close(out.rows[0].count_rate_adu_per_s,12);close(out.rows[2].count_rate_adu_per_s,10.2);checks++;
// Analytic OLS: points (1,3),(2,4),(3,8) -> a=0,b=2.5 and residuals .5,-1,.5.
out=analyze([point(1,3),point(2,4),point(3,8)]);
close(out.fits[0].intercept_adu,0);close(out.fits[0].slope_adu_per_s,2.5);
[0.5,-1,0.5].forEach((r,i)=>close(out.rows[i].residual_adu,r));
[20,-20,100/15].forEach((r,i)=>close(out.rows[i].residual_percent,r));checks++;
// Restricted fit retains every point, with predictions outside the selected interval.
out=analyze([point(1,3),point(2,4),point(3,8)],{minimum:3,maximum:4});
assert.equal(out.rows.length,3);assert.deepEqual(out.rows.map(r=>r.fit_included),[true,true,false]);
close(out.fits[0].intercept_adu,2);close(out.fits[0].slope_adu_per_s,1);close(out.rows[2].residual_adu,3);checks++;
// Distinct ROI fits are independent, regardless of their scale or order.
out=analyze([point(2,4),point(1,100,'R1'),point(1,2),point(2,200,'R1')]);
close(out.fits[0].slope_adu_per_s,2);close(out.fits[1].slope_adu_per_s,100);checks++;
// Null/zero/negative values stay explicit; rates at t=0 and percentages at nonpositive predictions are null.
out=analyze([point(0,0),point(1,-2),point(2,null)]);
assert.equal(out.rows[0].count_rate_adu_per_s,null);assert.equal(out.rows[0].residual_percent,null);
assert.equal(out.rows[1].residual_percent,null);assert.equal(out.rows[1].count_rate_adu_per_s,-2);
assert.equal(out.rows[2].residual_adu,null);checks++;
// Lack of rank, insufficient population and invalid bounds never manufacture a fit.
assert.equal(analyze([point(1,1),point(1,2)]).fits[0].reason,'no_exposure_time_span');
assert.equal(analyze([point(1,1)]).fits[0].reason,'fewer_than_two_points');
for(const limits of [{minimum:5,maximum:2},{minimum:NaN}]){
 out=analyze(input,limits);assert.equal(out.fits[0].reason,'invalid_fit_interval');
 assert.ok(out.rows.every(r=>r.residual_adu===null));assert.doesNotMatch(JSON.stringify(out),/NaN|Infinity/);
}checks++;
// Large time origin: predictions use the centered representation, not a+b*t cancellation.
out=analyze([point(1e12,3),point(1e12+1,5),point(1e12+2,7)]);
close(out.fits[0].slope_adu_per_s,2);out.rows.forEach(r=>close(r.residual_adu,0));checks++;
// Input arrays are never mutated; derived state is separate.
analyze(input,{maximum:999});assert.equal(JSON.stringify(input),frozen);checks++;
console.log(`PASS: ${checks} analytical diagnostic groups; no pixels, ASDF writes or physical calibration fits.`);
