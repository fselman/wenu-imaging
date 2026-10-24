"""Recover only missing Gaia DR3 IDs into new CSVs; never recalibrate data.

The manifest is a JSON list of {path, sha256, group} objects. Each group becomes
one output subdirectory. Default: local preflight only. Network retrieval needs
--allow-network; one bounded anonymous TAP job, with a 180-second parent limit.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

ENDPOINT = 'https://gea.esac.esa.int/tap-server/tap'
TOLERANCE_ARCSEC = 0.0001  # Same DR3 positions, not a new positional association.


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)


def prepare(manifest):
    import numpy as np
    entries, destinations, positions = [], set(), []
    if not 1 <= len(manifest) <= 4:
        raise ValueError('Expected 1..4 explicit raw/clean CSV inputs')
    for item in manifest:
        path = Path(item['path']).resolve()
        if sha256(path) != item['sha256']:
            raise ValueError('Input hash mismatch: ' + str(path))
        group = item['group']
        if not group or not group.replace('_', '').isalnum():
            raise ValueError('Unsafe output group')
        destination = (group, path.name)
        if destination in destinations:
            raise ValueError('Repeated output destination')
        destinations.add(destination)
        with path.open(newline='') as stream:
            reader = csv.reader(stream)
            header, rows = next(reader), list(reader)
        if len(set(header)) != len(header) or not rows:
            raise ValueError('Empty CSV or duplicate column names')
        indices = [header.index(key) for key in ('SOURCE_ID', 'raj2000', 'dej2000')]
        if any(len(row) != len(header) or row[indices[0]].strip() for row in rows):
            raise ValueError('Expected rectangular CSV with entirely empty SOURCE_ID')
        coords = np.array([[float(row[indices[1]]), float(row[indices[2]])]
                           for row in rows])
        validate_coordinates(coords)
        if len(np.unique(coords, axis=0)) != len(coords):
            raise ValueError('Duplicate cached positions')
        entries.append({'path': str(path), 'sha256': item['sha256'],
                        'group': group, 'header': header, 'rows': rows,
                        'id_index': indices[0], 'coordinates': coords})
        positions.extend(coords)
    unique = np.unique(positions, axis=0)
    if len(unique) > 12000:
        raise ValueError('Identity recovery exceeds 12000 unique cached positions')
    if abs(unique[:, 1]).max() >= 85:
        raise ValueError('Polar recovery is outside this bounded scope')
    # Include the full matching radius around boundary rows, so an adjacent
    # candidate cannot be hidden just outside the query box.
    margin = np.array([1e-6 / np.cos(np.deg2rad(abs(unique[:, 1]).max() + .001)), 1e-6])
    lo, hi = unique.min(axis=0) - margin, unique.max(axis=0) + margin
    if ((hi - lo) > 2).any() or lo[0] < 0 or hi[0] >= 360 or lo[1] < -90 or hi[1] > 90:
        raise ValueError('Bounding box outside this bounded recovery scope')
    cap = min(25000, 2 * len(unique) + 1)
    query = (f'SELECT TOP {cap} dr3.source_id AS SOURCE_ID, '
             'gspc.source_id AS GSPC_SOURCE_ID, dr3.ra AS ra, dr3.dec AS dec\n'
             'FROM gaiadr3.gaia_source AS dr3\n'
             'JOIN gaiadr3.synthetic_photometry_gspc AS gspc\n'
             'ON dr3.source_id = gspc.source_id\n'
             f'WHERE dr3.ra BETWEEN {lo[0]:.15f} AND {hi[0]:.15f}\n'
             f'AND dr3.dec BETWEEN {lo[1]:.15f} AND {hi[1]:.15f}\n')
    return entries, query, cap


def validate_coordinates(coords):
    import numpy as np
    if (coords.ndim != 2 or coords.shape[1] != 2 or not np.isfinite(coords).all()
            or (coords[:, 0] < 0).any() or (coords[:, 0] >= 360).any()
            or (abs(coords[:, 1]) > 90).any()):
        raise ValueError('Invalid positions')


def match_ids(coords, table, cap):
    import numpy as np
    from scipy.spatial import cKDTree
    from pycavi.pycavi.pycavi_gaia_ids import normalize_gaia_identifiers
    if not 1 <= len(table) < cap:
        raise ValueError('Empty response or possible row-cap truncation')
    table = normalize_gaia_identifiers(table)
    sky = []
    for key in ('ra', 'dec'):
        names = [name for name in table.colnames if name.casefold() == key]
        if len(names) != 1:
            raise ValueError('Missing/ambiguous response coordinates')
        column = table[names[0]]
        from astropy import units as u
        if column.unit is None or not u.Unit(column.unit).is_equivalent(u.deg):
            raise ValueError('Response coordinates need angular units')
        values = np.ma.asarray(column, dtype=float)
        if np.ma.getmaskarray(values).any():
            raise ValueError('Masked response coordinates')
        sky.append((np.asarray(values) * column.unit).to_value(u.deg))
    sky = np.array(sky).T
    validate_coordinates(sky)
    validate_coordinates(coords)

    def vectors(points):
        ra, dec = np.deg2rad(points).T
        return np.column_stack((np.cos(dec) * np.cos(ra),
                                np.cos(dec) * np.sin(ra), np.sin(dec)))

    source, targets = vectors(coords), vectors(sky)
    radius = 2 * np.sin(np.deg2rad(TOLERANCE_ARCSEC / 3600) / 2)
    candidates = cKDTree(targets).query_ball_point(source, radius)
    if any(len(matches) != 1 for matches in candidates):
        raise ValueError('Missing or ambiguous same-position identity match')
    indices = np.array([matches[0] for matches in candidates])
    ids = np.asarray(table['SOURCE_ID'])[indices]
    if len(np.unique(ids)) != len(ids):
        raise ValueError('Many cached rows map to the same ID')
    chord = np.linalg.norm(source - targets[indices], axis=1)
    separations = np.rad2deg(2 * np.arcsin(np.minimum(1, chord / 2))) * 3600
    return ids, separations


def recover(entries, table, cap, output):
    """Validate every mapping before publishing one fresh catalogue directory."""
    mappings = [match_ids(item['coordinates'], table, cap) for item in entries]
    staging = output / 'catalogues.pending'
    final = output / 'catalogues'
    if staging.exists() or final.exists():
        raise ValueError('Refusing existing catalogue directory')
    staging.mkdir()
    details = []
    for item, (ids, separations) in zip(entries, mappings):
        destination = staging / item['group'] / Path(item['path']).name
        destination.parent.mkdir(exist_ok=True)
        rows = [row.copy() for row in item['rows']]
        for row, identifier in zip(rows, ids):
            row[item['id_index']] = str(int(identifier))
        with destination.open('x', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(item['header'])
            writer.writerows(rows)
        with destination.open(newline='') as stream:
            reread = list(csv.reader(stream))
        if reread != [item['header']] + rows:
            raise ValueError('CSV roundtrip failed')
        for before, after in zip(item['rows'], reread[1:]):
            if any(a != b for i, (a, b) in enumerate(zip(before, after))
                   if i != item['id_index']):
                raise ValueError('Non-ID field changed')
        mapping = destination.with_suffix('.id-map.csv')
        with mapping.open('x', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(['row_index_zero_based', 'SOURCE_ID', 'separation_arcsec'])
            writer.writerows((index, str(int(identifier)), format(float(separation), '.17g'))
                             for index, (identifier, separation) in enumerate(zip(ids, separations)))
        details.append({'mapping': str(final / item['group'] / mapping.name),
                        'mapping_sha256': sha256(mapping),
                        'source': item['path'], 'source_sha256': item['sha256'],
                        'output': str(final / item['group'] / destination.name),
                        'output_sha256': sha256(destination), 'rows': len(rows),
                        'maximum_separation_arcsec': float(separations.max()),
                        'non_id_fields_unchanged': True})
    for item in entries:
        if sha256(item['path']) != item['sha256']:
            raise ValueError('Source changed during recovery')
    staging.rename(final)
    return details


def retrieve(output, query, client):
    raw = output / 'response.vot'
    if raw.exists():
        raise ValueError('Refusing existing query response')
    job = client.launch_job_async(query, background=True, dump_to_file=True,
                                 output_file=str(raw), output_format='votable', verbose=False)
    write_json(output / 'job.json', {'job_id': str(job.jobid), 'endpoint': ENDPOINT,
                                    'query_sha256': hashlib.sha256(query.encode()).hexdigest()})
    job.save_results()
    job.get_results()
    phase = str(job.get_phase())
    write_json(output / 'job-completed.json', {'phase': phase})
    if phase != 'COMPLETED':
        raise ValueError('Archive job did not complete')
    from xml.etree import ElementTree
    statuses = [node.get('value') for node in ElementTree.parse(raw).getroot().iter()
                if node.tag.rsplit('}', 1)[-1] == 'INFO' and node.get('name') == 'QUERY_STATUS']
    if not statuses or any(value != 'OK' for value in statuses):
        raise ValueError('Missing or unsuccessful VOTable QUERY_STATUS: ' + repr(statuses))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-network', action='store_true')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if not args.allow_network:
            parser.error('Worker needs explicit --allow-network')
        socket.setdefaulttimeout(30)
        from astroquery.gaia import Gaia
        retrieve(args.output, (args.output / 'query.adql').read_text(), Gaia)
        return
    if args.manifest is None:
        parser.error('--manifest is required')
    entries, query, cap = prepare(json.loads(args.manifest.read_text()))
    print(query, flush=True)
    print('Validated input rows:', [len(item['rows']) for item in entries], flush=True)
    if not args.allow_network:
        print('Preflight only; no query or file writes performed.')
        return
    if os.getpriority(os.PRIO_PROCESS, 0) < 10:
        parser.error('Run batch recovery at niceness >=10')
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    (output / 'query.adql').write_text(query)
    write_json(output / 'started.json', {'manifest': json.loads(args.manifest.read_text()),
               'row_cap': cap, 'tolerance_arcsec': TOLERANCE_ARCSEC,
               'tool_sha256': sha256(__file__), 'scope': 'SOURCE_ID-only metadata recovery'})
    try:
        with (output / 'query.log').open('x') as stream:
            subprocess.run([sys.executable, '-u', str(Path(__file__).resolve()),
                            '--worker', '--allow-network', '--output', str(output)],
                           stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=180)
        from astropy.table import Table
        details = recover(entries, Table.read(output / 'response.vot', format='votable'), cap, output)
        report = {'status': 'pass', 'files': details, 'response_sha256': sha256(output / 'response.vot'),
                  'scope': 'IDs only; no recalibration, new photometry or science-data correction'}
    except Exception as exc:
        write_json(output / 'report.json', {'status': 'fail', 'error': repr(exc),
                   'note': 'No retry performed; inspect job.json before any further query.'})
        raise
    write_json(output / 'report.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
