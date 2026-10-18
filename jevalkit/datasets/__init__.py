"""Dataset registry and verified TSV loaders, patterned after VLMEvalKit."""
from pathlib import Path
from ..io import load_json, read_tsv, sha256
from ..paths import data_root

BENCHMARKS = {
    "VisualDecisionBench": {"family": "VisualDecisionBench", "modality": "image,video"},
    "VisualDecisionBench_Image": {"family": "VisualDecisionBench", "modality": "image"},
    "VisualDecisionBench_Video": {"family": "VisualDecisionBench", "modality": "video"},
    "JevBench": {"family": "JevBench", "modality": "text"},
    "DecisionIndex": {"family": "DecisionIndex", "modality": "text"},
    "AGNews": {"family": "AGNews", "modality": "text"},
    "Banking77": {"family": "Banking77", "modality": "text"},
    "BoolQ": {"family": "BoolQ", "modality": "text"},
    "SST2": {"family": "SST2", "modality": "text"},
    "When2Call": {"family": "When2Call", "modality": "text"},
}


class DecisionDataset:
    def __init__(self, name, root=None):
        self.name = name
        self.root = data_root(root)
        self.path = self.root / "datasets" / (name + ".tsv")
        self.manifest_path = self.path.with_suffix(".manifest.json")
        self.manifest = load_json(self.manifest_path)
        if self.manifest["name"] != name or sha256(self.path) != self.manifest["sha256"]:
            raise ValueError("Dataset identity or TSV checksum mismatch: " + name)
        self.media_root = (self.path.parent / self.manifest.get("media_root", ".")).resolve()

    def __iter__(self):
        return read_tsv(self.path)

    def verify(self, media=False):
        from ..models.media import state_parts
        records, questions = 0, 0
        for record in self:
            records += 1
            questions += len(record["request"]["questions"])
            if media:
                state_parts(record["request"]["state"], self.media_root)
                for asset in record.get("assets", []):
                    if asset.get("sha256"):
                        path = self.media_root / asset.get("path", asset.get("url", ""))
                        if sha256(path) != asset["sha256"]:
                            raise ValueError("Media checksum mismatch: " + str(path))
        if records != self.manifest["records"] or questions != self.manifest["questions"]:
            raise ValueError("Dataset coverage differs from manifest")
        return {"name": self.name, "records": records, "questions": questions,
                "sha256": self.manifest["sha256"], "media_verified": media}


def build_dataset(name, root=None):
    return DecisionDataset(name, root)
