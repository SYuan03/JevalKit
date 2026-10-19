<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/branding/jevalkit-dark.svg">
    <img src="assets/branding/jevalkit-light.svg" alt="JevalKit — a unified evaluation toolkit for decision models" width="680">
  </picture>
</h1>

<p align="center">
  <b>A unified evaluation toolkit for Jev-like decision models.</b><br>
  Text · Image · Video → Choice · Noul · Score
</p>

<p align="center">
  <a href="https://huggingface.co/Valen-Team"><img src="https://img.shields.io/badge/Hugging_Face-Valen_Team-FFD21E?style=flat&amp;logo=huggingface&amp;logoColor=FFD21E&amp;labelColor=555555" alt="Hugging Face: Valen Team"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-80A51B?style=flat&amp;labelColor=555555" alt="License: Apache 2.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/Python-3.10%2B-1683BB?style=flat&amp;logo=python&amp;logoColor=FFD43B&amp;labelColor=555555" alt="Python 3.10+"></a>
  <br>
  <a href="https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard"><img src="https://img.shields.io/badge/Space-Leaderboard-009C83?style=flat&amp;logo=huggingface&amp;logoColor=FFD21E&amp;labelColor=555555" alt="Hugging Face Space: leaderboard"></a>
  <a href="https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets"><img src="https://img.shields.io/badge/Datasets-10_TSV_views-2185B5?style=flat&amp;logo=huggingface&amp;logoColor=FFD21E&amp;labelColor=555555" alt="Hugging Face: 10 dataset views"></a>
  <a href="#supported-models"><img src="https://img.shields.io/badge/Models-20_families-8A63B8?style=flat&amp;labelColor=555555" alt="20 model families"></a>
  <a href="#supported-benchmarks"><img src="https://img.shields.io/badge/Benchmarks-8_suites-E88B23?style=flat&amp;labelColor=555555" alt="8 Jev-related benchmark suites"></a>
</p>

<p align="center">
  <a href="#introduction">Introduction</a> · <a href="#latest-updates">News</a> · <a href="#quick-start">Quick Start</a> · <a href="#supported-models">Models</a> · <a href="#supported-benchmarks">Benchmarks</a> · <a href="#evaluation-results">Results</a> · <a href="#documentation">Docs</a>
</p>

<a id="introduction"></a>

## ✨ Introduction

