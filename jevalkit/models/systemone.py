"""Native author runtimes with explicit, versionable call conventions."""
import os
import sys
from pathlib import Path

from .base import DecisionModel
from .hf import render_criteria, render_questions, resolve_model
from .media import state_parts
from .native import load_module
from .provenance import cached_base_artifacts, inference_artifacts, runtime_versions
from ..io import sha256
from ..paths import data_root
from ..schema import Unsupported, candidates, native_answer


class NativeRuntime(DecisionModel):
    def __init__(self, model, device="cuda", revision="main", source=None, root=None, **options):
        import torch
        self.device = device
        self.folder = resolve_model(model, revision, root)
        self.root = data_root(root)
        self.options = options
        if source:
            source = str(Path(source).resolve())
            sys.path.insert(0, source)
        self.info = {"adapter": type(self).__name__, "model": model, "revision": revision,
                     "source": source, "path": str(self.folder), "device": device,
                     "hardware": torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
                     "versions": runtime_versions(), "cuda": torch.version.cuda,
                     "artifacts_sha256": inference_artifacts(self.folder),
                     "options": options}
        if source:
            source_root = Path(source)
            self.info["source_sha256"] = {str(p.relative_to(source_root)): sha256(p)
                for p in sorted(source_root.rglob("*.py"))
                if not {".git", ".venv", "__pycache__"}.intersection(p.parts)}

    def synchronize(self):
        if self.device.startswith("cuda"):
            import torch
            torch.cuda.synchronize(self.device)

    def metadata(self):
        return self.info

    def close(self):
        if hasattr(self, "engine"):
            del self.engine
        if self.device.startswith("cuda"):
            import torch
            torch.cuda.empty_cache()


class HFSystemOne(NativeRuntime):
    """Liquid d1 and vLLM Decision-1 ship AutoModel.system_one(state, questions)."""
    modalities = frozenset({"text", "image"})

    def __init__(self, model, image_support=True, max_score_levels=None, requires_nonempty_state=False, **options):
        os.environ.setdefault("HF_MODULES_CACHE", str(data_root(options.get("root")) / "cache" / "modules"))
        super().__init__(model, **options)
        from transformers import AutoModel
        self.image_support = image_support
        self.max_score_levels = max_score_levels
        self.requires_nonempty_state = bool(requires_nonempty_state)
        self.modalities = frozenset({"text", "image"} if image_support else {"text"})
        self.engine = AutoModel.from_pretrained(str(self.folder), trust_remote_code=True,
                                                local_files_only=True, dtype="auto").to(self.device).eval()
        self.info["image_support"] = bool(image_support)
        self.info["max_score_levels"] = max_score_levels
        self.info["requires_nonempty_state"] = self.requires_nonempty_state

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if videos or images and not self.image_support:
            raise Unsupported("This native release cannot represent the supplied media")
        if self.max_score_levels is not None and any(q["type"] == "score" and len(q["criteria"]) > self.max_score_levels
                                                    for q in request["questions"].values()):
            raise Unsupported(f"This native release supports at most {self.max_score_levels} score levels")
        if not text.strip() and not images and self.requires_nonempty_state:
            raise Unsupported("This native release requires a nonempty state; no placeholder evidence was inserted")
        import torch
        if images:
            from PIL import Image
            loaded = []
            for path in images:
                with Image.open(path) as image:
                    loaded.append(image.convert("RGB"))
            images = loaded
        kwargs = {"images": images} if images else {}
        with torch.inference_mode():
            result = self.engine.system_one(state=text, questions=request["questions"], **kwargs)
        return result


class ClefModel(NativeRuntime):
    modalities = frozenset({"text", "image", "video"})

    def __init__(self, model, max_length=16384, **options):
        super().__init__(model, **options)
        self.module = load_module(self.folder / "joint_schema_model.py")
        self.engine, self.processor = self.module.load_release_model(str(self.folder), device=self.device)
        self.max_length = int(max_length)
        self.info.update(max_length=self.max_length, truncation="forbidden; full native encoding checked before forward")

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        payload = {"model": self.info["model"], "state": text, "questions": request["questions"]}
        if images:
            payload["images"] = images
        if videos:
            payload["videos"] = videos
        # The release's convenience wrapper silently slices state tokens. Use its
        # encoder, collation, model and answer helpers with a checked full input.
        encoded = self.module.encode_record(self.processor.tokenizer, payload,
                                             max_length=2 ** 31 - 1, processor=self.processor)
        if len(encoded.input_ids) > self.max_length:
            raise Unsupported(f"Clef request has {len(encoded.input_ids)} tokens above {self.max_length}; truncation is forbidden")
        import torch
        with torch.inference_mode():
            device = next(self.engine.parameters()).device
            batch = self.module.collate_records([encoded], self.processor.tokenizer.pad_token_id, device)
            logits = self.engine(batch)[0]
            answers = {q.question_id: self.module.systemone_answer(
                request["questions"][q.question_id],
                dict(zip(q.option_ids, values.float().softmax(-1).tolist(), strict=True)))
                for q, values in zip(encoded.questions, logits, strict=True)}
        return {"model": self.info["model"], "answers": answers,
                "usage": {"input_tokens": len(encoded.input_ids), "output_tokens": 0}}


