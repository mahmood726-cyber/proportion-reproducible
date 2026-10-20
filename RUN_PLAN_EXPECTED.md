# Expected results for RUN_PLAN.cmd

The release run completed on **2026-10-20 for allmeta 1cb3f84**. Original and extras expected counts and tolerances are unchanged.

Run from the archive root. Every labelled command must exit zero; the batch stops on failure. All 26 labelled commands completed on 2026-10-20 with `RUN_EXIT 0`; [release log](provenance/run_plan-2026-10-20-release.log) and [exit marker](provenance/run_plan-2026-10-20-release.exit) preserve the evidence. Measured totals were **298,116/298,116 original checks**, **7,248/7,248 extras presentation/export checks**, **2,176/2,176 native pair comparisons**, and **4,352/4,352 generated native-script comparisons**. The live cross-runtime comparison retained **27 failures** with **2,139/2,166** assertions passing; its exact documented-exceptions contract passed. The table below remains the rerun contract from the unchanged original records and README-plus.md/MANIFEST-plus.json/check-plus.mjs.

Supply the following environment variables before calling `RUN_PLAN.cmd`. Missing variables fail immediately; no machine-specific library path is supplied by the archive.

| Variable | Caller-supplied value |
|---|---|
| `R_HOME` | Existing R 4.6.0 installation root containing `bin/Rscript.exe`; its `bin` is prepended to PATH. |
| `R_LIBS_USER` | Semicolon-separated existing native R package library directories. |
| `R_LIBS` | Semicolon-separated existing dependency library directories. |
| `PLAYWRIGHT_MODULE` | Existing Playwright package path, or `playwright` when resolvable through local `node_modules`; mapped to the wrapper's `PLAYWRIGHT_PATH`. |

The batch sets `R_ENVIRON_USER=NUL`. Node and Python must already be on PATH. Installed Chrome is the default browser; `PW_CHANNEL` can select another installed channel, which constitutes a different run environment. Port 8000 must be free. No package installation or Git operation occurs. [ENVIRONMENT.json](rerun/v1.1.0/ENVIRONMENT.json) and README record the host versions, pin differences and the limit on observed Python/Chrome versions.

