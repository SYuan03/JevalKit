#!/usr/bin/env python3
"""Submit pinned model validations as their verified downloads become ready."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jevalkit.io import atomic_json, load_json, object_hash, sha256
from jevalkit.matrix import matrix_commands
from jevalkit.paths import data_root


def source_fingerprint(repo_root):
    paths = [*(repo_root / "jevalkit").rglob("*.py"), *(repo_root / "scripts").glob("*.py"),
             *(repo_root / "scripts").glob("*.sh")]
    return {str(path.relative_to(repo_root)): sha256(path) for path in sorted(paths)}


def waiting_for(entry, root):
    waiting = []
    for model in entry.get("models", []):
        folder = root / "models" / model["repo"].replace("/", "--") / model["revision"]
        marker = folder / "jevalkit-download.json"
        if not marker.is_file():
            waiting.append(str(marker))
            continue
        saved = load_json(marker)
        if saved.get("model") != model["repo"] or saved.get("revision") != model["revision"] or not saved.get("lfs_sha256"):
            raise ValueError("Downloaded model identity or LFS verification is missing: " + str(marker))
    for source in entry.get("ready_files", []):
        path = Path(source)
        if not path.is_file():
            waiting.append(str(path))
        elif load_json(path).get("ready") is not True:
            raise ValueError("Environment readiness was not verified: " + str(path))
    return waiting


def advance_queue(config, report, status, repo_root=ROOT):
    root = data_root(config.get("root"))
    ledger = repo_root / "artifacts" / "gpu-ledger.json"
    reserved = {r["name"] for r in load_json(ledger)["reservations"]} if ledger.exists() else set()
    for index, entry in enumerate(config["jobs"]):
        row = report["jobs"][index]
        if row["state"] != "pending":
            continue
        log_folder = repo_root / "artifacts" / "jobs" / entry["name"]
        job_id = log_folder / "job_id"
        if job_id.is_file():
            row.update(state="submitted", job_id=job_id.read_text().strip())
        elif entry["name"] in reserved or log_folder.exists():
            row.update(state="needs-inspection", error="Existing reservation/submission has no saved handle; inspect it before any retry")
        else:
            try:
                row["waiting_for"] = waiting_for(entry, root)
                if config.get("validated_source"):
                    marker = Path(config["validated_source"])
                    if not marker.is_file() or load_json(marker).get("source_sha256") != source_fingerprint(repo_root):
                        row["waiting_for"].append(str(marker))
                if row["waiting_for"]:
                    continue
                if sha256(entry["matrix"]) != row["matrix_sha256"]:
                    raise ValueError("Queued matrix changed; inspect its configuration before submission")
                matrix_commands(load_json(entry["matrix"]), str(root))
                environment = {**os.environ, "JEVAL_PYTHON": entry["python"],
                               "JEVALKIT_DATA_ROOT": str(root),
                               "JEVAL_MEMORY_PER_GPU": str(entry.get("memory_per_gpu", 32768))}
                prepare_log = Path(status).parent / (entry["name"] + ".prepare.log")
                with prepare_log.open("a") as stream:
                    for command in entry.get("prepare_commands", []):
                        subprocess.run(command, cwd=repo_root, env=environment, check=True,
                                       stdout=stream, stderr=subprocess.STDOUT)
                if config.get("validated_source") and load_json(config["validated_source"]).get("source_sha256") != source_fingerprint(repo_root):
                    row["waiting_for"] = [config["validated_source"]]
                    continue
                # Persist the intent before the one permitted submission attempt.
                row.update(state="submitting", submitted_utc=datetime.now(timezone.utc).isoformat())
                atomic_json(status, report)
                command = ["bash", str(repo_root / "scripts/submit.sh"), entry["name"], "1", "matrix", entry["matrix"]]
                result = subprocess.run(command, cwd=repo_root, env=environment, check=False)
                if result.returncode != 0 or not job_id.is_file():
                    raise RuntimeError("Submission did not return a saved job handle; inspect its existing reservation")
                row.update(state="submitted", job_id=job_id.read_text().strip())
            except Exception as exc:
                row.update(state="needs-inspection", error=f"{type(exc).__name__}: {exc}")
        atomic_json(status, report)
        print(json.dumps(row), flush=True)
    report["complete"] = all(row["state"] == "submitted" for row in report["jobs"])
    atomic_json(status, report)
    return report


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--status", required=True)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    config = load_json(args.config)
    names = [entry["name"] for entry in config["jobs"]]
    if not names or len(names) != len(set(names)):
        raise ValueError("Queue requires uniquely named jobs")
    for entry in config["jobs"]:
        matrix_commands(load_json(entry["matrix"]))
    if Path(args.status).exists():
        report = load_json(args.status)
        if report["config_sha256"] != object_hash(config):
            raise ValueError("Queue configuration changed; inspect the existing queue status")
        for row in report["jobs"]:
            if row["state"] == "submitting":
                row.update(state="needs-inspection", error="Previous process stopped during submission; inspect the existing handle")
    else:
        report = {"config_sha256": object_hash(config), "jobs": [
            {"name": entry["name"], "matrix_sha256": sha256(entry["matrix"]), "state": "pending"}
            for entry in config["jobs"]]}
    report["pid"] = os.getpid()
    while True:
        advance_queue(config, report, args.status)
        if args.once or not any(row["state"] == "pending" for row in report["jobs"]):
            return 0 if report["complete"] else 1
        time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
