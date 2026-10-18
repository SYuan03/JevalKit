# JevalKit local leaderboard

The overview uses the latest complete run for each model, benchmark, data hash and protocol; repeated runs are never selected by their best score.
Missing and fully unsupported evaluations have no score. The detailed table retains every run, including smoke tests and imported measurements.

| Model | AGNews | Banking77 | BoolQ | DecisionIndex | JevBench | SST2 | VisualDecisionBench_Image | VisualDecisionBench_Video | When2Call |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Clef-Flash | — | — | — | — | 82.68% | — | 82.24% | — | — |
| Crivo-150M | 76.87% | 90.49% | 65.29% | — | 48.48% | 88.76% | — | — | 65.01% |
| Decision1-Kai | 77.20% | 46.23% | 74.68% | — | 49.35% | 79.36% | — | — | 28.92% |
| H2O-Lightning | — | — | — | — | 87.45% | — | 82.06% | — | — |
| Intern-Decision-0.8B | 85.47% | — | 75.54% | — | 71.00% | 87.04% | 66.35% | — | 45.81% |
| JevK5 | 81.79% | 71.07% | 87.95% | — | 88.74% | 93.12% | — | — | 74.21% |
| Kev | 90.17% | 85.06% | 89.36% | — | 74.03% | 94.27% | — | — | 64.40% |
| Laya | 92.76% | 37.92% | 76.91% | — | 58.87% | 91.63% | — | — | 15.39% |
| Liquid-d1-3B | 88.39% | 87.63% | 87.74% | — | 74.89% | 93.46% | 81.82% | — | 86.39% |
| OmniJev | — | — | — | — | — | — | 62.18% | 63.36% | — |
| OpenJev | — | — | — | — | 87.45% | — | 83.12% | — | — |
| Pplx-Decider | — | — | — | — | 89.18% | — | 86.88% | — | — |
| QEV | 83.57% | — | 78.62% | — | 61.47% | 88.65% | 73.59% | — | 35.16% |
| RSI-Jev-v4 | 85.20% | 61.36% | 86.79% | — | 70.13% | 92.32% | 80.18% | — | 44.58% |
| StartLux-0.8B | 90.53% | 89.12% | 84.19% | — | 76.62% | 92.89% | 71.59% | — | 76.26% |
| Valen-0.8B | 75.82% | 64.06% | 80.18% | 20.71 (imported) | 77.49% | 89.45% | 75.82% | 79.01% | 40.14% |
| Valen-2B | 83.30% | 70.00% | 85.87% | 27.20 (imported) | 82.68% | 92.89% | 80.47% | 82.74% | 47.51% |
| Valen-4B | 84.46% | 70.84% | 88.96% | 38.54 (imported) | 83.55% | 90.60% | 83.12% | 87.43% | 50.36% |
| Visual-Jev | — | — | — | — | — | — | 77.94% | — | — |
| Vjev-4B | 87.75% | 78.21% | 78.84% | — | 60.61% | 92.89% | 74.24% | — | 41.62% |

Accuracy is shown as a percentage. DecisionIndex uses the upstream weighted public index (0–100).

