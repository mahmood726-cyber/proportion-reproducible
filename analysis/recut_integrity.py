"""Standard-library integrity gate; does not certify numerical/runtime parity."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "__pycache__", "node_modules", "outputs", "rerun"}
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def source_files():
    evidence = list((ROOT/"rerun/v1.1.0").rglob("*"))
    return sorted([p for p in evidence if p.is_file()] + [p for p in ROOT.rglob("*") if p.is_file()
                  and p.name not in {"SOURCE_SHA256.json", "PROGRESS.md"}
                  and not any(x in EXCLUDED or x.startswith(".verify-")
                              for x in p.relative_to(ROOT).parts)])
def inventory():
    return {p.relative_to(ROOT).as_posix(): digest(p) for p in source_files()}
def app_inventory():
    return {p.relative_to(ROOT/"app").as_posix(): digest(p)
            for p in sorted((ROOT/"app").rglob("*"))
            if p.is_file() and p.name != "app-sha256.json"}
def verify_pins():
    provenance = read(ROOT/"RECUT_PROVENANCE.json")
    for name, expected in read(ROOT/"ORIGINAL_SHA256.json").items():
        assert digest(ROOT/name) == expected, "Protected original changed: "+name
    assert app_inventory() == provenance["candidate_app_sha256"], "Candidate app bytes drifted"
    for name, expected in provenance["validation_plus_source_sha256"].items():
        assert digest(ROOT/"validation-plus"/name) == expected, "Copied extras drifted: "+name
    for name in ["MANIFEST.json", "MANIFEST-plus.json"]:
        for f in read(ROOT/"app/proportion-ma/validate"/name)["files"]:
            p = ROOT/"app/proportion-ma"/f["path"]
            assert p.stat().st_size == f["bytes"] and digest(p) == f["sha256"], f["path"]
            assert b"\r" not in p.read_bytes(), "Pinned input must be LF bytes"
    for f in read(ROOT/"validation-plus/MANIFEST-plus.json")["files"]:
        p = ROOT/"validation-plus"/Path(f["path"]).relative_to("validate")
        assert p.stat().st_size == f["bytes"] and digest(p) == f["sha256"]
    for name in ["corpus.json", "reference.json"]:
        source = ROOT/("data" if name=="corpus.json" else "results")/name
        assert (ROOT/"app/proportion-ma/validate/corpus"/name).read_bytes() == source.read_bytes().replace(b"\r\n", b"\n")
    assert read(ROOT/"validation-plus/plus-corpus/corpus.json") == read(ROOT/"data/corpus.json")
    wr = ROOT/"app/r-shiny/shinylive/webr"
    manifest = read(wr/"repo/manifest.json")
    packages = {p["package"]:p for p in manifest["packages"]}
    seen = set()
    def visit(name):
        if name in seen:
            return
        seen.add(name)
        p = packages[name]
        target = wr/(p.get("path") or "repo/"+manifest["layout"]+p["file"])
        assert target.stat().st_size == p["bytes"] and digest(target) == p["sha256"], name
        for dep in p.get("dependencies", []):
            if dep in packages:
                visit(dep)
    for name in ["metafor", "lme4"]:
        visit(name)
    assert sorted(seen) == provenance["runtime_packages"]
    for edge in provenance["dependency_edges"]:
        assert (ROOT/"app"/edge["to"]).is_file(), edge
    for p in source_files():
        if p.suffix.lower() in {".json", ".js", ".mjs", ".cjs", ".py", ".r", ".md", ".csv", ".txt", ".html", ".cff", ".patch", ".css", ".cmd"}:
            raw = p.read_bytes()
            assert not raw.startswith(b"\xef\xbb\xbf"), "BOM: "+str(p)
            raw.decode("utf-8")
    z = read(ROOT/".zenodo.json")
    assert z["version"] == "1.1.0" and z["creators"] == [{"name":"Ahmad, Mahmood"}]
    relations = {(r["identifier"],r["relation"]) for r in z["related_identifiers"]}
    assert relations == {
        ("https://github.com/mahmood726-cyber/allmeta","isDerivedFrom"),
        ("10.5281/zenodo.23288388","isDerivedFrom"),
        (provenance["allmeta_doi"],"isDerivedFrom")}
    cff = (ROOT/"CITATION.cff").read_text(encoding="utf-8")
    assert re.search(r"^version: 1\.1\.0$", cff, re.M)
    assert re.search(r"^date-released: 2026-10-20$", cff, re.M)
    assert provenance["allmeta_commit"] in cff and provenance["allmeta_doi"] in cff
    assert "  - family-names: Ahmad\n    given-names: Mahmood\n" in cff
    return provenance
def refresh():
    verify_pins()
    def dump(path, value):
        path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    dump(ROOT/"app/app-sha256.json", app_inventory())
    dump(ROOT/"SOURCE_SHA256.json", inventory())
    print("REFRESHED: app/app-sha256.json and SOURCE_SHA256.json")
def main():
    p = verify_pins()
    assert read(ROOT/"app/app-sha256.json") == app_inventory(), "App manifest mismatch"
    assert read(ROOT/"SOURCE_SHA256.json") == inventory(), "Source inventory mismatch"
    print(f"RECUT INTEGRITY PASS: {len(app_inventory())} candidate app hashes; "
          f"{len(inventory())} source hashes; {len(read(ROOT/'ORIGINAL_SHA256.json'))} protected originals; "
          f"{len(p['validation_plus_source_sha256'])} verbatim extras; {len(p['runtime_packages'])} R package archives.")
    print("Numerical/browser reruns are separate; no runtime pass is inferred from hashes.")
if __name__ == "__main__":
    main()
