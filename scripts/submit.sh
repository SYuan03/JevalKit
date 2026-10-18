#!/usr/bin/env bash
# Reuse the user's Valen cluster configuration; never modify it or copy credentials.
set -euo pipefail
JEVAL_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
VALEN_ROOT="${VALEN_ROOT:-/mnt/shared-storage-user/liuziyu/My_Projects/Valen}"
source "$VALEN_ROOT/scripts/train/cluster_env.sh"
JEVAL_NAME="$1"
JEVAL_GPUS="$2"
shift 2
JEVAL_PYTHON="${JEVAL_PYTHON:-$VALEN_ROOT/.venv/bin/python}"
JEVAL_TIMEOUT="${JEVAL_TIMEOUT:-10800}"
JEVAL_MEMORY_PER_GPU="${JEVAL_MEMORY_PER_GPU:-32768}"
JEVAL_RESERVE_ARGS=("$JEVAL_NAME" "$JEVAL_GPUS")
if [[ "${1:-}" == matrix ]]; then JEVAL_RESERVE_ARGS+=("$2"); fi
JEVAL_CODE="$("$JEVAL_PYTHON" "$JEVAL_ROOT/scripts/gpu_reserve.py" "${JEVAL_RESERVE_ARGS[@]}")"
if [[ "${1:-}" == matrix ]]; then shift 2; set -- matrix "$JEVAL_CODE/matrix.json" "$@"; fi
JEVAL_LOG="$(dirname -- "$JEVAL_CODE")"
"$RJOB_BIN" submit --name="$JEVAL_NAME" --gpu="$JEVAL_GPUS" --cpu="$((JEVAL_GPUS * 4))" --memory="$((JEVAL_GPUS * JEVAL_MEMORY_PER_GPU))" \
  --charged-group="$RJOB_CHARGED_GROUP" --namespace="$RJOB_NAMESPACE" --private-machine="$RJOB_PRIVATE_MACHINE" \
  "${VALEN_MOUNT_ARGS[@]}" --image="$RJOB_IMAGE" --restart-policy=never --auto-restart=false -P 1 --host-network=false \
  -e JEVAL_PYTHON="$JEVAL_PYTHON" -e JEVALKIT_DATA_ROOT="${JEVALKIT_DATA_ROOT:-/mnt/shared-storage-user/mllm/liuziyu/share_data/JevalKit}" -e JEVAL_OFFLINE="${JEVAL_OFFLINE:-1}" \
  -- timeout "$JEVAL_TIMEOUT" bash "$JEVAL_CODE/cluster_entry.sh" "$JEVAL_CODE" "$JEVAL_LOG" "$@" \
  2>&1 | tee "$JEVAL_LOG/submit.log"
JEVAL_ID="$(awk '/created rjob_name:/ {print $NF}' "$JEVAL_LOG/submit.log" | tail -n 1)"
test -n "$JEVAL_ID"
printf '%s\n' "$JEVAL_ID" > "$JEVAL_LOG/job_id"
printf 'Job: %s\nLogs: %s\n' "$JEVAL_ID" "$JEVAL_LOG"
