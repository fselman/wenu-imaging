# Actual Intel Mac overscan preparation qualification

Owner-returned terminal receipt, 5 November 2026.
Qualified source: d8bf5608c73b3aee8b5411b3193f4184bd0f7b5a.
Retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-linearity-prepare-5QEzvc2c`.

The exact-source qualifier completed TOML controls, footprint controls, C17
configuration/build and the four selected native tests. Its successful overall
status also requires six TOML and five footprint controls with no skipped tests.

| Native control | Result | Seconds |
|---|---|---:|
| native_linearity_prepare | passed | 1.56 |
| native_linearity_pairs | passed | 0.95 |
| native_linearity_samples | passed | 0.98 |
| native_bias_service | passed | 2.42 |

CTest total: 4/4 passed in 5.91 seconds.
QUALIFICATION: passed.
PRESERVATION: checkout=True, installed_files=True, exported_source=True.

This is actual Intel Mac synthetic software qualification, as reported by the
owner, not a real-data correction or scientific calibration. No new raw images
were processed and no new corrected full-ROI ASDF archive was created. Normal
checkout, installed files and exported source stayed unchanged. Retain this
source/build and reuse its qualified kernels; do not repeat this gate.

Next: integrate explicit TOML resolution, existing master dependencies, full ROI
measurements/direct-site replay, and shared ASDF publication into the linearity
preparation recipe. First inspect existing metadata locators and completion
receipts for the master catalogue and corrected-site archive, without reprocessing.
Do not confuse the completed singleton archive with full corrected ROI products.
