"""Portable scratch wrappers; originals, reference JSON and tolerances stay immutable."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from recut_integrity import ROOT, digest, read, verify_pins

SCRATCH = ROOT/"rerun"
PLUS = SCRATCH/"plus/proportion-ma"
def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
def stage():
    verify_pins()
    SCRATCH.mkdir(exist_ok=True)
    shutil.copytree(ROOT/"app/proportion-ma", PLUS, dirs_exist_ok=True)
    for name in read(ROOT/"RECUT_PROVENANCE.json")["validation_plus_source_sha256"]:
        target = PLUS/"validate"/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/"validation-plus"/name, target)
    script = (PLUS/"validate/check-plus.mjs").read_text(encoding="utf-8")
    start = script.index("const base=execFileSync(")
    end = script.index("// Generate native-R input", start)
    # Git history belongs to allmeta, not this standalone archive. Replace only
    # the historical git block in this scratch wrapper with pinned-byte checks.
    pinned = {}
    for p in PLUS.rglob("*"):
        if p.is_file() and p.suffix != ".R" and p.name != "check-plus.archive.mjs":
            rel = p.relative_to(PLUS).as_posix()
            if rel in {"index.html","plus-core.js","plus-parity.js","validate/MANIFEST.json","validate/corpus/corpus.json","validate/corpus/reference.json"}:
                pinned[rel] = digest(p)
    replacement = "const archivePins="+json.dumps(pinned,sort_keys=True)+";\n"
    replacement += "for(const [p,sha] of Object.entries(archivePins)) assert.equal(createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),sha,'Archived candidate byte pin: '+p);\n"
    script = script[:start]+replacement+script[end:]
    script = script.replace("import {execFileSync} from 'node:child_process';\n", "")
    script = script.replace("originalPage:'unchanged except extras'", "originalPage:'candidate SHA-256 pins; historical git assertion not run'")
    script += "\nconsole.log('EXTRAS NATIVE PAIRS: '+checks+'/'+checks+' checks pass');\n"
    script = script.replace("console.log(JSON.stringify({runtimeConfigurations:", "assert.equal(runtimeChecks,4352); console.log('EXTRAS NATIVE SCRIPT: '+runtimeChecks+'/'+runtimeChecks+' checks pass');\n console.log(JSON.stringify({runtimeConfigurations:")
    put(PLUS/"validate/check-plus.archive.mjs", script)
    # Original R validation is run against fresh current-page observations.
    original = SCRATCH/"original"
    for rel in ["validate.R","data/corpus.json"]:
        target = original/rel; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/rel,target)
    (original/"results").mkdir(exist_ok=True)
    (original/"results/app-patched.json").unlink(missing_ok=True)
    shutil.copyfile(ROOT/"results/reference.json", original/"reference.json")
    # Prepend native library priority without editing the generated browser script.
    put(PLUS/"validate/run-native-plus.R",
        "userlib <- Sys.getenv('R_LIBS_USER')\n"
        "if(nzchar(userlib)) .libPaths(c(strsplit(userlib,.Platform$path.sep,fixed=TRUE)[[1]],.libPaths()))\n"
        "source('runtime-plus.R', chdir=FALSE)\n")
    print("STAGED: immutable originals copied to rerun/; candidate byte pins replace allmeta-only git history assertions in check-plus.archive.mjs.")
def run_logged(command, cwd, name):
    log = SCRATCH/name
    log.parent.mkdir(exist_ok=True)
    with log.open("wb") as output:
        result = subprocess.run(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT)
    sys.stdout.write(log.read_bytes().decode("utf-8", errors="replace"))
    print("Log:", log.relative_to(ROOT).as_posix(), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["stage","compare-original","original-r","plus-r","generate-plus"])
    action=parser.parse_args().action
    if action=="stage":
        stage(); return
    verify_pins()
    if action=="compare-original":
        observed=SCRATCH/"original/results/app-patched.json"
        assert observed.is_file(), "Run the current-page browser replay first"
        run_logged([sys.executable,str(ROOT/"bench/compare.py"),"results/app-patched.json","current"],SCRATCH/"original","original-compare.log")
        result=read(SCRATCH/"original/current-results.json")
        assert result["checks"]==result["passed"]==298116 and result["failed"]==0
        print("CURRENT ORIGINAL: 298116/298116 checks pass")
    elif action=="original-r":
        assert (SCRATCH/"original/results/app-patched.json").is_file(), "Fresh browser output required"
        run_logged(["Rscript","validate.R"],SCRATCH/"original","original-r.log")
    elif action=="plus-r":
        assert (PLUS/"validate/runtime-plus.R").is_file(), "Run check-plus.archive.mjs --write-r first"
        run_logged(["Rscript","run-native-plus.R"],PLUS/"validate","plus-runtime.log")
    else:
        # Optional source-package regeneration in a separate directory.
        target=SCRATCH/"regenerated-plus"
        shutil.copytree(PLUS/"validate",target,dirs_exist_ok=True)
        put(target/"run-generate.R",
            "userlib <- Sys.getenv('R_LIBS_USER')\n"
            "if(nzchar(userlib)) .libPaths(c(strsplit(userlib,.Platform$path.sep,fixed=TRUE)[[1]],.libPaths()))\n"
            "source('generate-plus.R', chdir=FALSE)\n")
        run_logged(["Rscript","run-generate.R"],target,"plus-regeneration.log")
if __name__=="__main__":
    main()
