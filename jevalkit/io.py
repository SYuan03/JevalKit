"""Strict JSON/TSV IO and content fingerprints."""
import csv
import hashlib
import json
import os
from pathlib import Path


def dumps(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def object_hash(value):
    return hashlib.sha256(dumps(value).encode("utf-8")).hexdigest()


def jsonl(path):
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except (ValueError, UnicodeDecodeError) as exc:
                    raise ValueError(f"Invalid JSONL: {path}:{number}") from exc


TSV_FIELDS = ("index", "request", "targets", "meta", "assets")


def write_tsv(path, records):
    """One row per shared state; nested fields are UTF-8 JSON, never Python repr."""
    from .schema import validate_record
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    seen, questions = set(), 0
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=TSV_FIELDS, delimiter="\t")
            writer.writeheader()
            for record in records:
                validate_record(record)
                index = str(record["index"])
                if index in seen:
                    raise ValueError(f"Duplicate record ID: {index}")
                seen.add(index)
                questions += len(record["request"]["questions"])
                writer.writerow({"index": index, **{k: dumps(record.get(k, {} if k != "assets" else []))
                                                       for k in TSV_FIELDS[1:]}})
        if not seen:
            raise ValueError("Refusing to create an empty benchmark TSV")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
    return {"records": len(seen), "questions": questions, "sha256": sha256(path)}


def read_tsv(path):
    from .schema import validate_record
    # Large multi-question states routinely exceed csv's 128 KiB default.
    csv.field_size_limit(256 * 1024 * 1024)
    seen = set()
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if tuple(reader.fieldnames or ()) != TSV_FIELDS:
            raise ValueError(f"Expected TSV columns {TSV_FIELDS}: {path}")
        for number, row in enumerate(reader, 2):
            try:
                record = {"index": row["index"], **{k: json.loads(row[k]) for k in TSV_FIELDS[1:]}}
                validate_record(record)
                if record["index"] in seen:
                    raise ValueError("Duplicate record ID")
                seen.add(record["index"])
                yield record
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f"Invalid TSV {path}:{number}: {exc}") from exc
