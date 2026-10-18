# Sources and attribution

The repository structure is inspired by [VLMEvalKit](https://github.com/open-compass/VLMEvalKit).
No VLMEvalKit implementation is copied.

`jevalkit/datasets/_jevbench/` contains the task schema and scoring/aggregation
modules from [fstandhartinger/jevbench](https://github.com/fstandhartinger/jevbench),
revision `bb05a335bc809e61b20c0f745d25499a82b326fc`, obtained through Valen's
attributed vendor snapshot. Its MIT license is retained in that directory.
This is the 231-task public benchmark used by Valen, distinct from other
projects also named JevBench.

Decision Index scoring is delegated to the separately installed upstream kit,
pinned in `pyproject.toml`. Its public index does not include private evaluations.

Model inference is delegated to the authors' published packages or release
modules. Weights, model code and benchmark datasets retain their own licenses.
Dataset manifests record source repositories, revisions, splits and checksums.
Do not treat JevalKit's Apache-2.0 license as a relicensing of those assets.

OpenAI Decisions uses the documented `/v1/decisions` schema:
https://developers.openai.com/api/reference/resources/decisions/methods/create
The adapter maps Noul to Predicate and preserves ordered Score levels.
