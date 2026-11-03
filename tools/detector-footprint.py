#!/usr/bin/env python3
"""Render detector and processing TOMLs as a self-contained, offline SVG/HTML mosaic."""
import argparse
import html
import json
from pathlib import Path
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rect(value, width, height, label):
    require(isinstance(value, list) and len(value) == 4 and
            all(type(v) is int for v in value), f'{label}: integer rectangle required')
    x1, x2, y1, y2 = value
    require(1 <= x1 <= x2 <= width and 1 <= y1 <= y2 <= height,
            f'{label}: rectangle outside footprint: {value}')
    return value


def load(detector_path, processing_path):
    with detector_path.open('rb') as stream:
        geometry = tomllib.load(stream)
    with processing_path.open('rb') as stream:
        processing = tomllib.load(stream)
    require(geometry.get('footprint_schema_version') == 1, 'Unknown detector schema')
    require(processing.get('processing_footprint_schema_version') == 1,
            'Unknown processing schema')
    require(geometry['instrument'] == processing['instrument'], 'Instrument mismatch')
    require(geometry.get('binning') == [1, 1], 'Only explicit 1x1 profiles supported')
    detectors = geometry['detector']
    require(bool(detectors), 'No detectors')
    ids = [d['id'] for d in detectors]
    require(len(set(ids)) == len(ids), 'Duplicate detector identity')
    trims = processing['trim']
    require(len(trims) == len(ids) and {t['detector'] for t in trims} == set(ids),
            'Each detector needs exactly one trim')
    trim_by_id = {t['detector']: t for t in trims}
    positions = set()
    for d in detectors:
        size = d['raw_size']
        require(len(size) == 2 and all(type(v) is int and v > 0 for v in size),
                'Invalid raw size')
        w, h = size
        require(d['amplifier_corner'] in ('lower-left', 'lower-right', 'upper-left', 'upper-right'),
                'Invalid amplifier corner')
        position = (d['mosaic_column'], d['mosaic_row'])
        require(all(type(v) is int and v > 0 for v in position) and position not in positions,
                'Invalid or duplicate mosaic position')
        positions.add(position)
        for key in ('illuminated', 'prescan', 'overscan'):
            rect(d[key], w, h, d['id'] + ' ' + key)
        t = trim_by_id[d['id']]
        for key in ('retained', 'prescan_sample', 'overscan_sample'):
            rect(t[key], w, h, d['id'] + ' ' + key)
        for key in ('prescan', 'overscan'):
            full, sample = d[key], t[key + '_sample']
            require(full[0] <= sample[0] <= sample[1] <= full[1] and
                    full[2] <= sample[2] <= sample[3] <= full[3],
                    'Scan sample must lie inside full scan band')
    roi_ids = set()
    for r in processing.get('roi', []):
        require(r['id'] not in roi_ids, 'Duplicate ROI name')
        roi_ids.add(r['id'])
        require(r['detector'] in ids, 'ROI references unknown detector')
        d = detectors[ids.index(r['detector'])]
        require(r['amplifier'] == d['amplifier'], 'ROI amplifier mismatch')
        crop = trim_by_id[r['detector']]['retained']
        rect([r[k] for k in ('xmin', 'xmax', 'ymin', 'ymax')],
             crop[1]-crop[0]+1, crop[3]-crop[2]+1, r['id'])
    require(processing.get('roi_coordinates') == 'retained-active', 'Unknown ROI coordinates')
    return geometry, processing, trim_by_id


def svg(d, t, rois):
    """SVG y is inverted once; stored arrays/bounds remain unrotated FITS coordinates."""
    w, h = d['raw_size']
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-140 -160 {w+280} {h+320}" '
             f'role="img" aria-label="{html.escape(d["id"], quote=True)} raw footprint">']
    def box(bounds, css, title):
        x1, x2, y1, y2 = bounds
        parts.append(f'<rect class="{css}" x="{x1-.5}" y="{h-y2+.5}" '
                     f'width="{x2-x1+1}" height="{y2-y1+1}"><title>'
                     f'{html.escape(title)}: {bounds}</title></rect>')
    box([1,w,1,h], 'raw', 'Raw footprint')
    a = d['illuminated']
    if a[2] > 1:
        box([1,w,1,a[2]-1], 'extra', 'Extra rows below illuminated area')
    if a[3] < h:
        box([1,w,a[3]+1,h], 'extra', 'Extra rows above illuminated area')
    box(a, 'illuminated', 'Illuminated')
    for key in ('prescan','overscan'):
        box(d[key], key, key)
        box(t[key+'_sample'], 'sample', key+' selected sample')
    box(t['retained'], 'retained', 'Retained after trimming')
    x0, _, y0, _ = t['retained']
    for n, r in enumerate(rois, 1):
        b=[r['xmin']+x0-1,r['xmax']+x0-1,r['ymin']+y0-1,r['ymax']+y0-1]
        box(b, 'roi', r['id'])
        parts.append(f'<text x="{(b[0]+b[1])/2}" y="{h-(b[2]+b[3])/2}" '
                     f'class="roi-label">{n}</text>')
    corner = d['amplifier_corner']
    ax = w+65 if corner.endswith('right') else -65
    ay = -65 if corner.startswith('upper') else h+65
    parts.append(f'<rect x="{ax-48}" y="{ay-48}" width="96" height="96" class="amp">'
                 f'<title>Output {html.escape(d["amplifier"])}; schematic {corner} corner, '
                 'not a measured physical package location</title></rect>')
    parts.append(f'<text class="axis" x="{w/2}" y="{h+145}">X → 1 … {w}</text>'
                 f'<text class="axis" x="{w/2}" y="-75">Y ↑ 1 … {h}</text></svg>')
    return ''.join(parts)


