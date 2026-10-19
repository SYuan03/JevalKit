"""Portable dataset, model and cache locations with explicit overrides."""

import os
from pathlib import Path


def data_root(root=None):
    default = Path.home() / ".cache" / "jevalkit"
    return Path(root or os.environ.get("JEVALKIT_DATA_ROOT", default)).expanduser().resolve()
