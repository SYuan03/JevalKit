"""ProceduralTypedDecisions conversion, acquisition and reference scoring."""

from .._shared import parsed, normalize_questions, reference, canonical, prepare_rows, decision_report
from ...schema import target_probabilities
from ...metrics import score_predictions


SOURCE = {
    "repository": "tasksource/procedural-typed-decisions",
    "revision": "e4b21b7b55f6cc9e76e33563e9d604ac5fcd25ad",
    "split": "test",
    "license": "Apache-2.0",
    "records": 18000,
    "questions": 57016,
    "files": {
        "all/test-00000-of-00001.parquet": "9f16b7415fef05a01654c1fb4b743d6c43fd09e86d4d5b96b510a260239fbe9e"
    },
    "protocol": "18-tasks-test-native-probability-v1",
}


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
    return canonical(
        row,
        parsed(row["state"]),
        questions,
        targets,
        subset=row["task"],
        domain=row["task"],
        task=row["task"],
        level=row["level"],
        language="en",
    )


def prepare(root=None, source=None, **options):
    return prepare_rows("ProceduralTypedDecisions", SOURCE, procedural_record, root, source)


def evaluate(dataset, records, predictions, output):
    rows = score_predictions(records, predictions)
    report = decision_report(dataset, records, predictions, rows=rows)
    by_id = {record["index"]: record for record in records}
    probabilistic = [r for r in rows if r["status"] == "ok" and not r["hard"] and r["type"] == "noul"]
    errors = []
    for row in probabilistic:
        record = by_id[row["index"]]
        truth = target_probabilities(
            record["request"]["questions"][row["qid"]], record["targets"][row["qid"]]
        )
        errors.append(abs(row["probabilities"]["true"] - truth["true"]))
    report.update(
        probabilistic_noul_questions=len(errors),
        probabilistic_noul_mae=sum(errors) / len(errors) if errors else None,
        accuracy_policy="Pure soft references have no fabricated modal label and do not enter accuracy/ECE.",
    )
    return report