class PplxDecider(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        sys.path.insert(0, str(self.folder / "source" / "src"))
        from autojev.model import DecisionModel, answer
        self.engine = DecisionModel(self.folder, device=self.device)
        self.answer = answer
        self.info.update(temperature=self.engine.temperature, attention_mode=self.engine.attention_mode,
                         pooling=self.engine.pooling, base_model=self.engine.base_model,
                         base_revision=self.engine.revision, max_length=8192, max_options=255)

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("pplx-decider has no native video request")
        if any(len(candidates(q)) > 255 for q in request["questions"].values()):
            raise Unsupported("Pplx-Decider release supports at most 255 options")
        rows = [{"state": state, "question": q, **({"images": images} if images else {})}
                for q in request["questions"].values()]
        try:
            probabilities = self.engine.predict(rows)
        except ValueError as exc:
            from ..schema import is_capacity_error
            if is_capacity_error(str(exc)):
                raise Unsupported(str(exc)) from exc
            raise
        return {"answers": {qid: self.answer(q, p) for (qid, q), p in zip(request["questions"].items(), probabilities, strict=True)}}


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
        self.info.update(temperature=self.engine.temperature, method=self.engine.method,
                         knockout_temperature=self.engine.knockout_temperature,
                         cuda_graphs=bool(self.engine.graphs), execution="author SDK per question")

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if images or videos:
            raise Unsupported("JevK5 supports text inputs only")
        return {"answers": {qid: self.engine.decide(text, q) for qid, q in request["questions"].items()}}


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
        self.info.update(allow_slow=bool(allow_slow), fast_kernels=self.engine.fast_kernels,
                         cuda_graphs=bool(self.engine.graphs), temperature=self.engine.temperature,
                         max_score_levels=10, prefix_sharing=bool(share_prefix))

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("StartLux release has no native video input")
        if any(q["type"] == "score" and len(q["criteria"]) > 10 for q in request["questions"].values()):
            raise Unsupported("StartLux release supports at most 10 score levels; all levels were retained")
        answers, usage = self.engine.decide(state, request["questions"], images=images or None)
        return {"answers": answers, "usage": usage}


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


class RSIJevModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        os.environ["RSIJEV_DOC_CACHE"] = "0"
        os.environ["RSIJEV_VISION_CACHE"] = "0"
        from rsijev import Decider
        self.engine = Decider(str(self.folder), device=self.device, dtype="bf16", batch_size=16)
        self.info.update(calibration=self.engine.calibration, image_limits=self.engine.image_limits,
                         base_model=self.engine.served.meta.get("base_model"))
        from dataclasses import asdict, replace
        self.engine.served.enc = replace(self.engine.served.enc, truncate="none")
        if self.engine.served.venc is not None:
            self.engine.served.venc = replace(self.engine.served.venc, truncate="none")
        self.info["encoding"] = asdict(self.engine.served.enc)
        meta = self.engine.served.meta
        self.info["base"] = cached_base_artifacts(meta["base_model"], (meta.get("vision") or {}).get("revision"))

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
            cut = any(cut.get(key, 0) for key in
                      ("state_tokens_omitted", "option_desc_tokens_omitted", "question_tokens_omitted"))
        if cut:
            raise Unsupported("RSI-Jev reported truncated evidence; the partial answer was excluded")
        return response


class VjevModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        self.module = load_module(self.folder / "vjev_infer.py")
        self.engine = self.module.Vjev(str(self.folder), device=self.device)
        self.info["max_length"] = self.engine.meta.get("max_len", 2560) + 1536
        self.info["criteria_rendering"] = "JSON descriptions; null Choice uses its ID; Noul rubrics included in instructions"

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("Vjev has no native video input")
        class LiteralText:
            def __str__(self):
                return text
        try:
            answers = self.engine.ask([*images, LiteralText()], render_questions(request["questions"]), batch_rows=8)
        except ValueError as exc:
            from ..schema import is_capacity_error
            if is_capacity_error(str(exc)):
                raise Unsupported(str(exc)) from exc
            raise
        return {"answers": answers}


class QEVModel(NativeRuntime):
    modalities = frozenset({"text", "image"})

    def __init__(self, model, **options):
        super().__init__(model, **options)
        from veyra.option_model import OptionModel
        from veyra.schema import DecisionRequest
        from veyra.constants import MODEL_ID, MODEL_REVISION
        self.engine = OptionModel.load(self.folder, device=self.device,
                                       cache_dir=str(self.root / "cache" / "hf" / "hub"),
                                       local_files_only=True, merge=True)
        self.request_type = DecisionRequest
        self.info["calibration"] = self.engine.calibration.to_dict()
        self.info["encoding"] = self.engine.encoder.config.to_dict()
        self.info["base"] = cached_base_artifacts(MODEL_ID, MODEL_REVISION,
                                                   str(self.root / "cache" / "hf" / "hub"))
        self.info.update(max_options=16, max_images=1, max_state_characters=100000,
                         criteria_rendering="JSON descriptions; null Choice uses its ID",
                         execution="one native SDK request per question; full state retained")

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
                native = self.request_type.model_validate({"state": {"text": state, "images": [{"path": p} for p in images]},
                                                           "questions": {"decision": rendered}})
            except ValidationError as exc:
                # Only published representational limits qualify as unsupported.
                errors = exc.errors()
                allowed = {"too_long", "string_too_long", "string_too_short", "string_pattern_mismatch"}
                if all(error["type"] in allowed or error["type"] == "value_error" and
                       any(message in error["msg"] for message in
                           ("choice descriptions must be distinct", "state must contain nonempty text"))
                       for error in errors):
                    raise Unsupported("QEV native request constraints: " + str(exc)) from exc
                raise
            answer = self.engine.predict(native)["answers"]["decision"]
            if q["type"] == "score":
                answer["probabilities"] = dict(zip(candidates(q), answer["probabilities"].values(), strict=True))
            result[qid] = answer
        return {"answers": result}


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
        self.info["probability_policy"] = "Choice conditional on supplied candidates; raw native abstention mass retained"
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
        return {"answers": {qid: omni_answer(request["questions"][qid], answer) for qid, answer in raw.items()},
                "native_answers": raw}


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
    full = distribution({**probabilities, sentinel: answer["abstain"]}, [*keys, sentinel], tolerance=.02)
    total = sum(full[k] for k in keys)
    if total == 0:
        return {"type": "refusal", "reason": "native_abstention"}
    return native_answer(question, {k: full[k] / total for k in keys})


class VisualJevModel(NativeRuntime):
    """Paper author's VDM + answer-SFT readout, with typed questions as candidates."""
    modalities = frozenset({"image"})

    def __init__(self, model, base_model, **options):
        super().__init__(model, **options)
        import torch
        from vdm.models.vdm_model import VDM
        from peft import PeftModel
        self.engine = VDM(str(base_model), device=self.device, dtype=torch.bfloat16, with_heads=False)
        self.engine.processor.image_processor.max_pixels = 200704
        self.engine.backbone = PeftModel.from_pretrained(self.engine.backbone, str(self.folder)).eval()
        self.info.update(base_model=str(base_model), base_artifacts_sha256=inference_artifacts(base_model),
                         image_max_pixels=200704)
        self.info["typed_mapping"] = "Noul and Score expanded as fixed candidates; native LM-head logits"

    def predict(self, request, *, media_root=None, assets=None):
        from PIL import Image
        text, images, videos = state_parts(request["state"], media_root)
        if len(images) != 1 or videos:
            raise Unsupported("Visual Jev paper release requires exactly one image")
        questions = request["questions"]
        specs = [{"qtype": "choice", "instruction": q["instructions"],
                  "candidates": [f"{k}: {v}" for k, v in candidates(q).items()]} for q in questions.values()]
        with Image.open(images[0]) as image:
            group = self.engine.prepare_group(image.convert("RGB"), specs, shared_context=text)
        result = self.engine.run_prefix_share_batch(group)
        answers = {}
        for i, (qid, q) in enumerate(questions.items()):
            values = result["lm_option_logits"][i, :len(candidates(q))].float().softmax(-1).cpu().tolist()
            answers[qid] = native_answer(q, dict(zip(candidates(q), values, strict=True)))
        return {"answers": answers}
