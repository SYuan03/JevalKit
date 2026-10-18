"""Content identities for weights, tokenizer/configuration and native source files."""
from pathlib import Path

from ..io import sha256


def runtime_versions():
    from importlib.metadata import PackageNotFoundError, version
    versions = {}
    for package in ("torch", "transformers", "torchvision", "Pillow", "safetensors", "accelerate",
                    "peft", "huggingface-hub", "flash-linear-attention", "causal-conv1d", "triton"):
        try:
            versions[package] = version(package)
        except PackageNotFoundError:
            pass
    return versions


def inference_artifacts(folder):
    folder = Path(folder)
    suffixes = {".safetensors", ".pt", ".pth", ".bin", ".json", ".py", ".model", ".txt", ".jinja", ".tiktoken"}
    ignored = {".git", ".cache", ".venv", "__pycache__"}
    return {str(path.relative_to(folder)): sha256(path)
            for path in sorted(folder.rglob("*"))
            if path.is_file() and path.suffix in suffixes
            and not ignored.intersection(path.relative_to(folder).parts)
            and not path.name.startswith("jevalkit-")}


def cached_base_artifacts(model, revision=None, cache_dir=None):
    """Locate the already-loaded base without triggering another Hub download."""
    folder = Path(model)
    if not folder.is_dir():
        from huggingface_hub import try_to_load_from_cache
        config = try_to_load_from_cache(model, "config.json", revision=revision, cache_dir=cache_dir)
        if not isinstance(config, str):
            raise ValueError("Cannot identify the loaded base model in its offline cache: " + model)
        folder = Path(config).parent
    return {"model": model, "revision": revision, "path": str(folder),
            "artifacts_sha256": inference_artifacts(folder)}
