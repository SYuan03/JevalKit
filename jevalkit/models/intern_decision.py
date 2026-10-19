"""Native InternDecision adapter."""

import copy
from .base import DecisionModel
from ._utils import resolve_model, load_module
from .media import state_parts
from .provenance import inference_artifacts, runtime_versions
from ..schema import Unsupported


class InternDecision(DecisionModel):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, device="cuda", revision="main", root=None, **options):
        folder = resolve_model(model, revision, root)
        self.module = load_module(folder / "inference.py")
        self.engine = self.module.DecisionEngine(
            str(folder),
            temperature=1.0,
            backend="hf",
            device=device,
            dtype="bfloat16" if device.startswith("cuda") else "float32",
            max_length=8192,
            attn_implementation="sdpa",
        )
        self.device = device
        self.info = {
            "model": model,
            "path": str(folder),
            "revision": revision,
            "max_options": len(self.module.ANSWER_SYMBOLS),
            "max_questions": 16,
            "artifacts_sha256": inference_artifacts(folder),
            "temperature": self.module.DEFAULT_TEMPERATURE,
            "calibration": "author release default; no test-set fitting",
        }
        import torch

        self.info.update(
            hardware=torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
            torch=torch.__version__,
            cuda=torch.version.cuda,
            versions=runtime_versions(),
        )

    def predict(self, request, *, media_root=None, assets=None):
        # The release accepts images at the top level; text-only requests are unchanged.
        import copy
        from .media import state_parts

        if len(request["questions"]) > 16:
            raise Unsupported(
                "Intern-Decision release supports at most 16 questions per request; all questions were retained"
            )
        maximum = len(self.module.ANSWER_SYMBOLS)
        for question in request["questions"].values():
            if question["type"] != "noul" and len(question["criteria"]) > maximum:
                raise Unsupported(
                    f"Intern-Decision release supports at most {maximum} options; no candidates were removed"
                )
        request = copy.deepcopy(request)
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("Intern-Decision release has no native video input")
        if images:
            request["state"], request["images"] = state, images
        try:
            raw = self.engine.predict(request)
            return self.module.scale_result(raw, self.module.DEFAULT_TEMPERATURE)
        except ValueError as exc:
            from ..schema import is_capacity_error

            if is_capacity_error(str(exc)):
                raise Unsupported(str(exc)) from exc
            raise

    def synchronize(self):
        if self.device.startswith("cuda"):
            import torch

            torch.cuda.synchronize(self.device)

    def metadata(self):
        return {"adapter": "InternDecision", **self.info}
