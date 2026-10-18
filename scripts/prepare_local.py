"""Import existing public Valen benchmark snapshots without modifying the source."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jevalkit.datasets.prepare import (prepare_decision_index, prepare_jevbench,
                                       prepare_visual, prepare_when2call)
from jevalkit.io import atomic_json
from jevalkit.paths import data_root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--valen-root", type=Path, required=True)
    parser.add_argument("--valen-data", type=Path, required=True)
    parser.add_argument("--root")
    args = parser.parse_args()
    root = data_root(args.root)
    experiments = args.valen_root / "output" / "decision-index-20261016"
    tasks = [
        ("JevBench", lambda: prepare_jevbench(root, args.valen_data / "eval" / "JevBench")),
        ("When2Call", lambda: prepare_when2call(root, experiments / "hf-when2call.jsonl")),
        ("VisualDecisionBench", lambda: prepare_visual(root, args.valen_data / "eval" / "VisualDecisionBench_local")),
        ("DecisionIndex", lambda: prepare_decision_index(root, experiments / "suite-0.3")),
    ]
    results, failed = {}, False
    for name, operation in tasks:
        try:
            value = operation()
            results[name] = value
            values = value if isinstance(value, list) else [value]
            print(json.dumps({"event": "prepared", "benchmarks": [{k: m[k] for k in ("name", "records", "questions", "sha256")}
                                                                      for m in values]}), flush=True)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            results[name] = {"error": type(exc).__name__ + ": " + str(exc)}
            failed = True
    atomic_json(root / "preparation.json", results)
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
