import json

from jevalkit.conformance import check_model
from jevalkit.models.uniform import UniformModel


def test_interface_checks_have_no_labels_or_benchmark_scores(tmp_path):
    output = tmp_path / "conformance.json"
    report = check_model("Uniform", output, model_instance=UniformModel())
    assert report["passed"] and len(report["cases"]) == 2
    assert all(set(case["request"]) == {"state", "questions"} for case in report["cases"])
    assert "metrics" not in report and "dataset_sha256" not in report
    assert json.loads(output.read_text())["schema_version"] == "adapter-conformance-v1"


def test_interface_checks_reject_missing_candidates(tmp_path):
    class Incomplete(UniformModel):
        def predict(self, request, **kwargs):
            response = super().predict(request)
            for answer in response["answers"].values():
                if answer["type"] == "choice":
                    answer["probabilities"].pop(next(iter(answer["probabilities"])))
            return response

    report = check_model("Uniform", tmp_path / "invalid.json", model_instance=Incomplete())
    assert not report["passed"] and all(row["status"] == "error" for row in report["cases"])
