from ..schema import Unsupported


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


class UniformModel(DecisionModel):
    """Deterministic pipeline baseline, excluded from the model-family count."""
    modalities = frozenset({"text", "image", "video"})

    def __init__(self, **options):
        pass

    def predict(self, request, **kwargs):
        from ..schema import candidates, native_answer
        return {"answers": {qid: native_answer(q, {k: 1 / len(candidates(q)) for k in candidates(q)})
                            for qid, q in request["questions"].items()}}
