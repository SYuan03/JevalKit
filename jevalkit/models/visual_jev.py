"""Native VisualJevModel adapter."""

from .base import NativeRuntime
from .media import state_parts
from .provenance import inference_artifacts
from ..schema import Unsupported, candidates, native_answer


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
        self.info.update(
            base_model=str(base_model),
            base_artifacts_sha256=inference_artifacts(base_model),
            image_max_pixels=200704,
        )
        self.info["typed_mapping"] = "Noul and Score expanded as fixed candidates; native LM-head logits"

    def predict(self, request, *, media_root=None, assets=None):
        from PIL import Image

        text, images, videos = state_parts(request["state"], media_root)
        if len(images) != 1 or videos:
            raise Unsupported("Visual Jev paper release requires exactly one image")
        questions = request["questions"]
        specs = [
            {
                "qtype": "choice",
                "instruction": q["instructions"],
                "candidates": [f"{k}: {v}" for k, v in candidates(q).items()],
            }
            for q in questions.values()
        ]
        with Image.open(images[0]) as image:
            group = self.engine.prepare_group(image.convert("RGB"), specs, shared_context=text)
        result = self.engine.run_prefix_share_batch(group)
        answers = {}
        for i, (qid, q) in enumerate(questions.items()):
            values = result["lm_option_logits"][i, : len(candidates(q))].float().softmax(-1).cpu().tolist()
            answers[qid] = native_answer(q, dict(zip(candidates(q), values, strict=True)))
        return {"answers": answers}
