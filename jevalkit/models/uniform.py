"""Native UniformModel adapter."""

from .base import DecisionModel


class UniformModel(DecisionModel):
    """Deterministic pipeline baseline, excluded from the model-family count."""

    modalities = frozenset({"text", "image", "video"})

    def __init__(self, **options):
        pass

    def predict(self, request, **kwargs):
        from ..schema import candidates, native_answer

        return {
            "answers": {
                qid: native_answer(q, {k: 1 / len(candidates(q)) for k in candidates(q)})
                for qid, q in request["questions"].items()
            }
        }
