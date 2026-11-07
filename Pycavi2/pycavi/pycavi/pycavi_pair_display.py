"""Lossless display projection of saved pair means; no measurement or fitting."""


def exposure_rows(rows):
    """Expose both members separately, preserving pair populations and provenance.

    Signal values are the saved bias-subtracted raw-pair ROI means, without
    overscan correction. They are not corrected singleton-pixel samples.
    Original pair fields remain available for exact inspection, including nulls.
    """
    result = []
    for index, row in enumerate(rows):
        for member, prefix in ((1, 'first'), (2, 'second')):
            result.append(dict(row, source_row_index=index, pair_member=member,
                asset=row[prefix + '_asset'], hdu=row[prefix + '_hdu'],
                input_index=row[prefix + '_input_index'],
                exposure_seconds=row[prefix + '_seconds'],
                signal_adu=row['signal%d_adu' % member],
                processing_stage='raw_pair_bias_subtracted_without_overscan',
                population='pair_common_accepted_pixels'))
    return sorted(result, key=lambda r: (r['input_index'], r['roi'], r['source_row_index']))
