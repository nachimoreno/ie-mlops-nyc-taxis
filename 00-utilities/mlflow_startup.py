import os
import subprocess
import sys
import tomli as tomllib
from pathlib import Path

def get_config() -> dict:
    with open("config.toml", "rb") as f:
        return tomllib.load(f)

def main() -> int:
    config = get_config()
    host = config["mlflow"]["host"]
    port = config["mlflow"]["port"]
    url = config["mlflow"]["url"]
    allowed_hosts = config["mlflow"]["allowed_hosts"]

    project_root = Path(__file__).resolve().parent
    mlflow_data_directory = project_root / "mlflow_data"
    backend_store_path = mlflow_data_directory / "mlflow.db"
    artifact_root_path = mlflow_data_directory / "artifacts"

    mlflow_data_directory.mkdir(parents=True, exist_ok=True)
    artifact_root_path.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable, "-m", "mlflow", "server",
        "--backend-store-uri", f"sqlite:///{backend_store_path.as_posix()}",
        "--default-artifact-root", artifact_root_path.as_posix(),
        "--host", host,
        "--port", port,
        "--allowed-hosts", allowed_hosts
    ]

    print("Starting MLflow server:")
    print(" ".join(command))

    # On Windows, this keeps it alive in a new process group; on Unix it's fine as-is.
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]

    process = subprocess.Popen(command, cwd=str(project_root), creationflags=creationflags)
    print(f"MLflow PID: {process.pid}")
    print(f"Open: {url}")

    # Wait so Ctrl+C stops it cleanly
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping MLflow...")
        process.terminate()
        process.wait()

    return process.returncode or 0

if __name__ == "__main__":
    raise SystemExit(main())