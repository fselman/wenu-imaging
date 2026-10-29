# Chapman4 reduction-directory inventory — 29 October 2026

The later compact census below supersedes the partial scan's science-partition totals only. The earlier partial calibration/link inventory remains bounded as recorded; no large recursive retry or processing resume is required.

## Evidence and scope

Actual host: chapman4.sc.eso.org, Linux 3.10.0-1160.71.1.el7.x86_64.
Shared checkout: /home1/fselman/Software/wenu-imaging, clean main e41525ed318f81e8b9ba9e6df538b4cb6758dc1f.
Python: /home/fselman/.conda/envs/wenu-imaging/bin/python, 3.11.14.
The user selected chapman4 for this inspection; earlier qualification remains attributed to chapman3, not transferred to this host.

Evidence: returned Pasted text(9).txt, SHA256 8def115c1c5515f40363ef980a57d585fd74987640ecdbe0f1872a009cb2a9d9. The agent parsed the two JSON inventory objects and independently aggregated partition/link counts. No pipeline import, native command, FITS-header/pixel verification, repair or reduction ran. Counts refer to filesystem presence, including file symlinks.

## Root coverage and observations

| Root | Resolved location | Coverage | Observation |
|---|---|---|---|
| ~/fits | /gluster/fselman/fits | Entire one-directory listing; no reported limit/errors | 2,032 entries; 2,030 FITS files or file links; no partition lists/configurations reported |
| ~/omegacam/testing | /home1/fselman/omegacam/testing | PARTIAL: 45-second traversal limit after 575 visited directories / 11,198 entries | Counts below are lower bounds for this root, not whole-dataset totals |

The partial scan reached only testing/reduced records in its returned partition table. It did not establish coverage of testing/wenu-imaging-test. The last reported science partition was J1649-3307_164955p600_m330702p0/NB_659/2017-04-13T05:11:38; the precise unvisited directory frontier was not recorded. Do not claim a complete resume position or repeat the expensive full descendant scan merely to infer it.

Shallow discovery also found ~/omegacam/m42/reduced/{calibs,logs,science} and ~/omegacam/workflows/wenu-imaging-test/{config,data}. Their reduction contents remain unexamined.

## Partial testing/reduced results

| Observation | Count in visited portion |
|---|---:|
| Partition directories / lists | 187 |
| Bias lists | 67 |
| BPM lists | 1 |
| Dome lists | 33 |
| Sky lists | 33 |
| Science lists | 53 |
| Entries in those 53 science lists | 264 |
| _pre.fits files | 10 |
| _pre_wcs.fits files | 10 |
| _newwcs.fits detector files | 320 |
| .solved markers | 320 |
| .head files / .cat files | 10 / 20 |
| FITS files or file links | 6,865 |
| PAF files observed and hashed | 7 |

The ten _pre.fits files are in two CN Ori NB_659 partitions, five each: 2017-03-11T01:24:08 and 2017-03-12T00:24:41. In the visited CN Ori r_SDSS partitions, the corresponding lists contain five and four entries, with no local _pre.fits products observed. The other 51 visited science partitions have no local _pre.fits files in this inventory. Alternate product locations/names, normalization state, valid WCS and detector completeness were not checked. The matching global 10/320 counts do not prove one-to-one association or successful completion.

Seven observed PAFs share SHA256 47f9ca706d7b9e9e244023b0c7f772d0640b7bd91144ab5189b74c4dca3e4587 (26,641 bytes). These span three bias partitions, one NB_659 dome, one NB_659 sky and the two NB_659 science partitions. No configuration variation was demonstrated in this subset; the newer test project and other roots may differ. Contents and effective CLI/default overrides remain unreviewed.

### Absent link targets and shared dependencies

181 FITS links in the recorded partition directories had target_exists=false:

| Link name | Count |
|---|---:|
| OMEGACAM_MB_1x1.fits | 105 |
| OMEGACAM_DOMEFF_r_SDSS_1x1.fits | 17 |
| OMEGACAM_DOMEFF_NB_659_1x1.fits | 15 |
| OMEGACAM_MFF_NB_659_1x1.fits | 16 |
| OMEGACAM_MFF_r_SDSS_1x1.fits | 28 |

These represent 95 distinct target strings before canonical path normalization. Sixteen links point to the same r_SDSS master-flat target under calibs/sky/200253584/r_SDSS/2017-03-13T23:12:13. Eight point to the same bias target dated 2017-03-13T09:44:19.

An absent target may be an intentionally planned, unbuilt calibration, a stale association, an inaccessible asset or another incomplete state. This inventory does not classify it as a software defect or authorize rebuilding/removing links. Earlier PartitionsTree behavior explicitly permits dependencies to be linked before products exist.

