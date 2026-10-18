import json
import os
from pathlib import Path
import subprocess
import sys


def test_worker_uses_short_socket_paths_and_preserves_shared_temporary_files(tmp_path):
    code = tmp_path / "code"
    package = code / "jevalkit"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "__main__.py").write_text('''import json, os, socket, tempfile, uuid
from pathlib import Path
paths = []
for root in [os.environ["VLLM_RPC_BASE_PATH"], tempfile.gettempdir()]:
    path = str(Path(root) / str(uuid.uuid4()))
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(path)
    os.unlink(path)
    paths.append(path)
bulk = Path(tempfile.gettempdir()) / "retained.bin"
bulk.write_bytes(b"keep shared data")
Path(os.environ["JEVAL_TEST_PROOF"]).write_text(json.dumps({
    "paths": paths, "bulk": str(bulk.resolve()), "short_root": str(Path(tempfile.gettempdir()).parent)
}))
''')
    logs = tmp_path / "job"
    logs.mkdir()
    shared = tmp_path / ("long-shared-storage-" * 7)
    proof = tmp_path / "proof.json"
    script = Path(__file__).parents[1] / "scripts/cluster_entry.sh"
    result = subprocess.run(["bash", str(script), str(code), str(logs), "probe"],
        env={**os.environ, "JEVAL_PYTHON": sys.executable, "JEVALKIT_DATA_ROOT": str(shared),
             "JEVAL_TEST_PROOF": str(proof)}, capture_output=True, text=True)
    assert result.returncode == 0, (logs / "console.log").read_text()
    saved = json.loads(proof.read_text())
    assert all(len(p.encode()) < 107 for p in saved["paths"])
    assert Path(saved["bulk"]).is_relative_to(shared)
    assert Path(saved["bulk"]).read_bytes() == b"keep shared data"
    assert not Path(saved["short_root"]).exists()
    assert (logs / "exit_code").read_text().strip() == "0"
