# JevalKit local leaderboard

The overview uses the latest complete run for each model, benchmark, data hash and protocol; repeated runs are never selected by their best score.
Missing and fully unsupported evaluations have no score. The detailed table retains every run, including smoke tests and imported measurements.

Only currently registered Jev-related benchmarks are included; retired tasks remain in the original result storage.

| Model | DecisionIndex | JevBench | VisualDecisionBench_Image | VisualDecisionBench_Video |
|---|---:|---:|---:|---:|
| Clef-Flash | — | 82.68% | 82.24% | — |
| Crivo-150M | — | 48.48% | — | — |
| Decision1-Kai | — | 49.35% | — | — |
| H2O-Lightning | — | 87.45% | 82.06% | — |
| Intern-Decision-0.8B | — | 71.00% | 66.35% | — |
| JevK5 | — | 88.74% | — | — |
| Kev | — | 74.03% | — | — |
| Laya | — | 58.87% | — | — |
| Liquid-d1-3B | — | 74.89% | 81.82% | — |
| OmniJev | — | — | 62.18% | 63.36% |
| OpenJev | — | 87.45% | 83.12% | — |
| Pplx-Decider | — | 89.18% | 86.88% | — |
| QEV | — | 61.47% | 73.59% | — |
| RSI-Jev-v4 | — | 70.13% | 80.18% | — |
| StartLux-0.8B | — | 76.62% | 71.59% | — |
| Valen-0.8B | 20.71 (imported) | 77.49% | 75.82% | 79.01% |
| Valen-2B | 27.20 (imported) | 82.68% | 80.47% | 82.74% |
| Valen-4B | 38.54 (imported) | 83.55% | 83.12% | 87.43% |
| Visual-Jev | — | — | 77.94% | — |
| Vjev-4B | — | 60.61% | 74.24% | — |

Accuracy is shown as a percentage. DecisionIndex uses the upstream weighted public index (0–100).

