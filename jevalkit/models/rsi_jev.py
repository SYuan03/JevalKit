"""Native RSIJevModel adapter."""

import os
from .base import NativeRuntime
from ._utils import render_criteria
from .media import state_parts
from .provenance import cached_base_artifacts
from ..schema import Unsupported


class RSIJevModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        os.environ["RSIJEV_DOC_CACHE"] = "0"
        os.environ["RSIJEV_VISION_CACHE"] = "0"
        from rsijev import Decider

        self.engine = Decider(str(self.folder), device=self.device, dtype="bf16", batch_size=16)
        self.info.update(
            calibration=self.engine.calibration,
            image_limits=self.engine.image_limits,
            base_model=self.engine.served.meta.get("base_model"),
        )
        from dataclasses import asdict, replace

        self.engine.served.enc = replace(self.engine.served.enc, truncate="none")
        if self.engine.served.venc is not None:
            self.engine.served.venc = replace(self.engine.served.venc, truncate="none")
        self.info["encoding"] = asdict(self.engine.served.enc)
        meta = self.engine.served.meta
        self.info["base"] = cached_base_artifacts(
            meta["base_model"], (meta.get("vision") or {}).get("revision")
        )

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("RSI-Jev has no native video request; no implicit frame mosaic")
        if images:
            text = "\n".join(["<image>"] * len(images)) + "\n" + text
        from rsijev.encode import InputTooLong

        try:
            response = self.engine.request(text, render_criteria(request["questions"]), images=images)
        except InputTooLong as exc:
            raise Unsupported(str(exc)) from exc
        cut = response.get("truncated")
        if isinstance(cut, dict):
            cut = any(
                cut.get(key, 0)
                for key in ("state_tokens_omitted", "option_desc_tokens_omitted", "question_tokens_omitted")
            )
        if cut:
            raise Unsupported("RSI-Jev reported truncated evidence; the partial answer was excluded")
        return response
