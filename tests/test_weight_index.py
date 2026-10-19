import json
import struct

import pytest

from jevalkit.models import h2o_lightning as module


def weight_file(path, name):
    header = json.dumps({name: {"dtype": "F32", "shape": [1], "data_offsets": [0, 4]}}).encode()
    header += b" " * (-len(header) % 8)
    path.write_bytes(struct.pack("<Q", len(header)) + header + struct.pack("<f", 1.0))


def test_backbone_index_keeps_auxiliary_readout_intact_and_outside_loader(tmp_path):
    backbone, auxiliary = tmp_path / "model.safetensors", tmp_path / "label_rows.safetensors"
    weight_file(backbone, "model.weight")
    weight_file(auxiliary, "W")
    before = backbone.read_bytes(), auxiliary.read_bytes()
    index = module.prepare_index(tmp_path, ["model.safetensors"])
    assert index["weight_map"] == {"model.weight": "model.safetensors"}
    assert index["metadata"]["total_size"] == 4
    assert (backbone.read_bytes(), auxiliary.read_bytes()) == before
    assert module.prepare_index(tmp_path, ["model.safetensors"]) == index


def test_index_rejects_conflicting_selection_and_duplicate_tensor_keys(tmp_path):
    weight_file(tmp_path / "model.safetensors", "weight")
    weight_file(tmp_path / "extra.safetensors", "other")
    original = module.prepare_index(tmp_path, ["model.safetensors"])
    with pytest.raises(ValueError, match="different weight index"):
        module.prepare_index(tmp_path, ["extra.safetensors"])
    assert json.loads((tmp_path / "model.safetensors.index.json").read_text()) == original
    weight_file(tmp_path / "extra.safetensors", "weight")
    with pytest.raises(ValueError, match="multiple selected files"):
        module.prepare_index(tmp_path, ["model.safetensors", "extra.safetensors"])
