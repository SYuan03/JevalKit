"""Load author-supplied inference implementations without altering model heads."""
import importlib.util
import sys
from pathlib import Path

from .base import DecisionModel
from .hf import resolve_model
from .provenance import inference_artifacts, runtime_versions
from ..io import object_hash
from ..schema import Unsupported


def load_module(path):
    path = Path(path).resolve()
    name = "_jeval_native_" + object_hash(str(path))[:16]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    spec.loader.exec_module(module)
    return module


class InternDecision(DecisionModel):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, device="cuda", revision="main", root=None, **options):
        folder = resolve_model(model, revision, root)
        self.module = load_module(folder / "inference.py")
        self.engine = self.module.DecisionEngine(str(folder), temperature=1.0, backend="hf", device=device,
                                                dtype="bfloat16" if device.startswith("cuda") else "float32",
                                                max_length=8192, attn_implementation="sdpa")
        self.device = device
        self.info = {"model": model, "path": str(folder), "revision": revision,
                     "max_options": len(self.module.ANSWER_SYMBOLS),
                     "max_questions": 16,
                     "artifacts_sha256": inference_artifacts(folder),
                     "temperature": self.module.DEFAULT_TEMPERATURE,
                     "calibration": "author release default; no test-set fitting"}
        import torch
        self.info.update(hardware=torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
                         torch=torch.__version__, cuda=torch.version.cuda, versions=runtime_versions())

    def predict(self, request, *, media_root=None, assets=None):
        # The release accepts images at the top level; text-only requests are unchanged.
        import copy
        from .media import state_parts
        if len(request["questions"]) > 16:
            raise Unsupported("Intern-Decision release supports at most 16 questions per request; all questions were retained")
        maximum = len(self.module.ANSWER_SYMBOLS)
        for question in request["questions"].values():
            if question["type"] != "noul" and len(question["criteria"]) > maximum:
                raise Unsupported(f"Intern-Decision release supports at most {maximum} options; no candidates were removed")
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


class LayaModel(DecisionModel):
    def __init__(self, model="convaiinnovations/laya", source=None, device="cuda", revision="main", root=None, **options):
        if source:
            sys.path.insert(0, str(Path(source).resolve()))
        import laya
        folder = resolve_model(model, revision, root)
        self.agent = laya.load(str(folder), device=device, fast=False, compile=False)
        self.device = device
        self.info = {"adapter": "LayaModel", "model": model, "revision": revision,
                     "package": laya.__version__, "temperature": self.agent.temperature,
                     "artifacts_sha256": inference_artifacts(folder),
                     "source_sha256": inference_artifacts(Path(laya.__file__).parent),
                     "temperature_by_options": self.agent.temperature_by_options,
                     "max_length": self.agent.cfg["max_len"], "truncation": "author runtime defaults"}
        import torch
        self.info.update(hardware=torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
                         torch=torch.__version__, cuda=torch.version.cuda, versions=runtime_versions())

    def predict(self, request, **kwargs):
        from .media import state_parts
        state, images, videos = state_parts(request["state"], kwargs.get("media_root"))
        if images or videos:
            raise Unsupported("Laya release supports text inputs only")
        return self.agent.predict(state, request["questions"])

    def synchronize(self):
        if self.device.startswith("cuda"):
            import torch
            torch.cuda.synchronize(self.device)

    def metadata(self):
        return self.info
