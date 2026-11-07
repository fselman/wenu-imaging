/* Bias scalar inspection only: no estimator, fit, time conversion or file IO. */
(function(root){
  'use strict';
  function stable(value){
    if(Array.isArray(value))return '['+value.map(stable).join(',')+']';
    if(value!==null&&typeof value==='object')return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+stable(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  function metricKey(row){const m=row.measurement,d=m.definition;return stable([m.name,m.unit,d.stage,d.method,d.region]);}
  function numeric(row){return row.measurement.status==='measured'&&typeof row.measurement.value==='number'&&Number.isFinite(row.measurement.value);}
  function rowsFor(rows,state){return rows.filter(r=>r.scope===state.scope&&(!state.detector||r.detector===state.detector));}
  function definitionGroups(rows){const out=new Map();for(const r of rows){const k=metricKey(r);if(!out.has(k))out.set(k,r);}return [...out.entries()].sort((a,b)=>a[1].measurement.name.localeCompare(b[1].measurement.name));}
  function points(rows,key){return rows.filter(r=>metricKey(r)===key&&numeric(r));}
  function range(values){if(!values.length)return null;let lo=Infinity,hi=-Infinity;for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}const pad=lo===hi?Math.max(Math.abs(lo)*.05,1e-6):(hi-lo)*.08;return [lo-pad,hi+pad];}
  function page(rows,index,size=150){const pages=Math.max(1,Math.ceil(rows.length/size)),current=Math.min(Math.max(0,index),pages-1);return {rows:rows.slice(current*size,(current+1)*size),index:current,pages,total:rows.length};}
  const model={stable,metricKey,numeric,rowsFor,definitionGroups,points,range,page};
  root.BiasQcInspection=model;
  if(typeof module!=='undefined'&&module.exports)module.exports=model;
  if(typeof document==='undefined')return;
  const data=JSON.parse(document.getElementById('bias-qc-data').textContent),products=data.products;
  const all=products.flatMap(p=>p.rows),byId=new Map(products.map(p=>[p.id,p]));
  const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pretty=v=>v===null?'—':typeof v==='number'?String(v):String(v);
  let highlighted=products.at(-1)?.id??'',pageIndex=0,selected=null;
  const detectors=[...new Set(all.map(r=>r.detector))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
  $('coverage').textContent=products.length+' validated products · '+detectors.length+' detectors · '+all.length+' scalar measurements';
  $('directory').textContent=data.directory;
  if(data.errors.length){const p=document.createElement('p');p.className='warning';p.textContent='Incomplete collection: '+data.errors.map(e=>e.path+' — '+e.error).join('; ');$('errors').append(p);}
  $('product').innerHTML=products.map(p=>`<option value="${esc(p.id)}">${esc(p.filename)}</option>`).join('');$('product').value=highlighted;
  $('detector').innerHTML='<option value="">All detectors</option>'+detectors.map(d=>`<option>${esc(d)}</option>`).join('');
  const groupCounts=new Map();for(const p of products)groupCounts.set(p.raw_sequence,(groupCounts.get(p.raw_sequence)||0)+1);
  function state(){return {scope:$('scope').value,detector:$('detector').value};}
  function productTable(){
    $('products').innerHTML=products.map(p=>`<tr tabindex="0" data-product="${esc(p.id)}" class="${p.id===highlighted?'selected':''}"><td>${esc(p.filename)}</td><td>${esc(p.created_at)}</td><td>${p.detectors.length}</td><td>${esc(p.raw_sequence.slice(0,10))} · ${p.raw_inputs.length} inputs${groupCounts.get(p.raw_sequence)>1?' · shared by '+groupCounts.get(p.raw_sequence)+' products':''}</td></tr>`).join('');
    for(const row of $('products').querySelectorAll('[data-product]')){const choose=()=>{highlighted=row.dataset.product;$('product').value=highlighted;render();};row.onclick=choose;row.onkeydown=e=>{if(e.key==='Enter'){choose();}};}
    const p=byId.get(highlighted);$('provenance').textContent=p?JSON.stringify({metadata:p.metadata,raw_inputs:p.raw_inputs,participation:p.participation,array_measurements:p.array_measurements},null,2):'';
    $('array-note').textContent=p?p.array_measurements.length+' stored array measurements are listed by name/count; this first view displays scalar values.':'';
  }
  function metrics(){
    const previous=$('metric').value,groups=definitionGroups(rowsFor(all,state()));
    $('metric').innerHTML=groups.map(([k,r],i)=>{const m=r.measurement,d=m.definition;return `<option value="${esc(k)}">${esc(m.name)} [${esc(m.unit)}] · ${esc(d.stage)} · ${esc(d.region.detector_bpm)} · group ${i+1}</option>`;}).join('');
    const found=groups.find(([k])=>k===previous)||groups.find(([,r])=>r.measurement.name==='read_noise')||groups[0];
    if(found)$('metric').value=found[0];
  }
  function select(row){selected=row;$('detail').textContent=JSON.stringify(row,null,2);}
  function table(){
    const query=$('search').value.toLowerCase();let rows=rowsFor(all,state());
    if($('table-mode').value==='metric')rows=rows.filter(r=>metricKey(r)===$('metric').value);
    if(query)rows=rows.filter(r=>[byId.get(r.product).filename,r.detector,r.input,r.input_path,r.measurement.name,r.measurement.status,r.measurement.reason].join(' ').toLowerCase().includes(query));
    const view=page(rows,pageIndex);pageIndex=view.index;
    $('measurements').innerHTML=view.rows.map((r,i)=>{const m=r.measurement;return `<tr tabindex="0" data-row="${i}" class="${r.product===highlighted?'selected':''}"><td>${esc(byId.get(r.product).filename)}</td><td>${esc(r.detector)}${r.input?'<br>'+esc(r.input):''}</td><td>${esc(m.name)}</td><td class="number">${esc(pretty(m.value))}</td><td>${esc(m.unit)}</td><td>${esc(m.status)}${m.reason?'<br>'+esc(m.reason):''}</td></tr>`;}).join('');
    for(const tr of $('measurements').querySelectorAll('[data-row]')){const choose=()=>select(view.rows[Number(tr.dataset.row)]);tr.onclick=choose;tr.onkeydown=e=>{if(e.key==='Enter')choose();};}
    $('page').textContent=`Page ${view.index+1} / ${view.pages} · ${view.total} scalar rows`;$('previous').disabled=view.index===0;$('next').disabled=view.index===view.pages-1;
  }
  function plot(){
    const key=$('metric').value,rows=rowsFor(all,state()),plotted=points(rows,key),sample=rows.find(r=>metricKey(r)===key);
    $('definition').textContent=sample?JSON.stringify({unit:sample.measurement.unit,...sample.measurement.definition}):'No stored measurements in this scope.';
    $('plot-note').textContent=plotted.length+' numeric measured values; unavailable/nonnumeric values remain in the table. Horizontal offsets separate products/inputs within each detector. No fit or aggregation.';
    if(!plotted.length){$('plot').innerHTML='<p class="empty">No numeric measured values for this definition group.</p>';return;}
    const ds=[...new Set(rows.map(r=>r.detector))].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})),yr=range(plotted.map(r=>r.measurement.value));
    const width=Math.max(960,ds.length*62),height=420,left=85,right=25,top=24,bottom=100;
    const box={width,height,left,right,top,bottom,xmin:-.5,xmax:ds.length-.5,ymin:yr[0],ymax:yr[1],xunit:'detector index (offset for visibility)',yunit:sample.measurement.unit};
    const x=v=>left+(v-box.xmin)/(box.xmax-box.xmin)*(width-left-right),y=v=>height-bottom-(v-yr[0])/(yr[1]-yr[0])*(height-top-bottom);
    let svg=`<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Stored QC by detector; diamonds highlight selected product" data-inspection="${esc(JSON.stringify(box))}">`;
    for(let i=0;i<=5;i++){const v=yr[0]+i*(yr[1]-yr[0])/5;svg+=`<line x1="${left}" x2="${width-right}" y1="${y(v)}" y2="${y(v)}" stroke="#e3e9ef"/><text x="${left-9}" y="${y(v)+4}" text-anchor="end" font-size="12">${esc(Number(v.toPrecision(5)))}</text>`;}
    ds.forEach((d,i)=>{svg+=`<text transform="translate(${x(i)},${height-bottom+18}) rotate(40)" font-size="12">${esc(d)}</text>`;});
    plotted.forEach((r,i)=>{const pi=products.findIndex(p=>p.id===r.product),input=r.input?Number(r.input.split('-').at(-1)):0,offset=(pi-(products.length-1)/2)*.13+(Number.isFinite(input)?input*.008:0),px=x(ds.indexOf(r.detector)+Math.max(-.35,Math.min(.35,offset))),py=y(r.measurement.value),chosen=r.product===highlighted;
      const title=esc(byId.get(r.product).filename+' · '+r.detector+' · '+(r.input||'master')+' · '+r.measurement.name+' = '+pretty(r.measurement.value)+' '+r.measurement.unit);
      svg+=chosen?`<path tabindex="0" data-row="${i}" d="M${px},${py-6}l6,6 -6,6 -6,-6Z" fill="#b75d00"><title>${title}</title></path>`:`<circle tabindex="0" data-row="${i}" cx="${px}" cy="${py}" r="4" fill="#2878a6" opacity=".7"><title>${title}</title></circle>`;
    });
    svg+='<g data-crosshair style="display:none;pointer-events:none"><line data-vertical y1="'+top+'" y2="'+(height-bottom)+'" stroke="#52697a" stroke-dasharray="3"/><line data-horizontal x1="'+left+'" x2="'+(width-right)+'" stroke="#52697a" stroke-dasharray="3"/></g></svg>';
    $('plot').innerHTML=svg+'<p data-cursor-readout class="note">Move over plot for x/y coordinates.</p>';root.QcPlotInspection.bind($('plot'));
    for(const point of $('plot').querySelectorAll('[data-row]')){const choose=()=>select(plotted[Number(point.dataset.row)]);point.onclick=choose;point.onkeydown=e=>{if(e.key==='Enter')choose();};}
  }
  function render(){productTable();table();plot();if(selected)$('detail').textContent=JSON.stringify(selected,null,2);}
  $('product').onchange=()=>{highlighted=$('product').value;render();};
  for(const id of ['scope','detector'])$(id).onchange=()=>{pageIndex=0;metrics();render();};
  $('metric').onchange=()=>{pageIndex=0;table();plot();};
  for(const id of ['search','table-mode'])$(id).oninput=()=>{pageIndex=0;table();};
  $('previous').onclick=()=>{pageIndex--;table();};$('next').onclick=()=>{pageIndex++;table();};
  metrics();render();
})(globalThis);
