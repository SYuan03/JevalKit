# Benchmark protocols

Eight evaluation families are implemented: three Jev-related suites
(VisualDecisionBench, JevBench and Decision Index) and five auxiliary general NLP
tasks adapted to typed decisions (AG News, Banking77, BoolQ, SST-2 and When2Call).
The auxiliary tasks are not independent Jev-specific benchmarks. The Image/Video
views are subdivisions of VisualDecisionBench, not additional benchmark families.

| Family | Evaluation data | Scoring |
|---|---|---|
| VisualDecisionBench | Full released `eval.jsonl`, 1,696 shared states, 9,143 questions: 2,000 image and 7,143 video | Hard-label accuracy; soft-label NLL/Brier; ordinal MAE/RPS; modality/type/domain breakdowns |
| JevBench | 231 frozen public tasks: 48 easy, 72 original, 111 hard | Vendored official task scorer, calibration and family/paraphrase reports |
| Decision Index | Edition 0.3 public suite, 140,178 requests after native subset/exclusion rules | Upstream edition-specific, chance-corrected weighted public index; 43 constituent datasets |
| AG News | All 7,600 test examples | Four-way topic accuracy and probability metrics |
| Banking77 | All 3,080 test examples | 77-way intent accuracy and probability metrics |
| BoolQ | All 3,270 public validation examples | Boolean accuracy and probability metrics |
| SST-2 | All 872 labeled public validation examples | Sentiment accuracy and probability metrics |
| When2Call | All 3,652 MCQ test examples | Four supplied responses in published order, following HF Decision Index's MCQ projection |

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
