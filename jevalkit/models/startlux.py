"""Official StartLux v1 native and v1.1 Instant HTTP adapters."""

import copy
import os
import sys
from ._http import HttpDecisionModel, media_data_url
from .base import NativeRuntime
from .media import state_parts
from ..schema import Unsupported, is_message_state


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
        self.info.update(
            allow_slow=bool(allow_slow),
            fast_kernels=self.engine.fast_kernels,
            cuda_graphs=bool(self.engine.graphs),
            temperature=self.engine.temperature,
            max_score_levels=10,
            prefix_sharing=bool(share_prefix),
        )

    def predict(self, request, *, media_root=None, assets=None):
        state, images, videos = state_parts(request["state"], media_root)
        if videos:
            raise Unsupported("StartLux release has no native video input")
        if any(q["type"] == "score" and len(q["criteria"]) > 10 for q in request["questions"].values()):
            raise Unsupported("StartLux release supports at most 10 score levels; all levels were retained")
        answers, usage = self.engine.decide(state, request["questions"], images=images or None)
        return {"answers": answers, "usage": usage}


class StartLuxInstant(HttpDecisionModel):
    """v1.1 Instant through the author's server; no local readout reimplementation."""

    def __init__(self, endpoint, model, token_env="STARTLUX_API_KEY", timeout=120,
                 retries=3, server_manifest=None, expected_response_model=None, root=None):
        super().__init__(endpoint=endpoint, model=model, token_env=token_env,
                         timeout=timeout, retries=retries, media_format="top_level",
                         server_manifest=server_manifest)
        # The official server ignores the request's model field. Check its reply
        # rather than silently attributing another deployment's answers to this ID.
        self.expected_response_model = expected_response_model or model.rsplit("/", 1)[-1]

    def build_payload(self, request, *, media_root=None):
        state = copy.deepcopy(request["state"])
        images = []
        if is_message_state(state):
            parts = []
            for message in state["messages"]:
                if message["role"] != "user":
                    raise Unsupported("StartLux decision input supports user messages only")
                content = message["content"]
                if isinstance(content, str):
                    parts.append(content)
                    continue
                for part in content:
                    kind = part["type"]
                    if kind == "text":
                        parts.append(part["text"])
                    elif kind == "image_url":
                        url = part["image_url"]["url"]
                        if url.startswith(("https://", "http://")):
                            raise Unsupported("Materialize StartLux images locally or use image data URIs")
                        encoded = media_data_url(url, media_root)
                        if not encoded.startswith("data:image/"):
                            raise Unsupported("StartLux images require an image MIME type")
                        images.append(encoded)
                        parts.append("<image>")
                    elif kind == "video_url":
                        raise Unsupported("StartLux Instant has no native video input")
                    else:
                        raise Unsupported("Unsupported StartLux evidence part: " + kind)
            state = "\n".join(parts)
            if state.count("<image>") != len(images):
                raise Unsupported("Ambiguous StartLux image markers; no evidence was removed")
        if len(images) > 8:
            raise Unsupported("StartLux Instant supports at most 8 images; all images were retained")
        for question in request["questions"].values():
            if question["type"] == "score" and not 2 <= len(question["criteria"]) <= 10:
                raise Unsupported("StartLux Instant supports 2 to 10 score levels; all levels were retained")
        payload = {
            "model": self.model,
            # Keep JSON states structured: the author's server owns rendering.
            "state": state,
            "questions": copy.deepcopy(request["questions"]),
            "think_mode": "never",
            "allow_none": False,
            "none_check": True,
        }
        if images:
            payload["images"] = images
        return payload

    def predict(self, request, *, media_root=None, assets=None):
        response = self.post(self.build_payload(request, media_root=media_root))
        if response.get("model") != self.expected_response_model:
            raise ValueError("StartLux server model does not match expected_response_model")
        return response

    def metadata(self):
        return {
            **super().metadata(),
            "expected_response_model": self.expected_response_model,
            "request_controls": {"think_mode": "never", "allow_none": False, "none_check": True},
            "max_images": 8,
            "max_score_levels": 10,
        }
