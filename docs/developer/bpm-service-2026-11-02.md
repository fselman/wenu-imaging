# Typed BPM numerical service - 2 November 2026

## Actual Mac qualification returned

At 970bdfb9ad232df353aab18c7a1cd2f0957c737e, native_operation_template and
native_bpm_service passed on MC02VV0HPHTDG in 1.72 s. Retained evidence:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-service-AUUCnlyT`.
All three preservation checks passed; main remained clean. This supersedes
pending-Mac statements below for that exact service revision only.
The [file-input increment](bpm-file-input-2026-11-02.md) extends saturation and
explicit frame exclusion; its changed service requires a focused new gate.


## Qualified basis

Fernando returned actual Mac success for the checked Eclipse core at
14e9bb68ffe58f765576413063e0c99a6cfb311e: native_measurement_stats and
native_bpm_response, 4.22 s total. Retained run:
`/Users/fselman/Software/build/wenu-imaging/mac-bpm-response-rMPj2sY4`.
Installed files, checkout and exported source were preserved; main stayed clean.
That evidence qualifies the earlier core, not this new service revision.

The [PDF formula design](detector-characterization-design-2026-11-02.pdf) and
[matching LaTeX](detector-characterization-design-2026-11-02.tex) remain unchanged.
CMOS initially uses the CCD mechanism; specialized CMOS work is deferred.

## Implemented boundary

`mef_cal_bpm` uses `mef_operation_run` for validate/load/calculate/cleanup.
It accepts a resolved CAL_BPM v1 request for one detector, borrowed raw ADU
flats, an explicitly selected active scan-corrected master bias, and an omitted
or selected prior BPM. Input HDUs are independent of the explicit configuration
detector index. Snapshot settings control the proportional/robust choice and
strict response thresholds; no recipe-specific copy of a fitter is added.

Validation checks request/calibration roles, image/mask dimensions, finite master
bias and electronic reads, scan rejection/trim bounds, options and ROI geometry
before correction. Selected data are the caller's responsibility until the file
adapter composes the existing bound layout loader. The service does not claim
to establish correspondence between a borrowed array and a filesystem path.

Raw copies use the existing `mef_overscan_correction`, or existing `image_getvig`
when both scans are disabled. Active planes then use existing `cube_sub_im` and
the qualified `cube_response_checked`. Detector BPMs never select electronic
scan samples. Input frames, master bias, priors and snapshot stay immutable.
Nonfinite active samples become missing numerical coverage; invalid selected
electronic reads fail before correction.

## Prior mask, ownership and numerical QC

- Reason prior: copy the original bytes, derive reference selection using the
  explicit reject-bit set, preserve newly measured reasons separately, and
  provide `combined = prior OR new` without changing the original.
- Binary prior: copy its normalized 1=good selection. Do not invent a reason
  for an unknown legacy defect. Combined reason bytes are explicitly unavailable;
  the final combined selection still rejects its excluded pixels.
- Omitted prior: no invented calibration and no hidden PAF-default mask.
- Final selection also rejects unavailable fits, including with reject_bits=0.
  Reason value zero alone is never certification that all tests ran.
- Return the owned response maps, original request, prior/combined byte masks,
  final selection and per-frame corrected-active/prescan/overscan statistics.
  Optional MAD uses the existing checked helper; scan statistics have no BPM.
- Results outlive all input arrays and context. Service allocator callbacks own
  request/QC/byte buffers; Eclipse retains its established allocation policy.
  Pending results are destroyed on failure. Occupied outputs/errors are rejected
  intact; status remains authoritative when diagnostic allocation fails.

QC explicitly marks the result `provisional_numerical_only`. This API has no
acquisition-pair/exposure-time/saturation certification, gain/RON measurement,
shutter/linearity fit, file/CLI publication or ASDF completion. Per-plane sample
selections may be supplied, but the service does not invent their scientific
thresholds. The returned statistics describe their stated populations; corrected
active QC is not silently restricted to the fitter's ROI/sample population.

## Preparation controls and Mac gate

Purpose: verify the numerical composition and template lifetimes before adding
file publication. Inputs: actual WFI/OmegaCAM PAF snapshots and generated tiny
raw arrays with row-dependent pedestals, known response and active master bias.
No observational inputs or installed products are opened or changed.

Actions: run both fit modes and four scan selections (both, pre, over, neither),
with omitted/byte/binary priors. Check known response and combined bit values,
snapshot authority, missing-sample coverage, scan-mask non-applicability,
input immutability, detached result lifetimes, malformed requests/geometry,
calculation failures and persistent failures at every service-owned allocation.
Pass criteria: 16 successful instrument/mode/scan controls; every negative case
returns the expected failure without a partial result or lost owned allocation.
The dependency allocators are not fault-injected; no general OOM qualification.

Agent preparation on optimized C17/GCC13.3 passed the new service and existing
operation-template contracts in 0.09 s. The unchanged response contract also
passed during initial integration. Python AST/whitespace checks passed; new
source units compile without new warnings. This is not actual Mac acceptance.

The existing protected runner's `--bpm-service` gate builds only
bpm_service_probe and operation_template_probe, inventories exactly
native_bpm_service/native_operation_template, and verifies checkout, installed
files and exported source preservation. The earlier response, statistics and
ASDF gates are not replayed: their relevant numerical source is unchanged.

After the Mac service gate, add file-level admission/layout binding, configured
saturation coverage, checked FITS/common ASDF publication and whole-command
completion. Chapman changed-code validation precedes full real-data acceptance.
No production installation, activation, merge or branch cleanup is authorized.
