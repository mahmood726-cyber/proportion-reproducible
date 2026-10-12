# Proportion MA validation

The unmodified application passed **237911/298116 primary checks**; the locally patched copy passed **298116/298116 primary checks**. Two source defects were identified and corrected in `fix.patch`. Native meta passed **7432/8046 secondary checks**; its 614 differences are raw-proportion boundary-correction conventions, documented below. The original allmeta tree was not modified. This is a validation result, not a release or Overmind certification.

Source commit: `6036f3b6c1fd404b6da7916460faa8b3ebaf56bc`. Runtime: R version 4.6.0 (2026-04-24 ucrt); metafor 5.2.1; metadat 1.6.0; meta 8.5.0; Chrome 154.0.8037.99. `source-provenance.json` records SHA-256 for 153 byte-identical copied source files. The job directory is not a git worktree; no commit, push, deployment, registry, or workbook changes were made.

## Corpus and scope

`data(package="metadat")` enumerated 114 entries: 62 used and 52 excluded. There are 240 separate count/denominator analyses, 4768 input rows across these analyses, 478 zero-event rows and 23 all-event rows. Repeated arms/outcomes/aliases are retained intentionally; these are computational checks, not independent studies or new scientific findings. Every analysis was run under logit/PFT/raw crossed with PM/DL/FE, for 2160 configurations: 1962 successful and 198 matched refusals (fewer than two valid rows). Eight analyses have no usable rows. No synthetic observations were added.

Rule: each documented arm and binary outcome is a separate proportion analysis. Wide binary tables use both arms, all listed endpoints are included, long treatment-arm tables are split by treatment, and diagnostic datasets contribute sensitivity and specificity counts separately. Single-group event counts are used directly. Multi-arm datasets, genotype-category proportions and the nested `dat.metap$cholest` trials are included. Missing, nonfinite, fractional, negative, x>n, and n<=0 rows are excluded without imputation, with exact row indices in `row-audit.json`. Conditioning totals are explicit sums where the source supplies cells rather than totals. For Higgins, response is conditional on observed response/failure; missing outcomes are excluded from the denominator. Clinical interpretations of these computational regroupings are outside scope.

All numerical inputs come from the installed metadat package. `corpus.json` is the exact shared browser/R input; `schema-evidence.json` verifies all 240 mappings against the bundled open package manuals. Original row numbers are provenance identifiers, not invented trial identifiers. No PMIDs, DOIs, NCT IDs, or study dates were fabricated or re-keyed. Excluded nested objects contain correlations/phylogenies, trend statistics, or effect/covariance data; the count-containing nested cholesterol data were included. Metafor uses metadat for its example datasets; no separate synthetic metafor examples were substituted for this catalogue.

## Exact app contract

The separate `data(package="metafor")` catalogue contains zero datasets, recorded in `metafor-catalogue.json`; the full metadat catalogue is therefore the source-data catalogue for this validation.

| Feature | What is actually computed and compared |
|---|---|
| Transforms | PLO logit; PFT half-sum of arcsines, variance 1/(4n+2); PR raw. PAS and PLN are not offered. |
| Boundary handling | PLO/PR add 0.5 events and 0.5 non-events only at x=0 or x=n; adjusted total n+1. PFT uses original counts without a continuity correction. |
| Pooling | Shared ma-core tau2 PM/DL/FE; inverse-variance pooled mean and SE in the page. No GLMM option and no HKSJ/t CI. |
| CI | z=qnorm(.975), 95% Wald interval on transform scale. PR limits clipped to [0,1]. |
| PI | For k>=3 only: mu +/- qt(.975,k-1)*sqrt(tau2+SE^2), including FE. The explicit R formula matches this app convention; metafor's default z-based PI is stored separately and is not silently treated as equivalent. |
| Inverse | ilogit, identity/clipping for raw, and Miller PFT inverse using harmonic mean of original included n_i. Patched PFT boundary behavior matches transf.ipft.hm. |
| Heterogeneity | Q and df; displayed I2=max(0,100*(Q-df)/Q). This Q-based convention is checked directly; metafor's estimator-dependent I2 and H2 are stored under `metafor` in reference.json. |
| Not exposed | H2 and Q-test p-value are neither returned nor displayed by this page; R values are saved, but no app parity is claimed for them. |
| Per study | yi, vi, raw observed p, exact Clopper-Pearson limits, percentage inverse-variance weights. |
| UI | Actual click handler, table row count, forest diamond count, pooled displayed percentages and displayed PI text. Both runs had zero browser page errors. |

