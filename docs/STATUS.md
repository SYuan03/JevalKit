# Implementation and evaluation status

Updated UTC: 2026-10-18T06:42:17.235658+00:00

The original goal is not complete. Public checkpoint validation is complete;
live measurements for the two hosted APIs still require credentials.

- Implemented: 20 model families, 8 Jev-related benchmark suites / 10 active TSV views.
- Real inference verified: 18 families, including Valen and all public checkpoint integrations.
- Results: 68 retained artifacts in the active board; 40 distinct eligible primary full scores.
- Checks: 75 tests passed. A fresh wheel matched all 32 source modules and bundled licenses; its CLI started using only the standard library.
- Data: the five new suites (45,794 states / 91,817 questions) passed full schema, count and content-hash checks. Existing media checks remain valid; retired data remains archived.
- GPU budget: 31/32 cumulative reservations, including failed/stopped/repeated attempts. All planned GPU tasks have finished.

The [leaderboard](../leaderboard/README.md) selects the latest complete measurement
per model, data hash and protocol, without selecting the best repeat. It retains
smoke, imported, unsupported and repeated runs in the detailed results.
The [data inventory](data-manifest.json) records persistent TSV paths, hashes,
sources and counts under `/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit`.
The [requirement audit](validation-audit.json) records the original scope and pending evidence.
The [runtime guide](runtime-environments.md) records the tested environments.

Five decision-specific suites are now integrated: TypedDecisions, DecisionBench,
ProceduralTypedDecisions, ZhDecisionBench and JevAltBench. Their complete pinned
TSVs are retained in shared storage. The original 5–10-benchmark scope is met
with eight families. The five retired general NLP tasks remain excluded.

CPU Uniform smoke runs passed inference, protocol scoring and re-scoring on all
five new suites; these diagnostic records are outside the main leaderboard.
No new trained-model full measurements are claimed. Upstream parity checks
covered 39 DecisionBench cases plus JevOss/Chinese reference ECE conventions.
The [protocol guide](benchmarks.md) describes soft labels and interface projections.

## Latest completed evaluations

| Model | JevBench (231 questions) | VDB Image (2,000 questions) |
|---|---:|---:|
| Pplx-Decider | 89.18% | 86.88% |
| OpenJev | 87.45% | 83.12% |
| H2O-Lightning | 87.45% | 82.06% |
| Clef-Flash | 82.68% | 82.24% |

Every question in these runs has a valid response, with no failures or unsupported
questions. VDB Image accuracy uses the 1,700 hard-label questions; all 2,000,
including 300 soft-label questions, contribute probability metrics. The latest
Pplx, OpenJev, H2O and Clef scheduler tasks were verified Succeeded.

Families with successful real local GPU or author-server inference:
Clef, Crivo, H2O-Lightning, Intern-Decision, JevK5, Kev, Laya, Liquid-d1,
OmniJev, OpenJev, Pplx-Decider, QEV, RSI-Jev, StartLux, Valen,
Visual-Jev, Vjev and vLLM-Decision1.

Existing Valen Decision Index predictions were imported only after request IDs,
payload hashes, shard provenance and official scoring were verified. They remain
labeled imported. No model-card scores were copied into measured results.

## Pending hosted validation

Jev and OpenAI-Decisions adapters are implemented. Local HTTP tests cover native
request mapping, authentication, retries, probabilities and refusals. These tests
are not hosted inference and produce no leaderboard scores.

`OPENAI_API_KEY`, `TYPESAFE_API_KEY` and `JEV_ENDPOINT` are absent from the current
evaluation environment. Once configured, the [hosted matrix](../examples/hosted-apis.json)
can run full JevBench for both services:

```bash
python -m jevalkit matrix examples/hosted-apis.json
```

Credentials are inherited through environment variables, never stored in the
matrix. Its schema and generated commands have been checked; live measurements
remain pending. The full 20-family validation is therefore not claimed complete.

## Corrections and retained evidence

H2O's first two starts failed before evaluation: an overlong UNIX socket path,
then a local vLLM glob that included the separate decision label rows. The worker
now uses short IPC paths. A standard weight index selects the unchanged backbone
while the author's readout loads the unchanged label rows separately. Actual
vLLM preflights and regression tests cover both fixes; the third task succeeded.

Structured/null candidate descriptions and custom Noul rubrics are preserved.
Vjev's old JevBench results omitted those rubrics and remain diagnostic only;
the corrected full result is 60.61%, with all 231 answers valid. QEV and Vjev also
passed real GPU interface checks, which have no benchmark scores.

The earliest Valen workers reported Failed after saving complete, hash-verified
metrics for all originally requested views. Log retrieval failed with SSL errors, so
that wrapper exit cause remains unverified. New tasks freeze their worker scripts.
All reservations, including a redundant early Vjev run, remain counted.

Dataset TSVs/media and borrowed Valen checkpoints remain intact. Owned temporary
weights are retained for now. Job IDs, frozen source, logs, prediction evidence,
checks and continuation state remain in `artifacts/` and the shared results root.
