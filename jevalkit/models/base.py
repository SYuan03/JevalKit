"""Common decision-model interface and native runtime lifecycle."""

import sys
from pathlib import Path
from ._utils import resolve_model
from .provenance import inference_artifacts, runtime_versions
from ..io import sha256
from ..paths import data_root


class DecisionModel:
    modalities = frozenset({"text"})

    def predict(self, request, *, media_root=None, assets=None):
        raise NotImplementedError

    def synchronize(self):
        pass

    def metadata(self):
        return {"adapter": type(self).__name__}

    def close(self):
        pass


class NativeRuntime(DecisionModel):
    def __init__(self, model, device="cuda", revision="main", source=None, root=None, **options):
        import torch

        self.device = device
        self.folder = resolve_model(model, revision, root)
        self.root = data_root(root)
        self.options = options
        if source:
            source = str(Path(source).resolve())
            sys.path.insert(0, source)
        self.info = {
            "adapter": type(self).__name__,
            "model": model,
            "revision": revision,
            "source": source,
            "path": str(self.folder),
            "device": device,
            "hardware": torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
            "versions": runtime_versions(),
            "cuda": torch.version.cuda,
            "artifacts_sha256": inference_artifacts(self.folder),
            "options": options,
        }
        if source:
            source_root = Path(source)
            self.info["source_sha256"] = {
                str(p.relative_to(source_root)): sha256(p)
                for p in sorted(source_root.rglob("*.py"))
                if not {".git", ".venv", "__pycache__"}.intersection(p.parts)
            }

    def synchronize(self):
        if self.device.startswith("cuda"):
            import torch

            torch.cuda.synchronize(self.device)

    def metadata(self):
        return self.info

    def close(self):
        if hasattr(self, "engine"):
            del self.engine
        if self.device.startswith("cuda"):
            import torch

            torch.cuda.empty_cache()
