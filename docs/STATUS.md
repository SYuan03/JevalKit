# Implementation and evaluation status

Updated UTC: 2026-10-19T05:01:35.306871+00:00

Public checkpoint integrations are validated. A coverage audit found 22 compatible
local model–benchmark pairs that had never been evaluated; these are being
evaluated with 32 single-GPU workers. Hosted API measurements still require credentials.

- Implemented: 20 model families, 8 Jev-related benchmark suites / 10 active TSV views.
- Real inference verified: 18 families, including Valen and all public checkpoint integrations.
- Results: 206 retained active artifacts; 144 distinct eligible primary full scores. Gap-fill audit: 5/22 complete. The five-suite matrix remains 110/110 complete (99 eligible, 11 fully unsupported).
- Checks: 95 regression tests passed, including native question capacity, matrix shard validation and exact-partition merge checks. The pre-run wheel check matched all 32 package modules and bundled licenses.
- Data: the five new suites (45,794 states / 91,817 questions) passed full schema, count and content-hash checks. Existing media checks remain valid; retired data remains archived.
- GPU limit: at most 32 concurrent GPUs. Gap-fill audit: 5/22 complete; latest worker states: 5 succeeded, 27 running. Historical completed jobs do not consume parallel capacity.

The [leaderboard](../leaderboard/README.md) selects the latest complete measurement
per model, data hash and protocol, without selecting the best repeat. It retains
smoke, imported, unsupported and repeated runs in the detailed results.
The [HF Space](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)
provides an interactive snapshot with benchmark/metric filters, model comparison,
coverage, per-run provenance and CSV/JSON export. It runs as a static website.
The [data inventory](data-manifest.json) records persistent TSV paths, hashes,
sources and counts under `/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit`.
The [requirement audit](validation-audit.json) records the original scope and pending evidence.
The [runtime guide](runtime-environments.md) records the tested environments.

Five decision-specific suites are now integrated: TypedDecisions, DecisionBench,
ProceduralTypedDecisions, ZhDecisionBench and JevAltBench. Their complete pinned
TSVs are retained in shared storage. The original 5–10-benchmark scope is met
with eight families. The five retired general NLP tasks remain excluded.

The ten active TSV views and a concise dataset card are published in
[Valen-Team/JevalKit_Datasets](https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets).
Source revisions and checksums remain in this toolkit's data inventory; local
manifests and official scoring inputs are created by `jevalkit prepare`.
Visual media remain in the original VisualDecisionBench repository.

CPU Uniform smoke runs passed inference, protocol scoring and re-scoring on all
five new suites; these diagnostic records are outside the main leaderboard.
The first full trained-model matrix has ended. It produced 109 complete metric
artifacts and 77 eligible new scores; error-containing measurements remain excluded
from the primary score table. Raw prediction and manifest hashes were verified. Upstream parity checks
covered 39 DecisionBench cases plus JevOss/Chinese reference ECE conventions.
The [protocol guide](benchmarks.md) describes soft labels and interface projections.

## Missing-pair evaluation started on 2026-10-19

The earlier 110/110 completion refers to the five new benchmark suites. It did
not cover all older benchmarks. The [gap-fill plan](coverage-gapfill.json) lists
all 22 newly scheduled pairs: 17 DecisionIndex models, Intern-Decision-2B/4B on
JevBench and VisualDecisionBench_Image, and Clef-Flash on VisualDecisionBench_Video.

Intern-Decision accepts at most16 questions per request; Decision1-Kai rejects
empty state text. These native input limits are recorded as unsupported without
removing questions or inserting placeholder evidence. Five Intern workers and
one Decision1 worker were replaced with these explicit checks; their original
failed evidence is retained.

Each DecisionIndex model evaluates all 140,178 states / 312,320 questions.
Pplx-Decider uses four independent request shards; seven other larger runs use
two shards each. Nine DecisionIndex models and the five shorter pairs use one
worker each, for 32 single-GPU workers in total. No sample limit is applied.
The existing merger checks exact, non-overlapping full request coverage and
identical source, checkpoint, runtime and settings before global official scoring.

Results are promoted only after evidence hashes, frozen source, request IDs and
unchanged checkpoint hashes pass auditing. Local progress and audit files are
retained in `artifacts/gapfill-progress.json` and `artifacts/gapfill-audit.json`.
The existing leaderboard remains the latest published snapshot while jobs run.

## Full evaluation of the five new suites

Job: `jevalkit-decisions-full-261018a-40776756`, one H200, 22 local model
configurations covering 18 families × 5 suites = 110 planned full evaluations.
It started on 2026-10-18 at 06:59:28 UTC and ended on 2026-10-19 at 02:32:20 UTC
(10:32 Hong Kong time), after about 19.5 hours. Every pair was attempted.

**109 pairs produced complete metric artifacts.** Of those, 77 have eligible full
scores, nine are fully unsupported, and 23 contain question errors. One additional
pair, Laya / DecisionBench, stopped before finishing. The scheduler correctly
reports **Failed**, with worker exit code 1 from that failed pair; this does not
invalidate the independently completed, hash-verified measurements.

