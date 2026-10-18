"""Acquire public evaluation splits and retain canonical TSVs plus source manifests."""
import copy
import hashlib
import json
import shutil
from pathlib import Path

from ..io import atomic_json, jsonl, sha256, write_tsv
from ..paths import data_root

JEV_REVISION = "bb05a335bc809e61b20c0f745d25499a82b326fc"
JEV_FILES = {
    "easy": (48, "231df3c2c8e88a1a8c137ebe85de96ba70fabd330849098ac7b3c52c70b7172b"),
    "original": (72, "5c2414edb3006b8bfcb70fda433f0f9ca015759433849f8d3104328a1f7c4180"),
    "hard": (111, "89e9e6becb33ed88c1de7d42dcc87531b2fb64cfaef4e1986faf7c37b3f80ebb"),
}


def commit_dataset(name, records, root, source, media_root=".", **extra):
    root = data_root(root)
    path = root / "datasets" / (name + ".tsv")
    manifest = {"schema_version": 1, "name": name, "source": source, "media_root": media_root,
                **extra, **write_tsv(path, records)}
    atomic_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def prepare_jevbench(root=None, source=None):
    root = data_root(root)
    raw = root / "raw" / "JevBench"
    raw.mkdir(parents=True, exist_ok=True)
    records = []
    for tier, (count, expected) in JEV_FILES.items():
        dest = raw / (tier + ".jsonl")
        if source:
            shutil.copyfile(Path(source) / "public" / dest.name, dest)
        elif not dest.exists():
            from urllib.request import urlopen
            url = f"https://raw.githubusercontent.com/fstandhartinger/jevbench/{JEV_REVISION}/datasets/public/{tier}.jsonl"
            with urlopen(url, timeout=60) as response:
                dest.write_bytes(response.read())
        if sha256(dest) != expected:
            raise ValueError("Frozen JevBench source checksum mismatch: " + tier)
        tasks = list(jsonl(dest))
        if len(tasks) != count:
            raise ValueError("JevBench source count mismatch")
        for task in tasks:
            q = {k: copy.deepcopy(v) for k, v in task["question"].items()
                 if k in {"type", "instructions", "criteria", "labels"}}
            records.append({"index": task["id"], "request": {"state": task["state"], "questions": {"decision": q}},
                            "targets": {"decision": {"label": task["expected"]}},
                            "meta": {"subset": tier, "domain": task["family"], "modality": "text",
                                     "group_id": task.get("group") or task["id"], "upstream_task": task}, "assets": []})
    return commit_dataset("JevBench", records, root,
                          {"repository": "https://github.com/fstandhartinger/jevbench", "revision": JEV_REVISION,
                           "license": "MIT", "public_only": True, "files": JEV_FILES},
                          protocol="public-231", official_scorer="jevalkit.datasets._jevbench")


def prepare_visual(root=None, source=None):
    root = data_root(root)
    if source is None:
        from huggingface_hub import snapshot_download
        source = snapshot_download("Valen-Team/VisualDecisionBench", repo_type="dataset",
                                   local_dir=root / "raw" / "VisualDecisionBench")
        from zipfile import ZipFile
        # Never execute the downloaded unpacking script.
        with ZipFile(Path(source) / "assets.zip") as archive:
            for info in archive.infolist():
                target = (Path(source) / info.filename).resolve()
                if not target.is_relative_to(Path(source).resolve()):
                    raise ValueError("Unsafe media archive path")
            archive.extractall(source)
    source = Path(source)
    media = root / "media" / "VisualDecisionBench"
    media.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / "assets", media / "assets", dirs_exist_ok=True)
    records = []
    for index, original in enumerate(jsonl(source / "eval.jsonl")):
        record = copy.deepcopy(original)
        meta = record.setdefault("meta", {})
        record["index"] = str(meta.get("benchmark_record_id", record.get("group_id", index)))
        meta["subset"] = meta.get("benchmark_subset", "unknown")
        records.append({k: record.get(k, [] if k == "assets" else {})
                        for k in ("index", "request", "targets", "meta", "assets")})
    origin = {"repository": "https://huggingface.co/datasets/Valen-Team/VisualDecisionBench",
              "local_source": str(source), "eval_jsonl_sha256": sha256(source / "eval.jsonl"),
              "source_manifest": json.loads((source / "source_manifest.json").read_text()),
              "license": "upstream datasets retain their own licenses"}
    results = [commit_dataset("VisualDecisionBench", records, root, origin,
                              media_root="../media/VisualDecisionBench", protocol="native-shared-state")]
    for subset in ("Image", "Video"):
        selected = [r for r in records if subset.lower() in r["meta"]["subset"].lower()]
        results.append(commit_dataset("VisualDecisionBench_" + subset, selected, root, origin,
                                      media_root="../media/VisualDecisionBench", protocol="native-shared-state"))
    return results


def install_digest_compat():
    """The pinned Decision Index kit uses Python 3.11's file_digest on Python 3.10."""
    if not hasattr(hashlib, "file_digest"):
        def file_digest(stream, algorithm):
            digest = hashlib.new(algorithm)
            for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                digest.update(chunk)
            return digest
        hashlib.file_digest = file_digest


def prepare_decision_index(root=None, source=None, edition="0.3"):
    install_digest_compat()
    from decision_index import editions
    from decision_index.suite.io import Suite
    root = data_root(root)
    folder = root / "raw" / ("DecisionIndex-" + edition)
    folder.mkdir(parents=True, exist_ok=True)
    if source:
        for name in editions.files(edition):
            shutil.copyfile(Path(source) / name, folder / name)
    else:
        from decision_index.suite.download import download
        download(folder, edition=edition)
    suite = Suite(folder, edition)
    checks = suite.verify(strict=True)
    if not checks.get("exclusions_match") or checks.get("subsets_match") is False:
        raise ValueError("Decision Index exclusion/subset checksums do not match the frozen release")

    def records():
        for row in suite.rows(apply_exclusions=True):
            questions = copy.deepcopy(row["questions"])
            for q in questions.values():
                if not isinstance(q["instructions"], str):
                    from ..io import dumps
                    q["instructions"] = dumps(q["instructions"])
            yield {"index": row["_evaluation"]["run_id"],
                   "request": {"state": row["state"], "questions": questions},
                   "targets": {k: {"label": v} if v is not None else {"unscored": True}
                               for k, v in row["expected"].items()},
                   "meta": {"subset": row["_evaluation"]["dataset"], "domain": row.get("family", "unknown"),
                            "modality": "text", "_evaluation": row["_evaluation"],
                            "expected": row["expected"], "source_metadata": row.get("metadata", {})}, "assets": []}
    return commit_dataset("DecisionIndex", records(), root,
                          {"repository": "https://github.com/apolinario/decision-index", "edition": edition,
                           "checks": checks, "suite_manifest": suite.manifest()},
                          protocol="official-public-" + edition, suite_dir="../raw/DecisionIndex-" + edition)
