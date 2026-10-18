"""Pinned public decision benchmarks and lossless canonical request projections."""
import copy
import json
import math
import os
import shutil
from pathlib import Path
from urllib.request import urlopen

from ..io import dumps, jsonl, sha256
from ..paths import data_root
from ..schema import candidates, distribution
from .prepare import commit_dataset


SOURCES = {
    "TypedDecisions": {
        "repository": "LocalLLaMA/typed-decisions", "revision": "7189f46b02248bd2569df7325c9df8e3b24e90a7",
        "split": "test", "license": "Apache-2.0", "records": 400, "questions": 2000,
        "files": {"all/test-00000-of-00001.parquet": "4f294f218ea1da27f3efef936359389c62ea4d3973a41457732990f1d31b647c"},
        "protocol": "test-400-shared-state-soft-gold-v1",
    },
    "DecisionBench": {
        "repository": "Hanno-Labs/decision-bench", "revision": "071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb",
        "split": "eval", "license": "source-specific; upstream license metadata: other", "records": 23900, "questions": 23900,
        "files": {"data/eval-00000-of-00001.parquet": "d9dd5be8e0944a7ceadfcac6cf8f9d17aab256093acff23c6de6a037ad6e55f6"},
        "protocol": "standard-eval-systemone-native-v1",
    },
    "ProceduralTypedDecisions": {
        "repository": "tasksource/procedural-typed-decisions", "revision": "e4b21b7b55f6cc9e76e33563e9d604ac5fcd25ad",
        "split": "test", "license": "Apache-2.0", "records": 18000, "questions": 57016,
        "files": {"all/test-00000-of-00001.parquet": "9f16b7415fef05a01654c1fb4b743d6c43fd09e86d4d5b96b510a260239fbe9e"},
        "protocol": "18-tasks-test-native-probability-v1",
    },
    "ZhDecisionBench": {
        "repository": "CodyQin/zh-decision-bench", "revision": "c4f90cdd973f5f5c0793c30a2ff3b77ea42d2266",
        "split": "validation", "license": "CC-BY-4.0; Amazon MASSIVE and CodyQin attribution", "records": 378, "questions": 467,
        "files": {"voice_routing.jsonl": "3be12956bd7cbf23a09056d55a741178466f3214f4e03dbb4dda9581ac9b8cba",
                  "business_scenarios.jsonl": "4a48af57e67e6977f47d4180b1d3392d938eb2ccf0318a2c273fb85ce2f71f30"},
        "protocol": "v0.2-validation-378-native-v1",
    },
    "JevAltBench": {
        "repository": "mertkayacs/jevalt-bench", "revision": "950b95fac0950d85b6383dccbe3445726c1ccc3c",
        "split": "test", "license": "mixed permissive; record-level licenses retained", "records": 3116, "questions": 8434,
        "files": {"data/en/test.jsonl": "6ca22d30eb83eaf014d80ef448e82ecd26370f415d77c2c894129b5344c734b6",
                  "data/tr/test.jsonl": "fa02b3d392da2febf3579f99dcf0bc063bbb72347e74d6f47d5453ba01475e44",
                  "data/de/test.jsonl": "6904b1f96bf76fecf50558f40285d899568074f48ef35c1308d945265f1bd6d7"},
        "protocol": "test-en-tr-de-explicit-unknown-v1",
    },
}


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
        probabilities = {binary_label(k) if question["type"] == "noul" else str(k): v
                         for k, v in probabilities.items()}
        result["probabilities"] = distribution(probabilities, candidates(question), tolerance=0.001)
        if abs(sum(probabilities.values()) - 1) > 1e-12:
            result["source_probability_sum"] = sum(probabilities.values())
    if not result:
        raise ValueError("Missing upstream reference")
    return result


def typed_record(row):
    questions = normalize_questions(row["questions"])
    gold = parsed(row["gold"])
    targets = {qid: reference(q, gold[qid]["label"], gold[qid]["probabilities"])
               for qid, q in questions.items()}
    return canonical(row, parsed(row["state"]), questions, targets,
                     subset=row["workflow"], domain=row["workflow"], language="en")


def procedural_record(row):
    questions = normalize_questions(row["questions"])
    answers, targets = parsed(row["answers"]), {}
    for qid, q in questions.items():
        a = answers[qid]
        if q["type"] == "noul":
            p = a["noul"]
            targets[qid] = reference(q, probabilities={"false": 1 - p, "true": p})
        else:
            targets[qid] = reference(q, a.get("choice"), a["probabilities"])
    return canonical(row, parsed(row["state"]), questions, targets,
                     subset=row["task"], domain=row["task"], task=row["task"], level=row["level"], language="en")


def zh_record(row):
    questions = normalize_questions(row["questions"])
    targets, order = {}, {}
    for qid, q in questions.items():
        label = row["gold"][qid]
        if q["type"] == "score":
            label = q["criteria"].index(label)
        targets[qid] = reference(q, label)
        order[qid] = ["true", "false"] if q["type"] == "noul" else list(candidates(q))
    return canonical(row, row["state"], questions, targets, candidate_order=order,
                     subset=row["domain"], domain=row["domain"], language="zh-CN", source=row["source"])


