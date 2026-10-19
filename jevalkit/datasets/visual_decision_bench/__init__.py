"""VisualDecisionBench preparation, image/video views and media provenance."""

import copy
import json
import shutil
from pathlib import Path
from ...io import jsonl, sha256
from ...paths import data_root
from .._shared import commit_dataset


def prepare(root=None, source=None, **options):
    root = data_root(root)
    if source is None:
        from huggingface_hub import snapshot_download

        source = snapshot_download(
            "Valen-Team/VisualDecisionBench",
            repo_type="dataset",
            local_dir=root / "raw" / "VisualDecisionBench",
        )
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
        records.append(
            {
                k: record.get(k, [] if k == "assets" else {})
                for k in ("index", "request", "targets", "meta", "assets")
            }
        )
    origin = {
        "repository": "https://huggingface.co/datasets/Valen-Team/VisualDecisionBench",
        "local_source": str(source),
        "eval_jsonl_sha256": sha256(source / "eval.jsonl"),
        "source_manifest": json.loads((source / "source_manifest.json").read_text()),
        "license": "upstream datasets retain their own licenses",
    }
    results = [
        commit_dataset(
            "VisualDecisionBench",
            records,
            root,
            origin,
            media_root="../media/VisualDecisionBench",
            protocol="native-shared-state",
        )
    ]
    for subset in ("Image", "Video"):
        selected = [r for r in records if subset.lower() in r["meta"]["subset"].lower()]
        results.append(
            commit_dataset(
                "VisualDecisionBench_" + subset,
                selected,
                root,
                origin,
                media_root="../media/VisualDecisionBench",
                protocol="native-shared-state",
            )
        )
    return results
