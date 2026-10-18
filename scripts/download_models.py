#!/usr/bin/env python3
"""Download pinned public model snapshots, retaining resumable files and LFS evidence."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jevalkit.io import atomic_json, sha256
from jevalkit.paths import data_root


def retryable_transfer_error(error):
    errors = (ConnectionError, TimeoutError)
    try:
        from httpx import TransportError
        errors += (TransportError,)
    except ImportError:
        pass
    try:
        from requests.exceptions import ChunkedEncodingError, ConnectionError as RequestsConnectionError, Timeout
        errors += (ChunkedEncodingError, RequestsConnectionError, Timeout)
    except ImportError:
        pass
    return isinstance(error, errors)


def download_with_resume(model, revision, folder, downloader, update, attempts=3, sleep=time.sleep):
    """Retry terminated network transfers in place; leave verification outside retries."""
    if attempts < 1:
        raise ValueError("Transfer attempts must be positive")
    for attempt in range(1, attempts + 1):
        update(model, state="downloading", transfer_attempt=attempt, error=None, retry_delay_seconds=0)
        try:
            return downloader(model, revision=revision, local_dir=folder, max_workers=2)
        except Exception as exc:
            if attempt == attempts or not retryable_transfer_error(exc):
                raise
            delay = min(2 ** attempt, 30)
            update(model, state="retrying", error=f"{type(exc).__name__}: {exc}",
                   retry_delay_seconds=delay)
            sleep(delay)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", help="JSON list of {model, revision, metadata} entries")
    parser.add_argument("--root")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--attempts", type=int, default=3, help="Bounded network transfer attempts per model")
    parser.add_argument("--status", required=True)
    args = parser.parse_args()
    entries = json.loads(Path(args.config).read_text())
    if args.workers < 1 or args.attempts < 1 or not entries:
        parser.error("A nonempty model list and positive worker/attempt counts are required")
    for entry in entries:
        if not re.fullmatch(r"[0-9a-f]{40}", entry["revision"]):
            parser.error("Every model must be pinned to a full Hub commit hash")
        metadata = json.loads(Path(entry["metadata"]).read_text())
        if metadata["id"] != entry["model"] or metadata["sha"] != entry["revision"]:
            parser.error("Saved Hub metadata does not match the requested model revision")
    status = {"models": {}, "config_sha256": sha256(args.config)}
    lock = threading.Lock()

    def update(model, **values):
        with lock:
            status["models"].setdefault(model, {}).update(values)
            status["updated_utc"] = datetime.now(timezone.utc).isoformat()
            atomic_json(args.status, status)
        print(json.dumps({"model": model, **values}), flush=True)

    def download(entry):
        from huggingface_hub import snapshot_download
        model, revision = entry["model"], entry["revision"]
        folder = data_root(args.root) / "models" / model.replace("/", "--") / revision
        update(model, state="downloading", revision=revision, path=str(folder))
        try:
            download_with_resume(model, revision, folder, snapshot_download, update, args.attempts)
            update(model, state="verifying")
            metadata = json.loads(Path(entry["metadata"]).read_text())
            hashes = {}
            for item in metadata["siblings"]:
                path = folder / item["rfilename"]
                if not path.is_file() or item.get("size") is not None and path.stat().st_size != item["size"]:
                    raise ValueError(f"Missing or incomplete file: {item['rfilename']}")
                if item.get("lfs", {}).get("sha256"):
                    digest = sha256(path)
                    if digest != item["lfs"]["sha256"]:
                        raise ValueError(f"LFS digest mismatch: {item['rfilename']}")
                    hashes[item["rfilename"]] = digest
            atomic_json(folder / "jevalkit-download.json", {"model": model, "revision": revision,
                        "metadata_sha256": sha256(entry["metadata"]), "lfs_sha256": hashes})
            update(model, state="complete", verified_lfs_files=len(hashes))
        except Exception as exc:
            update(model, state="failed", error=f"{type(exc).__name__}: {exc}")
            return False
        return True

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = [future.result() for future in as_completed([pool.submit(download, entry) for entry in entries])]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
