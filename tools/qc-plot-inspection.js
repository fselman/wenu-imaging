/* Generic plot interaction and signal axes. No scientific curve computations. */
(function(root){
  'use strict';
  let spec;
  function configure(value){
    if(value.schema_version!==1||!(value.signal_major_step_adu>0)||!(value.signal_maximum_adu>value.signal_minimum_adu)||!Array.isArray(value.signal_ticks_adu))
      throw new Error('Unknown signal-axis specification');
    spec=value;
  }
  function signalRange(minimum,maximum){
    return [Math.min(spec.signal_minimum_adu,Math.floor(minimum/spec.signal_major_step_adu)*spec.signal_major_step_adu),
            maximum<=spec.signal_maximum_adu?spec.signal_maximum_adu:Math.ceil(maximum/spec.signal_major_step_adu)*spec.signal_major_step_adu];
  }
  function signalTicks(minimum,maximum){
    const ticks=new Set(spec.signal_ticks_adu);
    for(let value=Math.floor(minimum/spec.signal_major_step_adu)*spec.signal_major_step_adu;
        value<=maximum;value+=spec.signal_major_step_adu)if(value>=minimum)ticks.add(value);
    return [...ticks].filter(value=>value>=minimum&&value<=maximum).sort((a,b)=>a-b);
  }
  function coordinateAt(box,px,py){
    if(px<box.left||px>box.width-box.right||py<box.top||py>box.height-box.bottom)return null;
    return {x:box.xmin+(px-box.left)/(box.width-box.left-box.right)*(box.xmax-box.xmin),
            y:box.ymin+(box.height-box.bottom-py)/(box.height-box.top-box.bottom)*(box.ymax-box.ymin)};
  }
  function bind(container){
    for(const svg of container.querySelectorAll('svg[data-inspection]')){
      const box=JSON.parse(svg.dataset.inspection),group=svg.querySelector('[data-crosshair]'),
        vertical=group.querySelector('[data-vertical]'),horizontal=group.querySelector('[data-horizontal]'),
        readout=svg.parentElement.querySelector('[data-cursor-readout]');
      function clear(){group.style.display='none';if(readout)readout.textContent='Move over plot for x/y coordinates.';}
      svg.onpointermove=event=>{
        const matrix=svg.getScreenCTM();if(!matrix)return;
        const point=svg.createSVGPoint();point.x=event.clientX;point.y=event.clientY;
        const local=point.matrixTransform(matrix.inverse()),value=coordinateAt(box,local.x,local.y);
        if(!value){clear();return;}
        group.style.display='';
        for(const name of ['x1','x2'])vertical.setAttribute(name,local.x);
        for(const name of ['y1','y2'])horizontal.setAttribute(name,local.y);
        const number=v=>Number(v).toLocaleString('en-US',{maximumSignificantDigits:8});
        if(readout)readout.textContent='Cursor x: '+number(value.x)+' '+box.xunit+' · y: '+number(value.y)+' '+box.yunit;
      };
      svg.onpointerleave=clear;svg.onpointercancel=clear;
    }
  }
  root.QcPlotInspection={configure,signalRange,signalTicks,coordinateAt,bind};
  if(typeof module!=='undefined'&&module.exports)module.exports=root.QcPlotInspection;
})(globalThis);