The reference calls `metafor::escalc` followed by `rma(method=...,test="z")`, and `predict(...,transf=...)` for pooled back-transforms. PM uses `control=list(threshold=1e-12,tol=1e-18,maxiter=10000)`. The initial default R uniroot tolerance, and then 1e-12, were inadequate for PM weights in the very small raw variances of `dat.crisafulli2020`; tightening only the reference removed those discrepancies. The shipped PM routine needed no change. No final metafor fit warnings occurred. Startup emitted four Windows locale warnings; loading metadat emitted three character-encoding warnings. These did not affect the numeric input.

The browser loads the complete copied HTML and shared scripts via file URLs. `run-app.cjs` uses conditional debugger probes to read the actual closure's transformed rows, computed CI/PI limits, and rendered studies; it does not extract or reimplement its functions. No computation functions are replaced or wrapped in the final harness. No alternate pooling implementation is used as the app under test. The final browser reruns directly observe local interval variables, replacing an earlier harness that reconstructed CI limits from exported mean/SE.

## Failures and minimal patch

1. `proportion-ma/index.html:246-252`: ftBack applies a periodic algebraic inverse beyond the finite-n PFT domain and falls back to sin(y)^2 on invalid radicands. R's transf.ipft.hm instead clamps below transf.pft(0,nH) to zero and above transf.pft(1,nH) to one. This produces materially wrong interval limits and sometimes changes displayed intervals. The patch adds domain checks before evaluating the inverse; it uses the existing ftTransform and original harmonic-mean n.
2. `proportion-ma/index.html:198,227`: beta continued-fraction tolerance 3e-7 and quantile bisection stopping width 1e-8 are too coarse for the required 1e-9 absolute CI agreement. The patch tightens both to 1e-14. Patched per-study lower/upper CI maxima are 1.2542744620702706e-12 / 1.2484457911909885e-12.

`fix.patch` is a unified diff against allmeta, applies cleanly to the copied original, and changes only this HTML file. `patched/` contains the rerun copy. `original-results.json` contains every failed quantity/configuration with observed and reference values. The bounded sequence was: original run; one numerical app patch; two reference precision refinements; final comparison. No broad refactor was made.

UI/documentation observations: the header's “incidences / event rates” wording is too broad for an integer binomial events/total interface (no person-time model). GLMM is advice to use external R, not an available option. The source explicitly preserves Q-based I2, which differs from metafor PM's default; it also displays a t-based PI under FE. The existing `test_against_r.py` references an R reimplementation and a small fixture, rather than proving full-corpus metafor parity. The PFT caution about potentially inverted/out-of-range intervals should be revisited if this patch is adopted. These observations are documented without changing unrelated UI copy.

## Per-quantity primary comparison

Difference is abs(app-ref)/max(1,abs(ref)); proportions therefore use absolute error. Closed-form quantities use 1e-9. PM-dependent estimates, SEs, intervals, tau2 and weights use 1e-6; no flat-likelihood relaxation was needed. Status and UI text are exact checks. Null PI absence is checked explicitly. Counts include repeated per-study checks under each configuration, matched refusals and UI checks; they are not counts of independent estimates.

