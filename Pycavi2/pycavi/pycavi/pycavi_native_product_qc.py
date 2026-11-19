"""Read the shared native product schema offline; no computation or publication."""
import json
from pathlib import Path
try:
    from . import pycavi_qc as qc
except ImportError:
    import pycavi_qc as qc
SCHEMA = Path(__file__).resolve().parents[3]/'mefpp2/ins/mef/config/qc-product-schema-2.0.0.json'


def read(path):
    asdf = qc._asdf()
    schema_bytes = SCHEMA.read_bytes()
    schema_id = json.loads(schema_bytes)['id']
    with asdf.config_context() as configuration:
        configuration.add_resource_mapping({schema_id: schema_bytes})
        with asdf.open(path, custom_schema=schema_id, lazy_load=False, memmap=False) as archive:
            archive.validate()
            return dict(archive.tree['qc'])
