import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("jeval_download_models", Path(__file__).parents[1] / "scripts/download_models.py")
downloads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(downloads)


def test_interrupted_transfer_reuses_partial_file_and_pinned_identity(tmp_path):
    httpx = pytest.importorskip("httpx")
    partial = tmp_path / "model.safetensors.incomplete"
    calls, events, delays = [], [], []
    revision = "a" * 40

    def fetch(model, **options):
        calls.append((model, options))
        if len(calls) == 1:
            partial.write_bytes(b"first part")
            raise httpx.RemoteProtocolError("peer closed connection without sending complete message body")
        assert partial.read_bytes() == b"first part"
        partial.write_bytes(partial.read_bytes() + b" remainder")
        return tmp_path

    result = downloads.download_with_resume("Author/Model", revision, tmp_path, fetch,
        lambda model, **event: events.append(event), sleep=delays.append)
    assert result == tmp_path and partial.read_bytes() == b"first part remainder"
    assert calls == [("Author/Model", {"revision": revision, "local_dir": tmp_path, "max_workers": 2})] * 2
    assert any(e["state"] == "retrying" for e in events) and len(delays) == 1
    assert events[-1]["state"] == "downloading" and events[-1]["error"] is None


def test_download_retries_are_bounded(tmp_path):
    calls = []
    def fetch(*args, **kwargs):
        calls.append(1)
        raise TimeoutError("disconnected")
    with pytest.raises(TimeoutError, match="disconnected"):
        downloads.download_with_resume("Author/Model", "a" * 40, tmp_path, fetch,
                                      lambda *a, **kw: None, attempts=3, sleep=lambda _: None)
    assert len(calls) == 3


@pytest.mark.parametrize("error", [ValueError("checksum mismatch"), OSError(28, "No space left on device")])
def test_permanent_download_failures_do_not_repeat(tmp_path, error):
    calls = []
    def fetch(*args, **kwargs):
        calls.append(1)
        raise error
    with pytest.raises(type(error)):
        downloads.download_with_resume("Author/Model", "a" * 40, tmp_path, fetch,
                                      lambda *a, **kw: None, sleep=lambda _: pytest.fail("Unexpected retry"))
    assert len(calls) == 1
