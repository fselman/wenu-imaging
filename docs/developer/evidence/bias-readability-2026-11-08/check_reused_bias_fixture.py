"""Execute only the real fixture-restoration branch, with metadata-only files.
No native/ASDF claim: reproduce and verify the expected-snapshot omission itself.
"""
import ast, hashlib, json, subprocess, tempfile, tomllib
from pathlib import Path
from types import SimpleNamespace
source=Path('mefpp2/tests/bias_toml_recipe_contract.py')
original=subprocess.check_output(['git','show','e09388b5be911e267e0c977e838483ab6c31fe46'],text=True)
fixed=source.read_text()
results={}
for label,text in [('before',original),('after',fixed)]:
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);previous=root/'fixture';previous.mkdir()
        (previous/'raw').mkdir();(previous/'orchestration').mkdir()
        members=[previous/'raw'/f'bias-{i}.fits' for i in range(4)]
        for member in members:member.write_bytes(b'metadata-only fixture')
        (previous/'bias.list').write_text('\n'.join(map(str,members))+'\n')
        (previous/'bias.toml').write_text('schema_version=1\n[native]\n"MEF.BIAS.MEDIAN.EVEN.HANDLING"="lower"\n')
        for mode in ('masked','omitted','renamed'):
            for index in range(2):
                path=previous/f'reference-{mode}-{index}';path.mkdir()
                (path/'qc.json').write_text('{}')
        (previous/'reference-masked-0/config.json').write_text('{"UNCHANGED":{"type":"int","value":3}}')
        work=root/'new';work.mkdir()
        cls=type('Fixture',(),{})
        context={'a':SimpleNamespace(reuse_fixture=previous,work=work),
            'old':SimpleNamespace(RecipeTests=cls,digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()),
            'json':json,'Path':Path,'tomllib':tomllib}
        node=next(node for node in ast.parse(text).body if isinstance(node,ast.If) and
            ast.unparse(node.test)=='a.reuse_fixture is None')
        exec(compile(ast.Module(body=node.orelse,type_ignores=[]),str(source),'exec'),context)
        expected={'UNCHANGED':{'type':'int','value':3},'MEF.BIAS.MEDIAN.EVEN.HANDLING':{'type':'string','value':'lower'}}
        matches=cls.configuration==expected
        assert matches == (label=='after')
        results[label]={'full_expected_snapshot_matches':matches,'configuration':cls.configuration}
print(json.dumps({'scope':'actual metadata restoration branch only; no native/ASDF execution','results':results},indent=2))
