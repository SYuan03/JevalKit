"""Unscored adapter checks for complete typed responses and JSON descriptions."""
import copy
from pathlib import Path
import time

from .config import build_model
from .io import atomic_json, sha256
from .schema import Unsupported, answer_probabilities


CASES = [
    {"id": "typed-questions", "request": {"state": "A customer bought a red shirt for 12 dollars and asks for a refund.",
     "questions": {
        "route": {"type": "choice", "instructions": "Which team should handle this?",
                  "criteria": {"billing": "Charges and refunds", "technical": "Software problems"}},
        "condition": {"type": "noul", "instructions": "Does the refund policy apply?",
                      "criteria": {"true": "The customer requests their money back.", "false": "The customer only reports a software problem."}},
        "priority": {"type": "score", "instructions": "Rate the urgency.", "criteria": ["Low", "Medium", "High"]}}}},
    {"id": "json-and-null-descriptions", "request": {"state": {"item": {"color": "red", "quantity": 2}},
     "questions": {"match": {"type": "choice", "instructions": "Which candidate describes the item?",
                   "criteria": {"red": None, "structured": {"color": "blue", "quantity": 3}}}}}},
]


def check_model(model_name, output, root=None, model_options=None, model_instance=None):
    output = Path(output)
    if output.exists():
        raise ValueError("Conformance report exists; choose a new output path")
    model = model_instance or build_model(model_name, root=root, **(model_options or {}))
    report = {"schema_version": "adapter-conformance-v1", "model": model_name, "runtime": model.metadata(),
              "policy": "Synthetic interface checks only; no gold labels, accuracy or leaderboard score", "cases": [],
              "source_sha256": {str(p.relative_to(Path(__file__).parent)): sha256(p)
                                for p in sorted(Path(__file__).parent.rglob("*.py"))}}
    try:
        for case in CASES:
            row = copy.deepcopy(case)
            supplied = copy.deepcopy(row["request"])
            model.synchronize()
            started = time.perf_counter()
            try:
                response = model.predict(supplied)
                model.synchronize()
                if supplied != row["request"]:
                    raise ValueError("Adapter mutated its supplied request")
                if set(response["answers"]) != set(row["request"]["questions"]):
                    raise ValueError("Response must contain every requested question exactly once")
                for qid, q in row["request"]["questions"].items():
                    answer_probabilities(q, response["answers"][qid])
                row.update(status="passed", response=response)
            except Unsupported as exc:
                row.update(status="unsupported", error=str(exc))
            except Exception as exc:
                if type(exc).__name__ in {"OutOfMemoryError", "AcceleratorError"}:
                    raise
                row.update(status="error", exception=type(exc).__name__, error=str(exc))
            row["latency_s"] = time.perf_counter() - started
            report["cases"].append(row)
    finally:
        model.close()
    report["passed"] = all(row["status"] == "passed" for row in report["cases"])
    atomic_json(output, report)
    return report
