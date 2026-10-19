"""Native VjevModel adapter."""

from .base import NativeRuntime
from ._utils import render_questions, load_module
from .media import state_parts
from ..schema import Unsupported


class VjevModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        self.module = load_module(self.folder / "vjev_infer.py")
        self.engine = self.module.Vjev(str(self.folder), device=self.device)
        self.info["max_length"] = self.engine.meta.get("max_len", 2560) + 1536
        self.info["criteria_rendering"] = (
            "JSON descriptions; null Choice uses its ID; Noul rubrics included in instructions"
        )

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("Vjev has no native video input")

        class LiteralText:
            def __str__(self):
                return text

        try:
            answers = self.engine.ask(
                [*images, LiteralText()], render_questions(request["questions"]), batch_rows=8
            )
        except ValueError as exc:
            from ..schema import is_capacity_error

            if is_capacity_error(str(exc)):
                raise Unsupported(str(exc)) from exc
            raise
        return {"answers": answers}
