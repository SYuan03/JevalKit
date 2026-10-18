# Running evaluations

[Back to the project overview](../README.md)

## Install and inspect

Python 3.10+ is required. Inference environments are model-specific; for example,
Intern-Decision and pplx-decider require Python 3.12+. The base package has no
third-party dependencies.

```bash
python -m pip install -e .
python -m jevalkit list models
python -m jevalkit list benchmarks
python -m pip install -e '.[hf,data,decision-index,test]'
```

Use the authors' pinned dependencies for each native model. The runner imports
only the selected adapter so incompatible runtimes can use separate environments.
See [tested environment versions](runtime-environments.md) for the workspace runtimes.
On this workspace, Valen's environment is available at
`/mnt/shared-storage-user/liuziyu/My_Projects/Valen/.venv/bin/python`.

## Data and checkpoints

`JEVALKIT_DATA_ROOT` defaults to
`/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit`. All newly downloaded
weights, source data, media and caches are stored there. Existing model weights
can be reused through `--option model=/absolute/path`.

```bash
export JEVALKIT_DATA_ROOT=/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit
```

```text
$JEVALKIT_DATA_ROOT/
  datasets/*.tsv                   retained benchmark data
  datasets/*.manifest.json         hashes, source revisions, splits and counts
  raw/                            original evaluation data and frozen suites
  media/                          images and videos referenced by the TSVs
  models/                         temporary downloaded model checkpoints
  cache/                          runtime and download caches
  results/                        prediction journals, manifests and metrics
```

```bash
python -m jevalkit prepare JevBench
python -m jevalkit prepare VisualDecisionBench
python -m jevalkit prepare DecisionIndex --source /path/to/verified/suite-0.3
python -m jevalkit verify JevBench VisualDecisionBench_Image --media
```

The workspace's existing public Valen snapshots can also be imported without
changing their originals:

```bash
python scripts/prepare_local.py \
  --valen-root /mnt/shared-storage-user/liuziyu/My_Projects/Valen \
  --valen-data /mnt/shared-storage-user/mllm/liuziyu/share_data/Valen_Data
```

TSV rows contain `index`, `request`, `targets`, `meta` and `assets`. Nested cells
are JSON, preserving option order and multi-question shared states. Only a copy
of `request` is sent to inference; targets and provenance remain with the scorer.
See [data protocols](benchmarks.md) and [third-party terms](../THIRD_PARTY.md).

## Evaluate and resume

```bash
python -m jevalkit run --model Valen-0.8B \
  --data JevBench VisualDecisionBench_Image VisualDecisionBench_Video \
  --output "$JEVALKIT_DATA_ROOT/results/full"

# Explicit smoke subset, excluded from full leaderboard rankings.
python -m jevalkit run --model Valen-0.8B --data JevBench \
  --limit 10 --output "$JEVALKIT_DATA_ROOT/results/smoke"

# Same model, data, source, runtime and evaluation settings are required.
python -m jevalkit run --model Valen-0.8B --data JevBench \
  --output "$JEVALKIT_DATA_ROOT/results/full" --resume
```

The runner writes `manifest.json`, `predictions.jsonl` and `metrics.json` under
`<output>/<model>/<benchmark>/`. It locks active outputs, recovers only a truncated
last journal line, rejects changed resume inputs, and synchronizes GPU timing.
Failures and unsupported questions stay in the hard-label accuracy denominator.
Soft targets contribute probability metrics, not hard-label accuracy.

`python -m jevalkit check --model MODEL --output /path/to/conformance.json` checks
complete Choice/Noul/Score responses and JSON/null candidate descriptions with
unlabeled synthetic requests. These interface checks produce no benchmark score.
Matrix rows can use `"mode": "check"` to run them before benchmark evaluations.

Stored predictions can be scored again after temporary checkpoints are deleted:

```bash
python -m jevalkit score "$JEVALKIT_DATA_ROOT/results/full/Valen-0.8B/JevBench"
```

## Hosted and self-hosted APIs

