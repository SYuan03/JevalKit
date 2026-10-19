"""Native LayaModel adapter."""

import sys
from pathlib import Path
from .base import DecisionModel
from ._utils import resolve_model
from .media import state_parts
from .provenance import inference_artifacts, runtime_versions
from ..schema import Unsupported


class LayaModel(DecisionModel):
    def __init__(
        self,
        model="convaiinnovations/laya",
        source=None,
        device="cuda",
        revision="main",
        root=None,
        **options,
    ):
        if source:
            sys.path.insert(0, str(Path(source).resolve()))
        import laya

        folder = resolve_model(model, revision, root)
        self.agent = laya.load(str(folder), device=device, fast=False, compile=False)
        self.device = device
        self.info = {
            "adapter": "LayaModel",
            "model": model,
            "revision": revision,
            "package": laya.__version__,
            "temperature": self.agent.temperature,
            "artifacts_sha256": inference_artifacts(folder),
            "source_sha256": inference_artifacts(Path(laya.__file__).parent),
            "temperature_by_options": self.agent.temperature_by_options,
            "max_length": self.agent.cfg["max_len"],
            "truncation": "author runtime defaults",
        }
        import torch

        self.info.update(
            hardware=torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
            torch=torch.__version__,
            cuda=torch.version.cuda,
            versions=runtime_versions(),
        )

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
