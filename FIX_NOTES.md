Finalization note (2026-10-20): this file records the earlier fix session. Release identities and the later 1cb3f84 run are resolved in RECUT_NOTES.md, Finalize; earlier placeholder-preservation statements below are historical.

# Required review fixes F1-F8

Scope: archive-only edits; no Git metadata, corpus, R reference, expected value, tolerance, creator/author or licence changes. Final v1.8.0 SHA/DOI placeholders are preserved.

| Fix | Files and lines | Change / limitations |
|---|---|---|
| F1 | `README.md:11`; `CHANGELOG.md:7`; `RECUT_NOTES.md:28`; `RUN_PLAN_EXPECTED.md:33`; `validation-plus/README.md:3` | Replaced every extras-count token with measured, labelled presentation/export (7,248/7,248), native-pair (2,176/2,176) and native-script (4,352/4,352) results and evidence links. All seven release-SHA and seven release-DOI tokens remain unchanged. |
| F2 | `README.md:3`; `CHANGELOG.md:3`; `.zenodo.json:29`; `CITATION.cff:34`; `RECUT_PROVENANCE.json:8`; `RECUT_NOTES.md:23`; `validation-plus/README.md:3`; `RUN_PLAN_EXPECTED.md:3`; `STUCK_FAILURES.md:1` | Replaced stale execution status with the 20 October measured run and evidence pointers. Live GLMM remains 2,139/2,166 with 27 failures in 23 configurations. Source inspection found 25 run-log headings, including environment setup (the review described 24); documentation uses the observed count. |
| F3 | `RUN_PLAN.cmd:4`; `RUN_PLAN_EXPECTED.md:5` | Removed all machine-specific paths. Require caller-supplied R_HOME, R_LIBS_USER, R_LIBS and PLAYWRIGHT_MODULE; map the latter to the existing wrapper's PLAYWRIGHT_PATH. Missing R_HOME was tested to exit 1 before runtime work. |
| F4 | `.gitignore:5`; `analysis/recut_integrity.py:13`; `analysis/verify_archive.py:6`; `rerun/v1.1.0/README.md:1`; `rerun/v1.1.0/RUN_LOG.txt:1` | Ship 15 copied run artifacts, source-copy hashes, an environment summary and an evidence guide. RUN_LOG.txt and plus-runtime.log redact only local R library paths, with notices; all other copied files are byte-identical. Both verifiers now share the source inventory, including rerun/v1.1.0; other scratch stays ignored. |
| F5 | `README.md:17`; `RECUT_NOTES.md:35`; `rerun/v1.1.0/ENVIRONMENT.json:3` | Record Node v24.16.0, Playwright 1.59.1 and the ignored junction, default chrome channel, observed Chrome 155.0.8059.82/Python 3.13.13, and all native/browser R package versions and pin differences. Python/Chrome versions were observed on the same host during fixes; their exact run-time versions and channel override were not recorded by the original runner. |
| F6 | `CITATION.cff:11` | Verified all three references already have family-names Ahmad / given-names Mahmood, including allmeta 1.8.0; retained these authors unchanged. Metadata creators/authors and licence are unchanged. |
| F7 | `README.md:23`; `RECUT_NOTES.md:41` | State and independently verify 78/78 app files equal the supplied d04b0a9 checkout. Preserve its CRLF/LF mix, LF-pinned validation JSON and binary bytes; existing * -text prevents checkout conversion. No app or scientific input bytes were edited. |
| F8 | `analysis/refresh_manifests.py:2`; `SOURCE_SHA256.json:1`; `RUN_FIX.cmd:6` | Regenerate manifests with the archive's own script and run its Python verifiers; exact outcomes are recorded below. RUN_FIX.cmd lists host commands for unavailable Git/Node/R and full native-library verification. No Git checkout or restoration was prescribed by F1-F8, so none was performed. |

## Verification

Commands executed during this fix session:

- `python -X utf8 analysis/refresh_manifests.py` - exit 0:
  `REFRESHED: app/app-sha256.json and SOURCE_SHA256.json`
- `python -X utf8 analysis/recut_integrity.py` - exit 0:
  `RECUT INTEGRITY PASS: 78 candidate app hashes; 299 source hashes; 159 protected originals; 21 verbatim extras; 20 R package archives.`
- `python -X utf8 analysis/run_recut.py compare-original` - exit 0:
  `CURRENT ORIGINAL: 298116/298116 checks pass`
  This rechecks the saved fresh-page observations with the unchanged original comparator; it does not launch a browser.
- Focused Python checks - exit 0:
  `EVIDENCE INTEGRITY PASS: 18 shipped files covered; altered evidence rejected and restored.`
  `RESULT EVIDENCE PASS: recorded counts and 240 GLMM IDs verified; 27 failed fields in 23 configurations match retained diagnostics.`
  `METADATA PASS: 3/3 reference authors; 0 count tokens; 7 SHA and 7 DOI release tokens preserved; no shipped user paths/BOM.`
  `PRESERVATION PASS: app, original scientific sources and historical outputs unchanged from fix-session baseline.`
- Python AST checks for the archive analysis scripts passed. The portable batch's missing-R_HOME check exited 1 with the expected configuration error before invoking runtimes.
- `python -X utf8 analysis/verify_archive.py` - **exit 1**, blocked while importing `PIL.Image`: `ImportError: DLL load failed while importing _imaging: A dynamic link library (DLL) initialization routine failed.` The separate matplotlib import also fails at its native DLL. No current full-verifier/image pass is claimed.

Recorded host result, **not a new fix-session result**, in `rerun/v1.1.0/RUN_LOG.txt`:

```text
PASS: 15/15 paper-value assertions; 298116/298116 final checks; 237911/298116 before fixes.
ARCHIVE PASS: 78 app hashes; 279 source hashes; 298116/298116 historical checks; tables, metadata, reproducible outputs and image pixels verified.
```

The historical 279-source count predates the evidence and review-fix additions; the current source inventory has 299 entries. `RUN_FIX.cmd` records Git status/whitespace and Node syntax checks and invokes the full portable `RUN_PLAN.cmd` Node/R/browser/Python sequence on a working host. Set the documented caller variables first. Node/R/browser and Git commands were not executed in this fix sandbox. The exact original Python/Chrome run versions cannot be recovered from the saved log; same-host observations are explicitly distinguished.

| Content | Static or dynamic | Evidence |
|---|---|---|
| Formulas, tolerances and reference values | Unchanged static protocol / preserved data | Original and extras byte pins |
| 20 October counts and exceptions | Recorded measured results | Copied logs/JSON; diagnostic ID/field comparison |
| Fix-session integrity and comparison results | Computed | Python checks above |
| Python/Chrome environment observations | Same-host observations, not run telemetry | ENVIRONMENT.json source labels |
| Release SHA/DOI | Unresolved by instruction | Original placeholders preserved |

No outstanding edit was identified within F1-F7. F8 manifest regeneration and the standard-library verifier passed; the full native-library verifier needs the host follow-up above. No Git metadata, app bytes or scientific values were changed.
