"""Preserve prior run outputs before staging fresh observations; never delete them."""
from pathlib import Path

TARGETS = (
    "original", "plus",
    "original-browser.json", "original-live.json", "original-transport.json",
    "original-compare.log", "original-r.log", "plus-runtime.log",
    "extras-offline.json", "extras-transport.json",
    "glmm-browser-comparison.json", "glmm-browser-results.json",
    "live-plus-transport.json",
)

def preserve(root):
    root = Path(root).resolve()
    scratch = root / "rerun"
    if not scratch.exists():
        print("PRESERVED: no previous scratch outputs")
        return []
    if scratch.resolve() != scratch or scratch.is_symlink() or scratch.is_junction():
        raise ValueError("Refusing a redirected rerun directory")
    existing = [scratch / name for name in TARGETS if (scratch / name).exists()]
    for source in existing:
        if source.is_symlink() or source.is_junction() or source.resolve().parent != scratch:
            raise ValueError("Refusing a redirected output: " + source.name)
    attempt = 1
    while any((scratch / (name + ".prev-" + str(attempt))).exists() for name in TARGETS):
        attempt += 1
    pairs = [(source, source.with_name(source.name + ".prev-" + str(attempt)))
             for source in existing]
    # Validate every final source/destination before moving any directory.
    for source, target in pairs:
        if target.resolve().parent != scratch or target.exists():
            raise ValueError("Unsafe backup destination: " + target.name)
    for source, target in pairs:
        source.rename(target)
        print("PRESERVED: " + source.name + " -> " + target.name)
    if not pairs:
        print("PRESERVED: no previous scratch outputs")
    return pairs

if __name__ == "__main__":
    preserve(Path(__file__).resolve().parents[1])
