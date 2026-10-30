# Optional overscan and amplifier-specific readout policy

Owner additions, 30 October 2026, after accepted/merged PR #149: overscan
**definition and subtraction are optional**. Detector technology does not imply
the presence/absence of overscan or select a correction. Carry this policy into
configuration, request resolution, numerical service extraction and provenance.
It applies to CCD and CMOS; it is not CMOS numerical qualification.

| Declared geometry | Subtraction requested | Meaning |
|---|---|---|
| absent | false | No region required; skip overscan subtraction |
| defined | false | Retain geometry without applying subtraction |
| defined | true | Validate selected channel/geometry and apply the qualified correction |
| absent | true | Error; no fallback, inferred region, zero/sentinel region or silent skip |

Keep requested correction distinct from applied state. An enabled correction
must reject missing/incompatible regions, rather than treating a failed lookup
as explicit omission. Prescan, trimming, master-bias subtraction and reference
pixel correction are separate choices, not synonyms for overscan subtraction.
Optional overscan does not silently disable those other corrections.

Geometry belongs to a detector's selected readout configuration, with separate
channel/amplifier regions and correction requests where needed. Available
amplifiers and active amplifiers are different. One selected channel does not
establish that a detector has only one physical amplifier. Two simultaneous
channels require their own signal regions, overscan definitions and correction
settings; no shared geometry or common correction is assumed.

Owner reports two amplifiers per WFI chip and an alternative amplifier on one
chip; OmegaCAM hardware details also require confirmation. Preserve that report
without inventing chip/amplifier IDs. Checked-in WFI configuration currently has
overscan x=5..48 for legacy chips 5–7, x=2100..2142 for 1–4 and 8. OmegaCAM has
x=2100..2142 for 1–8/17–24 and x=5..48 for 9–16/25–32. These are configured
FITS-one-based-inclusive x strips, not independently established physical
amplifier mappings. Differences may reflect readout/orientation conventions;
source geometry alone does not establish their hardware cause. Actual headers,
readout documentation and owner mapping must establish physical identities and
exposure applicability before a numerical adapter selects them.

## Header evidence and authority

Owner clarification, 30 October: frames may report amplifier names, the active
amplifier and overscan definitions, but those values may be unreliable. Treat
these as reported candidates, not automatic authority. Preserve original FITS
cards, asset/version, HDU and occurrence before any normalization. Keep reported,
configured, explicitly verified and applied values separate. Configuration itself
is an assumption, not proof that a header is wrong.

A future adapter must compare candidates with the selected readout and established
instrument mapping, identify missing/inconsistent values and retain conflict and
selection reasons. An unresolved contradiction blocks execution until explicit
resolution; neither “always trust header” nor “always overwrite with PAF” is the
policy. No hardware IDs or regions inferred from detector technology or position.
Trusted mappings require provenance from actual reviewed evidence, not merely a
nonempty keyword. Actual keyword mapping and applicability are M4 adapter work.

The authoring contract retains optional exact raw-card evidence, explicitly
unverified/unresolved, and marks its review pending. It does not parse supplied
FITS files or resolve header conflicts. Synthetic contrary header evidence does
not overwrite selected geometry or establish verified hardware identity.

## Staged implementation

M2's [project authoring contract](m2/project-contracts/README.md) validates the
three valid states, contradiction rejection, per-channel settings, active channel
selection and frozen source records. WFI/OmegaCAM examples preserve exact accepted
native geometry and explicitly unknown physical identity/inventory. Separate
synthetic examples exercise no region, defined-but-disabled, alternative selected
and simultaneous channels. They do not establish real hardware support.

The accepted native schema-1/2/3 compatibility mapper still requires its original
per-detector keys and global scan switch; no numerical/constructor behavior is
changed by this contract increment. Geometry-free and multi-active examples have
native_mode=unavailable and cannot be silently translated to that mapper. Do not
claim that current mef_cal_bias or ordinary mefpp now processes geometry-free or
multi-amplifier requests.

During M4/M5/M6 adapter/service qualification, represent omission explicitly in
the native settings/request contract, validate actual channel/HDU geometry,
preserve current CCD results, and qualify correction-skipped cases and
per-amplifier correction behavior. No fabricated zero regions, detector-wide
single-amplifier assumptions or implicit correction ordering. Required M6a
variance/covariance propagation and masks must follow the actual applied
corrections; signal-only legacy paths remain explicitly variance-unavailable.
Normal activation still requires the separate integrated acceptance decision.