| Quantity | Original pass/checks | Original max difference | Patched pass/checks | Patched max difference | Tolerance |
|---|---:|---:|---:|---:|---|
| status | 2160/2160 | 0 | 2160/2160 | 0 | [0] |
| mu_re | 1962/1962 | 1.440785877150696e-15 | 1962/1962 | 1.440785877150696e-15 | [1e-09, 1e-06] |
| seRE | 1962/1962 | 6.106226635438361e-16 | 1962/1962 | 6.106226635438361e-16 | [1e-09, 1e-06] |
| tau2 | 1962/1962 | 4.5303204736917725e-15 | 1962/1962 | 4.5303204736917725e-15 | [1e-09, 1e-06] |
| Q | 1962/1962 | 2.3141067508736556e-14 | 1962/1962 | 2.3141067508736556e-14 | [1e-09] |
| df | 1962/1962 | 0 | 1962/1962 | 0 | [1e-09] |
| i2 | 1962/1962 | 2.1005438652314009e-14 | 1962/1962 | 2.1005438652314009e-14 | [1e-09] |
| k | 1962/1962 | 0 | 1962/1962 | 0 | [1e-09] |
| lo | 1962/1962 | 1.4184638608631378e-15 | 1962/1962 | 1.4184638608631378e-15 | [1e-09, 1e-06] |
| hi | 1962/1962 | 1.4638216782346601e-15 | 1962/1962 | 1.4638216782346601e-15 | [1e-09, 1e-06] |
| piLo | 1962/1962 | 1.9340085088970227e-13 | 1962/1962 | 1.9340085088970227e-13 | [1e-09, 1e-06] |
| piHi | 1962/1962 | 3.6326497365735122e-13 | 1962/1962 | 3.6326497365735122e-13 | [1e-09, 1e-06] |
| poolP | 1962/1962 | 3.6637359812630166e-15 | 1962/1962 | 3.6637359812630166e-15 | [1e-09, 1e-06] |
| poolLo | 1954/1962 | 0.0040907694850491061 | 1962/1962 | 1.4432899320127035e-15 | [1e-09, 1e-06] |
| poolHi | 1962/1962 | 2.2204460492503131e-15 | 1962/1962 | 2.2204460492503131e-15 | [1e-09, 1e-06] |
| poolPiLo | 1817/1962 | 0.32734291565423357 | 1962/1962 | 7.7271522513910895e-14 | [1e-09, 1e-06] |
| poolPiHi | 1948/1962 | 0.18396796721055675 | 1962/1962 | 8.8762330818781265e-14 | [1e-09, 1e-06] |
| yi | 42786/42786 | 2.1820096582259427e-16 | 42786/42786 | 2.1820096582259427e-16 | [1e-09] |
| vi | 42786/42786 | 0 | 42786/42786 | 0 | [1e-09] |
| study_lo | 14904/42786 | 4.4494902207148357e-09 | 42786/42786 | 1.2542744620702706e-12 | [1e-09] |
| study_hi | 10746/42786 | 4.2376748776717932e-09 | 42786/42786 | 1.2484457911909885e-12 | [1e-09] |
| study_rel | 42786/42786 | 4.0036760827818629e-11 | 42786/42786 | 4.0036760827818629e-11 | [1e-09, 1e-06] |
| study_p | 42786/42786 | 0 | 42786/42786 | 0 | [1e-09] |
| ui_row_count | 1962/1962 | 0 | 1962/1962 | 0 | [0] |
| ui_forest_diamond | 1962/1962 | 0 | 1962/1962 | 0 | [0] |
| ui_pooled_text | 1961/1962 | 1 | 1962/1962 | 0 | [0] |
| ui_prediction_text | 1847/1962 | 1 | 1962/1962 | 0 | [0] |

## Secondary meta comparison

`meta::metaprop(method="Inverse",method.incr="only0",incr=.5,method.random.ci="classic",method.ci="CP")` was run for every configuration, with the same refusal rule. Source inspection confirms meta 8.5.0 uses the same half-sum PFT scale as the page and metafor; no scaling adjustment is used. FE uses the common-effect estimate, PM/DL the random-effect estimate. This secondary comparison covers pooled transformed mean, SE and tau2; full CI/PI and per-study validation is supplied by the primary metafor comparison. `meta-reference.json` is the clean final full run; earlier initial/refinement artifacts are diagnostic only.

Native meta PRAW intentionally differs at boundary counts: `metaprop-source.txt:377-380` retains TE=event/n while correcting its variance. The page (`index.html:335-348`) and metafor PR correct both yi and vi. All remaining secondary mismatches are raw configurations containing boundary counts; these are recorded convention differences, not app defects, and the patch does not change the app to disagree with its declared metafor convention. Logit and PFT agree with native meta. The initial secondary harness incorrectly rescaled PFT; source inspection corrected that harness assumption before the final full rerun. That initial run also emitted a trailing parse error after writing its output because the runner file was edited while executing; the clean final rerun supersedes it.

| Quantity | Pass/checks | Maximum difference |
|---|---:|---:|
| status | 2160/2160 | 0 |
| mu_re | 1683/1962 | 0.047597465602425171 |
| seRE | 1794/1962 | 0.011904168932765857 |
| tau2 | 1795/1962 | 0.019598765987104649 |

## Static versus dynamic disclosure

| Component | Static or dynamic | Source |
|---|---|---|
| Column mappings, arm/outcome splitting | Static specification | reference.R and checked packaged manuals |
| Method options, tolerances, domain fix | Static algorithm/configuration | Actual page/core and comparison scripts |
| Observations and exclusions | Dynamic | Installed metadat data, corpus.json, row-audit.json |
| Reference estimates and warnings | Dynamic | Executed R/metafor/meta |
| App estimates and rendered output | Dynamic | Executed original/patched Chrome pages |
| Counts, maxima and tables | Dynamic | compare.py / compare-meta.py / write-report.py |

## Commands run

Commands below were executed in this job folder. The two R reference precision refinements are described above; final outputs use the final source. No packages were installed and no network was used.

