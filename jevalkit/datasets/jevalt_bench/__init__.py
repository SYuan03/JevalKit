"""JevAltBench conversion, acquisition and reference scoring."""

import copy
from .._shared import (
    normalize_questions,
    reference,
    canonical,
    prepare_rows,
    calibration_error,
    decision_report,
)
from ...metrics import score_predictions


SOURCE = {
    "repository": "mertkayacs/jevalt-bench",
    "revision": "950b95fac0950d85b6383dccbe3445726c1ccc3c",
    "split": "test",
    "license": "mixed permissive; record-level licenses retained",
    "records": 3116,
    "questions": 8434,
    "files": {
        "data/en/test.jsonl": "6ca22d30eb83eaf014d80ef448e82ecd26370f415d77c2c894129b5344c734b6",
        "data/tr/test.jsonl": "fa02b3d392da2febf3579f99dcf0bc063bbb72347e74d6f47d5453ba01475e44",
        "data/de/test.jsonl": "6904b1f96bf76fecf50558f40285d899568074f48ef35c1308d945265f1bd6d7",
    },
    "protocol": "test-en-tr-de-explicit-unknown-v1",
}


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
                q["criteria"].setdefault(
                    "unknown", "The supplied evidence is insufficient to choose an option."
                )
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
    return canonical(
        row,
        row["state"],
        questions,
        targets,
        group_id=group,
        subset=row["lang"],
        domain=next((t[7:] for t in row.get("tags", []) if t.startswith("domain:")), "mixed"),
        language=row["lang"],
        license=row["license"],
        source=row["source"],
        abstention_projection="explicit-choice-unknown" if row.get("abstain") else "none",
        ordinal_id_mapping=mappings,
        question_projection="Extra upstream question fields serialized into instructions; Score dictionaries retain insertion order.",
    )


def prepare(root=None, source=None, **options):
    return prepare_rows("JevAltBench", SOURCE, jevalt_record, root, source)


def evaluate(dataset, records, predictions, output):
    rows = score_predictions(records, predictions)
    report = decision_report(dataset, records, predictions, rows=rows)
    report["ece_15_equal_mass"] = calibration_error(rows, equal_mass=True)
    report["reference_scorer"] = "mertkayacs/jevoss@0dbffa411fc4adfc1728113a5d34bc6adfb142cb"
    report["interface_projection"] = (
        "Public abstain input flag becomes an explicit unknown Choice candidate; no gold-driven input selection."
    )
    return report
