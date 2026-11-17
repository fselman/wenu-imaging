"""Analytical two-master MFF test with an independent FITS/ASDF reader."""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import argparse
import subprocess
import numpy as np
from astropy.io import fits

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--command', type=Path, required=True)
parser.add_argument('--capture-writer', action='store_true',
                    help='Exercise assembly and typed QC records with the local capture harness')
args = parser.parse_args()
command = args.command.resolve(strict=True)
with TemporaryDirectory(prefix='native-mff-') as temporary:
    root = Path(temporary).resolve()
    raw = root / 'raw'
    controls = root / 'controls'
    reduced = root / 'reduced'
    cal = reduced / 'cal'
    out = cal / 'mff'
    for path in (raw, controls, out):
        path.mkdir(parents=True)
    (controls / 'project.toml').write_text(f'''project_schema_version = 2
[project]
schema_version = 1
id = "synthetic"
[project.roots]
raw = "{raw}"
output = "{reduced}"
calibration = "{cal}"
''')
    (controls / 'detector.toml').write_text('''footprint_schema_version = 1
instrument = "omegacam"
binning = [1, 1]
readout_id = "synthetic"
[[detector]]
id = "CCD-A"
amplifier = "L"
native_paf_chip = 1
[[detector]]
id = "CCD-B"
amplifier = "L"
native_paf_chip = 2
''')
    config = controls / 'mff.toml'
    recipe = '''mff_recipe_schema_version = 1
project = "project.toml"
detector_toml = "detector.toml"
run = "cal/mff"
[inputs]
dome = "dome.fits"
sky = "sky.fits"
[mff]
filter = "r_SDSS"
radius = 1
reference_detector = "CCD-B"
'''
    def master(path, product, pairs):
        primary = fits.PrimaryHDU()
        primary.header['INSTRUME'] = 'OMEGACAM'
        primary.header['PRODCATG'] = product
        primary.header['FILTER'] = 'r_SDSS'
        detectors = [fits.ImageHDU(np.tile(row, (3, 1)).astype('f4'), name=name)
                     for name, row in pairs]
        fits.HDUList([primary, *detectors]).writeto(path)

    dome, sky = cal / 'dome.fits', cal / 'sky.fits'
    master(dome, 'CALIB.MASTER_DOME_FLAT', [('CCD-A', [1, 2, 3]), ('CCD-B', [2, 4, 6])])
    master(sky, 'CALIB.MASTER_SKY_FLAT', [('CCD-B', [8, 32, 72]), ('CCD-A', [2, 8, 18])])
    hashes = [sha256(path.read_bytes()).hexdigest() for path in (dome, sky)]

    def run(contents):
        config.write_text(contents)
        return subprocess.run([str(command), 'cal', 'mff', '--config', str(config)],
                              cwd=controls, text=True, capture_output=True)

    invalid = run(recipe.replace('r_SDSS', 'wrong'))
    assert invalid.returncode != 0 and not list(out.iterdir()), (invalid.stdout, invalid.stderr)
    result = run(recipe)
    assert result.returncode == 0, (result.stdout, result.stderr)
    [product] = out.glob('*.fits')
    with fits.open(product) as hdus:
        assert hdus[0].header['PRODCATG'] == 'CALIB.MASTER_FLAT'
        assert hdus[0].header['NEXTEND'] == 2
        assert [hdu.name for hdu in hdus[1:]] == ['CCD-A', 'CCD-B']
        for hdu, row in zip(hdus[1:], ([3, 8, 15], [12, 32, 60])):
            np.testing.assert_array_equal(hdu.data, np.tile(row, (3, 1)))
            assert hdu.header['ESO MPP QC FRMEDIAN'] == row[1]
    digest = sha256(product.read_bytes()).hexdigest()
    if args.capture_writer:
        assert product.with_suffix('.asdf').read_text().splitlines() == [digest, 'CCD-A 1 2', 'CCD-B 2 1']
    else:
        import asdf
        with asdf.open(product.with_suffix('.asdf')) as af:
            tree = af.tree['qc']
            assert tree['provenance']['operation'] == 'cal.mff'
            assert tree['file']['sha256'] == digest
            assert tree['provenance']['configuration']['format'] == 'mff_recipe_toml_v1'
            assert tree['provenance']['configuration']['snapshot'] == recipe
            assert len(tree['characterization']['detectors']) == 2
            recorded = tree['embedded_input_records']
            assert [entry['file']['kind'] for entry in recorded] == ['calibration'] * 2
            assert [entry['file']['sha256'] for entry in recorded] == hashes
            assert [[d['source_hdu'] for d in entry['detectors']] for entry in recorded] == [[1, 2], [2, 1]]
    assert product.with_suffix('.log').is_file()
    assert sorted(p.suffix for p in out.iterdir()) == ['.asdf', '.fits', '.log']
    assert [sha256(path.read_bytes()).hexdigest() for path in (dome, sky)] == hashes
    print('PASS: two-master CLI, detector mapping, exact combined pixels and input preservation')
    print('PASS: ' + ('QC record capture' if args.capture_writer else 'ASDF round trip'))
