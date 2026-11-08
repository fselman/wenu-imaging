"""Exercise real continuation preflight with simulated host/receipt metadata.
No native recipe, ASDF, build or target host execution. Stop at first write.
"""
import importlib.util,json,sys,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path('mefpp2/tests').resolve()))
import continue_bias_readability_mac as runner
class WriteBoundary(Exception):pass

def exercise(module):
    gate=module.gate
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory);previous=root/'previous';previous.mkdir();source=root/'source';source.mkdir()
        recipe=root/'recipe';recipe.write_text('unchanged binary')
        cache=root/'cache';cache.write_text('TEST:STRING=x\n')
        adapter=root/'adapter';adapter.write_text('unchanged reference')
        (previous/'CMakeCache.configured.txt').write_bytes(cache.read_bytes())
        (source/'example.c').write_text('unchanged source')
        native=previous/'native-recipe';native.mkdir()
        (native/'bias-recipe-results.json').write_text(json.dumps(dict(successful=True,tests=8,real_asdf_exercised=True)))
        (native/'bias.toml').write_text('[native]\n"MEF.BIAS.MEDIAN.EVEN.HANDLING"="lower"\n')
        commands=[]
        for label in ['revision-stamp','build','run-resources','operation-template','service','native-recipe','recipe-envelope']:
            log=previous/(label+'.log');log.write_text('simulated log')
            commands.append(dict(label=label,exit_status=int(label=='recipe-envelope'),log=str(log),sha256=gate.digest(log)))
        before=dict(status='stopped',producer_revision=gate.CANDIDATE,commands=commands,
            binary_after=gate.digest(recipe),cache_after=gate.digest(cache),source_sha256={'example.c':gate.digest(source/'example.c')})
        (previous/'qualification.json').write_text(json.dumps(before))
        args=SimpleNamespace(repository=Mock(resolve=Mock(return_value=Path('/Users/fselman/Developer/wenu-imaging'))),test_revision='simulated-test-head')
        def output(command,**kwargs):
            if command[0]=='ps':return ''
            parts=command[1:]
            if parts==['remote','get-url','origin']:return 'git@github.com:fselman/wenu-imaging.git'
            if parts==['branch','--show-current']:return 'refactor/bias-readability'
            if parts==['rev-parse','HEAD']:return args.test_revision
            if parts[0]=='status':return ''
            if parts[0]=='diff':return 'docs/test-only.md'
            if parts[0]=='ls-tree':return ''
            raise AssertionError(command)
        from contextlib import ExitStack
        with ExitStack() as stack:
            for obj,name,value in [(module,'PREVIOUS',previous),(gate,'SOURCE',source),(gate,'BUILD',root/'build'),(gate,'CACHE',cache),(gate,'RECIPE',recipe),(gate,'ADAPTER',adapter),(gate,'ADAPTER_HASH',gate.digest(adapter)),(sys,'prefix',gate.PYTHON_PREFIX)]:
                stack.enter_context(patch.object(obj,name,value))
            stack.enter_context(patch.object(module.platform,'system',return_value='Darwin'))
            stack.enter_context(patch.object(module.socket,'gethostname',return_value='MC02VV0HPHTDG'))
            stack.enter_context(patch.object(module.argparse.ArgumentParser,'parse_args',return_value=args))
            stack.enter_context(patch.object(module.subprocess,'check_output',side_effect=output))
            stack.enter_context(patch.object(module.subprocess,'run',return_value=None))
            stack.enter_context(patch.object(module.tempfile,'mkdtemp',side_effect=WriteBoundary))
            try:module.main()
            except WriteBoundary:return 'reached first-write boundary'
            except UnboundLocalError:return 'failed on uninitialized record'
            raise AssertionError('Unexpected completion')

original_text=__import__('subprocess').check_output(['git','show','0ef5b93fca73549f29143526bbec4e4d7d2b7e40'],text=True)
original=__import__('types').ModuleType('original_continuation');original.__file__=runner.__file__;exec(compile(original_text,runner.__file__,'exec'),original.__dict__)
before=exercise(original);after=exercise(runner)
assert before=='failed on uninitialized record' and after=='reached first-write boundary',(before,after)
print(json.dumps(dict(scope='simulated host/receipt control-flow only; no native or Mac execution',before=before,after=after),indent=2))
