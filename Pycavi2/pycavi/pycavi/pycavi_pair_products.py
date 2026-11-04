"""Read completed raw-pair batch metadata; shared by compute and display commands."""
import json
from pathlib import Path
import pycavi_pair_qc as bridge
require=bridge.qc.require

def freeze(paths):
    return {str(Path(p).resolve(strict=True)):bridge.sha(bridge.small(Path(p))) for p in paths}

def batch_products(batch):
    batch=batch.resolve(strict=True)
    paths=[batch/name for name in ('batch.json','execution.json','shared-verification.json')]
    frozen=freeze(paths)
    manifest,receipt,verification=[json.loads(bridge.small(p)) for p in paths]
    require(receipt['status']=='complete_for_owner_inspection' and receipt['source_preservation'] is True and
            receipt['detectors_processed']==len(manifest['entries']) and verification['status']=='passed',
            'Require completed preserved batch')
    require(receipt['manifest_sha256']==frozen[str(paths[0])] and verification['hash_passes_per_image']==2,
            'Batch manifest/verification differs')
    for label in ('before','after'):
        path=batch/('shared-'+label+'.json');frozen.update(freeze([path]))
        require(frozen[str(path)]==verification[label+'_sha256'],'Shared verification hash differs')
    require(json.loads(bridge.small(batch/'shared-before.json'))==json.loads(bridge.small(batch/'shared-after.json')),
            'Shared source verification contents differ')
    products=[Path(manifest['reference']['pairs'])]
    for entry in manifest['entries']:
        parent=Path(entry['measurement']).parent
        require(parent.is_relative_to(batch/'detectors'),'Batch detector path escapes retained batch')
        persistence=parent/'persistence.json';frozen.update(freeze([persistence]))
        saved=json.loads(bridge.small(persistence));path=parent/'asdf/pairs.asdf'
        require(saved['status']=='complete' and saved['roundtrip_exact'] is True and
                saved['metadata_preservation'] is True and saved['products']['pairs']['path']==str(path),
                'Incomplete detector ASDF publication')
        require(bridge.qc.read_record(path).digest==saved['products']['pairs']['digest'],'Saved product digest differs')
        products.append(path)
    return products,frozen

