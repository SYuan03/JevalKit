import json
from types import SimpleNamespace

import pytest

from jevalkit.io import load_json
from jevalkit.matrix import matrix_commands, run_matrix


def test_matrix_retains_failures_and_continues_independent_models(tmp_path, monkeypatch):
    config = {"schema_version": 1, "data": ["JevBench"], "output": str(tmp_path / "results"),
              "runs": [{"model": "Valen-0.8B", "options": {"device": "cpu"}},
                       {"model": "Laya", "limit": 4}]}
    source = tmp_path / "matrix.json"
    source.write_text(json.dumps(config))
    calls = []
    def execute(command, check):
        calls.append(command)
        assert not check
        return SimpleNamespace(returncode=1 if len(calls) == 1 else 0)
    monkeypatch.setattr("jevalkit.matrix.subprocess.run", execute)
    report = run_matrix(source, root=tmp_path)
    assert len(calls) == 2 and not report["complete"]
    assert report["runs"][0]["state"] == "failed"
    assert report["runs"][1]["state"] == "succeeded"
    assert calls[0][:3] == calls[1][:3]
    assert calls[0][1:3] == ["-m", "jevalkit"]
    assert "--root" in calls[0] and "device=\"cpu\"" in calls[0]
    assert load_json(source.with_suffix(".status.json")) == report


@pytest.mark.parametrize("run", [{"model": "missing"}, {"model": "Uniform", "data": ["missing"]},
                                {"model": "Uniform", "options": {"api_key": "must-not-persist"}},
                                {"model": "Uniform", "limit": 0}])
def test_matrix_validates_every_run_before_execution(run):
    config = {"schema_version": 1, "data": ["JevBench"], "output": "results", "runs": [run]}
    with pytest.raises(ValueError):
        matrix_commands(config)


def test_matrix_selects_an_explicit_environment_per_model():
    config = {"schema_version": 1, "data": ["JevBench"], "output": "results",
              "runs": [{"model": "Uniform", "python": "/environments/model/bin/python"}]}
    assert matrix_commands(config)[0][0] == "/environments/model/bin/python"


def test_matrix_supports_unscored_interface_checks():
    config = {"schema_version": 1, "output": "results", "runs": [{"model": "Uniform", "mode": "check"}]}
    command = matrix_commands(config)[0]
    assert command[1:4] == ["-m", "jevalkit", "check"]
    assert "--data" not in command and command[-1] == "results/Uniform/conformance.json"
