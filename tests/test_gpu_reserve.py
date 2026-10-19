import importlib.util
import json
from pathlib import Path
import sys

import pytest

from jevalkit.io import atomic_json


spec = importlib.util.spec_from_file_location("gpu_reserve", Path(__file__).parents[1] / "scripts/gpu_reserve.py")
reserve = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reserve)


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    (tmp_path / "jevalkit").mkdir()
    (tmp_path / "jevalkit/__init__.py").write_text("snapshot = True\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/cluster_entry.sh").write_text("#!/bin/bash\n")
    monkeypatch.setattr(reserve, "ROOT", tmp_path)
    return tmp_path


def invoke(monkeypatch, name, gpus):
    monkeypatch.setattr(sys, "argv", ["gpu_reserve.py", name, str(gpus)])
    reserve.main()


def test_finished_history_does_not_consume_parallel_capacity(workspace, monkeypatch):
    rows = []
    for i in range(32):
        name = f"previous-{i}"
        rows.append({"name": name, "gpus": 1, "state": "reserved-before-submission"})
        folder = workspace / "artifacts/jobs" / name
        folder.mkdir(parents=True)
        (folder / "ended_utc").write_text("2026-10-19T00:00:00Z\n")
        (folder / "exit_code").write_text("1\n")
    ledger = workspace / "artifacts/gpu-ledger.json"
    atomic_json(ledger, {"limit": 32, "reservations": rows})
    invoke(monkeypatch, "next", 1)
    saved = json.loads(ledger.read_text())
    assert len(saved["reservations"]) == 33 and reserve.active_gpus(saved) == 1
    assert saved["limit_mode"] == "max_parallel"
    assert all(r["state"] == "finished" for r in saved["reservations"][:-1])
    assert (workspace / "artifacts/jobs/next/code/jevalkit/__init__.py").read_text() == "snapshot = True\n"


def test_parallel_peak_stays_at_32_and_unknown_jobs_keep_their_slot(workspace, monkeypatch):
    ledger = workspace / "artifacts/gpu-ledger.json"
    atomic_json(ledger, {"limit": 32, "reservations": [
        {"name": f"unknown-{i}", "gpus": 1, "state": "reserved-before-submission"} for i in range(31)]})
    invoke(monkeypatch, "last-slot", 1)
    with pytest.raises(ValueError, match="Parallel GPU limit exceeded: 32\\+1>32"):
        invoke(monkeypatch, "over-limit", 1)
    saved = json.loads(ledger.read_text())
    assert reserve.active_gpus(saved) == saved["observed_parallel_peak"] == 32
    assert not (workspace / "artifacts/jobs/over-limit").exists()


def test_scheduler_terminal_evidence_releases_slot_without_worker_marker(workspace, monkeypatch):
    ledger = workspace / "artifacts/gpu-ledger.json"
    atomic_json(ledger, {"limit": 32, "reservations": [
        {"name": "old", "gpus": 32, "state": "reserved-before-submission"}]})
    atomic_json(workspace / "artifacts/jobs/old/scheduler-terminal.json", {"state": "Failed"})
    invoke(monkeypatch, "next", 1)
    saved = json.loads(ledger.read_text())
    assert reserve.active_gpus(saved) == 1
    with pytest.raises(ValueError, match="Job name already reserved"):
        invoke(monkeypatch, "next", 1)
