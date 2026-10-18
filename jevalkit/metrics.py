"""Probability metrics with explicit coverage and hard/soft label denominators."""
import math
from collections import defaultdict


def question_metrics(question, target, probabilities, candidate_order=None):
    from .schema import target_label, target_probabilities
    truth = target_probabilities(question, target)
    if truth is None:
        return {"hard": False, "scorable": False}
    gold = target_label(question, target)
    hard = gold is not None
    # JevBench's native rule: lexical tie break, including ordinal questions.
    predicted = (max(candidate_order, key=probabilities.get) if candidate_order is not None
                 else min(probabilities, key=lambda k: (-probabilities[k], k)))
    result = {"hard": hard, "correct": predicted == gold if hard else None,
              "predicted": predicted, "confidence": probabilities[predicted],
              "nll": -sum(t * math.log(max(probabilities[k], 1e-12)) for k, t in truth.items()),
              "brier": sum((probabilities[k] - t) ** 2 for k, t in truth.items())}
    result["kl"] = sum(t * math.log(t / max(probabilities[k], 1e-12)) for k, t in truth.items() if t)
    if hard:
        result["hard_nll"] = -math.log(max(probabilities[gold], 1e-12))
        result["hard_brier"] = sum((probabilities[k] - float(k == gold)) ** 2 for k in truth)
    if question["type"] == "score":
        keys = list(truth)
        levels = target.get("ordinal_values", [int(k) for k in keys]) if isinstance(target, dict) else [int(k) for k in keys]
        values = dict(zip(keys, levels))
        actual = sum(values[k] * p for k, p in truth.items())
        estimate = sum(values[k] * p for k, p in probabilities.items())
        cumulative = 0.0
        rps = 0.0
        for key in keys[:-1]:
            cumulative += probabilities[key] - truth[key]
            rps += cumulative ** 2
        result.update(mae=abs(actual - estimate), rps=rps / (len(keys) - 1))
    return result


def summarize(rows):
    """Failed and unsupported hard questions remain in the accuracy denominator."""
    hard = [r for r in rows if r["hard"]]
    valid = [r for r in rows if r["status"] == "ok"]
    calibrated = [r for r in valid if r["hard"]]
    out = {"questions": len(rows), "hard_questions": len(hard), "valid": len(valid),
           "failed": sum(r["status"] == "error" for r in rows),
           "unsupported": sum(r["status"] == "unsupported" for r in rows),
           "refused": sum(r["status"] == "refusal" for r in rows),
           "coverage": len(valid) / len(rows) if rows else 0,
           "accuracy": sum(bool(r.get("correct")) for r in hard) / len(hard) if hard else None,
           "probability_metric_questions": sum("nll" in r for r in valid), "ece_questions": len(calibrated)}
    for metric in ("nll", "brier", "kl", "hard_nll", "hard_brier", "mae", "rps"):
        values = [r[metric] for r in valid if metric in r]
        out[metric] = sum(values) / len(values) if values else None
    ece = 0.0
    for i in range(15):
        bucket = [r for r in calibrated if min(int(r["confidence"] * 15), 14) == i]
        if bucket:
            ece += abs(sum(r["confidence"] - bool(r["correct"]) for r in bucket)) / len(calibrated)
    out["ece"] = ece if calibrated else None
    latency = sorted(r["latency_s"] for r in rows if "latency_s" in r)
    out["request_latency_mean_s"] = sum(latency) / len(latency) if latency else None
    return out


def grouped_report(rows):
    groups = {}
    for name in ("type", "subset", "domain", "modality"):
        buckets = defaultdict(list)
        for row in rows:
            buckets[str(row.get(name, "unknown"))].append(row)
        groups[name] = {key: summarize(value) for key, value in sorted(buckets.items())}
    return {"overall": summarize(rows), "groups": groups}
