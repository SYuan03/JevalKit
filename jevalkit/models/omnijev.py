"""Native OmniJevModel adapter."""

from .base import NativeRuntime
from ._utils import render_questions
from .media import state_parts
from .provenance import inference_artifacts
from ..io import object_hash, sha256
from ..schema import Unsupported, candidates, native_answer


class OmniJevModel(NativeRuntime):
    modalities = frozenset({"image", "video"})

    def __init__(self, model, base_model, **options):
        super().__init__(model, **options)
        from mso.infer import MSO1

        self.engine = MSO1(str(self.folder), str(base_model))
        self.info.update(base_model=str(base_model), temperature=self.engine.temps, biases=self.engine.biases)
        self.info["base_artifacts_sha256"] = inference_artifacts(base_model)
        import shutil

        self.info["video_tools"] = {}
        for name in ("ffmpeg", "ffprobe"):
            path = shutil.which(name)
            self.info["video_tools"][name] = {"path": path, "sha256": sha256(path)} if path else None
        self.info["probability_policy"] = (
            "Choice conditional on supplied candidates; raw native abstention mass retained"
        )
        self.info["criteria_rendering"] = "JSON descriptions; Noul rubrics included in instructions"

    def predict(self, request, *, media_root=None, assets=None):
        from ..io import object_hash

        text, images, videos = state_parts(request["state"], media_root)
        if not images and not videos:
            raise Unsupported("OmniJev's released visual runtime requires image/video evidence")
        if videos:
            if len(videos) != 1 or images:
                raise Unsupported("OmniJev native video supports one clip")
            from mso.video import video_state

            folder = self.root / "cache" / "video"
            folder.mkdir(parents=True, exist_ok=True)
            state = video_state(videos[0], out_jpg=str(folder / (object_hash(videos[0]) + ".jpg")))
        else:
            state = {"images": images}
        questions = render_questions(request["questions"])
        for q in questions.values():
            if text:
                q["instructions"] = "State:\n" + text + "\nQuestion:\n" + q["instructions"]
            if q["type"] == "score":
                q["levels"] = [f"{k}: {v}" for k, v in candidates(q).items()]
        raw = self.engine.system_one(state, questions)
        return {
            "answers": {qid: omni_answer(request["questions"][qid], answer) for qid, answer in raw.items()},
            "native_answers": raw,
        }


def omni_answer(question, answer):
    """Close the release's explicit extra abstention outcome over benchmark options."""
    from ..schema import distribution

    keys = candidates(question)
    if question["type"] == "noul":
        return {"type": "noul", "noul": answer["noul"]}
    if question["type"] == "score":
        return native_answer(question, dict(zip(keys, answer["probabilities"].values(), strict=True)))
    probabilities = answer["probabilities"]
    if not probabilities and answer.get("abstain") == 1.0:
        return {"type": "refusal", "reason": "native_abstention"}
    sentinel = "__jeval_native_abstain__"
    while sentinel in keys:
        sentinel += "_"
    # Validate the complete native distribution before conditional normalization.
    full = distribution({**probabilities, sentinel: answer["abstain"]}, [*keys, sentinel], tolerance=0.02)
    total = sum(full[k] for k in keys)
    if total == 0:
        return {"type": "refusal", "reason": "native_abstention"}
    return native_answer(question, {k: full[k] / total for k in keys})
