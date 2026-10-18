"""Resolve local evidence without dropping any media or textual content."""
from pathlib import Path
from ..io import dumps
from ..schema import Unsupported


def state_parts(state, root=None):
    if isinstance(state, str):
        return state, [], []
    if not isinstance(state, dict) or "messages" not in state:
        return dumps(state), [], []
    text, images, videos = [], [], []
    for message in state["messages"]:
        content = message["content"]
        if isinstance(content, str):
            text.append(content)
            continue
        for part in content:
            kind = part["type"]
            if kind == "text":
                text.append(part["text"])
            elif kind in {"image_url", "video_url"}:
                url = part[kind]["url"]
                if url.startswith(("https://", "http://", "data:")):
                    raise Unsupported("Local native runtime requires materialized media files")
                path = str((Path(root or ".") / url).resolve(strict=True))
                (images if kind == "image_url" else videos).append(path)
            else:
                raise Unsupported("Unsupported evidence part: " + kind)
    return "\n".join(text), images, videos
