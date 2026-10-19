"""Synthetic v1.1 Instant contracts; no model weights or benchmark scores."""

import copy
import json

import pytest

from jevalkit.config import MODELS, build_model
from jevalkit.models.startlux import StartLuxInstant
from jevalkit.schema import Unsupported


CHECKPOINT = "startlux-models/StartLux-Decision-v1.1-4B-Instant"


@pytest.fixture
def source():
    return {
        "state": {"items": [{"id": i} for i in range(8)], "missing": None, "enabled": False},
        "questions": {
            "route": {"type": "choice", "instructions": "Route the ticket",
                      "criteria": {"billing": None, "support": {"team": "technical"}}},
            "check": {"type": "noul", "instructions": "Is this urgent?",
                      "criteria": {"true": "Needs attention", "false": "Can wait"}},
            "severity": {"type": "score", "instructions": "Rate severity", "criteria": ["low", "high"]},
        },
    }


@pytest.fixture
def model():
    return StartLuxInstant(endpoint="http://127.0.0.1:8090/v1/systemone", model=CHECKPOINT)


@pytest.mark.parametrize("size", ["0.8B", "2B", "4B", "9B", "27B"])
def test_instant_variants_register_separately(size, monkeypatch, tmp_path):
    monkeypatch.setenv("STARTLUX_ENDPOINT", "http://127.0.0.1:8090/v1/systemone")
    name = f"StartLux-v1.1-{size}-Instant"
    instance = build_model(name, root=tmp_path)
    assert isinstance(instance, StartLuxInstant)
    assert MODELS[name].family == "StartLux" and MODELS[name].transport == "http"
    assert instance.model == f"startlux-models/StartLux-Decision-v1.1-{size}-Instant"
    assert instance.expected_response_model == instance.model.split("/")[-1]
    assert MODELS["StartLux-0.8B"].model == "startlux-models/StartLux-Decision-v1-0.8B"
    assert MODELS["StartLux-0.8B"].transport == "native"


def test_payload_keeps_json_questions_and_original_order(model, source):
    before = copy.deepcopy(source)
    payload = model.build_payload(source)
    assert payload["state"] == source["state"]
    assert isinstance(payload["state"], dict)  # Server, not adapter, renders structured states.
    assert list(payload["questions"]) == ["route", "check", "severity"]
    assert payload["questions"] == source["questions"]
    assert list(payload["questions"]["route"]["criteria"]) == ["billing", "support"]
    assert {k: payload[k] for k in ("think_mode", "allow_none", "none_check")} == {
        "think_mode": "never", "allow_none": False, "none_check": True,
    }
    payload["state"]["enabled"] = True
    payload["questions"]["route"]["criteria"]["billing"] = "Changed copy"
    assert source == before


def test_native_response_is_retained_without_probability_rewrite(model, source, monkeypatch):
    native = {
        "model": model.expected_response_model,
        "answers": {
            "route": {"type": "choice", "choice": "support", "confidence": 0.6,
                      "probabilities": {"billing": 0.2, "support": 0.8}, "none_probability": 0.13},
            "check": {"type": "noul", "noul": 0.75},
            "severity": {"type": "score", "score": 0.6,
                         "probabilities": {"0": 0.4, "1": 0.6}},
        },
        "usage": {"input_tokens": 32, "output_tokens": 0},
        "timing_ms": {"wall": 12.5},
    }
    calls = []

    def post(payload):
        calls.append(payload)
        return native

    monkeypatch.setattr(model, "post", post)
    assert model.predict(source) is native
    assert calls == [model.build_payload(source)]


@pytest.mark.parametrize("reply_model", [None, "StartLux-Decision-v1-0.8B"])
def test_wrong_or_missing_server_model_cannot_be_attributed(model, source, monkeypatch, reply_model):
    monkeypatch.setattr(model, "post", lambda payload: {"model": reply_model, "answers": {}})
    with pytest.raises(ValueError, match="server model"):
        model.predict(source)


def message_state(parts, role="user"):
    return {"messages": [{"role": role, "content": parts}]}


def test_interleaved_images_keep_positions_and_data(model, source, tmp_path):
    (tmp_path / "photo.png").write_bytes(b"synthetic image fixture")
    source["state"] = message_state([
        {"type": "text", "text": "Before"},
        {"type": "image_url", "image_url": {"url": "photo.png"}},
        {"type": "text", "text": "Between"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64,YQ=="}},
        {"type": "text", "text": "After"},
    ])
    before = copy.deepcopy(source)
    payload = model.build_payload(source, media_root=tmp_path)
    assert payload["state"] == "Before\n<image>\nBetween\n<image>\nAfter"
    assert payload["images"][0].startswith("data:image/png;base64,")
    assert payload["images"][1] == "data:image/png;base64,YQ=="
    assert source == before


@pytest.mark.parametrize("state,reason", [
    (message_state([{"type": "video_url", "video_url": {"url": "missing.mp4"}}]), "video"),
    (message_state("Private", role="system"), "user messages"),
    (message_state([{"type": "image_url", "image_url": {"url": "https://example.com/a.png"}}]),
     "Materialize"),
    (message_state([{"type": "image_url", "image_url": {"url": "data:text/plain;base64,YQ=="}}]),
     "MIME"),
    (message_state([{"type": "text", "text": "<image>"}]), "Ambiguous"),
    (message_state([{"type": "image_url", "image_url": {"url": "data:image/png;base64,YQ=="}}] * 9),
     "8 images"),
])
def test_unsupported_evidence_never_reaches_server(model, source, monkeypatch, state, reason):
    source["state"] = state
    before = copy.deepcopy(source)
    monkeypatch.setattr(model, "post", lambda _: pytest.fail("Unsupported evidence reached the server"))
    with pytest.raises(Unsupported, match=reason):
        model.predict(source)
    assert source == before


def test_score_capacity_is_explicit_without_removing_levels(model, source):
    source["questions"]["severity"]["criteria"] = [str(i) for i in range(11)]
    before = copy.deepcopy(source)
    with pytest.raises(Unsupported, match="2 to 10"):
        model.build_payload(source)
    assert source == before


def test_metadata_records_controls_and_custom_server_name(source, monkeypatch):
    instance = StartLuxInstant(
        endpoint="http://127.0.0.1:8090/v1/systemone", model=CHECKPOINT,
        expected_response_model="local-4b-instant",
    )
    monkeypatch.setattr(instance, "post", lambda _: {"model": "local-4b-instant", "answers": {}})
    assert instance.predict(source)["model"] == "local-4b-instant"
    metadata = instance.metadata()
    assert metadata["model"] == CHECKPOINT
    assert metadata["expected_response_model"] == "local-4b-instant"
    assert metadata["request_controls"] == {
        "think_mode": "never", "allow_none": False, "none_check": True,
    }
    metadata["request_controls"]["allow_none"] = True
    assert instance.metadata()["request_controls"]["allow_none"] is False
    assert json.loads(json.dumps(instance.metadata())) == instance.metadata()


def test_unknown_or_thinking_options_are_not_silently_ignored():
    with pytest.raises(TypeError, match="think_mode"):
        StartLuxInstant(endpoint="http://localhost:8090/v1/systemone", model=CHECKPOINT, think_mode="auto")
