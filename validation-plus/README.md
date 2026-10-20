# GLMM extras for archive v1.1.0

Release validation completed on 2026-10-20 for allmeta 1cb3f84. Counts below are confirmed in [the release log](../provenance/run_plan-2026-10-20-release.log); detailed JSON under rerun/v1.1.0/ remains historical d04b0a9 evidence. All upstream extras and expected counts are unchanged.

The 2026-10-20 run measured **7,248/7,248 presentation/export checks** across 240 configurations (212 fits, 28 refusals), **2,176/2,176 native pair comparisons**, and **4,352/4,352 generated native-script comparisons** against both retained backends. These separate counts follow [README-plus.md](README-plus.md); see [release log](../provenance/run_plan-2026-10-20-release.log), [extras-offline.json](../rerun/v1.1.0/extras-offline.json) and [plus-runtime.log](../rerun/v1.1.0/plus-runtime.log).

The extra panel fits binomial-normal GLMMs with `metafor::rma.glmm(measure="PLO")` beside the original transformed-scale results. The pinned native references use **R 4.6.0, metafor 5.2-1, meta 8.5-0, metadat 1.6-0 and lme4 2.0-6**; see `plus-corpus/versions-plus.json`. The browser uses webR 0.5.5/metafor 4.8-0/lme4 2.0-1. Protocol and tolerances are copied without modification.

The offline tier compares pinned native fits and checks presentation, exported values, input records and provenance; it does not rerun the optimiser. Native pair checks passed **2,176/2,176** and the generated native script passed **4,352/4,352** comparisons against both references. The 20 October live webR comparison retains **2,139/2,166 passing assertions with 27 documented failures** in 23 configurations. The exact documented-exceptions contract passed; those failures are never counted as passes. See [glmm-browser-comparison.json](../rerun/v1.1.0/glmm-browser-comparison.json).

Run `RUN_PLAN.cmd` from the archive root for the complete ordered workflow. Individual extras commands, also from the archive root:

```text
python analysis/run_recut.py stage
node rerun/plus/proportion-ma/validate/check-plus.archive.mjs --write-r
python analysis/run_recut.py plus-r
node rerun/plus/proportion-ma/validate/check-plus.archive.mjs --runtime-log rerun/plus-runtime.log
node rerun/plus/proportion-ma/validate/check-plus-diagnostics.mjs
node analysis/run_browser.cjs extras
node analysis/run_browser.cjs live-plus
```

Supply `R_HOME`, `R_LIBS_USER`, `R_LIBS` and `PLAYWRIGHT_MODULE` as documented in [RUN_PLAN_EXPECTED.md](../RUN_PLAN_EXPECTED.md), with an existing Playwright package/Chrome installation. Each browser command owns a local server at `http://127.0.0.1:8000` and closes its browser/server. The live GLMM command allows up to 30 minutes.

All files copied from upstream validation retain their relative structure and bytes here. `analysis/run_recut.py` stages those files under `rerun/plus/proportion-ma/validate/` beside the copied app, restoring the upstream scripts' expected sibling paths. The upstream checker uses `git show` against an allmeta-only historical commit. The generated `check-plus.archive.mjs` replaces that Git-history block with byte-pin checks for the archived app and protected original corpus. It retains all native comparisons, negative assertions, reference pins and tolerances, and adds explicit N/N reporting. This archive pin check does not establish historical page equivalence to that allmeta commit. Upstream originals are never edited.

Optional source-package reference regeneration is isolated:

```text
python analysis/run_recut.py stage
python analysis/run_recut.py generate-plus
```

This writes to `rerun/regenerated-plus/`. Review its native output against the retained evidence; do not overwrite or silently repin `plus-corpus/`. The detailed upstream diagnostics mention lane-specific reports/configurations that were not part of the supplied validation directory; the archive's supported commands are those above.

| Content | Static or dynamic | Evidence |
|---|---|---|
| Fit settings, mappings and tolerances | Static protocol | Upstream scripts, unchanged |
| Native references and warning catalogue | Retained generated evidence | Pinned corpus and diagnostics |
| Offline presentation/export results | Dynamic replay of retained fits | Current app and adapter |
| Native/browser GLMM reruns | Measured on 2026-10-20 | Shipped rerun/v1.1.0 logs and JSON, with retained failures |
| Manifest hashes | Dynamic integrity evidence | Python SHA-256 checks |
