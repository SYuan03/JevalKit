"""Extension contracts for independent model modules and benchmark packages."""

import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

from jevalkit.cli import main
from jevalkit.config import MODELS
from jevalkit.datasets import BENCHMARKS, official_report, published_manifest


def test_model_families_have_separate_importable_modules():
    owners = {}
    for spec in MODELS.values():
        module_name, class_name = spec.adapter.split(":")
        module = importlib.import_module(module_name)
        assert getattr(module, class_name)
        assert Path(module.__file__).is_file()
        assert owners.setdefault(module_name, spec.family) == spec.family


def test_benchmarks_own_their_metadata_preparation_and_scoring():
    owners = {}
    for name, spec in BENCHMARKS.items():
        module = importlib.import_module("jevalkit.datasets." + spec["module"])
        folder = Path(module.__file__).parent
        assert (folder / "manifest.json").is_file()
        assert callable(module.prepare)
        assert published_manifest(name)["name"] == name
        assert owners.setdefault(folder, spec["family"]) == spec["family"]
        # VisualDecisionBench uses the common metrics; other suites own a scorer.
        if spec["family"] != "VisualDecisionBench":
            assert callable(module.evaluate)


def test_new_benchmark_dispatches_without_changing_cli_or_runner(monkeypatch, tmp_path, capsys):
    calls = []
    module = ModuleType("jevalkit.datasets.extension_fixture")

    def prepare(**options):
        calls.append(options)
        return {"prepared": True}

    def evaluate(dataset, records, predictions, output):
        assert dataset.name == "ExtensionFixture"
        assert records == ["record"] and predictions == ["prediction"]
        return {"scorer": "extension-fixture"}

    module.prepare, module.evaluate = prepare, evaluate
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setitem(
        BENCHMARKS,
        "ExtensionFixture",
        {
            "family": "ExtensionFixture",
            "modality": "text",
            "module": "extension_fixture",
        },
    )
    main(["prepare", "ExtensionFixture", "--root", str(tmp_path), "--source", "fixture-source"])
    assert calls == [{"root": str(tmp_path), "source": "fixture-source", "edition": "0.3"}]
    assert '"prepared":true' in capsys.readouterr().out
    assert official_report(
        SimpleNamespace(name="ExtensionFixture"), ["record"], ["prediction"], tmp_path
    ) == {
        "scorer": "extension-fixture",
    }
