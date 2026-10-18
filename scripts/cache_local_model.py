"""Reference an existing pinned model in JevalKit's offline cache; never move its weights."""
import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jevalkit.io import atomic_json, sha256
from jevalkit.paths import data_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--ref", action="append", default=[], help="Additional exact aliases needed by an author runtime")
    parser.add_argument("--root")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo) or not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        raise ValueError("Require a Hub repo ID and an exact 40-character commit")
    if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", ref) or ref in {".", ".."} for ref in args.ref):
        raise ValueError("Cache refs must be simple Hub aliases")
    source = args.source.resolve(strict=True)
    manifest = source / "download_manifest.json"
    if manifest.exists():
        info = json.loads(manifest.read_text())
        if info.get("repo") != args.repo or info.get("revision") != args.revision:
            raise ValueError("Existing checkpoint manifest differs from the requested Hub identity")
    manifest = source / "jevalkit-download.json"
    if manifest.exists():
        info = json.loads(manifest.read_text())
        if info.get("model") != args.repo or info.get("revision") != args.revision:
            raise ValueError("Verified download identity differs from the requested Hub identity")
    repo_cache = data_root(args.root) / "cache" / "hf" / "hub" / ("models--" + args.repo.replace("/", "--"))
    destination = repo_cache / "snapshots" / args.revision
    destination.mkdir(parents=True, exist_ok=True)
    files = {}
    for path in source.rglob("*"):
        if not path.is_file() or {".git", ".cache"}.intersection(path.parts):
            continue
        if path.name.startswith(("download_", "verification", "jevalkit-")) or path.suffix not in {".json", ".py", ".safetensors", ".pt", ".bin", ".txt", ".jinja", ".model", ".tiktoken"}:
            continue
        relative = path.relative_to(source)
        target = destination / relative
        fingerprint = sha256(path)
        if target.exists():
            if sha256(target) != fingerprint:
                raise ValueError("Refusing to overwrite conflicting cached file: " + str(target))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(path)
        files[str(relative)] = {"source": str(path), "sha256": fingerprint, "bytes": path.stat().st_size,
                                "ownership": "borrowed; never delete source"}
    atomic_json(destination / "jevalkit-borrowed-weights.json", files)
    (repo_cache / "refs").mkdir(exist_ok=True)
    for ref in {"main", *args.ref}:
        target = repo_cache / "refs" / ref
        if target.exists() and target.read_text().strip() != args.revision:
            raise ValueError("Refusing to repoint a conflicting offline Hub ref: " + str(target))
        temporary = target.with_name(target.name + ".tmp")
        temporary.write_text(args.revision)
        temporary.replace(target)
    print(json.dumps({"cache": str(destination), "files": len(files), "source_unchanged": True}), flush=True)


if __name__ == "__main__":
    main()
