#!/usr/bin/env python3
"""Prepare one detector's modelling archive from explicit preserved dependencies.

Default is metadata admission only. --execute invokes the native preparation
recipe and common ASDF publisher in a fresh retained directory.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tomllib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Pycavi2/pycavi/pycavi'))
import pycavi_linearity_config as config
import pycavi_linearity_recipe as recipe
from pycavi_configuration import ProjectComposition


def read_recipe(path):
    """Resolve the execution envelope relative to its recipe file."""
    path = path.resolve(strict=True)
    data = tomllib.loads(path.read_text())
    recipe.require(set(data) == {'linearity_recipe_schema_version', 'project', 'preparation'} and
                   type(data['linearity_recipe_schema_version']) is int and
                   data['linearity_recipe_schema_version'] == 1, 'Unsupported recipe envelope')
    project_path = data['project']
    recipe.require(type(project_path) is str and bool(project_path.strip()), 'Explicit project TOML required')
    project_path = (path.parent / project_path).resolve(strict=True)
    project = ProjectComposition(ROOT).resolve_project(project_path)
    roots = project['roots']
    layout = dict(raw=roots['raw'], orchestration=str(project_path.parent),
                  reduced=roots['output'], calibration=roots['calibration'],
                  work=roots['work'], logs=roots['logs'])
    preparation = data['preparation']
    fields = {'detector_toml', 'processing_toml', 'source_samples', 'handoff',
              'native', 'run', 'source_revision'}
    recipe.require(isinstance(preparation, dict) and set(preparation) == fields,
                   'Incomplete or unknown preparation settings')
    recipe.require(all(type(value) is str and value.strip() for value in
                       preparation.values()), 'Nonempty recipe strings required')
    resolve = lambda value: (path.parent / value).resolve()
    recipe.require(path.is_relative_to(Path(layout['orchestration'])), 'Recipe must be in orchestration')
    arguments = {name: resolve(value) if name != 'source_revision' else value
                 for name, value in preparation.items()}
    for name in ('detector_toml', 'processing_toml'):
        recipe.require(arguments[name].is_relative_to(Path(layout['orchestration'])),
                       'Configuration must be in orchestration')
    arguments['run'] = (Path(roots['output']) / preparation['run']).resolve()
    recipe.require(not Path(preparation['run']).is_absolute(), 'Run must be relative to project output')
    sources = {item['path']: item['sha256'] for item in project['sources']}
    sources[str(path)] = recipe.hashlib.sha256(path.read_bytes()).hexdigest()
    return argparse.Namespace(**arguments), layout, sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, help='BPM/linearity preparation recipe TOML')
    for name in ('detector-toml', 'processing-toml', 'source-samples', 'handoff', 'run', 'native'):
        parser.add_argument('--'+name, type=Path)
    parser.add_argument('--source-revision')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    execute = args.execute
    layout = None
    sources = None
    if args.config:
        recipe.require(all(getattr(args, name) is None for name in
                           ('detector_toml', 'processing_toml', 'source_samples', 'handoff',
                            'run', 'native', 'source_revision')), 'Do not mix recipe and legacy arguments')
        args, layout, sources = read_recipe(args.config)
    recipe.require(all(getattr(args, name) is not None for name in
                       ('detector_toml', 'processing_toml', 'source_samples', 'handoff',
                        'run', 'source_revision')), 'Explicit preparation inputs required')
    work = args.run.resolve(strict=True)
    recipe.require(work.is_dir() and not any(work.iterdir()), 'Fresh empty retained directory required')
    resolved = config.resolve_files(args.detector_toml, args.processing_toml)
    dependencies = recipe.preparation_dependencies(args.source_samples, args.handoff, resolved)
    if layout:
        recipe.preparation_layout(dependencies, work, **layout)
    if not execute:
        report = dict(status='metadata_admitted', raw_FITS_opened=False, measurements_run=False,
                      source_revision=args.source_revision, resolved=resolved, dependencies=dependencies,
                      configuration_sources=sources)
        (work/'plan.json').write_text(json.dumps(report, indent=2)+'\n')
        print('LINEARITY PLAN: metadata_admitted', dependencies['selection']['detector'], flush=True)
        return
    recipe.require(args.native is not None, 'Explicit qualified native executable required')
    report = recipe.prepare_detector(dependencies, args.native, work, resolved=resolved,
        source_revision=args.source_revision, assessment_id='linearity:'+work.name,
        created_at=datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'), layout=layout, configuration_sources=sources)
    print('LINEARITY PREPARATION:', report['status'], flush=True)
    print('PRODUCT:', report['product']['path'], flush=True)


if __name__ == '__main__':
    main()
