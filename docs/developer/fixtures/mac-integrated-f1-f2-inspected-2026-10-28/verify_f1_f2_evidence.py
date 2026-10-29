"""Read-only receipt of archived F1 products and F1/F2 logs/reports; no engine run."""
import argparse, hashlib, json, re, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'mefpp2/tests'))
from integrated_campaign_products import verify, file_hash
from qualify_integrated_campaign_mac import comparable, diagnostic


def inspect(root):
    manifest=json.loads((root/'transfer-manifest.json').read_text())
    assert len(manifest['files'])==416
    for name,h in manifest['files'].items():assert file_hash(root/name)==h,name
    def local(path):return root/Path(path).relative_to(manifest['source_run'])
    reports={name:json.loads((root/name/'run-provenance.json').read_text()) for name in
             ('v2.2-bias-qc','v2.3-bpm-filenames')}
    latest=reports['v2.3-bpm-filenames']
    assert latest['source']['commit']=='f5afd08fbfb35a8a50409c92352f9061c92c1f69'
    assert latest['status']=='F1-F2-passed-awaiting-review' and latest['execution_complete']
    assert [latest[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]==[6,6,12,2]
    for key in ('protected_files_unchanged','checkout_unchanged','raw_files_preserved','previous_report_unchanged','inherited_evidence_unchanged'):assert latest[key],key
    count=0;native=0;path=root/'v2.3-bpm-filenames/run-provenance.json';sources=[]
    while path:
        report=json.loads(path.read_text());sources.append(report['source']['commit'])
        for cmd in report['commands']:
            assert file_hash(local(cmd['log']))==cmd['log_sha256']
            count+=1;native+=int(cmd.get('native',False))
        previous=report.get('previous_attempt')
        if previous:
            path=local(previous['report']);assert file_hash(path)==previous['sha256']
        else:path=None
    assert native==12 and len(sources)==5
    results=[]
    for name,row,tiny,detectors in [('v2.2-bias-qc','F1',True,2),('v2.3-bpm-filenames','F2',False,8)]:
        report=reports[name];cases=[c for c in report['cases'] if c['fixed_row']==row]
        assert [c['lane'] for c in cases]==['ordinary','instrumented','leaks']
        reference=None
        for case in cases:
            assert case['status']=='passed' and case['exit_status']==0 and not case['findings']
            products=case['products'];assert len(products)==6
            if tiny:
                actual=verify(local(case['directory']),case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
                assert actual==products
            if reference is None:reference=comparable(products)
            else:assert comparable(products)==reference
            for product in products.values():assert len(product['pixels'])==detectors
            log=(root/name/(row+'-'+case['lane']+'.log')).read_text(errors='replace')
            assert 'ERROR: AddressSanitizer' not in log and 'runtime error:' not in log
            state={}
            if case['lane']!='ordinary':
                diag,findings=diagnostic(log,detectors,case['lane']);assert not findings
                assert json.loads(json.dumps(diag))==case['diagnostics']
                state={phase:diag['accounting'][phase] for phase in ('after-purge','after-second-purge')}
            if not tiny:
                values=re.findall(r'^\[HIERARCH ESO MPP BPM FRAME\d+\]=\[([^\]\r\n]+)\]',log,re.M)
                # stdout/stderr may interleave mid-card; inspect complete lines only.
                expected={'WFI.2001-12-09T20:54:42.040.fits','WFI.2001-12-10T19:54:11.877.fits','WFI.2001-12-10T19:55:17.546.fits'}
                assert set(values)==expected
            results.append(dict(row=row,lane=case['lane'],status='passed',product_categories=len(products),
                detectors=detectors,post_purge=state,product_evidence='independently-read-archived-FITS' if tiny else 'host-verified-pixel/header-reports-and-archived-logs'))
        for p in (root/name).glob('build-c17-*/build-info.json'):
            info=json.loads(p.read_text());assert info['source_revision']==report['source']['commit']
            assert str(info['c_standard'])=='17' and info['system']=='Darwin' and info['osx_architectures']=='x86_64'
            assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
            if 'instrumented' in p.parts[-2]:
                assert '-fsanitize=address,undefined' in info['c_flags']
                symbols=(root/name/'symbols-instrumented.log').read_text();assert '__asan_' in symbols and '__ubsan_' in symbols
    return dict(status='accepted-F1-F2-bounded-functional-memory-slice',files_verified=416,command_logs_verified=count,
        actual_native_launches=native,general_repair_rounds=2,results=results,
        limitations=['Large WFI inputs/products remain on the Mac; their pixels/headers were verified there by the source-pinned runner, not reread from this transfer',
        'F1 is qualified at 9242174 and explicitly inherited; F2 at f5afd08',
        'No scientific/Phase3 acceptance; F3-F5/final C90 and unresolved #116 remain pending; #125 deferred'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--result',type=Path,required=True);a=p.parse_args()
    result=inspect(a.evidence);a.result.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