| Model | Benchmark | Score | Metric | Valid coverage | Status | Questions | Evidence |
|---|---|---:|---|---:|---|---:|---|
| Laya | AGNews | 92.76% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/AGNews/metrics.json>) |
| StartLux-0.8B | AGNews | 90.53% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/AGNews/metrics.json>) |
| Kev | AGNews | 90.17% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/AGNews/metrics.json>) |
| Liquid-d1-3B | AGNews | 88.39% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/AGNews/metrics.json>) |
| Vjev-4B | AGNews | 87.76% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/AGNews/metrics.json>) |
| Vjev-4B | AGNews | 87.75% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/AGNews/metrics.json>) |
| Intern-Decision-0.8B | AGNews | 85.47% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Intern-Decision-0.8B/AGNews/metrics.json>) |
| RSI-Jev-v4 | AGNews | 85.20% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/AGNews/metrics.json>) |
| Valen-4B | AGNews | 84.46% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/AGNews/metrics.json>) |
| QEV | AGNews | 83.57% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/QEV/AGNews/metrics.json>) |
| Valen-2B | AGNews | 83.30% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/AGNews/metrics.json>) |
| JevK5 | AGNews | 81.79% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/AGNews/metrics.json>) |
| Decision1-Kai | AGNews | 77.20% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/AGNews/metrics.json>) |
| Crivo-150M | AGNews | 76.87% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/AGNews/metrics.json>) |
| Valen-0.8B | AGNews | 75.82% | accuracy | 100.00% | full | 7600 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/AGNews/metrics.json>) |
| Crivo-150M | Banking77 | 90.49% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/Banking77/metrics.json>) |
| StartLux-0.8B | Banking77 | 89.12% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/Banking77/metrics.json>) |
| Liquid-d1-3B | Banking77 | 87.63% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/Banking77/metrics.json>) |
| Kev | Banking77 | 85.06% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/Banking77/metrics.json>) |
| Vjev-4B | Banking77 | 78.31% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/Banking77/metrics.json>) |
| Vjev-4B | Banking77 | 78.21% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/Banking77/metrics.json>) |
| JevK5 | Banking77 | 71.07% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/Banking77/metrics.json>) |
| Valen-4B | Banking77 | 70.84% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/Banking77/metrics.json>) |
| Valen-2B | Banking77 | 70.00% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/Banking77/metrics.json>) |
| Valen-0.8B | Banking77 | 64.06% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/Banking77/metrics.json>) |
| RSI-Jev-v4 | Banking77 | 61.36% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/Banking77/metrics.json>) |
| Decision1-Kai | Banking77 | 46.23% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/Banking77/metrics.json>) |
| Laya | Banking77 | 37.92% | accuracy | 100.00% | full | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/Banking77/metrics.json>) |
| Intern-Decision-0.8B | Banking77 | — | accuracy | 0.00% | unsupported | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/Intern-Decision-0.8B/Banking77/metrics.json>) |
| QEV | Banking77 | — | accuracy | 0.00% | unsupported | 3080 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/QEV/Banking77/metrics.json>) |
| Kev | BoolQ | 89.36% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/BoolQ/metrics.json>) |
| Valen-4B | BoolQ | 88.96% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/BoolQ/metrics.json>) |
| JevK5 | BoolQ | 87.95% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/BoolQ/metrics.json>) |
| Liquid-d1-3B | BoolQ | 87.74% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/BoolQ/metrics.json>) |
| RSI-Jev-v4 | BoolQ | 86.79% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/BoolQ/metrics.json>) |
| Valen-2B | BoolQ | 85.87% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/BoolQ/metrics.json>) |
| StartLux-0.8B | BoolQ | 84.19% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/BoolQ/metrics.json>) |
| Valen-0.8B | BoolQ | 80.18% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/BoolQ/metrics.json>) |
| Vjev-4B | BoolQ | 78.87% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/BoolQ/metrics.json>) |
| Vjev-4B | BoolQ | 78.84% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/BoolQ/metrics.json>) |
| QEV | BoolQ | 78.62% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/QEV/BoolQ/metrics.json>) |
| Laya | BoolQ | 76.91% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/BoolQ/metrics.json>) |
| Intern-Decision-0.8B | BoolQ | 75.54% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/Intern-Decision-0.8B/BoolQ/metrics.json>) |
| Decision1-Kai | BoolQ | 74.68% | accuracy | 99.97% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/BoolQ/metrics.json>) |
| Crivo-150M | BoolQ | 65.29% | accuracy | 100.00% | full | 3270 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/BoolQ/metrics.json>) |
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
| Kev | SST2 | 94.27% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/SST2/metrics.json>) |
| Liquid-d1-3B | SST2 | 93.46% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/SST2/metrics.json>) |
| JevK5 | SST2 | 93.12% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/SST2/metrics.json>) |
| StartLux-0.8B | SST2 | 92.89% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/SST2/metrics.json>) |
| Valen-2B | SST2 | 92.89% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/SST2/metrics.json>) |
| Vjev-4B | SST2 | 92.89% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/SST2/metrics.json>) |
| Vjev-4B | SST2 | 92.89% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/SST2/metrics.json>) |
| RSI-Jev-v4 | SST2 | 92.32% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/SST2/metrics.json>) |
| Laya | SST2 | 91.63% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/SST2/metrics.json>) |
| Valen-4B | SST2 | 90.60% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/SST2/metrics.json>) |
| Valen-0.8B | SST2 | 89.45% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/SST2/metrics.json>) |
| Crivo-150M | SST2 | 88.76% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/SST2/metrics.json>) |
| QEV | SST2 | 88.65% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/QEV/SST2/metrics.json>) |
| Intern-Decision-0.8B | SST2 | 87.04% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/Intern-Decision-0.8B/SST2/metrics.json>) |
| Decision1-Kai | SST2 | 79.36% | accuracy | 100.00% | full | 872 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/SST2/metrics.json>) |
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
| Liquid-d1-3B | When2Call | 86.39% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Liquid-d1-3B/When2Call/metrics.json>) |
| StartLux-0.8B | When2Call | 76.26% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/StartLux-0.8B/When2Call/metrics.json>) |
| JevK5 | When2Call | 74.21% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round4/JevK5/When2Call/metrics.json>) |
| Crivo-150M | When2Call | 65.01% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Crivo-150M/When2Call/metrics.json>) |
| Kev | When2Call | 64.40% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/served-round4/Kev/When2Call/metrics.json>) |
| Valen-4B | When2Call | 50.36% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-4B/When2Call/metrics.json>) |
| Valen-2B | When2Call | 47.51% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-2B/When2Call/metrics.json>) |
| Intern-Decision-0.8B | When2Call | 45.81% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Intern-Decision-0.8B/When2Call/metrics.json>) |
| RSI-Jev-v4 | When2Call | 44.58% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/RSI-Jev-v4/When2Call/metrics.json>) |
| Vjev-4B | When2Call | 41.70% | accuracy | 99.92% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Vjev-4B/When2Call/metrics.json>) |
| Vjev-4B | When2Call | 41.62% | accuracy | 99.92% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Vjev-4B/When2Call/metrics.json>) |
| Valen-0.8B | When2Call | 40.14% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Valen-0.8B/When2Call/metrics.json>) |
| QEV | When2Call | 35.16% | accuracy | 98.08% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round2/QEV/When2Call/metrics.json>) |
| Decision1-Kai | When2Call | 28.92% | accuracy | 73.66% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/round3/Decision1-Kai/When2Call/metrics.json>) |
| Laya | When2Call | 15.39% | accuracy | 100.00% | full | 3652 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/full/Laya/When2Call/metrics.json>) |
| Decision1-Kai | When2Call | 0.00% | accuracy | 100.00% | smoke | 4 | [run](</mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit/results/smoke-round3/Decision1-Kai/When2Call/metrics.json>) |

TSV/JSON include dataset hashes, protocol, hardware and evidence paths.
Accuracy counts failed/unsupported hard questions as incorrect. Probability metrics use valid outputs.
Decision Index is the upstream public index; its private Full score is not inferred.
