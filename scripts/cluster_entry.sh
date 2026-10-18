#!/usr/bin/env bash
set -euo pipefail
: "${JEVAL_PYTHON:?Set JEVAL_PYTHON to the selected inference environment}"
JEVAL_CODE="$1"
JEVAL_LOG="$2"
shift 2
cd "$JEVAL_CODE"
export PYTHONPATH="$JEVAL_CODE${PYTHONPATH:+:$PYTHONPATH}"
export JEVALKIT_DATA_ROOT="${JEVALKIT_DATA_ROOT:-/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit}"
export HF_HOME="$JEVALKIT_DATA_ROOT/cache/hf"
export HF_MODULES_CACHE="$JEVALKIT_DATA_ROOT/cache/modules"
JEVAL_CACHE="$JEVALKIT_DATA_ROOT/cache/jobs/$(basename -- "$JEVAL_LOG")"
export XDG_CACHE_HOME="$JEVAL_CACHE/xdg"
export TORCHINDUCTOR_CACHE_DIR="$JEVAL_CACHE/torchinductor"
export TRITON_CACHE_DIR="$JEVAL_CACHE/triton"
export CUDA_CACHE_PATH="$JEVAL_CACHE/cuda"
export VLLM_CACHE_ROOT="$JEVAL_CACHE/vllm"
mkdir -p "$JEVAL_CACHE/tmp" "$XDG_CACHE_HOME" "$TORCHINDUCTOR_CACHE_DIR" "$TRITON_CACHE_DIR" "$CUDA_CACHE_PATH" "$VLLM_CACHE_ROOT"
# Unix socket addresses are limited to 107 bytes. Keep bulk temporary files on
# shared storage through a short alias, with vLLM RPC sockets on local /tmp.
JEVAL_SHORT_TEMP="$(mktemp -d /tmp/jev.XXXXXX)"
trap 'rm -rf -- "$JEVAL_SHORT_TEMP"' EXIT
ln -s "$JEVAL_CACHE/tmp" "$JEVAL_SHORT_TEMP/tmp"
mkdir "$JEVAL_SHORT_TEMP/ipc"
export TMPDIR="$JEVAL_SHORT_TEMP/tmp"
export VLLM_RPC_BASE_PATH="$JEVAL_SHORT_TEMP/ipc"
export PATH="$JEVALKIT_DATA_ROOT/tools/bin:$PATH"
export NO_PROXY="${NO_PROXY:+$NO_PROXY,}127.0.0.1,localhost"
export no_proxy="$NO_PROXY"
export HF_HUB_DISABLE_XET=1
export HF_HUB_OFFLINE="${JEVAL_OFFLINE:-1}"
export TRANSFORMERS_OFFLINE="$HF_HUB_OFFLINE"
export TOKENIZERS_PARALLELISM=false
export USE_TF=0
export TRANSFORMERS_NO_TF=1
export OMP_NUM_THREADS=4
date -u +%FT%TZ > "$JEVAL_LOG/started_utc"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv > "$JEVAL_LOG/hardware.csv" 2>/dev/null || true
fi
set +e
"$JEVAL_PYTHON" -m jevalkit "$@" > "$JEVAL_LOG/console.log" 2>&1
JEVAL_EXIT_CODE=$?
set -e
printf '%s\n' "$JEVAL_EXIT_CODE" > "$JEVAL_LOG/exit_code"
date -u +%FT%TZ > "$JEVAL_LOG/ended_utc"
exit "$JEVAL_EXIT_CODE"
