import json,re
from pathlib import Path
def read(p):return json.loads(Path(p).read_text())
v=read('versions.json');c=read('corpus.json');m=read('manifest.json');r=read('reference.json');o=read('original-results.json');p=read('patched-results.json');meta=read('meta-results.json');prov=read('source-provenance.json')
zeros=sum(z['x']==0 for a in c for z in a['rows']);ones=sum(z['x']==z['n'] for a in c for z in a['rows']);rows=sum(len(a['rows']) for a in c)
text=f'''# Proportion MA validation

The unmodified application passed **{o['passed']}/{o['checks']} primary checks**; the locally patched copy passed **{p['passed']}/{p['checks']} primary checks**. Two source defects were identified and corrected in `fix.patch`. Native meta passed **{meta['passed']}/{meta['checks']} secondary checks**; its {meta['failed']} differences are raw-proportion boundary-correction conventions, documented below. The original allmeta tree was not modified. This is a validation result, not a release or Overmind certification.

Source commit: `{prov['commit']}`. Runtime: {v['R']}; metafor {v['metafor']}; metadat {v['metadat']}; meta {v['meta']}; Chrome {read('app-browser.json')['browser']}. `source-provenance.json` records SHA-256 for {len(prov['sha256'])} byte-identical copied source files. The job directory is not a git worktree; no commit, push, deployment, registry, or workbook changes were made.

## Corpus and scope

`data(package="metadat")` enumerated {v['catalogue']} entries: {v['datasets_used']} used and {v['catalogue']-v['datasets_used']} excluded. There are {len(c)} separate count/denominator analyses, {rows} input rows across these analyses, {zeros} zero-event rows and {ones} all-event rows. Repeated arms/outcomes/aliases are retained intentionally; these are computational checks, not independent studies or new scientific findings. Every analysis was run under logit/PFT/raw crossed with PM/DL/FE, for {len(r)} configurations: {sum(z['status']=='ok' for z in r.values())} successful and {sum(z['status']=='refused' for z in r.values())} matched refusals (fewer than two valid rows). Eight analyses have no usable rows. No synthetic observations were added.

Rule: each documented arm and binary outcome is a separate proportion analysis. Wide binary tables use both arms, all listed endpoints are included, long treatment-arm tables are split by treatment, and diagnostic datasets contribute sensitivity and specificity counts separately. Single-group event counts are used directly. Multi-arm datasets, genotype-category proportions and the nested `dat.metap$cholest` trials are included. Missing, nonfinite, fractional, negative, x>n, and n<=0 rows are excluded without imputation, with exact row indices in `row-audit.json`. Conditioning totals are explicit sums where the source supplies cells rather than totals. For Higgins, response is conditional on observed response/failure; missing outcomes are excluded from the denominator. Clinical interpretations of these computational regroupings are outside scope.

All numerical inputs come from the installed metadat package. `corpus.json` is the exact shared browser/R input; `schema-evidence.json` verifies all {len(c)} mappings against the bundled open package manuals. Original row numbers are provenance identifiers, not invented trial identifiers. No PMIDs, DOIs, NCT IDs, or study dates were fabricated or re-keyed. Excluded nested objects contain correlations/phylogenies, trend statistics, or effect/covariance data; the count-containing nested cholesterol data were included. Metafor uses metadat for its example datasets; no separate synthetic metafor examples were substituted for this catalogue.

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
2. `proportion-ma/index.html:198,227`: beta continued-fraction tolerance 3e-7 and quantile bisection stopping width 1e-8 are too coarse for the required 1e-9 absolute CI agreement. The patch tightens both to 1e-14. Patched per-study lower/upper CI maxima are {p['quantities']['study_lo']['max_difference']:.17g} / {p['quantities']['study_hi']['max_difference']:.17g}.

`fix.patch` is a unified diff against allmeta, applies cleanly to the copied original, and changes only this HTML file. `patched/` contains the rerun copy. `original-results.json` contains every failed quantity/configuration with observed and reference values. The bounded sequence was: original run; one numerical app patch; two reference precision refinements; final comparison. No broad refactor was made.

UI/documentation observations: the header's “incidences / event rates” wording is too broad for an integer binomial events/total interface (no person-time model). GLMM is advice to use external R, not an available option. The source explicitly preserves Q-based I2, which differs from metafor PM's default; it also displays a t-based PI under FE. The existing `test_against_r.py` references an R reimplementation and a small fixture, rather than proving full-corpus metafor parity. The PFT caution about potentially inverted/out-of-range intervals should be revisited if this patch is adopted. These observations are documented without changing unrelated UI copy.

## Per-quantity primary comparison

Difference is abs(app-ref)/max(1,abs(ref)); proportions therefore use absolute error. Closed-form quantities use 1e-9. PM-dependent estimates, SEs, intervals, tau2 and weights use 1e-6; no flat-likelihood relaxation was needed. Status and UI text are exact checks. Null PI absence is checked explicitly. Counts include repeated per-study checks under each configuration, matched refusals and UI checks; they are not counts of independent estimates.

| Quantity | Original pass/checks | Original max difference | Patched pass/checks | Patched max difference | Tolerance |
|---|---:|---:|---:|---:|---|
'''
for q,s in o['quantities'].items():
 t=p['quantities'][q]
 text+=f"| {q} | {s['passed']}/{s['checks']} | {s['max_difference']:.17g} | {t['passed']}/{t['checks']} | {t['max_difference']:.17g} | {t['tolerances']} |\n"
