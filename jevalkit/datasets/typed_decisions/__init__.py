"""TypedDecisions conversion, acquisition and reference scoring."""

from .._shared import parsed, normalize_questions, reference, canonical, prepare_rows, decision_report


SOURCE = {
    "repository": "LocalLLaMA/typed-decisions",
    "revision": "7189f46b02248bd2569df7325c9df8e3b24e90a7",
    "split": "test",
    "license": "Apache-2.0",
    "records": 400,
    "questions": 2000,
    "files": {
        "all/test-00000-of-00001.parquet": "4f294f218ea1da27f3efef936359389c62ea4d3973a41457732990f1d31b647c"
    },
    "protocol": "test-400-shared-state-soft-gold-v1",
}


def typed_record(row):
    questions = normalize_questions(row["questions"])
    gold = parsed(row["gold"])
    targets = {
        qid: reference(q, gold[qid]["label"], gold[qid]["probabilities"]) for qid, q in questions.items()
    }
    return canonical(
        row,
        parsed(row["state"]),
        questions,
        targets,
        subset=row["workflow"],
        domain=row["workflow"],
        language="en",
    )


def prepare(root=None, source=None, **options):
    return prepare_rows("TypedDecisions", SOURCE, typed_record, root, source)


def evaluate(dataset, records, predictions, output):
    report = decision_report(dataset, records, predictions)
    return report
