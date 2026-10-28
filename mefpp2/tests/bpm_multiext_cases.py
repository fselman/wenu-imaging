"""S2-05/#75 deterministic two-extension fixtures and independent exact oracle."""
import hashlib
import numpy as np
from bpm_metadata_cases import prepare as parent_prepare, header_block, PRIMARY


def prepare(root, fixture, kind, instrument):
    # Fixture preparation: preserve parents, mirror science only in extension two.
    parent_prepare(root, fixture, kind)
    repo = fixture.parents[3]
    if instrument not in ('omegacam', 'wfi'):
        raise RuntimeError('Unknown instrument')
    paf = (repo / ('mefpp2/ins/mef/config/' + instrument + '.paf')).read_bytes()
    (root / 'mefpp.paf').write_bytes(paf)
    for i in range(3):
        path = root / ('frame%d.fits' % i)
        raw = path.read_bytes()
        primary = header_block(raw[:2880], {'INSTRUME': instrument.upper(),
                              'TELESCOP': 'MPI-2.2' if instrument == 'wfi' else 'VST'})
        ext1 = header_block(raw[2880:5760], {'EXTNAME': 'S2_CCD_A'})
        ext2 = header_block(raw[2880:5760], {'EXTNAME': 'S2_CCD_B'})
        data = np.frombuffer(raw[5760:6408], dtype='>f4').reshape(9, 18).copy()
        data[:, :9] = data[:, :9][:, ::-1]
        path.write_bytes(primary + ext1 + raw[5760:] + ext2 +
                         data.astype('>f4').tobytes() + raw[6408:])
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir())
            if p.is_file() and p.name != 'run-provenance.json'}


def expected_mask(fixture, kind, reference):
    # Independent accepted-mask anchor, not an execution of either C constructor.
    from astropy.io import fits
    cube = np.stack([fits.getdata(fixture / kind / ('frame%d.fits' % i), 1)[:, :9]
                     for i in range(3)]).astype(np.float64)
    gains = np.median(cube / np.median(cube, axis=(1, 2))[:, None, None], axis=0).astype(np.float32)
    gain = (gains / gains.astype(np.float64).mean()).astype(np.float32)
    mask = ((gain >= .5) & (gain <= 1.5)).astype(np.uint8)
    if hashlib.sha256(mask.tobytes()).hexdigest() != reference['mask_pixels_sha256']:
        raise RuntimeError('Independent mask differs from immutable accepted reference')
    if np.array_equal(mask, mask[:, ::-1]):
        raise RuntimeError('Extension permutation sentinel is insensitive')
    return mask


def canonical_headers(previous, instrument):
    # Exact ordered reference cards; declare only instrument/extension differences.
    from astropy.io import fits
    answer = []
    first_only = {'ORIGIN', 'TELESCOP', 'INSTRUME', 'MJD-OBS',
                  'ESO DET WIN1 BINX', 'ESO DET WIN1 BINY'}
    for idx, cards in enumerate([previous['saved_headers'][0], previous['saved_headers'][1],
                                previous['saved_headers'][1]]):
        result = []
        for raw in cards:
            c = fits.Card.fromstring(raw)
            if idx == 2 and c.keyword in first_only:
                continue
            values = {'INSTRUME': instrument.upper(),
                      'TELESCOP': 'MPI-2.2' if instrument == 'wfi' else 'VST',
                      'EXTNAME': 'S2_CCD_A' if idx == 1 else 'S2_CCD_B'}
            if c.keyword in values:
                # Declared string values compare semantically; all other cards stay exact.
                c = fits.Card(c.keyword, values[c.keyword], c.comment)
                raw = c.image
            result.append(raw)
        answer.append(result)
    return answer


def verify(root, inputs, reference, flag, previous, instrument, fixture, kind):
    from astropy.io import fits
    # Preservation and exact product set.
    for name, sha in inputs.items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != sha:
            raise RuntimeError('Staged input changed: ' + name)
    saved_name = ('WFI_BPM' if instrument == 'wfi' else 'OCAM_BPM') + '.fits'
    wanted = set(inputs) | {saved_name, 'returned-01.fits', 'returned-02.fits', 'run-provenance.json'}
    if {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()} != wanted:
        raise RuntimeError('Unexpected/missing output files')
    masks = expected_mask(fixture, kind, reference)
    expected_headers = canonical_headers(previous, instrument)
    headers, origfiles, mask_hashes = [], [], []
    # Exact HDUs, detector order, every pixel, storage and provenance cards.
    with fits.open(root / saved_name, memmap=False) as saved:
        if len(saved) != 3 or saved[0].data is not None:
            raise RuntimeError('Expected primary and two image extensions')
        for index, hdu in enumerate(saved):
            if hdu.header['BITPIX'] != 8 or 'BSCALE' in hdu.header or 'BZERO' in hdu.header:
                raise RuntimeError('Storage/scaling changed')
            cards = [c.image for c in hdu.header.cards if c.keyword != 'ORIGFILE']
            expected = expected_headers[index]
            if len(cards) != len(expected):
                raise RuntimeError('Header card count differs: %d' % index)
            declared = {'INSTRUME', 'TELESCOP', 'EXTNAME'}
            for left, right in zip(cards, expected):
                a, b = fits.Card.fromstring(left), fits.Card.fromstring(right)
                if a.keyword in declared:
                    if (a.keyword, a.value, a.comment) != (b.keyword, b.value, b.comment):
                        raise RuntimeError('Declared metadata mismatch: ' + a.keyword)
                elif left != right:
                    raise RuntimeError('Unchanged canonical card differs: ' + a.keyword)
            origfiles.append(hdu.header.get('ORIGFILE'))
            headers.append(cards)
            if index:
                expected_mask_pixels = masks if index == 1 else masks[:, ::-1]
                with fits.open(root / ('returned-%02d.fits' % index), memmap=False) as returned:
                    if (len(returned) != 1 or returned[0].header['BITPIX'] != 8 or
                            'BSCALE' in returned[0].header or 'BZERO' in returned[0].header or
                            not np.array_equal(returned[0].data, expected_mask_pixels)):
                        raise RuntimeError('Returned mask differs: %d' % index)
                if not np.array_equal(hdu.data, expected_mask_pixels):
                    raise RuntimeError('Saved mask/extension order differs: %d' % index)
                mask_hashes.append(hashlib.sha256(hdu.data.tobytes()).hexdigest())
        if not all(isinstance(x, str) and x for x in origfiles) or len(set(origfiles)) != 1:
            raise RuntimeError('Missing/inconsistent original filename across extensions')
    return dict(saved_name=saved_name, saved_headers=headers, mask_pixels_sha256=mask_hashes,
                good=reference['good'], bad=reference['bad'], pixels_checked=162,
                extensions=['S2_CCD_A', 'S2_CCD_B']), origfiles
