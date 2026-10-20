# Meta-analysis of proportions in the browser: a tool validated against the R packages metafor and meta

Version 1.1.0, release date 2026-10-20. Creator: Mahmood Ahmad. MIT-licensed archive code.

## What's new in v1.1.0

The archive targets allmeta **v1.8.0**, release commit **1cb3f8409c7af75ed41f7e1811f9c502f900fc79**, Zenodo DOI **10.5281/zenodo.23515177** (concept DOI **10.5281/zenodo.20516880**). The **2026-10-20 release run on allmeta 1cb3f84** completed all 26 labelled commands with RUN_EXIT 0; see [redacted release log](provenance/run_plan-2026-10-20-release.log), [exit marker](provenance/run_plan-2026-10-20-release.exit) and [run provenance](provenance/release-run.json). The earlier d04b0a9 run retained under rerun/v1.1.0/ is historical evidence. The counts below are confirmed by the release log.

The copied `app/shared/build-info.js` now embeds version v1.8.0, build SHA `42a94da2110a02200d0b5bff4c56f636b9cbffa9` and builtAt `2026-10-20T20:32:27Z`. Those are verbatim upstream fields; the embedded SHA differs from the supplied checkout HEAD and does not replace the confirmed release commit. [RECUT_NOTES.md](RECUT_NOTES.md#re-sync-to-allmeta-v180-1cb3f84) records each changed file and both hashes.

The separate binomial-normal GLMM panel is now archived with its R corpus, scripts, diagnostics and dependency packages under `validation-plus/` and `app/`. Native reference versions are metafor 5.2-1, meta 8.5-0 and lme4 2.0-6. The 2026-10-20 run measured **7,248/7,248 presentation/export checks** (240 configurations, 212 fits and 28 refusals), **2,176/2,176 native pair comparisons**, and **4,352/4,352 generated native-script comparisons** against both retained backends. These are separate contracts as defined in [README-plus.md](validation-plus/README-plus.md); see [release log](provenance/run_plan-2026-10-20-release.log) and [historical extras-offline.json](rerun/v1.1.0/extras-offline.json).

The 2026-10-20 live cross-runtime comparison retains **2,139/2,166 passing assertions and 27 failures in 23 configurations**. These failures remain failures under an exact documented-exceptions contract; the archive does not claim whole-corpus webR/native GLMM parity. See [the upstream extras protocol](validation-plus/README-plus.md) and [diagnosis](validation-plus/diagnostics/README.md). Same-runtime native comparisons and offline presentation replay do not execute an independent browser optimiser. The exact documented-exceptions contract passed; [historical glmm-browser-comparison.json](rerun/v1.1.0/glmm-browser-comparison.json) records the previously documented failures.

Original corpus files, R references, expected values, validation formulas and tolerances are unchanged. The updated page, fresh-observation Python comparison and native R refit each measured **298,116/298,116** on 2026-10-20, including **198 matched refusals**; the live original R check passed **16/16** quantities. All 26 runner headings completed with `RUN_EXIT 0`; see [release log](provenance/run_plan-2026-10-20-release.log), [release exit marker](provenance/run_plan-2026-10-20-release.exit) and [historical original-browser.json](rerun/v1.1.0/original-browser.json).

## Run environment and checkout bytes

The 2026-10-20 run used Node **v24.13.0**, native **R 4.6.0**, **metafor 5.2-1**, **meta 8.5-0**, **lme4 2.0-6**, metadat 1.6-0 and jsonlite 2.0.0, as recorded by the version preflight in [release log](provenance/run_plan-2026-10-20-release.log). Historical environment inspection recorded Playwright **1.59.1**, available through an existing, git-ignored `node_modules` junction and matches the upstream shared-test lock. The runner defaults to the **chrome** channel. Historical same-host inspection found **Chrome 155.0.8059.82** and **Python 3.13.13**; the run itself did not emit their versions or record a `PW_CHANNEL` override, so these observations are not a captured run-time version attestation. [historical ENVIRONMENT.json](rerun/v1.1.0/ENVIRONMENT.json) records the evidence and this limit.

All native version pins passed. The browser used webR 0.5.5 / R 4.5.1 / metafor 4.8-0 / lme4 2.0-1, the disclosed differences from native R; installed Chrome was used rather than a bundled Playwright Chromium build. The historical allmeta Git-history assertion is replaced by current/original byte pins in the archive wrapper. The historical run used the earlier v1.7.0 embedded stamp; the current copied stamp is described above.

The release run used the supplied allmeta 1cb3f84 checkout (78 app assets and 21 extras files). Its Windows CRLF checkout bytes are not asserted to be Git blob bytes. From the parent workspace, run FINAL_BLOBS.cmd before publication: it reads all 99 mappings in COPY_MAP.json from the confirmed commit with binary-safe Git output, prints BLOB PASS 99/99, updates only source-byte pins, and runs manifest regeneration and verification. Until that command succeeds, exact release blob identity remains unverified. The archive disables Git text conversion to preserve restored bytes; original reference pins remain unchanged.

## Re-run v1.1.0 on the updated app

From this archive root on the human runner, with installed Node, Chrome/Playwright, Python and the R packages listed in `RUN_PLAN_EXPECTED.md`:

```bat
RUN_PLAN.cmd
```

Set caller-supplied `R_HOME`, `R_LIBS_USER`, `R_LIBS` and `PLAYWRIGHT_MODULE` as documented in [RUN_PLAN_EXPECTED.md](RUN_PLAN_EXPECTED.md). The batch validates these settings and fails immediately on an unsuccessful command. Before staging, it renames prior scratch result folders and reports to their next unused .prev-N names under rerun/, preserving all previous outputs and the shipped rerun/v1.1.0/ evidence. It starts and closes a local server at `http://127.0.0.1:8000` for each browser step; that port must be free. It installs nothing. `PLAYWRIGHT_MODULE` selects the existing package; the batch maps it to the wrapper's `PLAYWRIGHT_PATH`.

The original browser replay executes all current page configurations and captures fresh numerical and DOM observations to `rerun/original/results/app-patched.json`. Unchanged `bench/compare.py` compares those observations with preserved R references; an unchanged copy of `validate.R` then refits R values against the same fresh observations. Nothing overwrites the original `data/`, `results/`, `expected/` or original validation scripts.

Separate steps run native GLMM pair checks, generated native R scripts, the 7,248-check offline browser presentation/export replay, warning diagnostics and the exhaustive live webR documented-exceptions contract. Fresh runtime output goes to ignored scratch paths under `rerun/`; the retained 20 October evidence in `rerun/v1.1.0/` is shipped and hash-verified. `RUN_PLAN_EXPECTED.md` records expected results by command and distinguishes exact pass totals from the retained cross-runtime failures.

For Python-only integrity checking:

```text
python analysis/recut_integrity.py
```

After reviewed metadata changes, regenerate and verify the app/source inventories:

```text
python analysis/refresh_manifests.py
python analysis/recut_integrity.py
python analysis/verify_archive.py
```

Reference manifests are never regenerated by these commands. The full verifier additionally checks historical publication tables and images. It needs working Pillow/matplotlib native dependencies. `RECUT_NOTES.md` records the completed host run and current sandbox verification limits.

Historical v1.0.0 validated allmeta commit: **0ecad36**. The numerical source is PR #104's fix on base **6036f3b6c1fd404b6da7916460faa8b3ebaf56bc**. The bundled page also contains the local validation adapter and read-only observation hooks. The v1.0.0 snapshot was byte-identical to its supplied worktree. The current app copy is the v1.8.0 release described above; archived v1.0.0 results below remain historical evidence. The historical run used **R 4.6.0, metafor 5.2-1, meta 8.5-0 and metadat 1.6-0**. R reports package versions using dots in `results/versions.json`.

The historical v1.0.0 primary comparison passes **298,116/298,116 checks after two fixes**, versus **237,911/298,116 before fixes**. These are repeated numerical, status and rendering checks, not independent clinical estimates. The 114-entry metadat catalogue supplies 62 used and 52 excluded datasets; 240 analyses contain 4,768 rows, including 478 zero-event and 23 all-event rows. Crossing logit/PFT/raw with PM/DL/FE yields 2,160 configurations: 1,962 successful fits and 198 matched refusals. Eight analyses have no usable rows. The input corpus, row exclusions, explicit mappings and package manuals are preserved; output generation independently asserts these counts from records.

## Corpus and mathematical contract

Each documented binary arm and outcome is a separate count/denominator analysis. Wide tables contribute both arms and their listed outcomes; long treatment-arm tables are split by treatment. Diagnostic tables contribute sensitivity and specificity counts separately. Category proportions and nested cholesterol trials are included. Only finite integer counts with `0 <= x <= n` and `n > 0` are retained, without imputation. Where the source supplies cells, explicit sums define denominators. Original source-row numbers, mapping expressions and group labels remain intact. `data/row-audit.json` records excluded row indices; `data/schema-evidence.json` and `bench/manuals/` record mapping evidence. Computational regroupings of arms/outcomes, repeated aliases and overlapping rows are **not clinical analyses** or independent studies.

The reference uses `metafor::escalc(measure="PLO"/"PFT"/"PR")` and `rma(method="PM"/"DL"/"FE", test="z")`. PLO/PR add 0.5 events and 0.5 non-events only at zero/all-event boundaries; PFT uses original counts. Normal 95% CIs are computed on the transformed scale. Inverses are ilogit, `transf.ipft.hm` using the harmonic mean of original denominators, and identity with clipping. For k>=3 the page uses `mu +/- qt(.975,k-1)*sqrt(tau2+SE^2)` for prediction intervals, **including FE**. Its **Q-based I2** is `max(0,100*(Q-df)/Q)` and differs from metafor's default estimator-based I2. This original transformed-scale contract excludes GLMM, moderator and clinical-effect validation; the separate extras contract is described above.

Relative difference is `abs(App-R)/max(1,abs(R))`. Closed-form checks use **1e-9**; PM-dependent pooled estimates, SE, tau2, intervals and study weights use **1e-6**. Status, row count, forest diamond and rounded pooled/PI text are exact checks. Absent PIs are explicitly checked. All transformed yi/vi, observed study proportions, Clopper-Pearson limits and percentage weights are compared. H2 and Q-test p-values are saved in the reference but are not exposed by this app and are not part of the primary contract. PM reference controls are `threshold=1e-12,tol=1e-18,maxiter=10000`.

Two numerical defects were fixed: (1) the finite-n PFT inverse previously continued periodically beyond its valid domain; the patch clamps outside the zero/all-event transform bounds to 0/1, matching R; (2) Clopper-Pearson beta continued-fraction and quantile-bisection tolerances were too coarse, and were tightened to 1e-14. `bench/fix.patch` preserves the exact numerical patch. Table 1 recomputes before/after failures by quantity rather than trusting narrative totals.

## Secondary comparison with meta

`meta::metaprop(method="Inverse", method.incr="only0", incr=.5, method.random.ci="classic", method.ci="CP")` supplies a secondary check of pooled transformed mean, SE and tau2 plus status. It passes **7,432/8,046 checks**. Its 614 differences are raw-proportion boundary conventions: meta keeps `event/n` as the estimate while correcting its variance; the page and metafor PR correct both estimate and variance. Logit and PFT agree, and meta's PFT uses the same half-sum scale without rescaling. These differences are documented conventions, not extra app defects. The full primary comparison supplies interval and per-study coverage. `bench/metaprop-source.txt`, `results/meta-reference.json` and `results/meta-results.json` retain evidence.

## Original archived R recomputation

From this archive root, with R and the already installed metafor and jsonlite packages:

```text
Rscript validate.R
```

This uses no network, Python, Node, browser or metadat installation. Missing dependencies and unexpected fit errors fail closed. Set standard R library environment variables to your existing package libraries if necessary. The script prints actual R/metafor versions, per-quantity results and `298116/298116 checks pass` on success, writes `outputs/validate_R_table.csv`, and exits nonzero on failure or incomplete coverage.

Every numerical quantity is **recomputed** from `data/corpus.json` with the original reference formulas and controls, then compared with `results/app-patched.json`. Status checks recompute the k<2 refusal rule. Four checks per successful fit **replay archived browser evidence**: row count, diamond count, pooled text and PI text; expected numbers are newly calculated in R. This command does not launch a browser or certify current DOM behavior. The CSV Mode column distinguishes numerical recomputation from archived DOM evidence.

## Reproduce publication outputs

With existing Python, matplotlib, Pillow and PyYAML:

```text
python analysis/make_outputs.py
python analysis/verify_archive.py
```

These offline commands regenerate and verify `table1_by_quantity.csv`, `table2_datasets.csv`, agreement and visual-abstract PNG/TIFF pairs, `sizes.json`, numerical provenance in `numbers.json`, and `reproduction_report.md`. The agreement figure shows log10 maximum relative difference by quantity, tolerance lines and before-fix failures. Figures are 300 dpi, 170 mm wide, with text at least 8 pt. Expected values are assertions, never substituted for computed findings. Table 2 includes every catalogue entry, including excluded datasets with zero analysis counts.

`app/` contains the exact local allmeta assets, including the same-origin webR bundle and pinned metafor dependencies used by live validation. `app/app-sha256.json` verifies those source bytes. Serve `app/` locally at `http://127.0.0.1:8000` and open `/proportion-ma/index.html` to use the widget. Tier 1 uses **webR 0.5.5/metafor 4.8-0**, explicitly distinguished from paper metafor 5.2-1. Tier 2 reads hash-pinned inputs and replays **all 298,116 checks** through current page code; it does not substitute archived app outputs. It suppresses URL writes and restores inputs, results and rendered output. A warm replay works offline; file-URL users select both corpus JSON files. The linked future archive repository is an intended destination, not a claim of publication or hosted Actions availability.

`bench/README.md` explains the original scripts. `SOURCE_SHA256.json` pins source inventory, excluding itself, generated outputs, caches and git metadata. Verification permits a future `.git` directory. This preparation does not create a commit, push, deployment or Overmind certification. The historical 20 October d04b0a9 evidence in `rerun/v1.1.0/` is included in `SOURCE_SHA256.json` and both verifiers; other `rerun/` paths are excluded scratch. The original `results/` remains preserved. Counts describe this validation corpus only.

| Content | Static or dynamic | Evidence / transformation |
|---|---|---|
| Corpus rules, model, tolerances, methods | Static protocol | Original reference.R, compare.py and package manuals |
| Commit/PR provenance and expected counts | Static supplied metadata/assertions | Base revision, fix.patch and expected/paper_values.json |
| Inputs and archived fit results | Recorded source evidence | metadat corpus, original/patched browser runs and R references |
| Counts, errors, tables and figure coordinates | Dynamic | Recomputed from archived input/result records |
| R validation values | Dynamic | Every numerical reference refitted by validate.R |
| Four DOM checks per successful fit in validate.R | Replayed | Archived app display fields versus newly computed expectations |
| Browser replay and live R values | Dynamic | Current page engine/DOM and same-origin webR |
| Dimensions, typography and colours | Static presentation | make_outputs.py; dimensions and paired pixels verified |
| Hash manifests | Dynamic integrity evidence | SHA-256 of assembled source bytes; not scientific certification |

Historical v1.0.0 provenance: derived from [allmeta](https://github.com/mahmood726-cyber/allmeta) and allmeta v1.2.1, DOI **10.5281/zenodo.23288388** (`isDerivedFrom`). Identifiers are supplied provenance, not independently network-verified claims. Dataset documentation and vendored packages retain upstream attribution and licenses; the archive's MIT license covers archive code and does not replace upstream rights.
