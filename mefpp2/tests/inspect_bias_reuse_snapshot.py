"""Read-only confirmation of the exact retained fixture mismatch in issue #294.

Use the selected ASDF interpreter; check full typed snapshots and the actual ASDF schema.
No FITS/ASDF is created, changed, or reduced. No schema assertion is removed.
"""

import argparse
import json
from pathlib import Path
import asdf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', type=Path, required=True)
    args = parser.parse_args()
    attempt = args.attempt.resolve(strict=True)
    product_directory = attempt / 'recipe-envelope/products/default-all'
    products = list(product_directory.glob('*.asdf'))
    assert len(products) == 1, 'Expected exactly one failed-envelope ASDF'
    expected = json.loads((attempt / 'recipe-envelope/default-all-expected.json').read_text())
    key = 'MEF.BIAS.MEDIAN.EVEN.HANDLING'
    schema = Path(__file__).resolve().parents[1] / 'ins/mef/config/qc-product-schema-2.0.0.json'
    schema_bytes = schema.read_bytes()
    schema_id = json.loads(schema_bytes)['id']
    with asdf.config_context() as config:
        config.add_resource_mapping({schema_id: schema_bytes})
        with asdf.open(products[0], custom_schema=schema_id, lazy_load=False,
                       strict_extension_check=True) as handle:
            handle.validate()
            actual = json.loads(handle.tree['qc']['provenance']['configuration']['snapshot'])
    wanted = expected['configuration']
    changed = {name: {'expected': wanted.get(name), 'actual': actual.get(name)}
               for name in wanted.keys() | actual.keys() if wanted.get(name) != actual.get(name)}
    print(json.dumps({'snapshot_differences': changed}, indent=2), flush=True)
    assert key not in wanted, 'Mismatch is not the omitted expectation'
    assert changed == {key: {'expected': None, 'actual': {'type': 'string', 'value': 'lower'}}}, \
        'Unexpected snapshot difference; stop before retry'
    print('PASS: retained mismatch is exactly the omitted explicit lower-policy expectation')


if __name__ == '__main__':
    main()
