"""Shared lossless conversion, acquisition and reference reporting helpers."""

import copy
import json
import os
import shutil
from pathlib import Path
from urllib.request import urlopen
from bisect import bisect_left
from collections import defaultdict
from ..io import atomic_json, dumps, jsonl, sha256, write_tsv
from ..paths import data_root
from ..schema import candidates, distribution
from ..metrics import summarize, score_predictions


def commit_dataset(name, records, root, source, media_root=".", **extra):
    root = data_root(root)
    path = root / "datasets" / (name + ".tsv")
    manifest = {
        "schema_version": 1,
        "name": name,
        "source": source,
        "media_root": media_root,
        **extra,
        **write_tsv(path, records),
    }
    atomic_json(path.with_suffix(".manifest.json"), manifest)
    return manifest


def parsed(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def binary_label(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return {"yes": "true", "no": "false"}.get(str(value).lower(), str(value).lower())


def normalize_questions(value, *, extra_fields=False):
    questions = copy.deepcopy(parsed(value))
    for q in questions.values():
        extra = set(q) - {"type", "instructions", "criteria", "labels"}
        if extra:
            if not extra_fields:
                raise ValueError("Unexpected upstream inference question fields")
            payload = {"instructions": q["instructions"], **{k: q.pop(k) for k in sorted(extra)}}
            q["instructions"] = dumps(payload)
        if not isinstance(q["instructions"], str):
            q["instructions"] = dumps(q["instructions"])
        if q["type"] == "noul" and q.get("criteria"):
            q["criteria"] = {binary_label(k): v for k, v in q["criteria"].items()}
    return questions


def reference(question, label=None, probabilities=None):
    """Keep explicit modal labels separate from soft reference distributions."""
    result = {}
    if label is not None:
        result["label"] = binary_label(label) if question["type"] == "noul" else str(label)
    if probabilities is not None:
        probabilities = {
            binary_label(k) if question["type"] == "noul" else str(k): v for k, v in probabilities.items()
        }
        result["probabilities"] = distribution(probabilities, candidates(question), tolerance=0.001)
        if abs(sum(probabilities.values()) - 1) > 1e-12:
            result["source_probability_sum"] = sum(probabilities.values())
    if not result:
        raise ValueError("Missing upstream reference")
    return result


def canonical(row, state, questions, targets, **metadata):
    order = {qid: list(candidates(q)) for qid, q in questions.items()}
    return {
        "index": row["id"],
        "request": {"state": state, "questions": questions},
        "targets": targets,
        "meta": {"modality": "text", "group_id": row["id"], "candidate_order": order, **metadata},
        "assets": [],
    }


def acquire_files(spec, root, source=None):
    name = spec["name"]
    folder = data_root(root) / "raw" / name / spec["revision"]
    folder.mkdir(parents=True, exist_ok=True)
    for name, digest in spec["files"].items():
        dest = folder / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            temporary = dest.with_name(dest.name + f".{os.getpid()}.part")
            try:
                if source:
                    shutil.copyfile(Path(source) / name, temporary)
                else:
                    url = f'https://huggingface.co/datasets/{spec["repository"]}/resolve/{spec["revision"]}/{name}'
                    with urlopen(url, timeout=60) as response, temporary.open("wb") as output:
                        shutil.copyfileobj(response, output, length=1024 * 1024)
                if sha256(temporary) != digest:
                    raise ValueError("Pinned benchmark source checksum mismatch: " + name)
                temporary.replace(dest)
            finally:
                temporary.unlink(missing_ok=True)
        if sha256(dest) != digest:
            raise ValueError("Pinned benchmark source checksum mismatch: " + str(dest))
    return folder


def prepare_rows(name, spec, converter, root=None, source=None):
    folder = acquire_files({"name": name, **spec}, root, source)

    def records():
        count = questions = 0
        for filename in spec["files"]:
            if filename.endswith(".parquet"):
                import pyarrow.parquet as pq

                rows = (
                    row
                    for batch in pq.ParquetFile(folder / filename).iter_batches(batch_size=256)
                    for row in batch.to_pylist()
                )
            else:
                rows = jsonl(folder / filename)
            for row in rows:
                record = converter(row)
                count += 1
                questions += len(record["request"]["questions"])
                yield record
        if count != spec["records"] or questions != spec.get("questions", questions):
            raise ValueError(f"Pinned {name} coverage mismatch: {count} rows / {questions} questions")

    source_info = {k: v for k, v in spec.items() if k not in {"records", "questions", "protocol"}}
    source_info["repository"] = "https://huggingface.co/datasets/" + spec["repository"]
    return commit_dataset(
        name,
        records(),
        root,
        source_info,
        protocol=spec["protocol"],
        reference_normalization="sum-normalized only within 0.001 of one; original sum retained",
        tie_break="first upstream candidate; explicit mapping retained per question",
    )


def calibration_error(rows, *, equal_mass=False, right_closed=False, bins=15):
    rows = [r for r in rows if r["status"] == "ok" and r["hard"]]
    if not rows:
        return None
    if equal_mass:
        ordered = sorted(rows, key=lambda r: r["confidence"])
        groups = [ordered[b * len(rows) // bins : (b + 1) * len(rows) // bins] for b in range(bins)]
    else:
        groups = [[] for _ in range(bins)]
        upper_edges = [i * (1.0 / bins) for i in range(1, bins)] + [1.0]
        for row in rows:
            confidence = row["confidence"]
            index = bisect_left(upper_edges, confidence) if right_closed else int(confidence * bins)
            groups[max(0, min(index, bins - 1))].append(row)
    return sum(abs(sum(r["confidence"] - bool(r["correct"]) for r in g)) for g in groups) / len(rows)


def decision_report(dataset, records, predictions, *, rows=None):
    if rows is None:
        rows = score_predictions(records, predictions)
    overall = summarize(rows)
    valid_hard = [r for r in rows if r["status"] == "ok" and r["hard"]]
    report = {
        "scorer": "jevalkit-decision-protocol-v1",
        "protocol": dataset.manifest["protocol"],
        "accuracy": overall["accuracy"],
        "coverage": overall["coverage"],
        "hard_questions": overall["hard_questions"],
        "questions": overall["questions"],
        "valid_hard_accuracy": (
            sum(r["correct"] for r in valid_hard) / len(valid_hard) if valid_hard else None
        ),
        "kl_from_gold": overall["kl"],
        "soft_brier_sum": overall["brier"],
        "target_cross_entropy": overall["nll"],
        "hard_brier_sum": overall["hard_brier"],
        "hard_nll": overall["hard_nll"],
        "ece_15_equal_width": overall["ece"],
        "failure_policy": "Failed/unsupported/refused labeled questions count as incorrect; probability metrics use valid responses.",
    }
    by_id = {record["index"]: record for record in records}
    groups = {
        key: defaultdict(list)
        for key in ("task", "family", "domain", "language", "level", "primitive", "question")
    }
    for row in rows:
        metadata = by_id[row["index"]]["meta"]
        for key in groups:
            value = row["qid"] if key == "question" else metadata.get(key)
            if value is not None:
                groups[key][str(value)].append(row)
    report["groups"] = {
        key: {value: summarize(items) for value, items in sorted(buckets.items())}
        for key, buckets in groups.items()
        if buckets
    }
    return report
