"""ZhDecisionBench conversion, acquisition and reference scoring."""

from .._shared import (
    normalize_questions,
    reference,
    canonical,
    prepare_rows,
    calibration_error,
    decision_report,
)
from ...schema import candidates
from ...metrics import score_predictions


SOURCE = {
    "repository": "CodyQin/zh-decision-bench",
    "revision": "c4f90cdd973f5f5c0793c30a2ff3b77ea42d2266",
    "split": "validation",
    "license": "CC-BY-4.0; Amazon MASSIVE and CodyQin attribution",
    "records": 378,
    "questions": 467,
    "files": {
        "voice_routing.jsonl": "3be12956bd7cbf23a09056d55a741178466f3214f4e03dbb4dda9581ac9b8cba",
        "business_scenarios.jsonl": "4a48af57e67e6977f47d4180b1d3392d938eb2ccf0318a2c273fb85ce2f71f30",
    },
    "protocol": "v0.2-validation-378-native-v1",
}


def zh_record(row):
    questions = normalize_questions(row["questions"])
    targets, order = {}, {}
    for qid, q in questions.items():
        label = row["gold"][qid]
        if q["type"] == "score":
            label = q["criteria"].index(label)
        targets[qid] = reference(q, label)
        order[qid] = ["true", "false"] if q["type"] == "noul" else list(candidates(q))
    return canonical(
        row,
        row["state"],
        questions,
        targets,
        candidate_order=order,
        subset=row["domain"],
        domain=row["domain"],
        language="zh-CN",
        source=row["source"],
    )


def prepare(root=None, source=None, **options):
    return prepare_rows("ZhDecisionBench", SOURCE, zh_record, root, source)


def evaluate(dataset, records, predictions, output):
    rows = score_predictions(records, predictions)
    report = decision_report(dataset, records, predictions, rows=rows)
    report["ece_15_right_closed"] = calibration_error(rows, right_closed=True)
    report["reference_scorer"] = "CodyQin/zh-decision-bench@6769a45fc15c7d568450a9d34c977692a3f5faa6"
    return report
