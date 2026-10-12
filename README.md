# Meta-analysis of proportions in the browser: a tool validated against the R packages metafor and meta

Version 1.0.0. Creator: Mahmood Ahmad. MIT-licensed archive code.

Validated allmeta commit: **0ecad36**. The numerical source is PR #104's fix on base **6036f3b6c1fd404b6da7916460faa8b3ebaf56bc**. The bundled page also contains the local validation adapter and read-only observation hooks. It is byte-identical to the supplied allmeta worktree at archive assembly; no merged commit or deployment is claimed. The historical run used **R 4.6.0, metafor 5.2-1, meta 8.5-0 and metadat 1.6-0**. R reports package versions using dots in `results/versions.json`.

The primary comparison passes **298,116/298,116 checks after two fixes**, versus **237,911/298,116 before fixes**. These are repeated numerical, status and rendering checks, not independent clinical estimates. The 114-entry metadat catalogue supplies 62 used and 52 excluded datasets; 240 analyses contain 4,768 rows, including 478 zero-event and 23 all-event rows. Crossing logit/PFT/raw with PM/DL/FE yields 2,160 configurations: 1,962 successful fits and 198 matched refusals. Eight analyses have no usable rows. The input corpus, row exclusions, explicit mappings and package manuals are preserved; output generation independently asserts these counts from records.

## Corpus and mathematical contract

Each documented binary arm and outcome is a separate count/denominator analysis. Wide tables contribute both arms and their listed outcomes; long treatment-arm tables are split by treatment. Diagnostic tables contribute sensitivity and specificity counts separately. Category proportions and nested cholesterol trials are included. Only finite integer counts with `0 <= x <= n` and `n > 0` are retained, without imputation. Where the source supplies cells, explicit sums define denominators. Original source-row numbers, mapping expressions and group labels remain intact. `data/row-audit.json` records excluded row indices; `data/schema-evidence.json` and `bench/manuals/` record mapping evidence. Computational regroupings of arms/outcomes, repeated aliases and overlapping rows are **not clinical analyses** or independent studies.

The reference uses `metafor::escalc(measure="PLO"/"PFT"/"PR")` and `rma(method="PM"/"DL"/"FE", test="z")`. PLO/PR add 0.5 events and 0.5 non-events only at zero/all-event boundaries; PFT uses original counts. Normal 95% CIs are computed on the transformed scale. Inverses are ilogit, `transf.ipft.hm` using the harmonic mean of original denominators, and identity with clipping. For k>=3 the page uses `mu +/- qt(.975,k-1)*sqrt(tau2+SE^2)` for prediction intervals, **including FE**. Its **Q-based I2** is `max(0,100*(Q-df)/Q)` and differs from metafor's default estimator-based I2. No GLMM, moderator or clinical-effect validation is claimed.

Relative difference is `abs(App-R)/max(1,abs(R))`. Closed-form checks use **1e-9**; PM-dependent pooled estimates, SE, tau2, intervals and study weights use **1e-6**. Status, row count, forest diamond and rounded pooled/PI text are exact checks. Absent PIs are explicitly checked. All transformed yi/vi, observed study proportions, Clopper-Pearson limits and percentage weights are compared. H2 and Q-test p-values are saved in the reference but are not exposed by this app and are not part of the primary contract. PM reference controls are `threshold=1e-12,tol=1e-18,maxiter=10000`.

Two numerical defects were fixed: (1) the finite-n PFT inverse previously continued periodically beyond its valid domain; the patch clamps outside the zero/all-event transform bounds to 0/1, matching R; (2) Clopper-Pearson beta continued-fraction and quantile-bisection tolerances were too coarse, and were tightened to 1e-14. `bench/fix.patch` preserves the exact numerical patch. Table 1 recomputes before/after failures by quantity rather than trusting narrative totals.

## Secondary comparison with meta

`meta::metaprop(method="Inverse", method.incr="only0", incr=.5, method.random.ci="classic", method.ci="CP")` supplies a secondary check of pooled transformed mean, SE and tau2 plus status. It passes **7,432/8,046 checks**. Its 614 differences are raw-proportion boundary conventions: meta keeps `event/n` as the estimate while correcting its variance; the page and metafor PR correct both estimate and variance. Logit and PFT agree, and meta's PFT uses the same half-sum scale without rescaling. These differences are documented conventions, not extra app defects. The full primary comparison supplies interval and per-study coverage. `bench/metaprop-source.txt`, `results/meta-reference.json` and `results/meta-results.json` retain evidence.

## Validate with one command

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

`bench/README.md` explains the original scripts. `SOURCE_SHA256.json` pins source inventory, excluding itself, generated outputs, caches and git metadata. Verification permits a future `.git` directory. No repository was initialized, manuscript draft included, commit created, push performed or Overmind certification claimed. Counts describe this validation corpus only.

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

Derived from [allmeta](https://github.com/mahmood726-cyber/allmeta) and allmeta v1.2.1, DOI **10.5281/zenodo.23288388** (`isDerivedFrom`). Identifiers are supplied provenance, not independently network-verified claims. Dataset documentation and vendored packages retain upstream attribution and licenses; the archive's MIT license covers archive code and does not replace upstream rights.
