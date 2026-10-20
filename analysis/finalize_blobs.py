"""Restore exact upstream blobs; run with Git available on the human runner."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

COMMIT = "1cb3f8409c7af75ed41f7e1811f9c502f900fc79"

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")

def checked_path(root, name):
    path = PurePosixPath(name)
    if not name or "\\" in name or path.is_absolute() or any(p in {"..", ".git"} or ":" in p for p in path.parts):
        raise ValueError("Unsafe copy-map path")
    target = root.joinpath(*path.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("Copy-map path escapes root")
    # Refuse symlink/junction paths, even when they currently resolve inside root.
    for part in [target, *target.parents]:
        if part == root.parent:
            break
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError("Redirected copy-map path")
    return target

def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def finalize(archive, upstream, map_path):
    archive, upstream = archive.resolve(), upstream.resolve()
    mapping = json.loads(map_path.read_text(encoding="utf-8"))
    provenance_path = archive / "RECUT_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    expected = {
        **{"app/" + n: n for n in provenance["candidate_app_sha256"]},
        **{"validation-plus/" + n: "proportion-ma/validate/" + n
           for n in provenance["validation_plus_source_sha256"]},
    }
    if not isinstance(mapping, list) or len(mapping) != len(expected):
        raise ValueError("Copy map does not cover exactly the pinned upstream files")
    observed = {}
    for entry in mapping:
        if set(entry) != {"archive_path", "allmeta_path"}:
            raise ValueError("Unexpected copy-map fields")
        dst, src = entry["archive_path"], entry["allmeta_path"]
        checked_path(archive, dst)
        checked_path(upstream, src)
        if dst in observed:
            raise ValueError("Duplicate archive path")
        observed[dst] = src
    if observed != expected:
        raise ValueError("Copy map differs from provenance")
    if git(upstream, "rev-parse", "1cb3f84^{commit}").decode("ascii").strip() != COMMIT:
        raise ValueError("Short release revision does not resolve to expected commit")
    # Read every blob before writing any destination. Never decode binary payloads.
    blobs = {}
    for dst, src in observed.items():
        blobs[dst] = git(upstream, "cat-file", "blob", "1cb3f84:" + src)
    # Finalization may only remove checkout line-ending conversion. Any upstream
    # content difference needs a new review and must not silently repin references.
    for dst, raw in blobs.items():
        prior = checked_path(archive, dst).read_bytes()
        if prior != raw and prior.replace(b"\r\n", b"\n") != raw:
            raise ValueError("Unexpected content difference: " + dst)
    for dst, raw in blobs.items():
        checked_path(archive, dst).write_bytes(raw)
    for dst, raw in blobs.items():
        if checked_path(archive, dst).read_bytes() != raw:
            raise ValueError("Written blob mismatch: " + dst)
    print(f"BLOB PASS {len(blobs)}/{len(blobs)}", flush=True)
    provenance["candidate_app_sha256"] = {
        n: digest(blobs["app/" + n]) for n in provenance["candidate_app_sha256"]}
    provenance["validation_plus_source_sha256"] = {
        n: digest(blobs["validation-plus/" + n]) for n in provenance["validation_plus_source_sha256"]}
    provenance["blob_identity"] = {
        "status": "PASS", "commit": COMMIT, "copy_map": "COPY_MAP.json",
        "verified_files": len(blobs),
        "method": "git cat-file blob; binary byte-for-byte verification",
        "sha256": {n: digest(raw) for n, raw in sorted(blobs.items())}}
    provenance["status"] = (
        "Release run completed on 2026-10-20, RUN_EXIT 0; exact Git blob copies "
        "verified. See provenance/release-run.json; runtime evidence used the "
        "pre-finalization checkout. Final manifest checks must also pass.")
    dump(provenance_path, provenance)
    for name in ["refresh_manifests.py", "recut_integrity.py", "verify_archive.py"]:
        print("=== " + name, flush=True)
        subprocess.run([sys.executable, "-X", "utf8", str(archive / "analysis" / name)],
                       cwd=archive, check=True)
    print("FINAL BLOBS AND MANIFESTS PASS", flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--allmeta", type=Path, required=True)
    parser.add_argument("--copy-map", type=Path, required=True)
    args = parser.parse_args()
    finalize(args.archive, args.allmeta, args.copy_map)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        # Do not echo subprocess output or absolute local paths into release logs.
        print("FINAL BLOBS FAILED: " + type(exc).__name__, file=sys.stderr)
        sys.exit(1)
