"""F4 parser/parent/fixture controls only; never executes the native engine."""
import argparse,copy,json,re,tempfile,warnings
from pathlib import Path
from qualify_integrated_repeat_mac import cycles,parent_guard,F3_SHA,TESTED
from integrated_campaign_products import file_hash
from prepare_integrated_campaign_fixture import prepare


def rejected(action):
    try:action()
    except (RuntimeError,ValueError,KeyError):return
    raise AssertionError('Damaged control unexpectedly accepted')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True)
    args=parser.parse_args();root=args.evidence/'v2.5-cube-allocation'
    report=root/'run-provenance.json';assert file_hash(report)==F3_SHA
    old=json.loads(report.read_text());parent_guard(old)
    # Parent mutation controls prevent replaying an unaccepted/advanced campaign.
    for key,value in [('status','stopped'),('native_launches_consumed',27),('cube_exception_consumed',False),('fixture_inputs_unchanged',False)]:
        changed=copy.deepcopy(old);changed[key]=value;rejected(lambda:parent_guard(changed))
    changed=copy.deepcopy(old);changed['cases'][0]['findings']=['finding'];rejected(lambda:parent_guard(changed))
    # Repeat one real log for parser controls only: this is not a native repeat run.
    text=(root/'cube-smoke-instrumented.log').read_text()
    sample=''.join(text.replace('INTEGRATED CYCLE BEGIN 0','INTEGRATED CYCLE BEGIN '+str(i)).replace('INTEGRATED CYCLE END 0','INTEGRATED CYCLE END '+str(i)) for i in range(11))
    assert len(cycles(sample))==11
    rejected(lambda:cycles(sample.replace('INTEGRATED CYCLE END 10','INTEGRATED CYCLE END 9')))
    rejected(lambda:cycles(sample.replace('INTEGRATED CYCLE BEGIN 5','INTEGRATED CYCLE BEGIN 6')))
    rejected(lambda:cycles(sample+'runtime error: synthetic sanitizer control\n'))
    rejected(lambda:cycles(sample.replace('identity_equal=1','identity_equal=0',1)))
    rejected(lambda:cycles(sample.replace('native_exit=0','native_exit=1',1)))
    # Fresh fixture bytes must equal the accepted smoke, including exact expectations.
    repo=Path(__file__).resolve().parents[2]
    expected={k:v for k,v in old['cases'][1]['input_sha256'].items() if k!='run-provenance.json'}
    with tempfile.TemporaryDirectory() as tmp,warnings.catch_warnings():
        warnings.simplefilter('ignore')
        for i in range(2):assert prepare(Path(tmp)/str(i),repo)['input_sha256']==expected
    print('F4 controls passed: accepted parent, 11 parsed cycles, damaged-log/parent rejection, two byte-identical fixtures; native launches 0')


if __name__=='__main__':main()
