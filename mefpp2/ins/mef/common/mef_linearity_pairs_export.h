#ifndef MEF_LINEARITY_PAIRS_EXPORT_H
#define MEF_LINEARITY_PAIRS_EXPORT_H
#include <stdio.h>
#include "mef_linearity_pairs.h"
/* Diagnostic TSV v1, not a fitted calibration or ASDF QC product. Consume only
 * an unmodified result returned by mef_linearity_measure_pairs. No allocation,
 * numerical recomputation or ownership transfer. Caller owns stream and result.
 * Tab/newline/CR/backslash in text are encoded as \\t/\\n/\\r/\\\\; other ASCII
 * controls use \\xHH. Decode text only AFTER splitting TSV fields. Numeric
 * columns use 17 significant digits, C locale required (not changed globally).
 * Unavailable numeric fields are empty; availability/state columns are explicit.
 * Bias-only RON and matched four-plane statistics are separate populations.
 * Flush before success to surface buffered I/O failures; never close stream.
 * Errors may leave partial output: caller must discard it and publish only after
 * success. These writers do not freeze inputs or provide atomic publication. */
mef_status mef_linearity_pairs_write_tsv(FILE *, const mef_linearity_pairs_result *);
mef_status mef_linearity_bias_write_tsv(FILE *, const mef_linearity_pairs_result *);
#endif
