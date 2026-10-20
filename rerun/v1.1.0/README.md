# Evidence retained from the 2026-10-20 host run

`RUN_LOG.txt` copies the supplied `../run_plan.log`; `RUN_EXIT.txt` copies `../run_plan.exit`. The other JSON/log reports and the original R comparison CSV are copies of run-produced files. `COPY_PROVENANCE.json` lists each source path, its SHA-256 before copying, and whether redaction was applied.

Only local native R library paths were replaced with neutral tokens in `RUN_LOG.txt` and `plus-runtime.log`; a notice at the top of each states this. Remaining run output, including numeric records, is unchanged. Other copied files are byte-identical. The preserved logs report the source-hash count at execution time, before this evidence was added.

`ENVIRONMENT.json` is a fix-time evidence summary. Node and native R versions come from the run log. Playwright, Chrome and Python observations are labelled with their actual source; the original run did not record the exact Python/Chrome versions.

| Contract | Measured result | Evidence |
|---|---|---|
| Complete runner | 25 headings; RUN_EXIT 0 | RUN_LOG.txt; RUN_EXIT.txt |
| Original page / fresh comparison / R refit | 298116/298116 each; 198 matched refusals | original-browser.json; original/current-results.json; original-r.log |
| Original live R | 16/16 quantities | original-live.json |
| Extras presentation/export | 7248/7248; 28 refusals; 3/3 negative-control detections | extras-offline.json; RUN_LOG.txt |
| Native pairs / generated native script | 2176/2176; 4352/4352 | RUN_LOG.txt; plus-runtime.log |
| Live cross-runtime | 2139/2166; 27 failures in 23 configurations retained | glmm-browser-comparison.json; glmm-browser-results.json |
| Asset transport | No page errors, missing assets or off-origin requests | Three *-transport.json files |
| Historical figures/tables/metadata | ARCHIVE PASS | RUN_LOG.txt |

These are separate contracts as defined in `../../validation-plus/README-plus.md`. The documented-exceptions contract passes while the 27 numerical failures remain failures.

Both Python verifiers include every file in this directory in `SOURCE_SHA256.json`. Other `rerun/` content remains ignored scratch. The scripts do not overwrite this retained evidence directory.

| Content | Static or dynamic |
|---|---|
| Contract definitions and tolerances | Unchanged static protocol |
| Copied logs, JSON and CSV | Recorded run evidence |
| Environment summary | Source-backed observations with explicit limits |
| Source hashes and manifest hashes | Computed from file bytes |
