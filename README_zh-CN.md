<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/branding/jevalkit-dark.svg">
    <img src="assets/branding/jevalkit-light.svg" alt="JevalKit 决策模型评测工具" width="680">
  </picture>
</h1>

<p align="center">
  <b>Jev 类决策模型评测工具</b><br>
  文本 · 图像 · 视频 → Choice · Noul · Score
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
  <a href="#introduction">简介</a> · <a href="#latest-updates">更新</a> · <a href="#quick-start">快速开始</a> · <a href="#supported-models">模型</a> · <a href="#supported-benchmarks">基准</a> · <a href="#evaluation-results">结果</a> · <a href="#documentation">文档</a>
</p>

<p align="center">
  <a href="README.md">English</a> · <b>简体中文</b>
</p>

<a id="introduction"></a>

## ✨ 简介

JevalKit 用于评测 Jev 类决策模型。这类模型接收请求中指定的选项或评分标准，返回相应的概率：
`Choice` 表示从给定选项中选择，`Noul` 表示是非判断，`Score` 表示有序评分。
工具提供模型适配、数据准备、评分和结果比较功能，注册机制参考了
[VLMEvalKit](https://github.com/open-compass/VLMEvalKit)。

<a id="highlights"></a>

## 🎯 主要功能

- 支持 20 个模型家族，通过作者原生接口加载开放权重模型，或调用托管模型的公开 API。
- 接收文本、图像和视频，保留共享输入、多问题请求、候选项顺序及各模型的模态限制。
- 评测完整概率分布，报告准确率、Brier、NLL、校准和有序评分指标，并接入基准专用评分器。
- 保存数据哈希、原始预测、运行环境、失败记录和覆盖率，支持断点恢复和重新评分。
- 提供排行榜及 Markdown、TSV、JSON 导出，区分完整评测、冒烟测试和导入的预测结果。

<a id="latest-updates"></a>

## 📰 最近更新

<!-- jevalkit:coverage:start -->
- **2026-10-19：** 正在补测 22 组缺失的模型与基准组合，已核验 **19/22** 组。
  全量数据并行评测，GPU 并发不超过 **32 张**；通过核验的结果陆续发布到[排行榜](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)。
<!-- jevalkit:coverage:end -->
- **2026-10-19：** 发布 [🤗 排行榜](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)，支持基准筛选、模型比较、概率指标查看，以及 CSV/JSON 下载。
- **2026-10-19：** 在 [🤗 JevalKit Datasets](https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets) 发布全部 10 个 TSV 数据视图；来源和评分协议见[各基准目录](jevalkit/datasets/)。
- **2026-10-19：** 五个新增基准的 110/110 组评测全部完成，其中 99 组成绩符合收录条件，11 组完全不受模型支持。已核验代码、权重和请求覆盖情况，详情见[排行榜](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)。

<details>
<summary>更早的更新</summary>

- **2026-10-18：** 接入 Typed-Decisions、DecisionBench、Procedural Typed Decisions、zh-decision-bench 和 JevAlt-Bench，基准总数增至八个。
- **2026-10-18：** 完成 18 个模型家族的原生推理验证。Jev 和 OpenAI Decisions 的适配器已实现，实际 API 评测尚未完成。

</details>

<a id="quick-start"></a>

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/Valen-Team/JevalKit.git
cd JevalKit
python -m pip install -e '.[hf,data]'
```

命令行工具和评分器需要 Python 3.10 或更高版本。模型推理还需安装作者指定的依赖；部分模型需要
Python 3.12 或独立的服务环境，见[模型接入说明](docs/models_zh-CN.md)。

### 2. 下载模型和数据集

```bash
export JEVALKIT_DATA_ROOT="$PWD/data"

hf download Valen-Team/Valen-0.8B \
  --local-dir "$JEVALKIT_DATA_ROOT/models/Valen-0.8B"

hf download Valen-Team/JevalKit_Datasets --repo-type dataset \
  --include "datasets/JevBench.tsv" --local-dir "$JEVALKIT_DATA_ROOT"
```

发布的 TSV 可直接用于评测。将 `datasets/JevBench.tsv` 改为 `datasets/*.tsv` 可下载全部十个视图。
VisualDecisionBench 的媒体文件和 Decision Index 的评分输入需另行下载，见[使用指南](docs/quickstart_zh-CN.md#download-data)。

### 3. 运行评测并比较结果

```bash
python -m jevalkit run --model Valen-0.8B --data JevBench \
  --option model="$JEVALKIT_DATA_ROOT/models/Valen-0.8B" \
  --output "$JEVALKIT_DATA_ROOT/results"

python -m jevalkit leaderboard "$JEVALKIT_DATA_ROOT/results" \
  --output "$JEVALKIT_DATA_ROOT/leaderboard"
```

已有权重可通过 `--option model=/path/to/checkpoint` 指定。使用 `--limit 10` 可做冒烟测试；
使用 `--resume` 可在相同配置下继续中断的评测。完整命令见[使用指南](docs/quickstart_zh-CN.md)。

<a id="supported-models"></a>

## 🤖 支持的模型

同一家族的尺寸变体合并计数，Clef 和 Clef-Flash 也属于同一家族。
“已实测”表示该家族至少有一个注册变体完成了真实推理验证；各基准的覆盖情况见[排行榜](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)。

<details>
<summary>查看支持的模型（20 个家族）</summary>

| 模型家族 | 注册模型 ID | 接口 | 评测状态 |
|---|---|---|---|
| [Valen](https://github.com/Valen-Team/Valen) | `Valen-0.8B`, `Valen-2B`, `Valen-4B` | 原生接口 | 已实测 |
| [Intern-Decision](https://github.com/InternLM/Intern-Decision) | `Intern-Decision-0.8B`, `Intern-Decision-2B`, `Intern-Decision-4B` | 原生接口 | 已实测 |
| [Laya](https://github.com/NandhaKishorM/laya) | `Laya` | 原生接口 | 已实测 |
| [Liquid d1](https://huggingface.co/LiquidAI/d1-3B) | `Liquid-d1-3B` | 原生接口 | 已实测 |
| [vLLM Decision1](https://huggingface.co/vllm-sr/Decision-1.0-Kai-0.6B) | `Decision1-Kai` | 原生接口 | 已实测 |
| [Clef](https://huggingface.co/Cloudflare/clef) | `Clef`, `Clef-Flash` | 原生接口 | 已实测 |
| [Pplx-Decider](https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b) | `Pplx-Decider` | 原生接口 | 已实测 |
| [JevK5](https://huggingface.co/alibiserikbay/JevK5) | `JevK5` | 原生接口 | 已实测 |
| [StartLux](https://huggingface.co/startlux-models/StartLux-Decision-v1-0.8B) | `StartLux-0.8B` | 原生接口 | 已实测 |
| [Crivo](https://huggingface.co/tardellirs/crivo-150m) | `Crivo-150M` | 原生接口 | 已实测 |
| [RSI-Jev](https://github.com/Shanghua-Gao/RSI-Jev) | `RSI-Jev-v4` | 原生接口 | 已实测 |
| [Vjev](https://huggingface.co/yah01/vjev-vision) | `Vjev-4B` | 原生接口 | 已实测 |
| [QEV](https://github.com/ken-jo/qev) | `QEV` | 原生接口 | 已实测 |
| [OmniJev](https://github.com/tinnel123666888/OmniJev) | `OmniJev` | 原生接口 | 已实测 |
| [Visual-Jev](https://github.com/guanxuyu-sv/Visual-Jev) | `Visual-Jev` | 原生接口 | 已实测 |
| [Kev](https://github.com/jaredpalmer/kev) | `Kev` | 作者服务 | 已实测 |
| [H2O-Lightning](https://huggingface.co/h2oai/h2o-lightning-4b) | `H2O-Lightning` | 作者服务 | 已实测 |
| [OpenJev](https://huggingface.co/openjev/openjev) | `OpenJev` | 作者服务 | 已实测 |
| [Jev](https://typesafe.ai) | `Jev` | 托管 API | 待实际评测 |
| [OpenAI Decisions](https://developers.openai.com/api/docs/guides/decisions) | `OpenAI-Decisions` | 托管 API | 待实际评测 |

</details>

注册表还包含用于流程诊断的 `Uniform` 基线。作者依赖、上下文限制、问题类型和媒体输入约定见
[模型接入说明](docs/models_zh-CN.md)。

<a id="supported-benchmarks"></a>

## 🧩 支持的基准

<details>
<summary>查看支持的数据集（8 个基准）</summary>

| 基准 | 输入 | 评测数据 | 主要指标 |
|---|---|---|---|
| [VisualDecisionBench](https://huggingface.co/datasets/Valen-Team/VisualDecisionBench) | 🖼️ 图像 · 🎬 视频 | 1,696 个共享输入；9,143 个问题 | 准确率、软标签 Brier/NLL、有序评分指标 |
| [JevBench](https://github.com/fstandhartinger/jevbench) | 📝 文本 | 231 个公开任务，分为 easy/original/hard 三档 | 官方任务得分与校准指标 |
| [Decision Index](https://huggingface.co/spaces/multimodalart/jev-decision-index) | 📝 文本 | 0.3 版公开套件，包含 43 个数据集 | 官方随机水平校正后的加权公开指数 |
| [Typed-Decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) | 📝 文本 | 400 个共享输入；2,000 个决策问题 | 标签准确率、KL、软标签 Brier |
| [DecisionBench](https://huggingface.co/datasets/Hanno-Labs/decision-bench) | 📝 文本 | 23,900 条评测样本；43 个任务 | 准确率、参考 NLL、校准指标 |
| [Procedural Typed Decisions](https://huggingface.co/datasets/tasksource/procedural-typed-decisions) | 📝 文本 | 18,000 个测试输入；57,016 个问题 | 规则执行与精确概率判断 |
| [zh-decision-bench](https://github.com/CodyQin/zh-decision-bench) | 📝 中文 | v0.2：378 条样本；467 个问题 | 路由、内容审核、有序评分、校准指标 |
| [JevAlt-Bench](https://huggingface.co/datasets/mertkayacs/jevalt-bench) | 📝 英语 · 土耳其语 · 德语 | 3,116 个测试输入；8,434 个问题 | 硬标签与软概率决策、分语言统计 |

</details>

VisualDecisionBench 的图像和视频视图属于同一个基准。Decision Index 的公开得分与私有评测部分分别报告。
数据来源和评分细节见[各基准目录](jevalkit/datasets/)及[评分协议](docs/benchmarks_zh-CN.md)。

可从 [🤗 JevalKit Datasets](https://huggingface.co/datasets/Valen-Team/JevalKit_Datasets) 下载已转换的 TSV，
使用[矩阵配置示例](examples/decision-benchmarks.json)批量评测多个模型和基准。

<a id="evaluation-results"></a>

## 📊 评测结果

<!-- jevalkit:results-summary:start -->
当前快照包含 **158 条有效完整成绩**，保留 **236 份运行记录**，覆盖 **18 个已实测模型家族**。
两个托管 API 家族仍待实际评测。[🤗 打开排行榜](https://huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard)。
<!-- jevalkit:results-summary:end -->

<a id="documentation"></a>

## 📖 文档

| 文档 | 内容 |
|---|---|
| [使用指南](docs/quickstart_zh-CN.md) | 下载、评测命令、断点恢复、API 和并行任务 |
| [模型接入](docs/models_zh-CN.md) | 作者 SDK、运行依赖和输入限制 |
| [评分协议](docs/benchmarks_zh-CN.md) | 数据集定义、概率指标和官方评分器 |

<a id="contributing"></a>

## 🤝 参与贡献

每个模型实现在 `jevalkit/models/` 中有独立文件，通过 [jevalkit/config.py](jevalkit/config.py) 注册。
每个基准在 `jevalkit/datasets/` 中有独立目录，保存数据准备、评分和 TSV 元信息。
新增实现应保留原生概率、候选项顺序和公开评分协议，并附上可复现的命令及相关验证结果。

```bash
python -m pip install -e '.[test]'
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```

问题和建议可提交至 [Issues](https://github.com/Valen-Team/JevalKit/issues)，
代码贡献可通过 [Pull Requests](https://github.com/Valen-Team/JevalKit/pulls) 提交。

<a id="license-and-acknowledgements"></a>

## 📄 许可与致谢

JevalKit 采用 [Apache-2.0](LICENSE) 许可。模型权重、数据集和第三方代码各自保留原有许可，
详见 [THIRD_PARTY.md](THIRD_PARTY.md)。感谢 [VLMEvalKit](https://github.com/open-compass/VLMEvalKit)
提供的评测工具设计参考，以及各决策模型和基准的作者。