| Model | Benchmark | Score | Metric | Valid coverage | Status | Questions | Evidence |
|---|---|---:|---|---:|---|---:|---|
| Valen-4B | DecisionIndex | 38.54 | public index | 99.99% | imported full | 312320 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/imported/Valen-4B/DecisionIndex/metrics.json>) |
| Valen-2B | DecisionIndex | 27.20 | public index | 99.99% | imported full | 312320 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/imported/Valen-2B/DecisionIndex/metrics.json>) |
| Valen-0.8B | DecisionIndex | 20.71 | public index | 99.99% | imported full | 312320 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/imported/Valen-0.8B/DecisionIndex/metrics.json>) |
| Pplx-Decider | JevBench | 89.18% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/Pplx-Decider/JevBench/metrics.json>) |
| JevK5 | JevBench | 88.74% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/JevBench/metrics.json>) |
| H2O-Lightning | JevBench | 87.45% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/H2O-Lightning/JevBench/metrics.json>) |
| OpenJev | JevBench | 87.45% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/OpenJev/JevBench/metrics.json>) |
| Valen-4B | JevBench | 83.55% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/JevBench/metrics.json>) |
| Clef-Flash | JevBench | 82.68% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/Clef-Flash/JevBench/metrics.json>) |
| Valen-2B | JevBench | 82.68% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/JevBench/metrics.json>) |
| Valen-0.8B | JevBench | 77.49% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/JevBench/metrics.json>) |
| StartLux-0.8B | JevBench | 76.62% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/JevBench/metrics.json>) |
| Liquid-d1-3B | JevBench | 74.89% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/JevBench/metrics.json>) |
| Kev | JevBench | 74.03% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/JevBench/metrics.json>) |
| Intern-Decision-0.8B | JevBench | 71.00% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Intern-Decision-0.8B/JevBench/metrics.json>) |
| RSI-Jev-v4 | JevBench | 70.13% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/JevBench/metrics.json>) |
| QEV | JevBench | 61.47% | accuracy | 84.42% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/QEV/JevBench/metrics.json>) |
| Vjev-4B | JevBench | 60.61% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round5/Vjev-4B/JevBench/metrics.json>) |
| Laya | JevBench | 58.87% | accuracy | 100.00% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/JevBench/metrics.json>) |
| Decision1-Kai | JevBench | 49.35% | accuracy | 80.95% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/JevBench/metrics.json>) |
| Crivo-150M | JevBench | 48.48% | accuracy | 92.21% | full | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/JevBench/metrics.json>) |
| Clef-Flash | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round4/Clef-Flash/JevBench/metrics.json>) |
| Crivo-150M | JevBench | 100.00% | accuracy | 100.00% | smoke | 12 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Crivo-150M/JevBench/metrics.json>) |
| Decision1-Kai | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/Decision1-Kai/JevBench/metrics.json>) |
| Intern-Decision-0.8B | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Intern-Decision-0.8B/JevBench/metrics.json>) |
| JevK5 | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round4/JevK5/JevBench/metrics.json>) |
| Liquid-d1-3B | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/Liquid-d1-3B/JevBench/metrics.json>) |
| Pplx-Decider | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round4/Pplx-Decider/JevBench/metrics.json>) |
| RSI-Jev-v4 | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/RSI-Jev-v4/JevBench/metrics.json>) |
| StartLux-0.8B | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/StartLux-0.8B/JevBench/metrics.json>) |
| Valen-0.8B | JevBench | 100.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Valen-0.8B/JevBench/metrics.json>) |
| Vjev-4B | JevBench | 100.00% | accuracy | 100.00% | input-contract error | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Vjev-4B/JevBench/metrics.json>) |
| QEV | JevBench | 97.92% | accuracy | 100.00% | smoke | 48 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/QEV/JevBench/metrics.json>) |
| Vjev-4B | JevBench | 68.83% | accuracy | 100.00% | input-contract error | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/JevBench/metrics.json>) |
| Vjev-4B | JevBench | 68.83% | accuracy | 100.00% | input-contract error | 231 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/JevBench/metrics.json>) |
| Pplx-Decider | VisualDecisionBench_Image | 86.88% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/Pplx-Decider/VisualDecisionBench_Image/metrics.json>) |
| OpenJev | VisualDecisionBench_Image | 83.12% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/OpenJev/VisualDecisionBench_Image/metrics.json>) |
| Valen-4B | VisualDecisionBench_Image | 83.12% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/VisualDecisionBench_Image/metrics.json>) |
| Clef-Flash | VisualDecisionBench_Image | 82.24% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/Clef-Flash/VisualDecisionBench_Image/metrics.json>) |
| H2O-Lightning | VisualDecisionBench_Image | 82.06% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/H2O-Lightning/VisualDecisionBench_Image/metrics.json>) |
| Liquid-d1-3B | VisualDecisionBench_Image | 81.82% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/VisualDecisionBench_Image/metrics.json>) |
| Valen-2B | VisualDecisionBench_Image | 80.47% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/VisualDecisionBench_Image/metrics.json>) |
| RSI-Jev-v4 | VisualDecisionBench_Image | 80.18% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/VisualDecisionBench_Image/metrics.json>) |
| Visual-Jev | VisualDecisionBench_Image | 77.94% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/Visual-Jev/VisualDecisionBench_Image/metrics.json>) |
| Valen-0.8B | VisualDecisionBench_Image | 75.82% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/VisualDecisionBench_Image/metrics.json>) |
| Vjev-4B | VisualDecisionBench_Image | 74.35% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/VisualDecisionBench_Image/metrics.json>) |
| Vjev-4B | VisualDecisionBench_Image | 74.24% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/VisualDecisionBench_Image/metrics.json>) |
| QEV | VisualDecisionBench_Image | 73.59% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/QEV/VisualDecisionBench_Image/metrics.json>) |
| StartLux-0.8B | VisualDecisionBench_Image | 71.59% | accuracy | 99.60% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/VisualDecisionBench_Image/metrics.json>) |
| Intern-Decision-0.8B | VisualDecisionBench_Image | 66.35% | accuracy | 99.95% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Intern-Decision-0.8B/VisualDecisionBench_Image/metrics.json>) |
| OmniJev | VisualDecisionBench_Image | 62.18% | accuracy | 100.00% | full | 2000 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/OmniJev/VisualDecisionBench_Image/metrics.json>) |
| Pplx-Decider | VisualDecisionBench_Image | 75.00% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round4/Pplx-Decider/VisualDecisionBench_Image/metrics.json>) |
| QEV | VisualDecisionBench_Image | 64.15% | accuracy | 100.00% | smoke | 66 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/QEV/VisualDecisionBench_Image/metrics.json>) |
| Clef-Flash | VisualDecisionBench_Image | 62.50% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round4/Clef-Flash/VisualDecisionBench_Image/metrics.json>) |
| RSI-Jev-v4 | VisualDecisionBench_Image | 62.50% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/RSI-Jev-v4/VisualDecisionBench_Image/metrics.json>) |
| StartLux-0.8B | VisualDecisionBench_Image | 62.50% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/StartLux-0.8B/VisualDecisionBench_Image/metrics.json>) |
| Visual-Jev | VisualDecisionBench_Image | 62.50% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Visual-Jev/VisualDecisionBench_Image/metrics.json>) |
| Vjev-4B | VisualDecisionBench_Image | 62.50% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Vjev-4B/VisualDecisionBench_Image/metrics.json>) |
| Intern-Decision-0.8B | VisualDecisionBench_Image | 50.00% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Intern-Decision-0.8B/VisualDecisionBench_Image/metrics.json>) |
| Liquid-d1-3B | VisualDecisionBench_Image | 50.00% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/Liquid-d1-3B/VisualDecisionBench_Image/metrics.json>) |
| OmniJev | VisualDecisionBench_Image | 50.00% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/OmniJev/VisualDecisionBench_Image/metrics.json>) |
| Valen-0.8B | VisualDecisionBench_Image | 50.00% | accuracy | 100.00% | smoke | 8 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Valen-0.8B/VisualDecisionBench_Image/metrics.json>) |
| Valen-4B | VisualDecisionBench_Video | 87.43% | accuracy | 100.00% | full | 7143 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/VisualDecisionBench_Video/metrics.json>) |
| Valen-2B | VisualDecisionBench_Video | 82.74% | accuracy | 100.00% | full | 7143 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/VisualDecisionBench_Video/metrics.json>) |
| Valen-0.8B | VisualDecisionBench_Video | 79.01% | accuracy | 100.00% | full | 7143 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/VisualDecisionBench_Video/metrics.json>) |
| OmniJev | VisualDecisionBench_Video | 63.36% | accuracy | 100.00% | full | 7143 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/OmniJev/VisualDecisionBench_Video/metrics.json>) |
| Valen-0.8B | VisualDecisionBench_Video | 76.92% | accuracy | 100.00% | smoke | 104 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke/Valen-0.8B/VisualDecisionBench_Video/metrics.json>) |
| OmniJev | VisualDecisionBench_Video | 65.38% | accuracy | 100.00% | smoke | 104 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/OmniJev/VisualDecisionBench_Video/metrics.json>) |

TSV/JSON include dataset hashes, protocol, hardware and evidence paths.
Accuracy counts failed/unsupported hard questions as incorrect. Probability metrics use valid outputs.
Decision Index is the upstream public index; its private Full score is not inferred.
