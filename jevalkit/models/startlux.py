"""Native StartLuxModel adapter."""

import os
import sys
from .base import NativeRuntime
from .media import state_parts
from ..schema import Unsupported


class StartLuxModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, allow_slow=False, graphs=True, share_prefix=False, **options):
        super().__init__(model, **options)
        sys.path.insert(0, str(self.folder))
        from startlux_decision import StartLuxDecision

        previous = os.environ.get("STARTLUX_ALLOW_SLOW")
        if allow_slow:
            os.environ["STARTLUX_ALLOW_SLOW"] = "1"
        try:
            self.engine = StartLuxDecision(str(self.folder), device=self.device, graphs=graphs)
            # The release's prefix cache assumes tensor-valued linear-attention
            # state. Recent Transformers uses dictionaries; full native forward
            # avoids that incompatible optimization without truncating prompts.
            self.engine.share = bool(share_prefix)
        finally:
            if previous is None:
                os.environ.pop("STARTLUX_ALLOW_SLOW", None)
            else:
                os.environ["STARTLUX_ALLOW_SLOW"] = previous
        self.info.update(
            allow_slow=bool(allow_slow),
            fast_kernels=self.engine.fast_kernels,
            cuda_graphs=bool(self.engine.graphs),
            temperature=self.engine.temperature,
            max_score_levels=10,
            prefix_sharing=bool(share_prefix),
        )

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("StartLux release has no native video input")
        if any(q["type"] == "score" and len(q["criteria"]) > 10 for q in request["questions"].values()):
            raise Unsupported("StartLux release supports at most 10 score levels; all levels were retained")
        answers, usage = self.engine.decide(state, request["questions"], images=images or None)
        return {"answers": answers, "usage": usage}
