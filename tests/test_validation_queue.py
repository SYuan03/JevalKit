from pathlib import Path
from types import SimpleNamespace
import importlib.util

from jevalkit.io import atomic_json, sha256

spec = importlib.util.spec_from_file_location("jeval_validation_queue", Path(__file__).parents[1] / "scripts/validation_queue.py")
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)
advance_queue = queue.advance_queue


def fixture_queue(tmp_path):
    matrix = tmp_path / "matrix.json"
    atomic_json(matrix, {"schema_version": 1, "output": str(tmp_path / "output"),
                         "runs": [{"model": "Uniform", "data": ["JevBench"]}]})
    model = {"repo": "Author/Model", "revision": "a" * 40}
    config = {"root": str(tmp_path / "shared"), "jobs": [{"name": "eval-model", "matrix": str(matrix),
               "python": "/inference/python", "models": [model]}]}
    report = {"jobs": [{"name": "eval-model", "matrix_sha256": sha256(matrix), "state": "pending"}]}
    marker = Path(config["root"]) / "models/Author--Model" / model["revision"] / "jevalkit-download.json"
    return config, report, model, marker


def test_queue_waits_for_verified_weights_then_submits_once(tmp_path, monkeypatch):
    config, report, model, marker = fixture_queue(tmp_path)
    calls = []
    def submit(command, **kwargs):
        calls.append(command)
        assert kwargs["env"]["JEVAL_PYTHON"] == "/inference/python"
        job_id = tmp_path / "artifacts/jobs/eval-model/job_id"
        job_id.parent.mkdir(parents=True)
        job_id.write_text("actual-scheduler-handle")
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(queue.subprocess, "run", submit)
    status = tmp_path / "queue.status.json"
    advance_queue(config, report, status, tmp_path)
    assert not calls and report["jobs"][0]["state"] == "pending"
    atomic_json(marker, {"model": model["repo"], "revision": model["revision"], "lfs_sha256": {"weight": "fixture"}})
    advance_queue(config, report, status, tmp_path)
    advance_queue(config, report, status, tmp_path)
    assert len(calls) == 1 and report["complete"]
    assert report["jobs"][0]["job_id"] == "actual-scheduler-handle"


def test_queue_never_retries_unknown_existing_gpu_reservation(tmp_path, monkeypatch):
    config, report, _, _ = fixture_queue(tmp_path)
    atomic_json(tmp_path / "artifacts/gpu-ledger.json", {"reservations": [{"name": "eval-model", "gpus": 1}]})
    def unexpected(*args, **kwargs):
        raise AssertionError("An unknown reservation must be inspected, never submitted again")
    monkeypatch.setattr(queue.subprocess, "run", unexpected)
    advance_queue(config, report, tmp_path / "status.json", tmp_path)
    assert report["jobs"][0]["state"] == "needs-inspection"


def test_queue_requires_tested_source_before_gpu_submission(tmp_path, monkeypatch):
    config, report, model, marker = fixture_queue(tmp_path)
    atomic_json(marker, {"model": model["repo"], "revision": model["revision"], "lfs_sha256": {"weight": "fixture"}})
    source = tmp_path / "jevalkit/model.py"
    source.parent.mkdir()
    source.write_text("original")
    proof = tmp_path / "validated.json"
    atomic_json(proof, {"source_sha256": queue.source_fingerprint(tmp_path)})
    source.write_text("changed after tests")
    config["validated_source"] = str(proof)
    def unexpected(*args, **kwargs):
        raise AssertionError("Changed source must be verified before consuming GPU budget")
    monkeypatch.setattr(queue.subprocess, "run", unexpected)
    advance_queue(config, report, tmp_path / "status.json", tmp_path)
    assert report["jobs"][0]["state"] == "pending" and str(proof) in report["jobs"][0]["waiting_for"]