```bash
# Read OPENAI_API_KEY from your environment; never put its value in CLI options.
python -m jevalkit run --model OpenAI-Decisions --data JevBench \
  --output "$JEVALKIT_DATA_ROOT/results/api"

# Jev-compatible endpoint from the model author's server.
python -m jevalkit run --model Kev --data JevBench \
  --option endpoint=http://localhost:8008/v1/systemone \
  --output "$JEVALKIT_DATA_ROOT/results/api"
```

OpenAI uses the documented **`POST /v1/decisions`** endpoint, with
Noul → Predicate, Choice → choices and Score → ordered levels. It uses native
probabilities and records refusals per question. It does not approximate this
API with generated chat responses. See the [official OpenAI documentation](https://developers.openai.com/api/docs/guides/decisions).

The [model catalog](models.md) identifies native runtimes, author packages,
HTTP endpoints and each release's media limits. Unsupported video is reported
explicitly; no implicit blank image or frame mosaic is substituted.

## GPU cluster and results

`scripts/submit.sh` reuses Valen's existing local cluster configuration, freezes
the submitted source, disables automatic restarts and enforces **32 GPUs total
across cumulative job reservations**. It never modifies Valen's configuration.
Workers default to offline Hugging Face loading, so prefetch checkpoints and any
required base-model caches before submitting. Set `JEVAL_OFFLINE=0` only for a
worker with intentional Hub network access.

```bash
bash scripts/submit.sh jevalkit-valen-eval-001 1 run \
  --model Valen-0.8B --data JevBench --output "$JEVALKIT_DATA_ROOT/results/full"

python -m jevalkit leaderboard "$JEVALKIT_DATA_ROOT/results" --output leaderboard
```

For several models on one GPU, edit [a matrix example](../examples/matrix.json) and run
`python -m jevalkit matrix examples/matrix.json`. Each row uses an isolated subprocess,
can select its own Python interpreter, and retains its failure while later rows continue.
The cluster wrapper also accepts `matrix CONFIG.json` and freezes the configuration with the code.
Set `JEVAL_MEMORY_PER_GPU=98304` when a large model needs more host memory.

[Managed local services](../examples/served-model.json) can start the author's server before
an HTTP evaluation. JevalKit checks its localhost readiness endpoint, fingerprints the
specified weights/configuration/source, retains server logs, and stops the processes it
started after the run. Configure credentials in the environment; matrix files contain
only non-secret server settings. Existing servers can be used by supplying just an endpoint.

`scripts/download_models.py CONFIG.json --status STATUS.json` downloads resumable snapshots
under the shared root. Entries contain `model`, a full 40-character `revision`, and the
path to saved Hub `metadata` obtained with `?blobs=true`; downloaded LFS files are verified
against their published SHA-256 digests.
Interrupted network transfers retry in place up to three times (`--attempts`),
retaining completed and partial files. Integrity and storage errors stop immediately.

`scripts/validation_queue.py QUEUE.json --status STATUS.json` submits evaluations when
their verified model downloads and environment markers are ready. The queue contains
`root` and `jobs`; each job specifies `name`, `matrix`, `python`, and `models` entries
with `repo` and an immutable `revision`. Optional `ready_files` must contain `ready: true`.
The queue submits each job once through the same cumulative GPU ledger. A previous
reservation without a saved scheduler handle requires inspection before retrying.

Leaderboards include Markdown, TSV and JSON. They retain dataset hashes,
protocols, hardware, coverage and evidence paths; compare matching protocols and
data versions. JevBench uses the pinned public official scorer. Decision Index
delegates its weighted public index to the pinned upstream scorer; private
leaderboard components are not inferred from public results.
The Markdown overview uses the latest complete run per model, benchmark, data
hash and protocol. It keeps every repeated measurement in the detailed table;
it never selects the best repeat. JSON also exposes the selected `primary_results`.

Existing upstream Decision Index predictions can be imported with
`import-decision-index --model NAME --results RESULTS_JSONL --environment ENVIRONMENT_JSON... --output DIR`.
Every frozen request ID and payload hash must match; all source shard identities
must agree. Scores are recomputed from predictions and labeled **imported** in
the leaderboard. No model-card scores are copied into measured results.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```

This disables unrelated plugins in shared research environments. The tests cover
TSV round trips, label isolation, malformed probabilities, soft targets,
failure denominators, OpenAI schema mapping/refusals, resume integrity, record
sharding and leaderboard evidence verification.
