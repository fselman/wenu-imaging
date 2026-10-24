"""Exact Gaia identifiers at the query/cache boundary (no network requests)."""
import numpy as np
import pandas as pd


def integer_source_ids(values, label='SOURCE_ID'):
    """Reject masked, floating, duplicate or out-of-range identifiers."""
    values = np.ma.asarray(values)
    if (values.ndim != 1 or not len(values) or values.dtype.kind not in 'iu'
            or np.ma.getmaskarray(values).any() or (values <= 0).any()
            or (values > np.iinfo(np.int64).max).any()):
        raise ValueError('Expected non-null positive int64 Gaia identifiers: ' + label)
    result = np.asarray(values, dtype=np.int64)
    if len(np.unique(result)) != len(result):
        raise ValueError('Duplicate Gaia identifiers: ' + label)
    return result


def normalize_gaia_identifiers(table):
    """Validate explicitly aliased DR3/GSPC IDs, keeping canonical SOURCE_ID."""
    table = table.copy()
    for canonical in ('SOURCE_ID', 'GSPC_SOURCE_ID'):
        names = [name for name in table.colnames
                 if name.casefold() == canonical.casefold()]
        if len(names) != 1:
            raise ValueError('Missing or ambiguous Gaia identifier column: ' + canonical)
        if names[0] != canonical:
            table.rename_column(names[0], canonical)
        table[canonical] = integer_source_ids(table[canonical], canonical)
    if not np.array_equal(table['SOURCE_ID'], table['GSPC_SOURCE_ID']):
        raise ValueError('DR3/GSPC source identifiers do not match')
    table.remove_column('GSPC_SOURCE_ID')
    return table


def read_gaia_csv(path):
    """Read decimal IDs as text first; never round them through binary64."""
    frame = pd.read_csv(path, dtype={'SOURCE_ID': 'string'})
    if 'SOURCE_ID' not in frame or not len(frame):
        raise ValueError('Gaia cache lacks SOURCE_ID; recover IDs into a fresh copy')
    text = frame['SOURCE_ID']
    if text.isna().any() or not text.str.fullmatch(r'[1-9][0-9]*').all():
        raise ValueError('Invalid/missing Gaia SOURCE_ID cache; recover IDs into a fresh copy')
    # Python integers check range before constructing the fixed-width array.
    values = [int(value) for value in text]
    if any(value > np.iinfo(np.int64).max for value in values):
        raise ValueError('Gaia SOURCE_ID exceeds int64 range')
    frame['SOURCE_ID'] = integer_source_ids(np.array(values, dtype=np.int64))
    return frame
