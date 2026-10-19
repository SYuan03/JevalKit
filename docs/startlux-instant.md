# StartLux v1.1 Instant integration

This integration registers the author's v1.1 Instant models as separate configurations.
It does not add measurements, import model-card scores, or update the public leaderboard.
The existing native `StartLux-0.8B` ID still selects v1 and is unchanged.

| Registered ID | Author checkpoint |
|---|---|
| StartLux-v1.1-0.8B-Instant | startlux-models/StartLux-Decision-v1.1-0.8B-Instant |
| StartLux-v1.1-2B-Instant | startlux-models/StartLux-Decision-v1.1-2B-Instant |
| StartLux-v1.1-4B-Instant | startlux-models/StartLux-Decision-v1.1-4B-Instant |
| StartLux-v1.1-9B-Instant | startlux-models/StartLux-Decision-v1.1-9B-Instant |
| StartLux-v1.1-27B-Instant | startlux-models/StartLux-Decision-v1.1-27B-Instant |

## Author service

Use the [official package](https://github.com/StartLuxLabs/StartLux-Decision) in a
separate serving environment. Follow its installation instructions and pin the
source revision, dependencies and checkpoint revision used in an actual run.
For example, after installing the package and downloading the complete checkpoint:

```bash
startlux-decide serve \
  --model /models/StartLux-Decision-v1.1-4B-Instant \
  --name StartLux-Decision-v1.1-4B-Instant \
  --launch-vllm --gpus 0 --port 8090
```

Images require an image-capable author backend and a folder with vision weights;
the author documents vLLM 0.31+ for images. The adapter itself needs no Torch or
Transformers import. See the [author API](https://github.com/StartLuxLabs/StartLux-Decision/blob/main/docs/api.md)
for backend requirements, context limits and server configuration.

In the JevalKit environment:

```bash
export STARTLUX_ENDPOINT=http://127.0.0.1:8090/v1/systemone
# Set STARTLUX_API_KEY in the environment if the server requires authentication.
python -m jevalkit check --model StartLux-v1.1-4B-Instant \
  --output /tmp/startlux-instant-interface-check.json
```

`check` uses synthetic interface fixtures; it is not a benchmark measurement.
To run a benchmark later, after downloading and verifying its published data:

```bash
python -m jevalkit run --model StartLux-v1.1-4B-Instant --data JevBench \
  --output ./results/startlux-instant
```

Each registered ID needs a server actually serving that checkpoint. The author
server ignores the request's `model` field; it does not switch weights per request.
The adapter therefore checks the returned `model` against the checkpoint basename.
If the server deliberately uses another `--name`, supply
`--option expected_response_model=YOUR_SERVER_NAME`; that selection is recorded.
A matching name is a deployment check, not proof of weight identity. Use managed
service provenance to retain weights, configuration, source and startup arguments.
The [managed-service example](../examples/startlux-instant.json) fingerprints the
checkpoint and package source; replace its absolute paths with your deployment.
Preserve the serving environment's dependency lock/version inventory alongside
the run. The client environment alone does not describe a remote inference engine.

## Request and response contract

- Every request explicitly sends `think_mode=never`, `allow_none=false` and
  `none_check=true`. These fixed controls are also saved in runtime metadata.
  Instant never thinks; AutoThink models and control overrides are outside this integration.
- Plain text and JSON states are passed through, including `null`, `false` and
  ordered arrays. The author service owns JSON rendering. Question IDs, criteria,
  descriptions and ordering are retained without rewriting instructions.
- Canonical user-message evidence is flattened in order, with an `<image>` marker
  at each image position and image data URIs in the top-level `images` list.
  Local files and image data URIs are accepted. Materialize remote images first.
  Ambiguous pre-existing markers, non-user roles and native video are unsupported.
- At most eight images and two to ten Score levels are supported. Unsupported
  requests retain their evidence; images, options and levels are never silently removed.
  Context limits and wide-choice handling remain the author's server behavior.
- Native responses are retained intact, including probabilities, `confidence`,
  `none_probability`, usage, model name and any details. The adapter performs no
  probability recalibration or renormalization. Existing benchmark scorers remain unchanged.

## Interface tests

```bash
python -m pytest tests/test_startlux.py tests/test_http.py tests/test_registry.py
```

These tests use synthetic inputs and mocked/local HTTP responses. Passing them
does not establish successful GPU inference, benchmark quality, or leaderboard eligibility.

## 中文说明

新增的五个 ID 对应 v1.1 Instant 的 0.8B、2B、4B、9B、27B，均调用官方
`startlux-decide` HTTP 服务；旧版 `StartLux-0.8B` 原生接入保持原样。
本次仅注册和实现接口，不新增成绩，不导入模型卡分数，不更新排行榜。

每次请求固定发送并留档 `think_mode=never`、`allow_none=false`、`none_check=true`。
文本和 JSON 原样传递，消息中的图像按顺序转为顶层 `images` 与位置标记，
保留所有问题、候选项、原生概率及响应字段。视频、超过八张图或超出 2–10 档的
Score 请求会明确报告不支持，不裁剪输入；长上下文和宽选项由官方服务处理。

服务会忽略请求中的 `model`，因此每个尺寸必须指向实际加载该权重的服务。
适配器检查响应模型名；自定义服务名需显式设置 `expected_response_model`。
名称检查不能替代权重校验，正式评测应使用示例中的托管服务记录权重、配置与源码哈希，
并另存服务环境依赖版本。接口测试使用合成数据与模拟／本地 HTTP 响应，不构成实测成绩。