| Label / command | Expected result |
|---|---|
| R PATH, R user libraries, R dependency libraries, R environment file | Use caller-supplied R_HOME, R_LIBS_USER and R_LIBS; set R_ENVIRON_USER=NUL. No numerical total. |
| Existing Playwright package | Require PLAYWRIGHT_MODULE and map it to PLAYWRIGHT_PATH. Installed Chrome and free port 8000 are required. |
| Verify prepared source and original reference integrity | RECUT INTEGRITY PASS. Exact current source files (legacy pin field), verbatim extras, original protected records and pin manifests all match. Hash checks are not numerical tests. |
| Node preflight | Print installed Node version; no download. |
| Native R package version preflight | R 4.6.0; metafor 5.2.1, meta 8.5.0, metadat 1.6.0, lme4 2.0.6, jsonlite 2.0.0. Missing/different versions fail. |
| Preserve earlier scratch outputs | Rename prior scratch result folders/reports to the next unused .prev-N names under rerun/; never delete or overwrite old outputs. Preserve shipped rerun/v1.1.0/ evidence. A fresh state is a successful no-op. |
| Stage scratch wrappers and immutable input copies | STAGED message; output only in rerun/. Original references untouched. |
| Parse archive browser wrapper | node --check succeeds without syntax output. |
| Parse copied extras wrapper | node --check succeeds without syntax output. |
| Re-run original validation against current app and capture observations | **298116/298116** browser checks; 2,160 configurations and 198 matched refusals; inputs/results/DOM/URL restored. **16/16** live-R quantities. Capture fresh page results for the next two steps. No page errors, missing assets or off-origin requests. |
| Compare fresh app observations with original R references | Original bench/compare.py prints **298116/298116 checks pass**. Wrapper additionally requires checks=passed=298116, failed=0. |
| Refit original R validation against fresh app observations | Unchanged validate.R prints **298116/298116 checks pass**. Recomputed R fits versus fresh release observations; four DOM checks per fit use captured current-page evidence. Output in rerun/original/outputs/. |
| Check native extras pairs and generate exact browser R script | Six pins; 240 configurations; **2176/2176** native pair checks; 28 refusals; 22 negative assertions; original corpus pins **2/2**. Generate runtime-plus.R in scratch. Historical git assertion explicitly reported as not run. |
| Execute generated extras script in native R | 240 CASE/ALMJSON records, actual package paths/versions, exit 0; the following command supplies the comparison total. Full raw log in rerun/plus-runtime.log. |
| Compare new native script results with both GLMM references | **4352/4352** native-script comparisons across 240 configurations, plus the repeated **2176/2176** native pair checks and pins. This is native R, not webR parity. |
| Check retained GLMM warnings and diagnostic evidence | 240 configurations; 23 disclosed configurations: 21 Hessian-sensitivity and 2 optimiser-status cases; 27 failures preserved; 3 common-parameter cases, 15 sampled objective values, max difference below 1e-12. |
| Replay extras presentation and JSON export offline | **7248/7248** presentation/export checks, 240 configurations, 28 refusals, warm offline replay and restoration. **3/3** negative-control detections. The measured presentation/export result is **7,248/7,248** in provenance/run_plan-2026-10-20-release.log; native pairs and native-script comparisons have their separate totals above. |
| Re-run full live webR GLMM documented-exceptions contract | **2139/2166** numerical assertions pass; **27 remain failures** in exactly 23 configurations; 28 browser refusals. The *documented-exceptions contract* passes only if IDs, fields, counts and diagnosed reasons match exactly and no additional failures occur. This is not an N/N numerical pass. Changes, including vanished exceptions, require review. |
| Reproduce historical publication outputs | All **15/15** original paper-value assertions pass; **298116/298116** historical post-fix checks and **237911/298116** historical pre-fix checks. This command reads preserved v1.0.0 results, not current rerun results. |
| Verify no protected source changed during reruns | Same integrity gate; no source/reference drift. |
| Regenerate app and source inventories | REFRESHED message. Only app/app-sha256.json and SOURCE_SHA256.json are regenerated; reference pins stay fixed. |
| Verify regenerated source and reference manifests | RECUT INTEGRITY PASS; no runtime certification implied. |
| Full historical archive metadata table and image verification | ARCHIVE PASS: source/app hashes, version 1.1.0 metadata, preserved historical counts, reproducible tables/images and pixel comparisons. Requires working matplotlib/Pillow/PyYAML. |

The release log and its environment evidence are in provenance/; earlier run details remain under rerun/v1.1.0/. FIX_NOTES.md separates fix-session Python checks from that recorded host run. Rerun outputs use scratch paths; retained v1.1.0 evidence is preserved and included in both verifiers' source inventory.

| Material | Static or dynamic |
|---|---|
| Expected totals, tolerances, protocol | Static assertions from supplied evidence |
| Corpus/reference records | Preserved measured/package evidence |
| Rerun results | Release measured 2026-10-20 on 1cb3f84; provenance/ log, with earlier run JSON retained separately |
| Manifest values | Computed from current file bytes |

## Exact release blob finalization

From the parent workspace run FINAL_BLOBS.cmd. Git and Python must be on PATH; allmeta must contain commit 1cb3f8409c7af75ed41f7e1811f9c502f900fc79. The helper reads COPY_MAP.json, fetches all 99 Git blobs before writing, preserves binary bytes, verifies every written copy, updates source-byte provenance, then runs manifest scripts and the full verifier. Expected: BLOB PASS 99/99, REFRESHED, RECUT INTEGRITY PASS, and ARCHIVE PASS. Any failure returns nonzero. No scientific reference manifest is repinned. A standalone archive may run: python analysis/finalize_blobs.py --archive . --allmeta ../allmeta --copy-map COPY_MAP.json
