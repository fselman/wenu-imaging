// Stored-value filtering and comparison grouping; no ASDF/measurement mocks.
const assert=require('node:assert/strict'),m=require('../bias-qc-inspection.js');
const row=(value,unit='ADU',mask='applied')=>({scope:'product',detector:'CCD_A',measurement:{name:'read_noise',unit,status:value===null?'unavailable':'measured',value,definition:{stage:'raw_pair',method:'std',region:{detector_bpm:mask}}}});
const a=row(2),b=row(2,'electron'),c=row(2,'ADU','omitted'),missing=row(null),zero=row(0);
assert.equal(m.definitionGroups([a,b,c]).length,3);
assert.equal(m.points([a,b,c,missing,zero],m.metricKey(a)).length,2);
assert.equal(m.numeric(missing),false);assert.equal(m.numeric(zero),true);
assert.equal(m.numeric(row(Infinity)),false);assert.equal(m.numeric(row('2')),false);
assert.equal(m.rowsFor([a,{...b,scope:'input'}],{scope:'product',detector:'CCD_A'}).length,1);
assert.equal(m.rowsFor([a],{scope:'product',detector:'missing'}).length,0);
assert.equal(m.stable({b:1,a:2}),m.stable({a:2,b:1}));
const many=Array.from({length:301},(_,i)=>i),last=m.page(many,100);
assert.deepEqual(last.rows,[300]);assert.equal(last.pages,3);assert.equal(m.page([],9).index,0);
assert.equal(m.range([]),null);assert(m.range([0,0])[0]<0);assert(m.range([2,2])[1]>2);
console.log('PASS: separate units/definitions, unavailable vs zero, scope/detector filters, pagination and constant range.');
