"""Native JevK5Model adapter."""

from .base import NativeRuntime
from .media import state_parts
from ..schema import Unsupported


class JevK5Model(NativeRuntime):
    def __init__(self, model, graphs=True, **options):
        super().__init__(model, **options)
        from jevk5 import JevK5
        import inspect

        parameters = inspect.signature(JevK5).parameters
        kwargs = {"device": self.device} if "device" in parameters else {}
        if "graphs" in parameters:
            kwargs["graphs"] = graphs
        self.engine = JevK5(str(self.folder), **kwargs)
        self.info.update(
            temperature=self.engine.temperature,
            method=self.engine.method,
            knockout_temperature=self.engine.knockout_temperature,
            cuda_graphs=bool(self.engine.graphs),
            execution="author SDK per question",
        )

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if images or videos:
            raise Unsupported("JevK5 supports text inputs only")
        return {"answers": {qid: self.engine.decide(text, q) for qid, q in request["questions"].items()}}
