// Execute the real viewer script with a minimal DOM surface. This checks JS
// values/events/SVG generation, not browser layout, painting or pointer input.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const payload = html.match(/<script id="qc-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script = html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1];
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    textContent: id === 'qc-data' ? payload : '', innerHTML: '', style: {},
    value: id === 'metric' ? 'variance' : id === 'residual-x' ? 'signal_adu' : id === 'residual-y' ? 'residual_percent' : id === 'ratio-y' ? 'normalized_ratio' : '', checked: id === 'common',
    querySelectorAll: () => [], replaceChildren() { this.innerHTML = ''; this.textContent = ''; }
  });
  return elements.get(id);
}
const context = vm.createContext({document: {getElementById: element, querySelectorAll: () => []}, window: {print() {}}});
const run = code => vm.runInContext(code, context);
run(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
run(script);
assert.deepEqual(JSON.parse(run('JSON.stringify(bounds(panels[0].pairs))')).slice(0,2),[0,65535]);
assert.match(element('plot').innerHTML,/65,535/);
assert.match(element('plot').innerHTML,/10,000/);
assert.match(element('plot').innerHTML,/data-inspection/);
assert.match(element('plot').innerHTML,/data-cursor-readout/);
assert.equal(element('name').textContent, 'ESO_CCD_#65');
assert.equal((element('mosaic').innerHTML.match(/class="tile"/g) || []).length, 32);
element('metric').value = 'signal_time'; element('metric').onchange();
assert.match(element('plot').innerHTML, /Exposure time \(s\)/);
assert.equal((element('plot').innerHTML.match(/<circle /g) || []).length, 8);
assert.match(element('points').innerHTML, /F3.fits/);
run('showPoint(6)');
let sample = JSON.parse(element('point').textContent);
assert.equal(sample.asset, 'F3.fits');
assert.equal(sample.input_index, 13);
assert.equal(sample.exposure_seconds, 2);
assert.equal(sample.signal_adu, 1001.1234567890124);
assert.equal(sample.pair_member, 2);
assert.equal(sample.source_row_index, 0);
run("enabled.delete('CCD65.R0'); detail()");
assert.equal((element('plot').innerHTML.match(/<circle /g) || []).length, 4);
run("enabled.clear(); $('common').checked=false; detail()");
assert.match(element('plot').innerHTML, /No available values/);
run('selected=1; detail(true)');
assert.match(element('plot').innerHTML, /No saved QC/);
run('selected=0; detail(true)');
for (const metric of ['gain', 'variance', 'signal_time']) {
  element('metric').value = metric; element('metric').onchange();
  assert.match(element('point').textContent, /Select a measured point/);
}
// Residual UI uses actual calculated means, limits, axes and exact fit membership.
element('metric').value='residual';element('metric').onchange();
assert.match(element('plot').innerHTML,/Observed − line/);
assert.match(element('plot').innerHTML,/Mean bias-subtracted signal/);
assert.equal((element('plot').innerHTML.match(/<circle /g)||[]).length,8);
assert.match(element('fits').innerHTML,/Intercept ADU/);
run('showPoint(0)');
let diagnostic=JSON.parse(element('point').textContent);
assert.ok(Math.abs(diagnostic.residual_adu+1)<1e-10);
assert.equal(diagnostic.fit_included,true);
assert.equal(element('fit-min').onchange,undefined);
element('residual-x').value='exposure_seconds';element('residual-x').onchange();
element('residual-y').value='residual_adu';element('residual-y').onchange();
assert.match(element('plot').innerHTML,/Exposure time/);
assert.match(element('plot').innerHTML,/Observed − line \(ADU\)/);
// Plot the stored value verbatim; no fit/prediction is evaluated in the viewer.
run('diagnostics[0].rows[0].residual_adu=123.25; detail(); showPoint(0)');
assert.equal(JSON.parse(element('point').textContent).residual_adu,123.25);
element('metric').value='count_rate';element('metric').onchange();
assert.match(element('plot').innerHTML,/Count rate S\/t/);
element('metric').value='signal_time';element('metric').onchange();
// Null points stay in the exact table; negative signals stay in the curve.
run("panels[0].signals[0].signal_adu=null; panels[0].signals[1].signal_adu=-3.25; detail()");
assert.equal((element('plot').innerHTML.match(/<circle /g) || []).length, 7);
assert.match(element('points').innerHTML, /unavailable/);
assert.match(element('points').innerHTML, /-3.25/);
assert.doesNotMatch(element('plot').innerHTML, /NaN|Infinity|undefined/);
console.log('PASS: actual viewer JavaScript values, metric switching, member/source identity, ROI filtering, missing/null/negative data; browser layout not exercised.');

// Saved same-exposure ratios use the shared axes/cursor and no browser division.
if (JSON.parse(payload).panels[0].ratio) {
  element('residual-x').value='signal_adu';
  element('metric').value='ratio';element('metric').onchange();
  assert.equal((element('plot').innerHTML.match(/<circle /g)||[]).length,4);
  assert.match(element('plot').innerHTML,/65,535/);
  assert.match(element('plot').innerHTML,/data-inspection/);
  assert.match(element('points').innerHTML,/F3.fits/);
  run('showPoint(0)');
  let ratio=JSON.parse(element('point').textContent);
  assert.equal(ratio.asset,'F0.fits');assert.equal(ratio.pair_member,1);
  assert.ok(ratio.raw_ratio>0);assert.ok(ratio.normalized_ratio>0);
  element('ratio-y').value='ratio_departure_percent';element('ratio-y').onchange();
  assert.match(element('plot').innerHTML,/ROI ratio departure/);
  element('residual-x').value='exposure_seconds';element('residual-x').onchange();
  assert.match(element('plot').innerHTML,/Exposure time/);
  run('panels[0].ratio.rows[0].ratio_departure_percent=17.125;detail();showPoint(0)');
  assert.equal(JSON.parse(element('point').textContent).ratio_departure_percent,17.125);
  element('metric').value='variance';element('metric').onchange();
  assert.equal(run('enabled.size'),2);
  console.log('PASS: saved ROI ratios, normalization/departure views, exact values, shared signal/time axes and cursor hooks.');
}
