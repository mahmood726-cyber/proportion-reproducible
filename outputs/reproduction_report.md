# Reproduction report

All findings recomputed from input/result records; expected values are assertions.

| Claim | Expected | Reproduced | Verdict |
|---|---|---|---|
| datasets_enumerated | 114 | 114 | PASS |
| datasets_used | 62 | 62 | PASS |
| datasets_excluded | 52 | 52 | PASS |
| analyses | 240 | 240 | PASS |
| rows | 4768 | 4768 | PASS |
| zero_event_rows | 478 | 478 | PASS |
| all_event_rows | 23 | 23 | PASS |
| configurations | 2160 | 2160 | PASS |
| successful | 1962 | 1962 | PASS |
| refusals | 198 | 198 | PASS |
| checks | 298116 | 298116 | PASS |
| passed | 298116 | 298116 | PASS |
| before_passed | 237911 | 237911 | PASS |
| meta_checks | 8046 | 8046 | PASS |
| meta_passed | 7432 | 7432 | PASS |

Figures: 300 dpi, 170 mm nominal width, text >=8 pt. Figure 2 shows per-quantity maxima; red crosses mark before-fix results and annotations identify failures. Exact status/UI checks are in Table 1. Table 2 includes all catalogue entries, with zero counts for excluded datasets.

This command rechecks archived app/R records; validate.R recomputes R numerical fits and replays archived DOM evidence. No clinical interpretation, GLMM validation, deployment or Overmind certification is implied.

PASS: 15/15 paper-value assertions; 298116/298116 final checks; 237911/298116 before fixes.
