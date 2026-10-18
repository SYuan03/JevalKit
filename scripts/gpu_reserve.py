"""Reserve cumulative GPU submissions and freeze the exact evaluation source."""
import fcntl
import json
from pathlib import Path
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jevalkit.io import atomic_json, sha256


def main():
    name, count = sys.argv[1], int(sys.argv[2])
    if count < 1 or count > 32:
        raise ValueError("GPU count must be in [1,32]")
    artifacts = ROOT / "artifacts"
    artifacts.mkdir(exist_ok=True)
    with (artifacts / "gpu-budget.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        ledger_path = artifacts / "gpu-ledger.json"
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"limit": 32, "reservations": []}
        if any(r["name"] == name for r in ledger["reservations"]):
            raise ValueError("Job name already reserved; inspect its existing handle before resubmitting")
        total = sum(r["gpus"] for r in ledger["reservations"])
        if total + count > ledger["limit"]:
            raise ValueError(f"Cumulative GPU budget exceeded: {total}+{count}>{ledger['limit']}")
        destination = artifacts / "jobs" / name / "code"
        destination.mkdir(parents=True, exist_ok=False)
        shutil.copytree(ROOT / "jevalkit", destination / "jevalkit", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(ROOT / "scripts" / "cluster_entry.sh", destination / "cluster_entry.sh")
        if len(sys.argv) > 3:
            shutil.copyfile(sys.argv[3], destination / "matrix.json")
        hashes = {str(p.relative_to(destination)): sha256(p) for p in destination.rglob("*") if p.is_file()}
        atomic_json(destination.parent / "source.json", hashes)
        ledger["reservations"].append({"name": name, "gpus": count, "created_utc": datetime.now(timezone.utc).isoformat(),
                                        "code": str(destination), "state": "reserved-before-submission"})
        atomic_json(ledger_path, ledger)
    print(destination)


if __name__ == "__main__":
    main()
