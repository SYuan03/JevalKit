"""Published Valen releases via their native Hugging Face decision runtime."""
import copy
import os
from pathlib import Path

from .base import DecisionModel
from .provenance import inference_artifacts, runtime_versions
from ..io import dumps, sha256
from ..paths import data_root
from ..schema import Unsupported, is_message_state


def resolve_model(model, revision="main", root=None):
    path = Path(model).expanduser()
    if path.is_dir():
        return path.resolve()
    from huggingface_hub import snapshot_download
    destination = data_root(root) / "models" / model.replace("/", "--") / revision
    return Path(snapshot_download(model, revision=revision, local_dir=destination))


def render_criteria(questions):
    """Keep candidate identities/order while making description values textual."""
    out = copy.deepcopy(questions)
    for q in out.values():
        if not isinstance(q["instructions"], str):
            q["instructions"] = dumps(q["instructions"])
        if q["type"] == "choice":
            q["criteria"] = {k: k if v is None else v if isinstance(v, str) else dumps(v)
                             for k, v in q["criteria"].items()}
        elif q["type"] == "score":
            q["criteria"] = [v if isinstance(v, str) else dumps(v) for v in q["criteria"]]
        elif q["type"] == "noul":
            if not q.get("criteria"):
                q.pop("criteria", None)
            else:
                q["criteria"] = {k: k.capitalize() if v is None else v if isinstance(v, str) else dumps(v)
                                 for k, v in q["criteria"].items()}
    return out


def render_questions(questions):
    """Runtimes with an instruction-only Noul head receive its full rubric there."""
    out = render_criteria(questions)
    for q in out.values():
        if q["type"] == "noul" and "criteria" in q:
            criteria = q.pop("criteria")
            if criteria:
                q["instructions"] += "\nTrue criterion: " + str(criteria["true"]) + "\nFalse criterion: " + str(criteria["false"])
    return out


class ValenModel(DecisionModel):
    modalities = frozenset({"text", "image", "video"})

    def __init__(self, model="Valen-Team/Valen-0.8B", device="cuda", revision="main",
                 attention="sdpa", execution="shared_state", root=None, **options):
        os.environ.setdefault("HF_MODULES_CACHE", str(data_root(root) / "cache" / "modules"))
        from transformers import AutoModel
        import torch
        self.torch, self.device = torch, device
        self.folder = resolve_model(model, revision, root)
        self.model = AutoModel.from_pretrained(str(self.folder), trust_remote_code=True, dtype="auto",
                                               attn_implementation=attention, local_files_only=True).to(device).eval()
        self.execution = execution
        torch.set_float32_matmul_precision("highest")
        torch.backends.cudnn.allow_tf32 = False
        self.info = {"adapter": "ValenModel", "model": model, "revision": revision,
                     "path": str(self.folder), "execution": execution, "attention": attention,
                     "config_sha256": sha256(self.folder / "config.json"),
                     "dtype": str(next(self.model.parameters()).dtype), "temperature": 1.0,
                     "torch": torch.__version__, "cuda": torch.version.cuda,
                     "versions": runtime_versions(),
                     "hardware": torch.cuda.get_device_name(device) if device.startswith("cuda") else "cpu",
                     "artifacts_sha256": inference_artifacts(self.folder)}

    def predict(self, request, *, media_root=None, assets=None):
        request = copy.deepcopy(request)
        state = request["state"]
        if not isinstance(state, str) and not is_message_state(state):
            request["state"] = dumps(state)
        request["questions"] = render_questions(request["questions"])
        try:
            with self.torch.inference_mode():
                return self.model.predict(request, media_root=str(media_root or "."), execution=self.execution)
        except ValueError as exc:
            if "exceed max_length" in str(exc) or "Reserved tokenizer control token" in str(exc):
                raise Unsupported(str(exc)) from exc
            raise

    def synchronize(self):
        if self.device.startswith("cuda"):
            self.torch.cuda.synchronize(self.device)

    def metadata(self):
        return self.info

    def close(self):
        del self.model
        if self.device.startswith("cuda"):
            self.torch.cuda.empty_cache()