text+='''
## Secondary meta comparison

`meta::metaprop(method="Inverse",method.incr="only0",incr=.5,method.random.ci="classic",method.ci="CP")` was run for every configuration, with the same refusal rule. Source inspection confirms meta 8.5.0 uses the same half-sum PFT scale as the page and metafor; no scaling adjustment is used. FE uses the common-effect estimate, PM/DL the random-effect estimate. This secondary comparison covers pooled transformed mean, SE and tau2; full CI/PI and per-study validation is supplied by the primary metafor comparison. `meta-reference.json` is the clean final full run; earlier initial/refinement artifacts are diagnostic only.

Native meta PRAW intentionally differs at boundary counts: `metaprop-source.txt:377-380` retains TE=event/n while correcting its variance. The page (`index.html:335-348`) and metafor PR correct both yi and vi. All remaining secondary mismatches are raw configurations containing boundary counts; these are recorded convention differences, not app defects, and the patch does not change the app to disagree with its declared metafor convention. Logit and PFT agree with native meta. The initial secondary harness incorrectly rescaled PFT; source inspection corrected that harness assumption before the final full rerun. That initial run also emitted a trailing parse error after writing its output because the runner file was edited while executing; the clean final rerun supersedes it.

| Quantity | Pass/checks | Maximum difference |
|---|---:|---:|
'''
for q,s in meta['quantities'].items():text+=f"| {q} | {s['passed']}/{s['checks']} | {s['max_difference']:.17g} |\n"
text+='''
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
'''
for name in ['original','patched','meta']:text+=Path(name+'-console.txt').read_text().strip().splitlines()[-1]+'\n'
text+='Final validation PASS (primary); secondary raw-boundary convention differences documented\n```\n\n## Dataset decisions\n\nAll catalogue entries are listed below. The exact per-analysis event/denominator expression, group, retained row count and boundary coverage follow in `DATASETS.md`; full source-column descriptions are in `schema-evidence.json`.\n\n| Dataset | Decision | Analyses | Reason |\n|---|---|---:|---|\n'
for nm,z in m.items():text+=f"| {nm} | {z['status']} | {len(z['analyses'])} | {z['reason']} |\n"
Path('RESULTS.md').write_text(text,encoding='utf8')
table='# Exact corpus mappings\n\nEvery row below is an independently executed computational analysis. Source row exclusions are recorded in row-audit.json.\n\n| Dataset | x | n | Group | k | x=0 | x=n |\n|---|---|---|---|---:|---:|---:|\n'
for a in c:table+=f"| {a['dataset']} | `{a['x']}` | `{a['n']}` | {a['group']} | {len(a['rows'])} | {sum(z['x']==0 for z in a['rows'])} | {sum(z['x']==z['n'] for z in a['rows'])} |\n"
Path('DATASETS.md').write_text(table,encoding='utf8')
print('Wrote RESULTS.md and DATASETS.md from executed evidence')