| New suite | Complete artifacts | Eligible scores | Unresolved work |
|---|---:|---:|---|
| ZhDecisionBench | 22/22 | 20 | Two visual-only releases unsupported |
| TypedDecisions | 22/22 | 19 | Three native capability exclusions |
| JevAltBench | 22/22 | 0 | Compatibility errors; rerun all 22 configurations |
| DecisionBench | 21/22 | 19 | Laya incomplete; two visual-only releases unsupported |
| ProceduralTypedDecisions | 22/22 | 19 | StartLux cache errors; two visual-only releases unsupported |

Full runs had no sample limits. All three registered Valen and Intern-Decision
sizes were included. Clef-Flash represents Clef because the separate Clef
checkpoint is unavailable. Hosted Jev and OpenAI-Decisions still require their
API environment. Released modality, candidate and context limits remain visible;
unsupported questions were not removed from the scoring denominator.

The frozen matrix, source hashes, worker log, scheduler handle and final pair
status remain under `artifacts/jobs/jevalkit-decisions-full-261018a/`.
Predictions and metrics are retained at
`/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/decision-benchmarks-full-20261018/`.
All five TSVs and the 40-file source gate were verified before submission.
The original datasets, frozen worker and prediction journals are unchanged.

### Repairs prepared after the full pass

- Structured business records containing a `messages` field are serialized as
  complete JSON evidence. Only an explicit role/content chat envelope is treated
  as chat; ticket fields and message text are preserved.
- Strict author SDKs receive their native Noul defaults when the optional rubric
  is null/empty. Supplied structured rubric values remain present as JSON text.
- Laya's explicit option-marker capacity rejection is classified as unsupported,
  so repeated representational limits do not abort later supported requests.
  Its failed run stopped at 5,572/23,900 requests when 151 markers could not fit
  the released 512-token budget with a 192-token question head.
- StartLux uses its full native forward by default, bypassing an incompatible
  prefix-cache optimization whose tensor assumption fails with dictionary-valued
  linear-attention cache state in the tested Transformers environment. No prompt
  tokens, options or native calibration values are changed.

**83 regression tests pass.** Real upstream QEV and RSI-Jev schemas also accepted
all 50 previously failing requests (134 question schemas) after rendering.
StartLux long-input inference still needs GPU verification; its CPU diagnostic
exceeded a 240-second timeout and produced no benchmark score.
These fixes do not turn the previous errors into
passing model scores. A separate full rerun matrix is prepared for 24 pairs:
all 22 JevAltBench configurations, Laya / DecisionBench, and StartLux /
ProceduralTypedDecisions. It writes a new result directory and preserves the
first-pass evidence. The matrix is retained locally at
`artifacts/matrices/decision-benchmarks-repair-261019a.json`.

### Parallel repairs resumed on 2026-10-19

The user clarified that **32 GPUs is the maximum concurrent peak**, rather than
an historical cumulative allowance. The earlier interpretation was incorrect.
The reservation guard now releases completed workers and retains every historical
submission; uncertain jobs keep their slot until completion is proven. Three new
regression tests cover historical reuse, the 32-GPU boundary, terminal scheduler
evidence and duplicate-name protection. **86 tests pass** in total.

All 24 prepared repair pairs have been submitted as independent one-GPU tasks,
`jevalkit-repair-261019a-00` through `jevalkit-repair-261019a-23`.
The planned peak is 24 GPUs, below the 32-GPU limit. Each pair freezes its source,
uses its verified model environment, runs without a sampling limit, and writes
to the separate repair directory. The live submission map and evidence monitor
are retained in `artifacts/repair-parallel-submissions.json` and
`artifacts/repair-parallel-progress.json`. Valid full results enter the board only
after raw-evidence hashes pass verification.

### Final repair verification

All 24 workers succeeded by 2026-10-19 at 03:23:23 UTC. Their 110,452 requests
were checked against the complete dataset ID sequences, pinned source hashes,
unchanged checkpoint metadata and prediction/manifest hashes. All question error
counts are zero. The repair pass adds 22 eligible scores; the other two pairs are
visual-only releases that do not support JevAltBench's text inputs.

| New suite | Complete latest pairs | Eligible scores | Fully unsupported pairs |
|---|---:|---:|---:|
| ZhDecisionBench | 22/22 | 20 | 2 |
| TypedDecisions | 22/22 | 19 | 3 |
| JevAltBench | 22/22 | 20 | 2 |
| DecisionBench | 22/22 | 20 | 2 |
| ProceduralTypedDecisions | 22/22 | 20 | 2 |

The latest 110 logical pairs contain no question errors. Partial native capability
exclusions remain explicit in coverage; unsupported questions still count in the
full benchmark denominator. Laya completed all 23,900 DecisionBench requests;
StartLux completed all 18,000 ProceduralTypedDecisions requests and all 3,116
JevAltBench requests. The initial journals remain available separately.

The verified final audit is retained at `artifacts/repair-parallel-final-audit.json`.
The leaderboard now contains 201 retained artifacts and 139 eligible primary
scores across all active suites. Hosted Jev/OpenAI-Decisions measurements remain
pending their API environment; no hosted scores are inferred from local checks.

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
