#!/usr/bin/env python3
"""Index explicitly selected HF backbone files without changing their tensors.

For releases with auxiliary safetensors files, such as H2O's separate label rows,
vLLM's local wildcard loader needs an index naming only the backbone files.
"""
import argparse
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jevalkit.io import atomic_json, load_json


def prepare_index(folder, filenames):
    folder = Path(folder)
    mapping, total_size = {}, 0
    if not filenames or len(filenames) != len(set(filenames)):
        raise ValueError("Select distinct backbone filenames explicitly")
    for filename in filenames:
        if Path(filename).name != filename or not filename.endswith('.safetensors'):
            raise ValueError("Backbone filenames must be local safetensors basenames")
        path = folder / filename
        with path.open('rb') as stream:
            prefix = stream.read(8)
            if len(prefix) != 8:
                raise ValueError("Incomplete safetensors header: " + filename)
            length = struct.unpack('<Q', prefix)[0]
            if not 0 < length <= 100 * 1024 * 1024:
                raise ValueError("Invalid safetensors header length")
            header = json.loads(stream.read(length))
        size = path.stat().st_size - 8 - length
        for name, tensor in header.items():
            if name == '__metadata__':
                continue
            if name in mapping:
                raise ValueError("Tensor appears in multiple selected files: " + name)
            start, end = tensor['data_offsets']
            if not 0 <= start <= end <= size:
                raise ValueError("Tensor offsets exceed the selected weight file")
            mapping[name] = filename
            total_size += end - start
    if not mapping:
        raise ValueError("Selected files contain no model tensors")
    index = {'metadata': {'total_size': total_size}, 'weight_map': mapping}
    output = folder / 'model.safetensors.index.json'
    if output.exists() and load_json(output) != index:
        raise ValueError("A different weight index exists; inspect it before changing selection")
    atomic_json(output, index)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder')
    parser.add_argument('backbone_files', nargs='+')
    args = parser.parse_args()
    index = prepare_index(args.folder, args.backbone_files)
    print(json.dumps({'tensors':len(index['weight_map']),
                      'files':sorted(set(index['weight_map'].values())),
                      'index':str(Path(args.folder)/'model.safetensors.index.json')}))


if __name__ == '__main__':
    main()
