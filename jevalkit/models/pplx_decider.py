"""Native PplxDecider adapter."""

import sys
from .base import NativeRuntime
from .media import state_parts
from ..schema import Unsupported, candidates


class PplxDecider(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        sys.path.insert(0, str(self.folder / "source" / "src"))
        from autojev.model import DecisionModel, answer

        self.engine = DecisionModel(self.folder, device=self.device)
        self.answer = answer
        self.info.update(
            temperature=self.engine.temperature,
            attention_mode=self.engine.attention_mode,
            pooling=self.engine.pooling,
            base_model=self.engine.base_model,
            base_revision=self.engine.revision,
            max_length=8192,
            max_options=255,
        )

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("pplx-decider has no native video request")
        if any(len(candidates(q)) > 255 for q in request["questions"].values()):
            raise Unsupported("Pplx-Decider release supports at most 255 options")
        rows = [
            {"state": state, "question": q, **({"images": images} if images else {})}
            for q in request["questions"].values()
        ]
        try:
            probabilities = self.engine.predict(rows)
        except ValueError as exc:
            from ..schema import is_capacity_error

            if is_capacity_error(str(exc)):
                raise Unsupported(str(exc)) from exc
            raise
        return {
            "answers": {
                qid: self.answer(q, p)
                for (qid, q), p in zip(request["questions"].items(), probabilities, strict=True)
            }
        }
