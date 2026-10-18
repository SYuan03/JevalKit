# Tested inference environments

JevalKit isolates model runtimes in subprocesses. The package's optional `hf`
dependencies cover Valen; author SDKs and serving engines have their own
dependencies. The versions below describe environments actually used in this
workspace. Each result's `manifest.json` is the evidence for that particular run.

| Component | Valen environment | Native author SDK environment |
|---|---|---|
| Python | 3.10.18 | 3.12.0 |
| PyTorch | 2.6.0 / CUDA 12.4 | 2.10.0 / CUDA 12.8 |
| Transformers | 5.4.0 | 5.14.1 |
| torchvision | 0.21.0 | 0.25.0 |
| Pillow | 11.3.0 | 11.3.0 |
| safetensors | 0.6.2 | 0.8.0 |
| accelerate | 1.10.0 | 1.11.0 |
| PEFT | 0.18.1 | 0.18.1 |
| huggingface-hub | 1.7.1 | 1.6.0 |

The Valen interpreter is
`/mnt/shared-storage-user/liuziyu/My_Projects/Valen/.venv/bin/python`.
The author SDK interpreter is
`/mnt/shared-storage-user/liuziyu/My_Projects/Valen/JevBench-exp/.venv-baselines/bin/python`.
Existing environments are reused without changing Valen's configuration.
Valen's source dependency declaration pins Transformers 5.4.0; its published
runtime imports `transformers.models.qwen3_5`. JevalKit therefore requires
Transformers 5.4 or newer in its `hf` extra, together with torchvision and PyAV
for media processing. A later version is not automatically verified for every SDK.

`matrix` rows can select an absolute `python` path; see
[the matrix example](../examples/matrix.json). Source checkouts are passed through
the model's `source` option. Native author code, base weights, calibration and
library versions are fingerprinted in the result manifest. Temporary model
weights may be removed after evaluation; prediction journals and retained data
support subsequent scoring without loading weights.

H2O-Lightning and OpenJev use a separate environment under
`$JEVALKIT_DATA_ROOT/envs/vllm030`. Installation and CPU import checks have passed
for vLLM 0.30.0, PyTorch 2.13.0 with CUDA 13.0, torchvision 0.28.0,
Transformers 5.19.0, OpenAI SDK 3.16.2 and httpx 0.28.1. `pip check` found no
broken requirements. The environment contains `requirements.lock.txt` and
`jevalkit-environment.json`, recording every package version, the lock hash and
the verified imports. Its readiness marker was written only after these checks
passed, releasing the queued H2O-Lightning task. Package checks and actual GPU
serving are separate evidence; consult [the current status](STATUS.md) for server results.

GPU tasks retain `hardware.csv`, frozen source, scheduler handles and logs under
`artifacts/jobs/`. The cumulative reservation ledger is
`artifacts/gpu-ledger.json`; failed and stopped attempts count toward 32 GPUs.