JevalKit evaluates models that return **probabilities over decisions defined at
request time**: a yes/no judgment, a choice among named options, or a rating on an
ordered scale. It brings model adapters, benchmark preparation, scoring and result
comparison into one workflow, following the registry-based design of
[VLMEvalKit](https://github.com/open-compass/VLMEvalKit).

<a id="highlights"></a>

## 🎯 Highlights

- **20 model families in one registry.** Run open checkpoints through their native
  decision interfaces and hosted models through their published APIs.
- **Text, image and video evidence.** Preserve shared states, multiple questions,
  candidate order and model-specific modality limits.
- **Evaluate the whole distribution.** Report accuracy alongside Brier, NLL,
  calibration and ordinal metrics, with benchmark-specific official scorers.
- **Reproduce and resume.** Retain dataset hashes, raw predictions, runtime
  provenance, failures and coverage; resume interrupted runs or score them again.
- **Compare measured results.** Browse Markdown, TSV and JSON leaderboards, with
  smoke tests, imported predictions and complete runs identified separately.

<a id="latest-updates"></a>

## 📰 Latest Updates

<!-- jevalkit:coverage:start -->
- **2026-10-19:** Filling **22 missing model–benchmark pairs**, with **15/22 audited**.
  Full datasets run in parallel within the **32 concurrent GPU** limit; verified
  results are published as they finish on the [leaderboard](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard).
<!-- jevalkit:coverage:end -->
- **2026-10-19:** Released the [🤗 leaderboard](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)
  with benchmark filters, model comparison, probability metrics and CSV/JSON downloads.
- **2026-10-19:** Published all **10 TSV views** in
  [🤗 JevalKit Datasets](https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets),
  with pinned sources and scoring protocols in the [dataset catalog](jevalkit/datasets/catalog.json).
- **2026-10-19:** Completed **110/110 pairs** across the five new suites:
  99 eligible scores and 11 fully unsupported pairs. Source, checkpoint hashes
  and complete request coverage were verified; details are in the [leaderboard](leaderboard/README.md).

<details>
<summary>Earlier updates</summary>

- **2026-10-18:** Integrated Typed-Decisions, DecisionBench, Procedural Typed
  Decisions, zh-decision-bench and JevAlt-Bench, bringing the toolkit to eight suites.
- **2026-10-18:** Verified native inference for 18 model families. The Jev and
  OpenAI Decisions adapters are implemented; live API measurements remain pending.

</details>

<a id="quick-start"></a>

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/Valen-Team/JevalKit.git
cd JevalKit
python -m pip install -e '.[hf,data]'
```

The CLI and scorers require Python 3.10+. Model inference uses the dependencies
specified by each author; some models require Python 3.12+ or a separate serving
environment. See the [model integration guide](docs/models.md).

### 2. Download a model and dataset

```bash
export JEVALKIT_DATA_ROOT="$PWD/data"

hf download Valen-Team/Valen-0.8B \
  --local-dir "$JEVALKIT_DATA_ROOT/models/Valen-0.8B"

hf download Valen-Team/JevalKit_Datasets --repo-type dataset \
  --include "datasets/JevBench.tsv" --local-dir "$JEVALKIT_DATA_ROOT"
```

The published TSVs are ready to evaluate. To download all ten views, replace
`datasets/JevBench.tsv` with `datasets/*.tsv`. Visual media and Decision Index
scoring inputs have separate downloads in the [usage guide](docs/quickstart.md#download-data).

### 3. Run and compare

```bash
python -m jevalkit run --model Valen-0.8B --data JevBench \
  --option model="$JEVALKIT_DATA_ROOT/models/Valen-0.8B" \
  --output "$JEVALKIT_DATA_ROOT/results"

python -m jevalkit leaderboard "$JEVALKIT_DATA_ROOT/results" \
  --output leaderboard
```

Pass `--option model=/path/to/checkpoint` to reuse existing weights. Use
`--limit 10` for a smoke test, or `--resume` to continue an interrupted run with
the same settings. [Full usage guide →](docs/quickstart.md)

<a id="supported-models"></a>

## 🤖 Supported Models

Size variants and Clef/Clef-Flash count within their respective families.
**Measured** means real inference has been verified for at least one registered
variant; per-benchmark coverage is shown in the [leaderboard](leaderboard/README.md).

| Model family | Registered model IDs | Interface | Evaluation |
|---|---|---|---|
| [Valen](https://github.com/Valen-Team/Valen) | `Valen-0.8B`, `Valen-2B`, `Valen-4B` | Native | Measured |
| [Intern-Decision](https://github.com/InternLM/Intern-Decision) | `Intern-Decision-0.8B`, `Intern-Decision-2B`, `Intern-Decision-4B` | Native | Measured |
| [Laya](https://github.com/NandhaKishorM/laya) | `Laya` | Native | Measured |
| [Liquid d1](https://huggingface.co/LiquidAI/d1-3B) | `Liquid-d1-3B` | Native | Measured |
| [vLLM Decision1](https://huggingface.co/vllm-sr/Decision-1.0-Kai-0.6B) | `Decision1-Kai` | Native | Measured |
| [Clef](https://huggingface.co/Cloudflare/clef) | `Clef`, `Clef-Flash` | Native | Measured |
| [Pplx-Decider](https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b) | `Pplx-Decider` | Native | Measured |
| [JevK5](https://huggingface.co/alibiserikbay/JevK5) | `JevK5` | Native | Measured |
| [StartLux](https://huggingface.co/startlux-models/StartLux-Decision-v1-0.8B) | `StartLux-0.8B` | Native | Measured |
| [Crivo](https://huggingface.co/tardellirs/crivo-150m) | `Crivo-150M` | Native | Measured |
| [RSI-Jev](https://github.com/Shanghua-Gao/RSI-Jev) | `RSI-Jev-v4` | Native | Measured |
| [Vjev](https://huggingface.co/yah01/vjev-vision) | `Vjev-4B` | Native | Measured |
| [QEV](https://github.com/ken-jo/qev) | `QEV` | Native | Measured |
| [OmniJev](https://github.com/tinnel123666888/OmniJev) | `OmniJev` | Native | Measured |
| [Visual-Jev](https://github.com/guanxuyu-sv/Visual-Jev) | `Visual-Jev` | Native | Measured |
| [Kev](https://github.com/jaredpalmer/kev) | `Kev` | Author server | Measured |
| [H2O-Lightning](https://huggingface.co/h2oai/h2o-lightning-4b) | `H2O-Lightning` | Author server | Measured |
| [OpenJev](https://huggingface.co/openjev/openjev) | `OpenJev` | Author server | Measured |
| [Jev](https://typesafe.ai) | `Jev` | Hosted API | Live evaluation pending |
| [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions) | `OpenAI-Decisions` | Hosted API | Live evaluation pending |

The catalog also includes a `Uniform` diagnostic baseline. Author dependencies,
context limits, supported question types and media contracts are documented in
the [integration guide](docs/models.md).

<a id="supported-benchmarks"></a>

## 🧩 Supported Benchmarks

| Benchmark | Input | Evaluation data | Main measurements |
|---|---|---|---|
| [VisualDecisionBench](https://huggingface.co/datasets/Valen-Team/VisualDecisionBench) | 🖼️ Image · 🎬 Video | 1,696 states; 9,143 questions | Accuracy, soft-target Brier/NLL, ordinal metrics |
| [JevBench](https://github.com/fstandhartinger/jevbench) | 📝 Text | 231 public tasks across easy/original/hard tiers | Official task scores and calibration |
| [Decision Index](https://huggingface.co/spaces/multimodalart/jev-decision-index) | 📝 Text | Edition 0.3 public suite; 43 constituent datasets | Official chance-corrected, weighted public index |
| [Typed-Decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) | 📝 Text | 400 states; 2,000 decisions | Modal accuracy, KL and soft-target Brier |
| [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | 📝 Text | 23,900 evaluation rows; 43 tasks | Accuracy, reference NLL and calibration |
| [Procedural Typed Decisions](https://huggingface.co/datasets/tasksource/procedural-typed-decisions) | 📝 Text | 18,000 test states; 57,016 questions | Rule execution and exact probability judgments |
| [zh-decision-bench](https://github.com/CodyQin/zh-decision-bench) | 📝 Chinese | v0.2: 378 items; 467 questions | Routing, moderation, ordinal ratings and calibration |
| [JevAlt-Bench](https://huggingface.co/datasets/mertkayacs/jevalt-bench) | 📝 EN · TR · DE | 3,116 test states; 8,434 questions | Labeled and soft-probability decisions; language slices |

VisualDecisionBench's image and video views belong to the same benchmark.
Decision Index public scores and its private leaderboard components are reported
separately. See the [dataset catalog](jevalkit/datasets/catalog.json) and
[scoring protocols](docs/benchmarks.md).

Download the prepared TSVs from [🤗 JevalKit Datasets](https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets).
Use the [matrix example](examples/decision-benchmarks.json) to evaluate several
models and benchmarks. Protocol details are in the [scoring guide](docs/benchmarks.md).

<a id="evaluation-results"></a>

## 📊 Evaluation Results

<!-- jevalkit:results-summary:start -->
The current snapshot contains **154 eligible full scores** and **228 retained
run artifacts**. It covers **18 measured model families**; the two hosted API
families remain pending. [🤗 Open the leaderboard](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard).
<!-- jevalkit:results-summary:end -->

[Markdown leaderboard](leaderboard/README.md) ·
[Download TSV](leaderboard/leaderboard.tsv) ·
[Download JSON](leaderboard/leaderboard.json)

<a id="documentation"></a>

## 📖 Documentation

| Guide | Contents |
|---|---|
| [Running evaluations](docs/quickstart.md) | Downloads, evaluation commands, resume, APIs and parallel runs |
| [Model integrations](docs/models.md) | Author SDKs, runtime dependencies and input limits |
| [Scoring protocols](docs/benchmarks.md) | Dataset definitions, probability metrics and official scorers |

<a id="contributing"></a>

## 🤝 Contributing

Model adapters live in `jevalkit/models/` and are registered in
[`jevalkit/config.py`](jevalkit/config.py). Benchmark loaders live in
`jevalkit/datasets/`, with scoring in `jevalkit/scoring.py`. Contributions should
preserve native probabilities, candidate order and the published scoring protocol.
Include reproducible commands and the relevant validation when adding a model,
dataset or result.

```bash
python -m pip install -e '.[test]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```

Bug reports and contributions are welcome through
[Issues](https://github.com/Valen-Team/JevalKit/issues) and
[Pull Requests](https://github.com/Valen-Team/JevalKit/pulls).

<a id="license-and-acknowledgements"></a>

## 📄 License and Acknowledgements

JevalKit is released under [Apache-2.0](LICENSE). Model weights, datasets and
vendored code retain their own licenses; see [THIRD_PARTY.md](THIRD_PARTY.md).
We thank [VLMEvalKit](https://github.com/open-compass/VLMEvalKit) for its evaluation
toolkit design, and the authors of the integrated decision models and benchmarks.
