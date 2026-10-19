"""DecisionBench conversion, acquisition and reference scoring."""

import math
from .._shared import parsed, reference, canonical, prepare_rows, decision_report
from ...schema import target_probabilities
from ...metrics import score_predictions


SOURCE = {
    "repository": "Hanno-Labs/decision-bench",
    "revision": "071b7b2d2e1504c89e1e5a811a3f82e1bfe3aedb",
    "split": "eval",
    "license": "source-specific; upstream license metadata: other",
    "records": 23900,
    "questions": 23900,
    "files": {
        "data/eval-00000-of-00001.parquet": "d9dd5be8e0944a7ceadfcac6cf8f9d17aab256093acff23c6de6a037ad6e55f6"
    },
    "protocol": "standard-eval-systemone-native-v1",
}


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
        if any(
            not isinstance(c["ordinal_value"], (int, float)) or not math.isfinite(c["ordinal_value"])
            for c in ordered
        ):
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
    record = canonical(
        dict(row, id=row["row_id"]),
        parsed(row["state_json"]),
        {"decision": q},
        {"decision": target},
        subset=row["task_id"],
        domain=row["domain"],
        family=row["family"],
        task=row["task_id"],
        primitive=primitive,
        language="en",
        reasoning_required=row["reasoning_required"],
        candidate_count=len(original),
        candidate_order={"decision": [mapping[c["id"]] for c in original]},
        upstream_candidate_ids={v: k for k, v in mapping.items()},
        input_rendering="standard",
    )
    return record


def prepare(root=None, source=None, **options):
    return prepare_rows("DecisionBench", SOURCE, decisionbench_record, root, source)


def evaluate(dataset, records, predictions, output):
    rows = score_predictions(records, predictions)
    report = decision_report(dataset, records, predictions, rows=rows)
    by_id = {record["index"]: record for record in records}
    losses = []
    for row in rows:
        if row["status"] == "ok":
            record = by_id[row["index"]]
            truth = target_probabilities(
                record["request"]["questions"][row["qid"]], record["targets"][row["qid"]]
            )
            losses.append(-sum(t * math.log(max(row["probabilities"][k], 1e-15)) for k, t in truth.items()))
    report["reference_nll"] = sum(losses) / len(losses) if losses else None
    report["reference_nll_epsilon"] = 1e-15
    report["reference_scorer"] = "Hanno-Labs/decision-bench@89aaa85827912f8975c1835348ead7436710f581"
    return report
