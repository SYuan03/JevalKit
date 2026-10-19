"""Shared AutoModel.system_one calling convention."""

import os
from .base import NativeRuntime
from .media import state_parts
from ..paths import data_root
from ..schema import Unsupported


class HFSystemOne(NativeRuntime):
    """Liquid d1 and vLLM Decision-1 ship AutoModel.system_one(state, questions)."""

    modalities = frozenset({"text", "image"})

    def __init__(
        self, model, image_support=True, max_score_levels=None, requires_nonempty_state=False, **options
    ):
        os.environ.setdefault("HF_MODULES_CACHE", str(data_root(options.get("root")) / "cache" / "modules"))
        super().__init__(model, **options)
        from transformers import AutoModel

        self.image_support = image_support
        self.max_score_levels = max_score_levels
        self.requires_nonempty_state = bool(requires_nonempty_state)
        self.modalities = frozenset({"text", "image"} if image_support else {"text"})
        self.engine = (
            AutoModel.from_pretrained(
                str(self.folder), trust_remote_code=True, local_files_only=True, dtype="auto"
            )
            .to(self.device)
            .eval()
        )
        self.info["image_support"] = bool(image_support)
        self.info["max_score_levels"] = max_score_levels
        self.info["requires_nonempty_state"] = self.requires_nonempty_state

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if videos or images and not self.image_support:
            raise Unsupported("This native release cannot represent the supplied media")
        if self.max_score_levels is not None and any(
            q["type"] == "score" and len(q["criteria"]) > self.max_score_levels
            for q in request["questions"].values()
        ):
            raise Unsupported(f"This native release supports at most {self.max_score_levels} score levels")
        if not text.strip() and not images and self.requires_nonempty_state:
            raise Unsupported(
                "This native release requires a nonempty state; no placeholder evidence was inserted"
            )
        import torch

        if images:
            from PIL import Image

            loaded = []
            for path in images:
                with Image.open(path) as image:
                    loaded.append(image.convert("RGB"))
            images = loaded
        kwargs = {"images": images} if images else {}
        with torch.inference_mode():
            result = self.engine.system_one(state=text, questions=request["questions"], **kwargs)
        return result
