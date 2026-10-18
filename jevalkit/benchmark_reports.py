"""Explicit reference metrics and task slices for the public decision suites."""
import math
from bisect import bisect_left
from collections import defaultdict

from .metrics import summarize
from .schema import target_probabilities


def calibration_error(rows, *, equal_mass=False, right_closed=False, bins=15):
    rows = [r for r in rows if r["status"] == "ok" and r["hard"]]
    if not rows:
        return None
    if equal_mass:
        ordered = sorted(rows, key=lambda r: r["confidence"])
        groups = [ordered[b * len(rows) // bins:(b + 1) * len(rows) // bins] for b in range(bins)]
    else:
        groups = [[] for _ in range(bins)]
        upper_edges = [i * (1.0 / bins) for i in range(1, bins)] + [1.0]
        for row in rows:
            confidence = row["confidence"]
            index = bisect_left(upper_edges, confidence) if right_closed else int(confidence * bins)
            groups[max(0, min(index, bins - 1))].append(row)
    return sum(abs(sum(r["confidence"] - bool(r["correct"]) for r in g)) for g in groups) / len(rows)


def decision_report(dataset, records, predictions):
    from .runner import score_predictions
    rows = score_predictions(records, predictions)
    overall = summarize(rows)
    valid_hard = [r for r in rows if r["status"] == "ok" and r["hard"]]
    report = {
        "scorer": "jevalkit-decision-protocol-v1", "protocol": dataset.manifest["protocol"],
        "accuracy": overall["accuracy"], "coverage": overall["coverage"],
        "hard_questions": overall["hard_questions"], "questions": overall["questions"],
        "valid_hard_accuracy": sum(r["correct"] for r in valid_hard) / len(valid_hard) if valid_hard else None,
        "kl_from_gold": overall["kl"], "soft_brier_sum": overall["brier"],
        "target_cross_entropy": overall["nll"], "hard_brier_sum": overall["hard_brier"],
        "hard_nll": overall["hard_nll"], "ece_15_equal_width": overall["ece"],
        "failure_policy": "Failed/unsupported/refused labeled questions count as incorrect; probability metrics use valid responses.",
    }
    by_id = {record["index"]: record for record in records}
    groups = {key: defaultdict(list) for key in ("task", "family", "domain", "language", "level", "primitive", "question")}
    for row in rows:
        metadata = by_id[row["index"]]["meta"]
        for key in groups:
            value = row["qid"] if key == "question" else metadata.get(key)
            if value is not None:
                groups[key][str(value)].append(row)
    report["groups"] = {key: {value: summarize(items) for value, items in sorted(buckets.items())}
                        for key, buckets in groups.items() if buckets}
    if dataset.name == "DecisionBench":
        # Upstream DecisionBench floors the prediction at 1e-15 for its log loss.
        losses = []
        for row in rows:
            if row["status"] == "ok":
                record = by_id[row["index"]]
                truth = target_probabilities(record["request"]["questions"][row["qid"]], record["targets"][row["qid"]])
                losses.append(-sum(t * math.log(max(row["probabilities"][k], 1e-15)) for k, t in truth.items()))
        report["reference_nll"] = sum(losses) / len(losses) if losses else None
        report["reference_nll_epsilon"] = 1e-15
        report["reference_scorer"] = "Hanno-Labs/decision-bench@89aaa85827912f8975c1835348ead7436710f581"
    elif dataset.name == "JevAltBench":
        report["ece_15_equal_mass"] = calibration_error(rows, equal_mass=True)
        report["reference_scorer"] = "mertkayacs/jevoss@0dbffa411fc4adfc1728113a5d34bc6adfb142cb"
        report["interface_projection"] = "Public abstain input flag becomes an explicit unknown Choice candidate; no gold-driven input selection."
    elif dataset.name == "ZhDecisionBench":
        report["ece_15_right_closed"] = calibration_error(rows, right_closed=True)
        report["reference_scorer"] = "CodyQin/zh-decision-bench@6769a45fc15c7d568450a9d34c977692a3f5faa6"
    elif dataset.name == "ProceduralTypedDecisions":
        probabilistic = [r for r in rows if r["status"] == "ok" and not r["hard"] and r["type"] == "noul"]
        errors = []
        for row in probabilistic:
            record = by_id[row["index"]]
            truth = target_probabilities(record["request"]["questions"][row["qid"]], record["targets"][row["qid"]])
            errors.append(abs(row["probabilities"]["true"] - truth["true"]))
        report.update(probabilistic_noul_questions=len(errors),
                      probabilistic_noul_mae=sum(errors) / len(errors) if errors else None,
                      accuracy_policy="Pure soft references have no fabricated modal label and do not enter accuracy/ECE.")
    return report
