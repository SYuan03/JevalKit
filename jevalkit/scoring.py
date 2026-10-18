"""Use benchmark-owned scorers for public JevBench and Decision Index."""
from pathlib import Path
from .io import dumps


def official_report(dataset, records, predictions, output):
    if dataset.name == "JevBench":
        from .datasets._jevbench.tasks import Task
        from .datasets._jevbench.scoring import score_task
        from .datasets._jevbench.summarize import summarize
        tasks, scored = [], []
        by_id = {p["index"]: p for p in predictions}
        for record in records:
            task = Task.from_dict(record["meta"]["upstream_task"])
            tasks.append(task)
            p = by_id[record["index"]]
            row = {"task_id": task.id, "ok": False, "valid": False, "strict_valid": False,
                   "correct": False, "latency_s": p["latency_s"], "probs": None,
                   "model": "native", "cost_usd": None, "cost_basis": "unmeasured",
                   "probs_source": "native"}
            if p["status"] == "ok":
                try:
                    answer = p["response"]["answers"]["decision"]
                    probabilities = ({"no": 1 - answer["noul"], "yes": answer["noul"]}
                                     if task.question["type"] == "noul" else answer["probabilities"])
                    row.update(score_task(probabilities, task), ok=True)
                except (KeyError, ValueError, TypeError):
                    pass
            scored.append(row)
        return summarize(tasks, scored)
    if dataset.name == "DecisionIndex":
        from .datasets.prepare import install_digest_compat
        install_digest_compat()
        from decision_index.suite.io import Suite
        from decision_index.pipeline import score_run
        source = dataset.path.parent / dataset.manifest["suite_dir"]
        suite = Suite(source, dataset.manifest["source"]["edition"])
        by_id = {p["index"]: p for p in predictions}
        path = Path(output) / "decision-index-results.jsonl"
        with path.open("w", encoding="utf-8") as stream:
            for record in records:
                p = by_id[record["index"]]
                row = {**record["meta"]["_evaluation"], "status": p["status"],
                       "total_wall_ms": p["latency_s"] * 1000,
                       "model_request_wall_ms": p["latency_s"] * 1000}
                if row["status"] == "refusal":
                    row["status"] = "abstained"
                if "response" in p:
                    row["response"] = p["response"]
                    from decision_index.engines import validate
                    try:
                        validate(record["request"]["questions"], row["response"])
                    except (KeyError, ValueError, TypeError):
                        row.update(status="error", error="Native response fails official Decision Index validation")
                        row.pop("response")
                if "error" in p:
                    row["error"] = p["error"]
                stream.write(dumps(row) + "\n")
        return score_run(suite, path, "jevalkit", Path(output) / "official")
    return None