def details(d, t, rois):
    illum = d['illuminated']; h = d['raw_size'][1]
    rows = [('Raw size', str(d['raw_size'])), ('Illuminated', str(illum)),
            ('Retained after trimming', str(t['retained'])),
            ('Extra rows below', f'1–{illum[2]-1}' if illum[2]>1 else 'none'),
            ('Extra rows above', f'{illum[3]+1}–{h}' if illum[3]<h else 'none'),
            ('Prescan full band',str(d['prescan'])), ('Prescan sample',str(t['prescan_sample'])),
            ('Overscan full band',str(d['overscan'])), ('Overscan sample',str(t['overscan_sample'])),
            ('Amplifier',f'{d["amplifier"]}; {d["amplifier_corner"]} (schematic)'),
            ('Native PAF CHIP',str(d['native_paf_chip'])),
            ('Reference HDU',str(d['reference_hdu'])+'; identity must be checked for future files')]
    table='<table>'+''.join('<tr><th>'+html.escape(k)+'</th><td>'+html.escape(v)+'</td></tr>' for k,v in rows)+'</table>'
    table+='<h3>ROIs — retained-active coordinates</h3><table><tr><th>#</th><th>Name</th><th>X</th><th>Y</th></tr>'
    for n,r in enumerate(rois,1):
        table+=f'<tr><td>{n}</td><td>{html.escape(r["id"])}</td><td>{r["xmin"]}–{r["xmax"]}</td><td>{r["ymin"]}–{r["ymax"]}</td></tr>'
    return table+'</table>'


CSS='''
body{font:15px system-ui,sans-serif;margin:24px;background:#f7f8fa;color:#17212b}h1{font-size:24px}p{max-width:1000px}
.controls{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:18px 0}button,select{font:inherit;padding:7px}
#mosaic{display:grid;gap:10px;max-width:1500px}.tile{background:white;border:1px solid #b8c2cb;padding:8px;cursor:pointer;min-width:0}
.tile h2{font-size:13px;text-align:center;margin:0}.tile svg{width:100%;display:block}.raw{fill:#eef0f3;stroke:#1b2630;stroke-width:5}
.extra{fill:#bec6d0}.illuminated{fill:#d6eed8;stroke:#33834c;stroke-width:5}.prescan{fill:#cca4eb}.overscan{fill:#f2b34e}
.sample{fill:none;stroke:#151515;stroke-width:4;stroke-dasharray:14 9}.retained{fill:none;stroke:#0062b8;stroke-width:9}
.roi{fill:#3188d1;fill-opacity:.18;stroke:#155289;stroke-width:6}.roi-label{font:90px sans-serif;text-anchor:middle;dominant-baseline:middle;fill:#123858}
.amp{fill:#df2020;stroke:white;stroke-width:4}.axis{font:55px sans-serif;text-anchor:middle;fill:#34404b}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:15px 0}.swatch{display:inline-block;width:17px;height:13px;border:1px solid #555;vertical-align:middle}
#detail{background:white;margin-top:20px;padding:20px;display:none}.detail-grid{display:grid;grid-template-columns:minmax(240px,420px) minmax(330px,1fr);gap:25px;align-items:start}
#large{overflow:auto;max-height:85vh;border:1px solid #ddd}#large svg{width:100%;display:block}table{border-collapse:collapse;font-size:13px}th,td{padding:5px 9px;border-bottom:1px solid #ddd;text-align:left}th{font-weight:600}
@media(max-width:750px){.detail-grid{display:block}.tile h2{font-size:10px}}@media print{.controls{display:none}#mosaic{break-after:page}.tile{break-inside:avoid}}
'''