def jevalt_record(row):
    original = copy.deepcopy(row["questions"])
    mappings = {}
    for qid, q in original.items():
        if q["type"] == "score" and isinstance(q.get("criteria"), dict):
            mappings[qid] = {str(key): str(i) for i, key in enumerate(q["criteria"])}
            q["criteria"] = list(q["criteria"].values())
    questions = normalize_questions(original, extra_fields=True)
    # A published input flag enables abstention. Never infer it from gold labels.
    if row.get("abstain"):
        for q in questions.values():
            if q["type"] == "choice":
                q["criteria"].setdefault("unknown", "The supplied evidence is insufficient to choose an option.")
            elif q["type"] == "score":
                raise ValueError("An unordered unknown outcome cannot be appended to an ordinal rubric")
    targets = {}
    for qid, q in questions.items():
        raw = row["targets"][qid]
        label, probs = raw["label"], raw.get("dist")
        if qid in mappings:
            label = mappings[qid][str(label)]
            if probs is not None:
                probs = {mappings[qid][str(k)]: v for k, v in probs.items()}
        targets[qid] = reference(q, label, probs)
    group = next((tag[6:] for tag in row.get("tags", []) if tag.startswith("group:")), row["id"])
    return canonical(row, row["state"], questions, targets, group_id=group,
                     subset=row["lang"], domain=next((t[7:] for t in row.get("tags", []) if t.startswith("domain:")), "mixed"),
                     language=row["lang"], license=row["license"], source=row["source"],
                     abstention_projection="explicit-choice-unknown" if row.get("abstain") else "none",
                     ordinal_id_mapping=mappings,
                     question_projection="Extra upstream question fields serialized into instructions; Score dictionaries retain insertion order.")


def decisionbench_record(row):
    original = parsed(row["candidates_json"])
    if len(original) != len(row["gold_probabilities"]):
        raise ValueError("DecisionBench probabilities must align with every original candidate")
    if len({c["id"] for c in original}) != len(original):
        raise ValueError("Duplicate DecisionBench candidate IDs")
    description = lambda c: c["label"] if c["description"] is None else f'{c["label"]}: {c["description"]}'
    primitive = row["primitive"]
    q = {"instructions": row["instruction"]}
    if primitive == "binary_classification":
        if len(original) != 2:
            raise ValueError("Binary DecisionBench row requires exactly two outcomes")
        q.update(type="noul", criteria={"true": description(original[0]), "false": description(original[1])})
        mapping = {original[0]["id"]: "true", original[1]["id"]: "false"}
    elif primitive == "candidate_selection":
        q.update(type="choice", criteria={c["id"]: description(c) for c in original})
        mapping = {c["id"]: c["id"] for c in original}
    elif primitive == "ordinal_scoring":
        ordered = sorted(original, key=lambda c: c["ordinal_value"])
        if any(not isinstance(c["ordinal_value"], (int, float)) or not math.isfinite(c["ordinal_value"]) for c in ordered):
            raise ValueError("Ordinal values must be finite")
        if len({c["ordinal_value"] for c in ordered}) != len(ordered):
            raise ValueError("Ordinal values must be distinct")
        q.update(type="score", criteria=[description(c) for c in ordered])
        mapping = {c["id"]: str(i) for i, c in enumerate(ordered)}
    else:
        raise ValueError("Unknown DecisionBench primitive: " + primitive)
    probabilities = {mapping[c["id"]]: p for c, p in zip(original, row["gold_probabilities"])}
    target = reference(q, mapping[row["gold_candidate_id"]], probabilities)
    if primitive == "ordinal_scoring":
        target["ordinal_values"] = [c["ordinal_value"] for c in ordered]
    record = canonical(dict(row, id=row["row_id"]), parsed(row["state_json"]), {"decision": q}, {"decision": target},
                       subset=row["task_id"], domain=row["domain"], family=row["family"], task=row["task_id"],
                       primitive=primitive, language="en", reasoning_required=row["reasoning_required"],
                       candidate_count=len(original), candidate_order={"decision": [mapping[c["id"]] for c in original]},
                       upstream_candidate_ids={v: k for k, v in mapping.items()}, input_rendering="standard")
    return record


def canonical(row, state, questions, targets, **metadata):
    order = {qid: list(candidates(q)) for qid, q in questions.items()}
    return {"index": row["id"], "request": {"state": state, "questions": questions}, "targets": targets,
            "meta": {"modality": "text", "group_id": row["id"], "candidate_order": order, **metadata}, "assets": []}


CONVERTERS = {"TypedDecisions": typed_record, "DecisionBench": decisionbench_record,
              "ProceduralTypedDecisions": procedural_record, "ZhDecisionBench": zh_record, "JevAltBench": jevalt_record}


def acquire_files(name, root, source=None):
    spec = SOURCES[name]
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


def prepare_decision_benchmark(name, root=None, source=None):
    spec = SOURCES[name]
    folder = acquire_files(name, root, source)

    def records():
        count = questions = 0
        for filename in spec["files"]:
            if filename.endswith(".parquet"):
                import pyarrow.parquet as pq
                rows = (row for batch in pq.ParquetFile(folder / filename).iter_batches(batch_size=256)
                        for row in batch.to_pylist())
            else:
                rows = jsonl(folder / filename)
            for row in rows:
                record = CONVERTERS[name](row)
                count += 1
                questions += len(record["request"]["questions"])
                yield record
        if count != spec["records"] or questions != spec.get("questions", questions):
            raise ValueError(f"Pinned {name} coverage mismatch: {count} rows / {questions} questions")

    source_info = {k: v for k, v in spec.items() if k not in {"records", "questions", "protocol"}}
    source_info["repository"] = "https://huggingface.co/datasets/" + spec["repository"]
    return commit_dataset(name, records(), root, source_info, protocol=spec["protocol"],
                          reference_normalization="sum-normalized only within 0.001 of one; original sum retained",
                          tie_break="first upstream candidate; explicit mapping retained per question")
