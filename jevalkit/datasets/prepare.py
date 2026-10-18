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


HF_DATASETS = {
    "AGNews": ("fancyzhx/ag_news", "default", "test", "MIT"),
    "Banking77": ("PolyAI/banking77", "default", "test", "CC-BY-4.0"),
    "BoolQ": ("google/boolq", "default", "validation", "CC-BY-SA-3.0"),
    "SST2": ("stanfordnlp/sst2", "default", "validation", "research dataset; see source"),
}


def prepare_hf(name, root=None):
    """Use explicit public held-out splits; pin the resolved dataset commit."""
    if name == "Banking77":
        return prepare_banking77(root)
    from huggingface_hub import HfApi
    from datasets import load_dataset
    root = data_root(root)
    repo, config, split, license_name = HF_DATASETS[name]
    revision = HfApi().dataset_info(repo).sha
    parquet_revision = None
    try:
        dataset = load_dataset(repo, config, split=split, revision=revision,
                               cache_dir=str(root / "raw" / "hf-cache"))
    except RuntimeError as exc:
        if "Dataset scripts are no longer supported" not in str(exc):
            raise
        # HF publishes script-free Parquet conversions of older datasets. Pin that
        # branch's actual commit too, rather than executing a remote dataset script.
        from huggingface_hub import hf_hub_download
        converted = HfApi().dataset_info(repo, revision="refs/convert/parquet")
        parquet_revision = converted.sha
        files = [p.rfilename for p in converted.siblings
                 if p.rfilename.startswith(config + "/" + split + "/") and p.rfilename.endswith(".parquet")]
        if not files:
            raise ValueError("No public Parquet conversion for " + repo + ":" + split)
        paths = [hf_hub_download(repo, f, repo_type="dataset", revision=parquet_revision,
                                 local_dir=root / "raw" / name) for f in sorted(files)]
        dataset = load_dataset("parquet", data_files=paths, split="train",
                               cache_dir=str(root / "raw" / "hf-cache"))
    if name == "AGNews":
        labels = ["World news", "Sports", "Business", "Science and technology"]
    elif name == "Banking77":
        labels = [s.replace("_", " ") for s in dataset.features["label"].names]
    else:
        labels = ["Negative sentiment", "Positive sentiment"]

    def records():
        for i, row in enumerate(dataset):
            if name == "BoolQ":
                state, q = row["passage"], {"type": "noul", "instructions": row["question"]}
                target = {"label": bool(row["answer"])}
            else:
                field = "sentence" if name == "SST2" else "text"
                state = row[field]
                instructions = {"AGNews": "Classify this news article by topic.",
                                "Banking77": "Which banking intent best describes the customer's request?",
                                "SST2": "What is the sentiment of this movie review?"}[name]
                q = {"type": "choice", "instructions": instructions,
                     "criteria": {str(j): label for j, label in enumerate(labels)}}
                target = {"label": str(row["label"])}
            yield {"index": str(i), "request": {"state": state, "questions": {"decision": q}},
                   "targets": {"decision": target}, "meta": {"subset": split, "modality": "text", "domain": name},
                   "assets": []}
    return commit_dataset(name, records(), root,
                          {"repository": "https://huggingface.co/datasets/" + repo, "revision": revision,
                           "parquet_revision": parquet_revision,
                           "split": split, "license": license_name}, protocol="held-out-" + split)


def prepare_banking77(root=None):
    import csv
    from urllib.request import urlopen
    root = data_root(root)
    revision = "57ec275d8078af65b7731c2a98be812d844a6d6b"
    folder = root / "raw" / "Banking77"
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "test.csv"
    url = f"https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/{revision}/banking_data/test.csv"
    with urlopen(url, timeout=60) as response:
        source.write_bytes(response.read())
    with source.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    labels = sorted({r["category"] for r in rows})
    if len(rows) != 3080 or len(labels) != 77:
        raise ValueError("Unexpected Banking77 held-out split coverage")
    criteria = {key: key.replace("_", " ") for key in labels}
    records = ({"index": str(i), "request": {"state": row["text"], "questions": {
        "decision": {"type": "choice", "instructions": "Which banking intent best describes the customer's request?",
                     "criteria": criteria}}}, "targets": {"decision": {"label": row["category"]}},
        "meta": {"subset": "test", "modality": "text", "domain": "banking"}, "assets": []}
        for i, row in enumerate(rows))
    return commit_dataset("Banking77", records, root,
                          {"repository": "https://github.com/PolyAI-LDN/task-specific-datasets", "revision": revision,
                           "url": url, "sha256": sha256(source), "license": "CC-BY-4.0", "split": "test"},
                          protocol="held-out-test")


def prepare_when2call(root=None, source=None):
    root = data_root(root)
    if source is None:
        from huggingface_hub import hf_hub_download
        source = hf_hub_download("nvidia/When2Call", "test/when2call_test_mcq.jsonl", repo_type="dataset",
                                 revision="0582f7749df63a96fdc3070932e83e72396ace53",
                                 local_dir=root / "raw" / "When2Call")
        return prepare_when2call_raw(root, source)
    records = []
    for row in jsonl(source):
        records.append({"index": row["id"], "request": {"state": row["state"], "questions": row["questions"]},
                        "targets": {k: {"label": v} for k, v in row["expected"].items()},
                        "meta": {"subset": "test", "domain": "tool_selection", "modality": "text"}, "assets": []})
    return commit_dataset("When2Call", records, root,
                          {"repository": "https://huggingface.co/datasets/nvidia/When2Call",
                           "revision": "0582f7749df63a96fdc3070932e83e72396ace53", "license": "CC-BY-4.0",
                           "normalized_source_sha256": sha256(source)}, protocol="HF-DecisionIndex-MCQ-projection")


def prepare_when2call_raw(root, source):
    expected = "8c3694e583eeeb8dbc297e6cd90da70efc68efa4b6adb7227523e828c6b7b14c"
    if sha256(source) != expected:
        raise ValueError("When2Call raw test split checksum mismatch")
    keys, order = list("ABCD"), ["direct", "tool_call", "request_for_info", "cannot_answer"]
    records = []
    for row in jsonl(source):
        if list(row["answers"]) != order:
            raise ValueError("When2Call option schema/order changed")
        questions = {"q": {"type": "choice",
                           "instructions": "Which response should the assistant give to the user's question, given the available tools?",
                           "criteria": dict(zip(keys, [row["answers"][k] for k in order]))}}
        records.append({"index": "62:" + row["uuid"],
                        "request": {"state": {"tools": [json.loads(t) for t in row["tools"]], "question": row["question"]},
                                    "questions": questions},
                        "targets": {"q": {"label": keys[order.index(row["correct_answer"]) ]}},
                        "meta": {"subset": "test", "domain": "tool_selection", "modality": "text"}, "assets": []})
    return commit_dataset("When2Call", records, root,
                          {"repository": "https://huggingface.co/datasets/nvidia/When2Call",
                           "revision": "0582f7749df63a96fdc3070932e83e72396ace53", "license": "CC-BY-4.0",
                           "raw_source_sha256": expected}, protocol="HF-DecisionIndex-MCQ-projection")
