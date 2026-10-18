# Implementation and evaluation status

Updated UTC: 2026-10-18T16:38:08.765019+00:00

The original goal is not complete. Public checkpoint validation is complete;
live measurements for the two hosted APIs still require credentials.

- Implemented: 20 model families, 8 Jev-related benchmark suites / 10 active TSV views.
- Real inference verified: 18 families, including Valen and all public checkpoint integrations.
- Results before the new full matrix: 68 retained artifacts; 40 distinct eligible primary full scores. New verified results are added to the leaderboard as pairs finish.
- Checks: 75 tests passed. A fresh wheel matched all 32 source modules and bundled licenses; its CLI started using only the standard library.
- Data: the five new suites (45,794 states / 91,817 questions) passed full schema, count and content-hash checks. Existing media checks remain valid; retired data remains archived.
- GPU budget: 32/32 cumulative reservations, including failed/stopped/repeated attempts. The final reservation runs the five new benchmark suites.

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
The full trained-model matrix is now running; completed scores will be
added only after their prediction evidence passes verification. Upstream parity checks
covered 39 DecisionBench cases plus JevOss/Chinese reference ECE conventions.
The [protocol guide](benchmarks.md) describes soft labels and interface projections.

## Active full evaluation of the five new suites

Job: `jevalkit-decisions-full-261018a-40776756`, submitted on 2026-10-18.
The H200 worker started at 06:59:28 UTC and wrote real model predictions for
Valen-0.8B on ZhDecisionBench. The live pair status and progress evidence
are retained with the job. The first full result is **Valen-0.8B /
ZhDecisionBench: 82.44% accuracy, 467/467 valid questions, zero failures**;
its 378 request IDs and raw-evidence hashes were verified.

- Scope: **22 local model configurations covering all 18 available checkpoint
  families × 5 suites = 110 full evaluations**, with no sample limits.
- Variants: all three registered Valen and Intern-Decision sizes; Clef-Flash
  represents the Clef family because the separate Clef checkpoint is unavailable.
- Order: ZhDecisionBench, TypedDecisions, JevAltBench, DecisionBench,
  ProceduralTypedDecisions, evaluating every local configuration on each suite.
- Execution: one GPU, sequential isolated processes per model/benchmark pair;
  a failed pair retains its journal and does not prevent later pairs from running.
  The overall timeout is seven days, rather than the default three hours.
- Coverage: visual-only releases may reject these text-only requests. Their
  unsupported records remain visible and do not become valid scores.
- Hosted models: Jev and OpenAI-Decisions remain pending their API environment.

Before submission, all five full TSVs passed verification, the 40 source-gate
hashes matched, and all configured interpreters, weights and source paths existed.
Native author inference imports also passed for all three Intern-Decision sizes.
The plan contains 1,007,468 request attempts / 2,019,974 questions, including
requests that a release may report as unsupported.

The frozen matrix, source hashes, worker log, scheduler handle and live pair
status are retained under
`artifacts/jobs/jevalkit-decisions-full-261018a/`; the pair status is
`code/matrix.status.json`. Predictions and metrics are written to
`/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/decision-benchmarks-full-20261018/`.
No further GPU reservations remain within the agreed cumulative limit.

### Progress snapshot: 2026-10-19 00:37 Hong Kong time

The scheduler still reports **Running**. Of 110 planned pairs, **84 have complete
metric artifacts**, one stopped with an error, one is running, and 24 are pending.
The completed artifacts contain **55 eligible full scores**, seven fully
unsupported evaluations, and 22 evaluations with question errors that remain
excluded from the primary score table.

| New suite | Complete metric artifacts | Remaining work |
|---|---:|---|
| ZhDecisionBench | 22/22 | Complete, with native modality limits retained |
| TypedDecisions | 22/22 | Complete, with native question/modality limits retained |
| JevAltBench | 22/22 | Input compatibility errors require repair before promotion |
| DecisionBench | 18/22 | Kev running at about 15,000/23,900 requests; Laya stopped; two later models pending |
| ProceduralTypedDecisions | 0/22 | Pending in the same live GPU queue |

The shared JevAltBench failure is a structured ticket containing a `messages`
field with timestamp/sender/text entries. It was mistaken for a chat-message
envelope, causing a missing role/content error across releases. Some author SDKs
also reject null or structured Noul criteria. Original journals remain intact;
these measurements are not presented as passing full scores.

Laya stopped after 5,572/23,900 requests because 151 candidate markers do not fit
its released 512-token budget; only 126 fit with the question head. The capacity
rejection was classified as an error, triggering the consecutive-error stop.
The incomplete journal is retained. Neither candidates nor failed requests were
removed to manufacture a full result. The frozen running worker and its input
datasets remain unchanged while the independent pairs continue.

The leaderboard now retains 152 active artifacts in total, including the 84 new
completed measurements. Its primary table admits 55 new eligible scores; the
complete error and unsupported records remain in the detailed results. The live
monitor continues to verify prediction/manifest hashes before aggregation.

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
