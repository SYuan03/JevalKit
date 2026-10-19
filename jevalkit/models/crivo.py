"""Native CrivoModel adapter."""

from .base import NativeRuntime
from ._utils import load_module
from .media import state_parts
from ..schema import Unsupported


class CrivoModel(NativeRuntime):
    def __init__(self, model, **options):
        super().__init__(model, **options)
        module = load_module(self.folder / "decision_index_engine.py")
        self.engine = module.DecisionEngine(path=str(self.folder), device=self.device)

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if images or videos or any(q["type"] == "score" for q in request["questions"].values()):
            raise Unsupported("Crivo's released Decision Index engine supports text Choice/Noul only")
        from decision_index.engines import Unsupported as NativeUnsupported

        try:
            return self.engine(state, request["questions"])[0]
        except NativeUnsupported as exc:
            raise Unsupported(str(exc)) from exc
