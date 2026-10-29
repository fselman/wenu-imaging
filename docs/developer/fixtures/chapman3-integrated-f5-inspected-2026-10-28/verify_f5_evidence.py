"""Independent read-only F5 archive checks; never runs a native executable."""
import argparse,hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'mefpp2/tests'))
from integrated_campaign_products import verify,file_hash
from qualify_integrated_chapman3 import checked_diagnostics,WIRING,F4_SHA,F3_SHA
from qualify_integrated_campaign_mac import comparable


def inspect(root,repo):
    manifest=json.loads((root/'transfer-manifest.json').read_text());assert len(manifest['files'])==94
    for name,h in manifest['files'].items():assert file_hash(root/name)==h,name
    r=json.loads((root/'run-provenance.json').read_text())
    assert r['source']==dict(commit='57dd1739bd0bd30d7a74fe26f411fc07a3dc5373',dirty=False)
    assert r['fixed_row']=='F5' and r['host'].split('.')[0]=='chapman3' and r['status']=='F5-passed-awaiting-review' and r['execution_complete']
    assert [r[k] for k in ('planned_launches_consumed','retest_launches_consumed','native_launches_consumed','correction_rounds_consumed')]==[19,10,29,2]
    assert r['inherited_mac_reference_sha256']==F4_SHA and r['prior_mac_reference_sha256']==F3_SHA
    assert not r['installation_performed'] and not r['scientific_acceptance_claimed']
    for k in ('protected_files_unchanged','fixture_inputs_unchanged','fixture_reports_unchanged','checkout_unchanged'):assert r[k],k
    assert len(r['commands'])==6 and [c['label'] for c in r['commands']]==['configure-c17','build-c17','configure-c90','build-c90','F5-c17','F5-c90']
    assert sum(c['native'] for c in r['commands'])==2
    for c in r['commands']:
        assert c['exit_status']==0 and file_hash(root/Path(c['log']).name)==c['log_sha256']
    wiring=root/'source/mefpp2/CMakeLists.txt'
    assert wiring.read_bytes()==(repo/'mefpp2/CMakeLists.txt').read_bytes()+WIRING.encode()
    assert file_hash(wiring)==r['private_cmake_sha256']
    for name in ('integrated_calibration_observer.c','integrated_descriptor_observer.h'):
        assert (root/'source/mefpp2/tests'/name).read_bytes()==(repo/'mefpp2/tests'/name).read_bytes()
    receipts=repo/'docs/developer/fixtures';prior_path=receipts/'mac-integrated-f3-inspected-2026-10-28/v2.5-cube-allocation-run-provenance.json'
    assert file_hash(prior_path)==F3_SHA
    reference=json.loads(prior_path.read_text())['cases'][1];expected={k:v for k,v in reference['input_sha256'].items() if k!='run-provenance.json'}
    assert [(c['mode'],c['status']) for c in r['cases']]==[('17','passed'),('90','passed')]
    inventory_counts=[];warnings={};products_by_mode={}
    for case in r['cases']:
        mode=case['mode'];directory=root/('c'+mode+'-functional');build=root/('build-c'+mode)
        assert not case['findings'] and case['input_sha256']==expected
        assert file_hash(directory/'run-provenance.json')==case['fixture_report_sha256']
        products=verify(directory,case['input_sha256'],2,True,['F1_CCD_A','F1_CCD_B'])
        assert products==case['products'] and comparable(products)==comparable(reference['products'])
        products_by_mode[mode]=comparable(products)
        state=checked_diagnostics((root/('F5-c'+mode+'.log')).read_text())
        assert json.loads(json.dumps(state))==case['diagnostics']
        info=json.loads((build/'build-info.json').read_text())
        assert info['source_revision']==r['source']['commit'] and str(info['c_standard'])==mode
        assert info['system']=='Linux' and info['processor']=='x86_64' and info['compiler_id']=='GNU' and info['compiler_version']=='10.2.1' and info['cmake_version']=='3.29.6'
        assert info['qfits_memory_mode']==2 and info['qfits_max_pointers']==2000000
        assert '-std=c'+mode in (build/'CMakeFiles/integrated_observer.dir/flags.make').read_text()
        inventory=build/'source-sha256.txt';assert file_hash(inventory)==info['native_source_inventory_sha256']
        rows=inventory.read_text().splitlines();assert len(rows)==len(set(x.rsplit(' ',1)[0] for x in rows))
        for row in rows:
            name,h=row.rsplit(' ',1);path=wiring if name=='CMakeLists.txt' else repo/'mefpp2'/name
            assert file_hash(path)==h,name
        inventory_counts.append(len(rows))
        log=(root/('build-c'+mode+'.log')).read_text();assert 'Built target integrated_observer' in log and not re.search(r'^.*:\d+:\d+: (?:fatal )?error:',log,re.M)
        warnings[mode]=len(re.findall(r'warning:',log))
    assert products_by_mode['17']==products_by_mode['90']
    return dict(status='accepted-bounded-F5',archive_sha256='1eac1e5d6cef30f22c3ab8f5650556e66d516bec3a393ffb7c0db8242f0b4ef1',files_verified=94,command_logs_verified=6,builds_verified=2,source_inventory_entries_verified=inventory_counts,private_wiring_and_unchanged_observer_verified=True,exact_products_verified=12,ordered_detector_arrays_verified=24,native_roles_verified=2,cleaned_resources='zero both modes',descriptors='stable within both modes',compiler_warnings=warnings,planned_launches=19,retest_launches=10,total_launches=29,general_rounds=2,report_sha256=file_hash(root/'run-provenance.json'),limitations=['Internal target accounting/ownership/descriptors; no target external sanitizer/leaks suite','Binaries retained on Chapman with host-verified hashes, not independently reread','No scientific/full Stage 2/Phase 3 acceptance; #116 unresolved; owner review pending'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',type=Path,required=True);parser.add_argument('--result',type=Path,required=True);args=parser.parse_args()
    result=inspect(args.evidence,Path(__file__).resolve().parents[4]);args.result.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