def render(geometry, processing, trims):
    ds=geometry['detector']; cols=max(d['mosaic_column'] for d in ds); rows=max(d['mosaic_row'] for d in ds)
    cards=[]; payload=[]
    for i,d in enumerate(ds):
        rois=[r for r in processing.get('roi',[]) if r['detector']==d['id']]
        drawing=svg(d,trims[d['id']],rois)
        cards.append(f'<button class="tile" data-index="{i}" style="grid-column:{d["mosaic_column"]};grid-row:{rows-d["mosaic_row"]+1}">'
                     f'<h2>{html.escape(d["id"])}<br>CHIP {d["native_paf_chip"]} · output {html.escape(d["amplifier"])}</h2>{drawing}</button>')
        payload.append(dict(title=d['id'],svg=drawing,table=details(d,trims[d['id']],rois)))
    data=json.dumps(payload).replace('<','\\u003c')
    legends=[('#d6eed8','Illuminated'),('#0062b8','Retained boundary'),('#cca4eb','Prescan'),('#f2b34e','Overscan'),('#bec6d0','Extra rows'),('#8ebae0','ROIs'),('#df2020','Output amplifier')]
    legend=''.join(f'<span><i class="swatch" style="background:{c}"></i> {label}</span>' for c,label in legends)
    options=''.join(f'<option value="{i}">{html.escape(d["id"])}</option>' for i,d in enumerate(ds))
    policy=f'Prescan enabled: {processing["use_prescan"]}; overscan enabled: {processing["use_overscan"]}; rejected scan samples low/high: {processing["scan_reject_low"]}/{processing["scan_reject_high"]}.'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(geometry['instrument'])} detector footprints</title><style>{CSS}</style>
<h1>{html.escape(geometry['instrument'].upper())} — detector footprints and processing regions</h1>
<p>Full raw footprints at true pixel aspect ratio; FITS X increases right and Y up. No WCS, rotation or resampling. Mosaic spacing is schematic. Click a detector for coordinates and an enlarged view.</p>
<p>Blue outline encloses the area retained after trimming; everything outside it is discarded. Dashed scan outlines show PAF-selected sample ranges within the full scan bands. Red squares mark amplifier corners schematically, outside the pixel array.</p>
<div class="legend">{legend}</div><p>{policy}</p>
<div class="controls"><label>Detector <select id="choose">{options}</select></label><button id="inspect">Inspect</button><label>Detail magnification <select id="zoom"><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select></label><button id="print">Print / save PDF</button></div>
<div id="mosaic" style="grid-template-columns:repeat({cols},minmax(70px,1fr))">{''.join(cards)}</div>
<section id="detail"><h2 id="name"></h2><div class="detail-grid"><div id="large"></div><div id="numbers"></div></div></section>
<p>Reference geometry: validate against selected raw headers before numerical use. Candidate ROIs are editable processing choices. These visualization schemas do not activate native reduction settings.</p>
<script>const panels={data};
function show(i,scroll=true){{document.getElementById('choose').value=i;document.getElementById('detail').style.display='block';document.getElementById('name').textContent=panels[i].title;document.getElementById('large').innerHTML=panels[i].svg;document.getElementById('numbers').innerHTML=panels[i].table;zoom();if(scroll)document.getElementById('detail').scrollIntoView({{behavior:'smooth'}});}}
function zoom(){{const s=document.querySelector('#large svg');if(s)s.style.width=(100*Number(document.getElementById('zoom').value))+'%';}}
document.querySelectorAll('.tile').forEach(b=>b.onclick=()=>show(Number(b.dataset.index)));
document.getElementById('inspect').onclick=()=>show(Number(document.getElementById('choose').value));document.getElementById('zoom').onchange=zoom;document.getElementById('print').onclick=()=>window.print();show(0,false);
</script></html>'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('detectors',type=Path,help='Detector geometry TOML')
    p.add_argument('processing',type=Path,help='Processing / ROI TOML')
    p.add_argument('--output',required=True,type=Path,help='New standalone HTML file (never overwritten)')
    p.add_argument('--open',action='store_true',help='Open in default browser')
    args=p.parse_args()
    try:
        geometry,processing,trims=load(args.detectors,args.processing)
        document=render(geometry,processing,trims)
        with args.output.open('x',encoding='utf-8') as stream:
            stream.write(document)
    except (ValueError,KeyError,OSError) as error:
        p.exit(1,f'Footprint error: {error}\n')
    print(args.output.resolve())
    if args.open:
        import webbrowser
        webbrowser.open(args.output.resolve().as_uri())


if __name__=='__main__':
    main()
