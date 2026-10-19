"""Native QEVModel adapter."""

from .base import NativeRuntime
from ._utils import render_criteria
from .media import state_parts
from .provenance import cached_base_artifacts
from ..schema import Unsupported, candidates


class QEVModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        from veyra.option_model import OptionModel
        from veyra.schema import DecisionRequest
        from veyra.constants import MODEL_ID, MODEL_REVISION

        self.engine = OptionModel.load(
            self.folder,
            device=self.device,
            cache_dir=str(self.root / "cache" / "hf" / "hub"),
            local_files_only=True,
            merge=True,
        )
        self.request_type = DecisionRequest
        self.info["calibration"] = self.engine.calibration.to_dict()
        self.info["encoding"] = self.engine.encoder.config.to_dict()
        self.info["base"] = cached_base_artifacts(
            MODEL_ID, MODEL_REVISION, str(self.root / "cache" / "hf" / "hub")
        )
        self.info.update(
            max_options=16,
            max_images=1,
            max_state_characters=100000,
            criteria_rendering="JSON descriptions; null Choice uses its ID",
            execution="one native SDK request per question; full state retained",
        )

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("QEV supports native text and images only")
        if len(images) > 1 or len(state) > 100000:
            raise Unsupported("QEV release supports at most one image and 100000 state characters")
        for q in request["questions"].values():
            if q["type"] != "noul" and len(q["criteria"]) > 16:
                raise Unsupported("QEV release supports at most 16 options; no candidates were removed")
        from pydantic import ValidationError

        result = {}
        for qid, q in request["questions"].items():
            rendered = render_criteria({qid: q})[qid]
            try:
                native = self.request_type.model_validate(
                    {
                        "state": {"text": state, "images": [{"path": p} for p in images]},
                        "questions": {"decision": rendered},
                    }
                )
            except ValidationError as exc:
                # Only published representational limits qualify as unsupported.
                errors = exc.errors()
                allowed = {"too_long", "string_too_long", "string_too_short", "string_pattern_mismatch"}
                if all(
                    error["type"] in allowed
                    or error["type"] == "value_error"
                    and any(
                        message in error["msg"]
                        for message in (
                            "choice descriptions must be distinct",
                            "state must contain nonempty text",
                        )
                    )
                    for error in errors
                ):
                    raise Unsupported("QEV native request constraints: " + str(exc)) from exc
                raise
            answer = self.engine.predict(native)["answers"]["decision"]
            if q["type"] == "score":
                answer["probabilities"] = dict(
                    zip(candidates(q), answer["probabilities"].values(), strict=True)
                )
            result[qid] = answer
        return {"answers": result}
