// Execute actual corrected viewer scripts: metric source, units and saved values.
// No browser painting or scientific calculation is claimed by this DOM harness.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(process.argv[2],'utf8');
const payload=html.match(/<script id="qc-data" type="application\/json">([\s\S]*?)<\/script>/)[1];
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{textContent:id==='qc-data'?payload:'',innerHTML:'',style:{},
 value:id==='metric'?'variance':id==='residual-x'?'signal_adu':id==='residual-y'?'residual_percent':id==='ratio-y'?'normalized_ratio':'',
 checked:id==='common',querySelectorAll:()=>[],replaceChildren(){this.innerHTML='';this.textContent='';}});return elements.get(id);}
const context=vm.createContext({document:{getElementById:element,querySelectorAll:()=>[],querySelector:element},window:{print(){}}});
const run=code=>vm.runInContext(code,context);
run(html.match(/<script>([\s\S]*?)<\/script>/)[1]);
run(html.match(/<\/script><script>([\s\S]*?)<\/script>/)[1]);
assert.equal(run('corrected'),true);assert.equal(element('metric').value,'signal_time');
assert.match(element('measurement-title').textContent,/corrected preparation/);
assert.match(element('measurement-note').textContent,/row overscan corrected/);
assert.equal(run('rowsFor(panels[0])[0].signal_adu'),205.5);
element('metric').value='variance';
assert.equal(run('field()'),'spatial_variance_adu2');assert.equal(run('xfield()'),'signal_adu');
assert.equal(run('yunit()'),'ADU²');assert.equal(run('rowsFor(panels[0])[0].spatial_variance_adu2'),13);
assert.deepEqual(JSON.parse(run('JSON.stringify(bounds(rowsFor(panels[0])))')).slice(0,2),[0,65535]);
element('metric').value='gain';assert.match(run('xlabel()'),/Raw-pair/);
assert.equal(run('rowsFor(panels[0])[0].mean_signal_adu'),5001);
element('metric').value='residual';
assert.equal(run('rowsFor(panels[0])[0].residual_adu'),0);
element('metric').value='ratio';run('detail(true)');
assert.equal(run('rowsFor(panels[0])[0].normalized_ratio'),1);
assert.match(element('fit-note').textContent,/row overscan/);
assert.doesNotMatch(element('fit-note').textContent,/no overscan/);
console.log('PASS: corrected metric sources, saved residual/ratio values, stage labels and shared axes');