```powershell
git -C <ALLMETA_ROOT> rev-parse HEAD
$env:R_LIBS_USER='../re/Rlib_dta'
Rscript inventory.R
Rscript reference.R
$env:PLAYWRIGHT_PATH='<ALLMETA_ROOT>/hub/shared/tests/node_modules/playwright'
node run-app.cjs original app.json
python compare.py app.json original
python make-patch.py
node run-app.cjs patched app-patched.json
python compare.py app-patched.json patched
python prepare-meta.py
Rscript secondary-meta.R
Rscript secondary-meta.R --refine
python merge-meta.py
Rscript secondary-meta.R # clean final full rerun after harness corrections
python evidence.py <ALLMETA_ROOT>
Rscript catalogue-check.R
git apply --check --directory=original fix.patch
python final-checks.py
python write-report.py
```

`original/` was populated by copying proportion-ma/index.html, shared/, hub/app-style.css, and hub/shared JS plus glossary.json from the read-only source. `make-patch.py` creates `patched/` from that snapshot. Run `reference.R` before the browser harness to generate the corpus. For a clean full meta rerun, `prepare-meta.py` now includes empty analyses; the refinement is harmless and records the same final settings.

Verbatim terminal final lines (full final comparison output is in the corresponding `*-console.txt`):

```text
2160 reference configurations written
2160 app configurations written; 0 page errors
2160 app configurations written; 0 page errors
2160 meta reference configurations written
237911/298116 checks pass
298116/298116 checks pass
7432/8046 checks pass
Final validation PASS (primary); secondary raw-boundary convention differences documented
```

## Dataset decisions

All catalogue entries are listed below. The exact per-analysis event/denominator expression, group, retained row count and boundary coverage follow in `DATASETS.md`; full source-column descriptions are in `schema-evidence.json`.

| Dataset | Decision | Analyses | Reason |
|---|---|---:|---|
| dat.aloe2013 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.anand1999 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.anker2025 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.assink2016 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.axfors2021 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.bakdash2021 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.baker2009 | used | 8 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.bangertdrowns2004 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.bartos2023 | used | 3 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.baskerville2012 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.bassler2004 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.bauer2002 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.bcg | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.begg1989 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.berkey1998 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.berkey1998r | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.besson2016 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.bonett2010 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.bornmann2007 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.bourassa1996 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.cannon2006 | used | 12 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.chiarito2020 | used | 8 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.cohen1981 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.colditz1994 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.collins1985a | used | 6 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.collins1985b | used | 8 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.craft2003 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.crede2010 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.crisafulli2020 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.curtin2002 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.curtis1998 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.dagostino1998 | used | 16 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.damico2009 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.debruin2009 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.demir2022 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.dogliotti2014 | used | 8 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.dong2013 | used | 6 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.dorn2007 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.dumouchel1994 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.egger2001 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.feng2019 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.fine1993 | used | 8 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.franchini2012 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.frank2008 | used | 6 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.furukawa2003 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.gibson2002 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.graves2010 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.greb2008 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.greenland1992 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.gurusamy2011 | used | 7 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hackshaw1998 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.hahn2001 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hannum2020 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hart1999 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hartmannboyce2018 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hasselblad1998 | used | 4 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.higgins2008 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.hine1989 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.huber2000 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.ishak2007 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.kalaian1996 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.karner2014 | used | 12 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.kearon1998 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.knapp2017 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.konstantopoulos2011 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.landenberger2005 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.laopaiboon2015 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.lau1992 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.lee2004 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.lehmann2018 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.li2007 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.lim2014 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.linde2005 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.linde2015 | used | 15 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.linde2016 | used | 22 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.lloyd2010 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.lopez2019 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.maire2019 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.mccurdy2020 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.mcdaniel1994 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.meeker2017 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.metap | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.michael2013 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.molloy2014 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.moore1998 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.moura2021 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.nakagawa2007 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.nielweise2007 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.nielweise2008 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.nissen2007 | used | 4 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.normand1999 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.obrien2003 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.pagliaro1992 | used | 3 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.pignon2000 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.poole2003 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.pritz1997 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.quan2000 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.raudenbush1985 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.riley2003 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.rivera2025 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.roever2022 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.senn2013 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.spooner2002 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.steurer2006 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.stowe2010 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.tannersmith2016 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.thompson1999 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.tian2009 | used | 4 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.ursino2021 | used | 1 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.vanhowe1999 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.viechtbauer2021 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.white2020 | excluded | 0 | No documented binomial event-count / denominator pair (continuous, correlation, effect-only, rate-only, or non-count nested data) |
| dat.woods2010 | used | 4 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
| dat.yusuf1985 | used | 2 | Documented event counts and totals; each arm/outcome separate; see mappings and source manual |