## Consequences for the refactor design

1. Separate stable asset/product identity from logical and resolved filesystem locations. /home and /home1 aliases and the /gluster storage root are observed; do not rewrite paths or deduplicate by basename alone.
2. Distinguish raw availability, planned product, absent/unbuilt dependency, partial attempt, existing-unverified product, validated result and published result. Do not infer state from filenames or treat every dangling link as corruption.
3. Represent calibration dependencies once and reference them from multiple science groups. The observed repeated target links establish reuse demand; they do not by themselves authorize a particular recursive scheduler.
4. Import legacy partition lists as ordered membership with association provenance. Preserve the actual line order, filter spelling and OB metadata instead of sorting files during conversion.
5. Give ASDF records explicit inventory coverage/frontier and unknown states. Bounded inspection must not mark unvisited groups complete or absent.
6. Prefer a compact partition-level pass before descending through thousands of detector working files. Keep raw inventory, planned association and actual completion verification separate.
7. Retain local configuration source/hash even when equal across partitions. Content deduplication must preserve the association to each task/attempt and distinguish later overrides.

Next evidence: a compact science-partition census at the known target/filter/OB depth, plus configuration/project discovery for testing/wenu-imaging-test, workflows/wenu-imaging-test and m42/reduced. Header-only samples can follow for existing products if needed to distinguish preprocessing from normalization; no bulk pixel audit or processing restart is required.

## Compact partition census — later returned evidence

Evidence: Pasted text(10).txt, SHA256 106321b22c20077f7973c41f40e2cc97b65872de4fb3dbc1598c17fffe8886f9. Parsed 205 historical and two test-project partition rows; all numeric row sums agree with their root summaries. No reported traversal limits/errors for these expected-depth passes. The scope was science.list at target/filter/OB depth or shallower, excluding directory symlinks; it is not a universal filesystem or FITS validation.

| Science root | Target directory names | Partitions | Science-list memberships | Matching local _pre.fits | Expected _pre names absent locally | Expected WCS paths present |
|---|---:|---:|---:|---:|---:|---:|
| testing/reduced/science | 42 | 205 | 963 | 10 | 953 | 10 |
| testing/wenu-imaging-test/science | 1 | 2 | 10 | 10 | 0 | 0 |
| m42/reduced/science | Not established by this list-based census | 0 matching lists | 0 reported | Not established | Not established | Not established |

Historical filter grouping: 95 NB_659 partitions and 110 r_SDSS partitions. Counts refer to list memberships, not independently deduplicated raw exposures. The historic ten matched products remain the two NB_659 CN Ori groups identified above. The newer project has one CN Ori group per filter, five members each.

WCS counts are checks of the canonical source-stem subdirectory path only. The newer test project contains separate notebook04/05/etc. run directories, so zero canonical WCS paths is not evidence that astrometry never ran. Do not contradict the earlier qualified pilot records or move/reduce those files. Likewise, absent expected _pre names do not prove that alternate locations/names contain no products.

### Workspace/project relationship now observed

The configuration at ~/omegacam/workflows/wenu-imaging-test/config/pycavi.cfg specifies:

| Role | Configured location |
|---|---|
| Raw inputs | /home/fselman/fits/ |
| Reduction project | /home/fselman/omegacam/testing/wenu-imaging-test/ |
| Static calibration | Project static_calib/ |
| Reduced calibration | Project calib/ |
| Reduced standards | Project std/ |
| Reduced science | Project science/ |
| Logs | Project logs/ |
| Downstream stage names | Sextractor_dir, Scamp_dir, Swarp_dir, Calibration_dir |

The workflow workspace also contains config/ and data/, but workflows/wenu-imaging-test/data/science is absent at the checked location. This is consistent with its explicit external project_dir setting, not a broken workflow established by this census.

Its config directory contains mefpp.cfg/mefpp.paf, omegacam.cfg/omegacam.paf, pycavi.cfg, wfi.cfg/wfi.paf and example files. Presence does not establish which are effectively consumed; current source readers and actual run settings decide that. The test reduction project contains stage-specific successful/failed pilot directories and pre-normalization backups. Their names are context evidence, not completion certificates.

### Design disposition

This evidence is sufficient to inform the architecture analysis without more broad scans. Explicitly separate workspace, raw-storage root, reduction project, task attempt and published-product location. Keep project/asset identifiers stable when paths differ. Inventory and migrate the grouping/association descriptions without starting the 953 locally absent historical expected outputs.

Use the existing Mac baseline and already qualified Chapman pilot records for behavior comparisons. Further exact configuration consumption, local overrides and header/array checks should be tied to a concrete parser/interface implementation question, not added as a new full-dataset audit. No production changes, reductions, link repairs or dataset cleanup occurred.
