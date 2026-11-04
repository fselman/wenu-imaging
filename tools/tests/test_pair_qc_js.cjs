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
    value: id === 'metric' ? 'variance' : id === 'residual-x' ? 'signal_adu' : id === 'residual-y' ? 'residual_percent' : '', checked: id === 'common',
    querySelectorAll: () => [], replaceChildren() { this.innerHTML = ''; this.textContent = ''; }
  });
  return elements.get(id);
}
const context = vm.createContext({document: {getElementById: element, querySelectorAll: () => []}, window: {print() {}}});
const run = code => vm.runInContext(code, context);
run(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
run(script);
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
element('fit-min').value='1001';element('fit-min').onchange();
run('showPoint(0)');diagnostic=JSON.parse(element('point').textContent);
assert.equal(diagnostic.fit_included,false);
assert.ok(Math.abs(diagnostic.residual_adu+2)<1e-10);
assert.equal((element('plot').innerHTML.match(/<circle /g)||[]).length,8);
element('residual-x').value='exposure_seconds';element('residual-x').onchange();
element('residual-y').value='residual_adu';element('residual-y').onchange();
assert.match(element('plot').innerHTML,/Exposure time/);
assert.match(element('plot').innerHTML,/Observed − line \(ADU\)/);
element('fit-max').value='1000';element('fit-max').onchange();
assert.match(element('plot').innerHTML,/No available values/);
assert.match(element('fits').innerHTML,/invalid_fit_interval/);
element('fit-min').value='';element('fit-max').value='';element('fit-min').onchange();
element('metric').value='count_rate';element('metric').onchange();
assert.match(element('plot').innerHTML,/Count rate S\/t/);
element('metric').value='signal_time';element('metric').onchange();
// Null points stay in the exact table; negative signals stay in the curve.
run("panels[0].signals[0].signal_adu=null; panels[0].signals[1].signal_adu=-3.25; recalculate(); detail()");
assert.equal((element('plot').innerHTML.match(/<circle /g) || []).length, 7);
assert.match(element('points').innerHTML, /unavailable/);
assert.match(element('points').innerHTML, /-3.25/);
assert.doesNotMatch(element('plot').innerHTML, /NaN|Infinity|undefined/);
console.log('PASS: actual viewer JavaScript values, metric switching, member/source identity, ROI filtering, missing/null/negative data; browser layout not exercised.');
