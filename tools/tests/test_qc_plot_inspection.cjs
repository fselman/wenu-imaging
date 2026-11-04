// Shared plotting helpers: coordinates/ticks only, no measurement/model arithmetic.
const assert=require('node:assert/strict'),fs=require('node:fs');
const plotting=require('../qc-plot-inspection.js');
const spec=JSON.parse(fs.readFileSync(require('node:path').join(__dirname,'../../config/plotting/signal-axis-v1.json'),'utf8'));
plotting.configure(spec);
assert.deepEqual(plotting.signalRange(1000,53000),[0,65535]);
assert.deepEqual(plotting.signalRange(0,65535),[0,65535]);
assert.deepEqual(plotting.signalTicks(0,65535),[0,10000,20000,30000,40000,50000,60000,65535]);
assert.deepEqual(plotting.signalRange(-3.25,1000),[-10000,65535]);
const box={width:700,height:350,left:75,right:18,top:16,bottom:55,xmin:0,xmax:65535,ymin:-5,ymax:5,xunit:'ADU',yunit:'%'};
assert.deepEqual(plotting.coordinateAt(box,75,295),{x:0,y:-5});
assert.deepEqual(plotting.coordinateAt(box,682,16),{x:65535,y:5});
assert.deepEqual(plotting.coordinateAt(box,(75+682)/2,(16+295)/2),{x:32767.5,y:0});
assert.equal(plotting.coordinateAt(box,74,100),null);
assert.equal(plotting.coordinateAt(box,100,296),null);
// Exercise the shared event binding, including screen-to-SVG coordinate conversion.
const vertical={},horizontal={},readout={textContent:''},group={style:{},querySelector(selector){
  const target=selector==='[data-vertical]'?vertical:horizontal;
  return {setAttribute(key,value){target[key]=value;}};
}};
const svg={dataset:{inspection:JSON.stringify(box)},querySelector:()=>group,
  parentElement:{querySelector:()=>readout},getScreenCTM:()=>({inverse:()=>({})}),
  createSVGPoint:()=>({x:0,y:0,matrixTransform(){return {x:this.x/2,y:this.y/2};}})};
plotting.bind({querySelectorAll:()=>[svg]});
svg.onpointermove({clientX:2*(75+682)/2,clientY:2*(16+295)/2});
assert.equal(group.style.display,'');assert.equal(vertical.x1,378.5);assert.equal(horizontal.y1,155.5);
assert.match(readout.textContent,/32,767.5 ADU/);assert.match(readout.textContent,/y: 0 %/);
svg.onpointermove({clientX:0,clientY:0});assert.equal(group.style.display,'none');
svg.onpointerleave();assert.match(readout.textContent,/Move over plot/);
console.log('PASS: shared ticks/endpoints, negative range, inverse coordinates, pointer binding/units and exit handling. Browser painting not exercised.');
