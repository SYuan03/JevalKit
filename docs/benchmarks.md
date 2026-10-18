# Benchmark protocols

Three Jev-related benchmark families are implemented: VisualDecisionBench,
JevBench and Decision Index, exposed through five TSV views. The Image/Video
views are subdivisions of VisualDecisionBench, not additional benchmark families.

| Family | Evaluation data | Scoring |
|---|---|---|
| VisualDecisionBench | Full released `eval.jsonl`, 1,696 shared states, 9,143 questions: 2,000 image and 7,143 video | Hard-label accuracy; soft-label NLL/Brier; ordinal MAE/RPS; modality/type/domain breakdowns |
| JevBench | 231 frozen public tasks: 48 easy, 72 original, 111 hard | Vendored official task scorer, calibration and family/paraphrase reports |
| Decision Index | Edition 0.3 public suite, 140,178 requests after native subset/exclusion rules | Upstream edition-specific, chance-corrected weighted public index; 43 constituent datasets |

Dataset manifests pin the actual source revisions and SHA-256 fingerprints. The
existing Valen snapshots are copied to JevalKit storage; their sources remain
untouched. Media is stored with the TSVs using relative manifest references.

`JevBench` specifically means
[`fstandhartinger/jevbench`](https://github.com/fstandhartinger/jevbench), revision
`bb05a335bc809e61b20c0f745d25499a82b326fc`, used by Valen's public comparison.
Other projects named JevBench use different tasks and cannot share these scores.
The original task's custom true/false rubric is preserved for Noul inference.

Decision Index preserves question IDs, options, order, structured state, gold
labels, grouping, official exclusions and the frozen suite's source metadata.
Unlabeled diagnostic questions remain in the request and carry an explicit
`{"unscored": true}` target. They do not contribute to probability or accuracy
metrics. The official scorer is required for the headline weighted index;
generic field accuracy is a separate diagnostic, not a replacement.

Inference never receives gold labels, rationales, evaluation IDs or source
metadata. Native runtimes retain their published temperatures and context limits.
Models which cannot represent a modality or question type report it as
unsupported. Their failures remain visible in coverage and accuracy.

All probabilities must be finite, nonnegative, within [0,1], with complete
candidate coverage. Generic metrics allow at most 0.01 rounding error in the
sum, recording the raw answer and normalizing only for generic metrics. The
official JevBench scorer retains its own published strict/rounded tolerances and
lexical argmax tie rule. Its official aggregates are retained separately.

NLL floors probabilities at 1e-12; multiclass Brier is the sum of squared errors;
ECE uses 15 equal-width confidence bins; ordinal RPS averages squared cumulative
errors over the first K−1 levels. Soft targets have no hard-label accuracy.
Per-request synchronized latency includes preprocessing and native inference,
excludes model loading/warmup, and is counted once per multi-question request.

Dataset/provider licenses and usage restrictions remain in force. Data stays in
the user-requested shared directory, outside Git. Native Decision Index data with
redistribution restrictions is never automatically published by JevalKit.

## Benchmark research

Checked 2026-10-18. This survey covers all 20 registered model families, using
model-author documentation and benchmark-maintainer releases. It describes
reports across family versions, not fresh JevalKit measurements and not proof
that every registered checkpoint has run every listed evaluation.

The five general NLP tasks were removed from the active registry at the user's
request. Existing shared TSVs and original prediction records remain archived.
The supported count is **3 benchmark families / 5 views**; candidates below are
research findings, not implemented integrations.

### What the 20 model families evaluated or created

| Family | Reported evaluations | Self-created suites and release limits |
|---|---|---|
| [Valen](https://github.com/Liuziyu77/Valen) | VisualDecisionBench; JevBench; Decision Index | Created VisualDecisionBench, earlier General-5k, and Sokoban action/game evaluation. Public data; inspect overlap between earlier General-5k and VDB before pooling. |
| [Intern-Decision](https://github.com/InternLM/Intern-Decision/blob/main/docs/EVALUATION.md) | JevBench; Typed-Decisions; ToolACE; AG News; WildJailBreak | Released a 96-case known-distribution calibration pilot. Accuracy bundles and pilot inputs/references/scorer are public. |
| [Laya](https://github.com/NandhaKishorM/laya/blob/main/BENCHMARKS.md) | Typed-Decisions; zh-decision-bench (community); multilingual intent/NLI and application panels | Publishes application, calibration and option-order harnesses; Typed-Decisions is external. General and workflow-finetuned checkpoints have different training exposure. |
| [Liquid-d1](https://huggingface.co/LiquidAI/d1-3B) | Decision Index; DecisionBench; FastDecisions dev; ImajevBench dev/calibration; converted text/vision tasks | No separate self-created public decision benchmark located in the checked release. FastDecisions dev and Imajev dev/calibration are not their hidden-test leaderboards. |
| [vLLM-Decision1](https://huggingface.co/vllm-sr/Decision-1.0-Kai-0.6B/blob/main/evaluation/BENCHMARK.md) | Self-built fixed 54-task / 3,766-question regression suite | Five weighted groups: Reading, Decisions, Composition, Inference, Transfer. Published matrices/methods; a complete frozen request/label bundle was not located in the checked model files. |
| [Clef](https://huggingface.co/Cloudflare/clef) | Decision Index; four TypeSafe Workflow Evals | No separate self-created public benchmark located in the checked cards. Workflow results are public; bulk test inputs/golds/scorer availability still needs verification. |
| [Pplx-Decider](https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b) | Decision Index | No independent self-created public benchmark located in the checked card. Do not substitute tasksource training data for an evaluation benchmark. |
| [JevK5](https://huggingface.co/alibiserikbay/JevK5) | JevBench; BEV decision test sample; Decision Index proxy | 362 held-out teacher questions and 64 hand-written hard questions used for model selection. Its 16-source development proxy is not an official Decision Index score; BEV is external. |
| [StartLux](https://huggingface.co/startlux-models/StartLux-Decision-v1-0.8B) | Decision Index; JevBench; Intern-Decision seven-column accuracy comparison | No independent self-created public benchmark located in the checked card. The three JevBench tiers in that comparison count as one benchmark family. |
| [Crivo](https://huggingface.co/tardellirs/crivo-150m) | Decision Index; FastDecisions dev; JevAlt-Bench English test | Reports its own runs on external decision datasets. 2,964 requests is the combined FastDecisions + JevAlt panel, not JevAlt alone. |
| [RSI-Jev](https://github.com/Shanghua-Gao/RSI-Jev/blob/main/BENCHMARKS.md) | 15-part suite: Typed-Decisions, JevBench, Kev, procedural and other decision panels; Decision Index | Publishes versioned suite weights, pinned loaders and held-out evaluation protocols. A collection of overlapping benchmarks, not 15 newly created independent benchmarks. |
| [Vjev](https://huggingface.co/yah01/vjev-vision) | COCO geometry decisions; VQAv2 choices; POPE; 20k held-out text rows | Created annotation-derived geometry questions and a text holdout panel. These are author conversions/panels; a frozen standalone public test bundle was not located in the checked card. |
| [QEV](https://github.com/ken-jo/qev/blob/main/docs/LAYA_COMPARISON.md) | Typed-Decisions adapted for its one-question interface; AG News; Emotion; image guards; procedural workflows; 2048 | Created procedural workflow, uncertainty and game diagnostics; publishes qev-data. 15 historical corpus configurations are not 15 independent benchmarks; assistance variants remain separate. |
| [OmniJev](https://github.com/tinnel123666888/OmniJev) | 30 task-family aggregates spanning images/video, agents and games | Built a mixed multimodal evaluation collection and a later frozen question set. Capped/custom holdouts, differing image protocols and incomplete later SFT evaluation prevent uniform official-score claims. |
| [Visual-Jev](https://github.com/guanxuyu-sv/Visual-Jev) | GQA; SNLI-VE; TextVQA; TallyQA, converted to candidate decisions | Publishes a four-task forced-choice evaluation protocol and code. The original datasets are general vision benchmarks; conversions are not four new Jev-specific benchmarks. |
| [Jev](https://evals.typesafe.ai/) | TypeSafe Workflow Evals; Typed-Decisions, zh-decision-bench and procedural evaluations by external maintainers | TypeSafe publishes four structured workflow evaluations. Public external evaluations must be distinguished from TypeSafe-created datasets. |
| [OpenAI-Decisions](https://developers.openai.com/api/docs/guides/decisions) | No independent public decision-specific evaluation dataset established by the checked official documentation | Official documentation describes the typed Decisions API; no standalone benchmark bundle was found there. This is a bounded search finding, not a claim that OpenAI has no internal evaluations. |
| [Kev](https://github.com/jaredpalmer/kev) | JevBench; decision/transfer suites; breadth, hard, devtools, document and tasksource panels | Created versioned decision suites and published frozen data/manifests plus its scorer. Public Hub mirror verified; transfer-v4 test has 764 rows. Some document suites are private; training exposure differs by release. |
| [H2O-Lightning](https://huggingface.co/h2oai/h2o-lightning-4b) | BenchmarkHeaven JevBench; public decision comparisons; Plumb/Eikos routing panels | Released routing questions, predictions and threshold-analysis code. Routing panel mixes Plumb train/test and Eikos validation/heldout. BenchmarkHeaven and the pinned public-231 protocol are not interchangeable. |
| [OpenJev](https://huggingface.co/openjev/openjev) | 10k text questions from 34 sources; browser/desktop steps; option shuffles; MiniWoB development tasks | Created text and agent evaluation panels. Card reports results; a full frozen public request/gold bundle was not located in the checked release. Development-used items are disclosed. |

RSI-Jev's 15-part suite comprises Typed-Decisions, Nimble public, MMLU-Pro,
Jev-Style, Kev transfer, Kev hard, tasksource, SemIf, scienthoon OOD, Kev
documents, Kev devtools, Nimble holdout, procedural and Open-Jev OOD, alongside
JevBench. It is a versioned aggregate of existing sources. JevBench's three
difficulty tiers, Decision Index editions, and repeated views of one source
do not become independent benchmarks when counted separately.

### Candidates and integration priority

P1 means recommended next integration work. Public data alone does not establish
a matching scorer, independence from training, or comparability with an author's
score. Each integration still needs a frozen protocol and adapter validation.

| Candidate | Priority | Relationship and available evaluation | Material limits |
|---|---|---|---|
| [Typed-Decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) | P1 | 400 test states / 2,000 decisions; four workflows; Noul/Choice/Score and soft golds. Laya, Intern-Decision, QEV; Jev and Liquid API rows by the benchmark maintainer. Public test data and golds; evaluate all questions per state, preserving the chosen interface. | Teacher agreement is not objective correctness; mark general vs workflow-finetuned models. |
| [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | P1 | 23,900 eval rows; three primitives; 43 task IDs; candidates up to 255. Liquid d1 reports a full-suite evaluation. Public canonical eval Parquet, gold targets, provenance and evaluation code. | Standard and compact inputs are separate protocols; retain option IDs/order/ordinal values. |
| [Procedural Typed Decisions](https://huggingface.co/datasets/tasksource/procedural-typed-decisions) | P1 | Exact rule-derived multi-question decisions; current card lists 18 task configurations plus all. RSI-Jev evaluates a pinned version; Crivo also trains on this data. Public train/validation/test, reference answers and deterministic generators. | Pin a revision: the RSI-pinned release has a different configuration set. Known train exposure must be disclosed. |
| [zh-decision-bench](https://github.com/CodyQin/zh-decision-bench) | P1 | Current v0.2: 378 items / 467 questions; Chinese routing, service and moderation. Laya and Jev, with Qwen and NeoHorse baselines, evaluated by the benchmark author. Public golds, raw predictions, scorer and robustness/refit scripts. | Older Laya notes describe v0.1 219/284. Small subgroups and one human adjudicator limit conclusions. |
| [JevAlt-Bench](https://huggingface.co/datasets/mertkayacs/jevalt-bench) | P1 | 3,116 test requests / 8,434 questions across English, Turkish and German. Crivo reports English evaluation; dataset authors compare Kev and Laya. Public JSONL with probability targets; JevOss evaluator is public. | Mostly converted public tasks plus authored scenarios. File location defines split even when row split says train; upstream overlap is disclosed. |
| [Kev frozen suites](https://huggingface.co/datasets/jaredpalmer/kev-suites/tree/main) | P2 | Versioned decision, transfer, policy and robustness tests; transfer-v4 test has 764 rows. Kev; RSI-Jev reuses selected Kev suites. Verified public test JSONL/manifests in jaredpalmer/kev-suites; kev.benchmark scores native requests. | Select a named version and split; do not pool overlapping suite versions or private document tests. |
| [Intern known-distribution pilot](https://github.com/InternLM/Intern-Decision/blob/main/docs/CALIBRATION_BENCHMARK.md) | Diagnostic | 96 cases / 48 paired parameter settings with exact outcome distributions. Created and released by Intern-Decision. Public inputs, separate references, deterministic generator and offline scorer. | Use excess expected Brier/TVD/expected ECE, not hard-label accuracy. It is a small diagnostic pilot. |
| [ImajevBench](https://huggingface.co/datasets/mohit67890/imajev-bench) | Preview / partial public scoring | Text, visual and joint decision tracks; 533 public items including 279 test items. Liquid d1 evaluates public dev/calibration. Dev/calibration golds public; test golds withheld, scored by maintainers; additional private hidden set. | Keep public split scores separate from test leaderboard. Preserve evidence-cluster grouping and quarantine metadata. |
| [Valen General-5k / Sokoban](https://huggingface.co/datasets/Valen-Team/Valen-Eval-Game) | P2 | General-5k: 5,000 visual decisions. Sokoban: 500 actions and 100 full-game test levels. Created by Valen. Public data/media and evaluator references. | Check General-5k overlap with VDB. Sokoban action and game views share test layouts and measure different outcomes. |
| [BEV decision test split](https://huggingface.co/datasets/avbiswas/bev-decision) | Secondary corpus evaluation | Original default: 150k total rows, including 24,386 test rows; multiple typed questions. JevK5 evaluates 2,500 hashed test rows, not the whole release. Public held-out data, but collection is primarily a converted training corpus. | Old bev-decision-150K ID redirects to bev-decision; choose config/revision and audit source-specific terms (card says license unknown). |
| [FastDecisions](https://huggingface.co/datasets/fastino/fast-decisions) | Development diagnostic | 17 operational classification domains; public development set of 1,700 rows. Liquid d1 and Crivo evaluate development data. Development data public; official 300-per-domain test data is held out. | The card explicitly says not to report a public-dev score as its test benchmark score; support multi-label heads faithfully. |
| [Plumb / Eikos routing panels](https://huggingface.co/h2oai/h2o-lightning-4b/blob/main/routing_reproducibility/README.md) | Diagnostic | H2O release: 2,000 Plumb + 1,474 Eikos questions. H2O-Lightning evaluates these native decision datasets. Public frozen question conversions, predictions and threshold-analysis code. | Plumb includes 1,869 train + 131 test; Eikos combines English validation/heldout. Do not call the mixture a blind independent test. |
| [TypeSafe Workflow Evals](https://evals.typesafe.ai/) | Public results / bundle not verified | Four business workflows with typed primitives and consensus reference labels. Clef and Jev. Public evaluation website; a complete downloadable test/gold/scorer bundle was not verified. | Shares workflow themes with LocalLLaMA Typed-Decisions, but that dataset is independent; do not assume identical inputs or labels. |
| [Kai / OpenJev / Vjev custom panels](https://huggingface.co/vllm-sr/Decision-1.0-Kai-0.6B/blob/main/evaluation/BENCHMARK.md) | Reported panels / release needed | Fixed regression, agent/text and vision-geometry panels respectively. Their model authors. Published reports; complete canonical input/gold/scorer bundles not established by this survey. | A score table or screenshot is not enough to claim a reproducible public benchmark integration. |

The recommended primary expansion is **Typed-Decisions, DecisionBench, Procedural
Typed Decisions, zh-decision-bench and JevAlt-Bench**. Alongside the existing
three, that would provide eight Jev-related suite families after integration.
This selection targets workflow judgments, runtime-defined labels, rule execution,
Chinese calibration and multilingual decisions rather than padding the count
with standalone sentiment or topic-classification tasks.

Intern-Decision's exact-distribution pilot belongs in a separate calibration
report: outcomes are random and have no observed hard label. ImajevBench's
public dev/calibration scores must remain separate from its maintainer-scored
test. TypeSafe Workflow Evals and LocalLLaMA Typed-Decisions share workflow
themes but have different authors and reference-label mechanisms.

### Reproducibility checks

Direct public-file checks verified the Intern-Decision Typed-Decisions mirror
(400 rows, 2,000 questions, matching its release manifest), calibration inputs
(96 rows), Kev transfer-v4 test (764 rows), and Plumb test (131 rows). These checks
read public files in memory and did not run a model.

Versions matter: current zh-decision-bench is v0.2 (378/467), while older Laya
notes reference v0.1 (219/284). Current procedural data has 18 task configs,
while RSI's pinned revision exposes a smaller set. Pin exact files before
comparing results. JevAlt's current English test has 1,277 requests; Crivo's
2,964-request figure covers two datasets together.

[Machine-readable survey](benchmark-survey.json) records all 20 families,
candidate priorities, source URLs and document hashes, dataset revisions and
public-file check hashes. No candidate scores were added to the leaderboard.
