"""Internal worker for the explicitly selected gaia-dr3 dependency check.

Importing this module performs no scientific imports or network requests.
"""
import argparse
import hashlib
import json
from pathlib import Path
import socket

CENTER = (88.018586, -5.464047)
RADIUS_DEG = 5.0 / 60.0
ENDPOINT = 'https://gea.esac.esa.int/tap-server/tap'
DR3_COLUMNS = (
    'source_id', 'ra', 'ra_error', 'dec', 'dec_error', 'parallax', 'parallax_error',
    'pmra', 'pmra_error', 'pmdec', 'pmdec_error',
    'phot_g_mean_flux', 'phot_g_mean_flux_error', 'phot_g_mean_mag',
    'phot_bp_mean_flux', 'phot_bp_mean_flux_error', 'phot_bp_mean_mag',
    'phot_rp_mean_flux', 'phot_rp_mean_flux_error', 'phot_rp_mean_mag',
    'radial_velocity', 'radial_velocity_error', 'classprob_dsc_combmod_star',
)
GSPC_COLUMNS = tuple(band + '_sdss_' + quantity
                     for band in 'ugriz' for quantity in ('mag', 'flux', 'flux_error'))
REQUIRED_COLUMNS = DR3_COLUMNS + ('gspc_source_id',) + GSPC_COLUMNS


def build_query():
    columns = ['dr3.' + name + ' AS ' + name for name in DR3_COLUMNS]
    columns += ['gspc.source_id AS gspc_source_id']
    columns += ['gspc.' + name for name in GSPC_COLUMNS]
    return ('SELECT TOP 5 ' + ', '.join(columns) + '\n'
            'FROM gaiadr3.gaia_source AS dr3\n'
            'JOIN gaiadr3.synthetic_photometry_gspc AS gspc\n'
            'ON gspc.source_id = dr3.source_id\n'
            "WHERE 1 = CONTAINS(POINT('ICRS', dr3.ra, dr3.dec), "
            "CIRCLE('ICRS', 88.018586, -5.464047, 0.08333333333333333))\n")


def validate_table(table):
    import numpy as np
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    original_names = list(table.colnames)
    if len({name.lower() for name in original_names}) != len(original_names):
        raise ValueError('Ambiguous response column names')
    # Some TAP outputs capitalize source IDs. Normalize only a diagnostic copy;
    # preserve native response bytes and report the returned names separately.
    table = table.copy()
    for name in original_names:
        if name != name.lower():
            table.rename_column(name, name.lower())
    missing = sorted(set(REQUIRED_COLUMNS) - set(table.colnames))
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(missing))
    if not 1 <= len(table) <= 5:
        raise ValueError('Expected 1..5 joined sources, got ' + str(len(table)))
    # Do not convert identifiers to float64: that loses source-ID precision.
    for name in ('source_id', 'gspc_source_id'):
        values = np.ma.asarray(table[name])
        if values.dtype.kind not in 'iu' or np.ma.getmaskarray(values).any() or (values <= 0).any():
            raise ValueError('Invalid integer source identifiers: ' + name)
    if not np.array_equal(table['source_id'], table['gspc_source_id']):
        raise ValueError('DR3/GSPC source identifiers do not match')
    if len(set(map(int, table['source_id']))) != len(table):
        raise ValueError('Duplicate source identifiers')
    numeric, null_counts, units = {}, {}, {}
    for name in REQUIRED_COLUMNS:
        column = table[name]
        values = np.ma.asarray(column, dtype=float)
        valid = ~np.ma.getmaskarray(values) & np.isfinite(values.filled(np.nan))
        numeric[name] = (values.filled(np.nan), valid)
        null_counts[name] = int((~valid).sum())
        units[name] = str(column.unit) if column.unit is not None else None
    for name in ('ra', 'dec'):
        if not numeric[name][1].all():
            raise ValueError('Invalid or masked coordinates: ' + name)
        if table[name].unit is None or not u.Unit(table[name].unit).is_equivalent(u.deg):
            raise ValueError('Missing or non-angular coordinate unit: ' + name)
    ra = (numeric['ra'][0] * table['ra'].unit).to_value(u.deg)
    dec = (numeric['dec'][0] * table['dec'].unit).to_value(u.deg)
    if not ((ra >= 0).all() and (ra < 360).all() and (abs(dec) <= 90).all()):
        raise ValueError('Coordinates out of range')
    separations = SkyCoord(ra, dec, unit='deg').separation(SkyCoord(*CENTER, unit='deg')).deg
    if (separations > RADIUS_DEG + 1e-8).any():
        raise ValueError('Returned position is outside the requested cone')
    usable = np.ones(len(table), dtype=bool)
    for name in ('r_sdss_mag', 'i_sdss_mag', 'r_sdss_flux', 'i_sdss_flux',
                 'r_sdss_flux_error', 'i_sdss_flux_error'):
        values, valid = numeric[name]
        usable &= valid
        if name.endswith('_flux'):
            usable &= values > 0
        elif name.endswith('_flux_error'):
            usable &= values >= 0
    if not usable.any():
        raise ValueError('No usable r/i photometric row in bounded response')
    return {'rows': len(table), 'row_cap': 5, 'center_degrees': CENTER,
            'radius_arcmin': 5.0, 'maximum_distance_arcmin': float(separations.max() * 60),
            'columns': original_names, 'column_units': units,
            'null_or_nonfinite_counts': null_counts, 'usable_ri_rows': int(usable.sum()),
            'source_ids': [str(int(value)) for value in table['source_id']],
            'scope': 'bounded client/schema retrieval; no calibration or scientific accuracy claim'}


def run_probe(directory, client):
    query = build_query()
    with (directory / 'query.adql').open('x') as stream:
        stream.write(query)
    raw = directory / 'response.vot'
    if raw.exists():
        raise ValueError('Refusing existing response file')
    job = client.launch_job_async(query, background=True, dump_to_file=True,
                                  output_file=str(raw), output_format='votable', verbose=False)
    # Record the ID before waiting; timeout can leave an anonymous archive job.
    info = {'job_id': str(job.jobid), 'endpoint': ENDPOINT, 'anonymous': True,
            'query_sha256': hashlib.sha256(query.encode()).hexdigest()}
    with (directory / 'job.json').open('x') as stream:
        json.dump(info, stream, indent=2)
    # With background=True, get_results() alone downloads to memory in 0.4.11.
    # save_results() preserves the native response before get_results reads it.
    job.save_results()
    job.get_results()
    from astropy.table import Table
    table = Table.read(raw, format='votable')
    details = validate_table(table)
    details.update(info)
    details['response_sha256'] = hashlib.sha256(raw.read_bytes()).hexdigest()
    details['phase'] = str(job.get_phase())
    if details['phase'] != 'COMPLETED':
        raise ValueError('Archive job did not complete: ' + details['phase'])
    with (directory / 'details.json').open('x') as stream:
        json.dump(details, stream, indent=2)
    return details


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-network', action='store_true', required=True)
    parser.parse_args()
    socket.setdefaulttimeout(30)
    from astroquery.gaia import Gaia
    # Explicit ADQL controls this query; no global ROW_LIMIT/MAIN_GAIA_TABLE edits.
    # Import may print the installed client's archive notices.
    print(json.dumps(run_probe(Path.cwd(), Gaia), indent=2))


if __name__ == '__main__':
    main()
