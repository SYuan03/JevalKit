"""Frozen public JevBench preparation and official scoring."""

import copy
import shutil
from pathlib import Path
from ...io import jsonl, sha256
from ...paths import data_root
from .._shared import commit_dataset


JEV_REVISION = "bb05a335bc809e61b20c0f745d25499a82b326fc"
JEV_FILES = {
    "easy": (48, "231df3c2c8e88a1a8c137ebe85de96ba70fabd330849098ac7b3c52c70b7172b"),
    "original": (72, "5c2414edb3006b8bfcb70fda433f0f9ca015759433849f8d3104328a1f7c4180"),
    "hard": (111, "89e9e6becb33ed88c1de7d42dcc87531b2fb64cfaef4e1986faf7c37b3f80ebb"),
}


def prepare(root=None, source=None, **options):
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
            q = {
                k: copy.deepcopy(v)
                for k, v in task["question"].items()
                if k in {"type", "instructions", "criteria", "labels"}
            }
            records.append(
                {
                    "index": task["id"],
                    "request": {"state": task["state"], "questions": {"decision": q}},
                    "targets": {"decision": {"label": task["expected"]}},
                    "meta": {
                        "subset": tier,
                        "domain": task["family"],
                        "modality": "text",
                        "group_id": task.get("group") or task["id"],
                        "upstream_task": task,
                    },
                    "assets": [],
                }
            )
    return commit_dataset(
        "JevBench",
        records,
        root,
        {
            "repository": "https://github.com/fstandhartinger/jevbench",
            "revision": JEV_REVISION,
            "license": "MIT",
            "public_only": True,
            "files": JEV_FILES,
        },
        protocol="public-231",
        official_scorer="jevalkit.datasets.jevbench.official",
    )


def evaluate(dataset, records, predictions, output):
    from .official.tasks import Task
    from .official.scoring import score_task
    from .official.summarize import summarize

    tasks, scored = [], []
    by_id = {p["index"]: p for p in predictions}
    for record in records:
        task = Task.from_dict(record["meta"]["upstream_task"])
        tasks.append(task)
        p = by_id[record["index"]]
        row = {
            "task_id": task.id,
            "ok": False,
            "valid": False,
            "strict_valid": False,
            "correct": False,
            "latency_s": p["latency_s"],
            "probs": None,
            "model": "native",
            "cost_usd": None,
            "cost_basis": "unmeasured",
            "probs_source": "native",
        }
        if p["status"] == "ok":
            try:
                answer = p["response"]["answers"]["decision"]
                probabilities = (
                    {"no": 1 - answer["noul"], "yes": answer["noul"]}
                    if task.question["type"] == "noul"
                    else answer["probabilities"]
                )
                row.update(score_task(probabilities, task), ok=True)
            except (KeyError, ValueError, TypeError):
                pass
        scored.append(row)
    return summarize(tasks, scored)
