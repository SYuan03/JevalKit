"""Import actual upstream predictions, verify their frozen inputs, and re-score them."""
from pathlib import Path
import time

from . import __version__
from .config import MODELS
from .datasets import DecisionDataset
from .io import atomic_json, dumps, jsonl, load_json, sha256
from .metrics import grouped_report
from .runner import score_predictions
from .scoring import official_report


def import_decision_index(model_name, results, environments, output, root=None):
    """Import an upstream run, never a model-card score or leaderboard aggregate."""
    if model_name not in MODELS:
        raise ValueError("Model must be registered")
    dataset = DecisionDataset("DecisionIndex", root)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError("Imported output must be a new empty directory")
    allowed = {r["index"]: r["meta"]["_evaluation"]["payload_sha256"] for r in dataset}
    common, evidence = None, []
    for path in map(Path, environments):
        env = load_json(path)
        identity = {k: env.get(k) for k in ("model_source", "hardware", "versions", "cuda", "runner_sha256", "latency")}
        if common is None:
            common = identity
        elif common != identity:
            raise ValueError("Upstream shard model/runtime identities differ")
        evidence.append({"path": str(path.resolve()), "sha256": sha256(path)})
    if not common or not common["model_source"]:
        raise ValueError("Source inference environments are required")
    model_source = common["model_source"]
    declared_path = Path(model_source.get("model_path", model_source.get("model", "")))
    if declared_path.name != model_name:
        raise ValueError("Imported source environment declares a different model")
    config_path = declared_path / "config.json"
    if config_path.exists() and sha256(config_path) != model_source["config_sha256"]:
        raise ValueError("Source checkpoint configuration has changed since measurement")
    predictions, seen = [], set()
    with (output / "predictions.jsonl").open("w", encoding="utf-8") as stream:
        for row in jsonl(results):
            index = row["run_id"]
            if index not in allowed:
                continue  # An explicitly supplied union of frozen editions may contain extra rows.
            if index in seen or row["payload_sha256"] != allowed[index]:
                raise ValueError("Duplicate upstream prediction or frozen input identity mismatch")
            seen.add(index)
            status = {"ok": "ok", "error": "error", "unsupported": "unsupported", "abstained": "refusal"}.get(row["status"])
            if status is None:
                raise ValueError("Unknown upstream inference status")
            prediction = {"index": index, "status": status,
                          "latency_s": row["model_request_wall_ms"] / 1000}
            if "response" in row:
                prediction["response"] = row["response"]
            if "error" in row:
                prediction["error"] = row["error"]
            stream.write(dumps(prediction) + "\n")
            predictions.append(prediction)
    if seen != set(allowed):
        raise ValueError(f"Imported predictions cover {len(seen)} of {len(allowed)} frozen requests")
    runtime = {"origin": "imported-upstream-measurement", "adapter": "upstream Decision Index engine",
               "source_runtime": common, "hardware": common["hardware"],
               "source_results": str(Path(results).resolve()), "source_results_sha256": sha256(results),
               "environment_evidence": evidence,
               "identity_scope": "Model identity is declared by original inference environments; this import performs no new inference."}
    signature = {"model": model_name, "benchmark": dataset.name, "dataset_sha256": dataset.manifest["sha256"],
                 "protocol": dataset.manifest["protocol"], "records": len(allowed), "limit": None,
                 "rank": 0, "world_size": 1, "warmup": None, "jevalkit": __version__, "operation": "verified-upstream-import"}
    atomic_json(output / "manifest.json", {"signature": signature, "runtime": runtime,
                                           "dataset_manifest": dataset.manifest})
    started = time.perf_counter()
    metrics = grouped_report(score_predictions(dataset, predictions))
    official = official_report(dataset, dataset, predictions, output)
    report = {"schema_version": 1, "model": model_name, "benchmark": dataset.name,
              "dataset_sha256": dataset.manifest["sha256"], "protocol": dataset.manifest["protocol"],
              "attempted_requests": len(predictions), "selected_requests": len(allowed), "total_requests": len(allowed),
              "rank": 0, "world_size": 1, "complete": True, "smoke": False, "metrics": metrics,
              "official": official, "runtime": runtime, "scoring_seconds": time.perf_counter() - started,
              "predictions_sha256": sha256(output / "predictions.jsonl"),
              "manifest_sha256": sha256(output / "manifest.json")}
    atomic_json(output / "metrics.json", report)
    return report
