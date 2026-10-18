"""Keep datasets, media and temporary weights outside the source checkout."""
import os
from pathlib import Path

DEFAULT_ROOT = "/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit"


def data_root(root=None):
    return Path(root or os.environ.get("JEVALKIT_DATA_ROOT", DEFAULT_ROOT)).expanduser().resolve()
