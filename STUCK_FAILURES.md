# Finalization verification status

The release run on 2026-10-20 for allmeta 1cb3f84 completed with RUN_EXIT 0, including ARCHIVE PASS; see provenance/run_plan-2026-10-20-release.log. The 27 documented cross-runtime failures remain failures.

Exact Git blob identity was verified on 2026-11-03 (archive v1.2.0): `analysis/finalize_blobs.py` printed `BLOB PASS 99/99` against allmeta 1cb3f84, followed by RECUT INTEGRITY PASS and ARCHIVE PASS; logs are in provenance/v1.2.0-verification/. This supersedes the earlier statement that blob identity was unverified and required the human runner to execute FINAL_BLOBS.cmd. This is a hash-identity result only; numerical and browser reruns are the separate 2026-10-20 release run. Remaining notes are recorded in RECUT_NOTES.md. No Overmind certification is claimed.
