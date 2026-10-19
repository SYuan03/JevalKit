"""Native ClefModel adapter."""

from .base import NativeRuntime
from ._utils import load_module
from .media import state_parts
from ..schema import Unsupported


class ClefModel(NativeRuntime):
    modalities = frozenset({"text", "image", "video"})

    def __init__(self, model, max_length=16384, **options):
        super().__init__(model, **options)
        self.module = load_module(self.folder / "joint_schema_model.py")
        self.engine, self.processor = self.module.load_release_model(str(self.folder), device=self.device)
        self.max_length = int(max_length)
        self.info.update(
            max_length=self.max_length, truncation="forbidden; full native encoding checked before forward"
        )

    def predict(self, request, *, media_root=None, assets=None):
        text, images, videos = state_parts(request["state"], media_root)
        payload = {"model": self.info["model"], "state": text, "questions": request["questions"]}
        if images:
            payload["images"] = images
        if videos:
            payload["videos"] = videos
        # The release's convenience wrapper silently slices state tokens. Use its
        # encoder, collation, model and answer helpers with a checked full input.
        encoded = self.module.encode_record(
            self.processor.tokenizer, payload, max_length=2**31 - 1, processor=self.processor
        )
        if len(encoded.input_ids) > self.max_length:
            raise Unsupported(
                f"Clef request has {len(encoded.input_ids)} tokens above {self.max_length}; truncation is forbidden"
            )
        import torch

        with torch.inference_mode():
            device = next(self.engine.parameters()).device
            batch = self.module.collate_records([encoded], self.processor.tokenizer.pad_token_id, device)
            logits = self.engine(batch)[0]
            answers = {
                q.question_id: self.module.systemone_answer(
                    request["questions"][q.question_id],
                    dict(zip(q.option_ids, values.float().softmax(-1).tolist(), strict=True)),
                )
                for q, values in zip(encoded.questions, logits, strict=True)
            }
        return {
            "model": self.info["model"],
            "answers": answers,
            "usage": {"input_tokens": len(encoded.input_ids), "output_tokens": 0},
        }
