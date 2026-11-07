# Actual corrected diagnostic ASDF products complete

5 November 2026. Owner-supplied completion console.

Retained run: `/Users/fselman/Pictures/OCAM/wenu-imaging/ocam-corrected-diagnostics-i92m_n1n`.
Qualified computation source: `a321e6321daafdc04193f118c2d363670e59ae53`,
reused from `mac-corrected-diagnostics-M0t2gFsg/source`.

Both line and ratio commands completed. The supplied wrapper only reports
`complete_for_owner_inspection` after requiring 32 detectors, 3200 line rows,
160 ROI line fits and 640 ratio rows, and checking saved input fingerprints.
Both stages use the approved inclusive 15000–35000 ADU interval. These are
unweighted diagnostic lines and normalized same-exposure ratios, not a physical
correction model. Noise/covariance remains unavailable.

All five outer preservation guards were true: checkout, installed_files,
qualified_source, private_qc_runtime and qualification_receipt. No raw image
measurement, preparation replay or plotting occurred in this run.

The owner reports excessive duration. Console contains many30-second heartbeat
messages for both stages; these are not precise wall-time measurements. Source
inspection identifies repeated ASDF provenance traversal/decoding, repeated tree
copying across derived products, and whole private-runtime hashing in the outer
wrapper. Relative costs have not been profiled. No optimization has been designed
or implemented following the owner's request to consult before code design.

Remaining work: generate the existing qualified offline viewer from completed
preparation and diagnostic indexes, placing inspection output within this same
run. Viewer generation may remain slow because it validates source provenance.
No measurement, fit or ratio recomputation; no corrected HTML completion or owner
plot inspection is claimed yet. Preserve existing data and runs.

Future development will use incremental real-data stages in raw-data,
reduced-products and orchestration directories, after discussion and design
agreement with the owner. Exact paths and reuse/replacement rules remain pending.
