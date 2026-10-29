"""F5 preparation controls only: archived log parsing and fixed fixture identities."""
import argparse,json,re,tempfile,warnings
from pathlib import Path
from qualify_integrated_chapman3 import checked_diagnostics,WIRING,F4_SHA,F3_SHA
from integrated_campaign_products import file_hash
from prepare_integrated_campaign_fixture import prepare


def rejected(text):
    try:checked_diagnostics(text)
    except (RuntimeError,ValueError,KeyError):return
    raise AssertionError('Damaged log unexpectedly accepted')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--log',type=Path,required=True);args=parser.parse_args()
    # Read one real accepted cycle; altered copies exercise parser rejection only.
    output=args.log.read_text();match=re.search(r'^INTEGRATED CYCLE BEGIN 0\n.*?^INTEGRATED CYCLE END 0\n',output,re.M|re.S)
    assert match;good=match[0];state=checked_diagnostics(good)
    assert state['ownership']['native_exit']==0
    rejected(good.replace('INTEGRATED CYCLE END 0','INTEGRATED CYCLE END 1'))
    rejected(good+good)
    rejected(good.replace('native_exit=0','native_exit=1',1))
    rejected(good.replace('identity_equal=1','identity_equal=0',1))
    rejected(good+'runtime error: negative parser control\n')
    rejected(good+'F3 INJECT cube allocation\n')
    # Build wiring contains only the previously qualified observer target.
    assert WIRING.count('add_executable(integrated_observer ')==1
    assert 'target_link_libraries(integrated_observer PRIVATE mefpp_common)' in WIRING
    repo=Path(__file__).resolve().parents[2];receipts=repo/'docs/developer/fixtures'
    mac=receipts/'mac-integrated-f4-inspected-2026-10-28/run-provenance.json'
    prior=receipts/'mac-integrated-f3-inspected-2026-10-28/v2.5-cube-allocation-run-provenance.json'
    assert file_hash(mac)==F4_SHA and file_hash(prior)==F3_SHA
    expected={k:v for k,v in json.loads(prior.read_text())['cases'][1]['input_sha256'].items() if k!='run-provenance.json'}
    # Deterministic preparation in both directories, not actual target execution.
    with tempfile.TemporaryDirectory() as tmp,warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for mode in ('17','90'):assert prepare(Path(tmp)/mode,repo)['input_sha256']==expected
    print('F5 controls passed: real cycle parsed, malformed cycle/status/descriptor/diagnostic samples rejected, pinned references and exact fixture bytes verified; native launches 0')


if __name__=='__main__':main()
