import sys
from pathlib import Path
import json

default_config = {
    "inference_timeout_sec": 0.1,
    "model": "yolo26x.pt"
}


def _get_config_path() -> Path:
    name: str = "config.json"

    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / name

    return Path(__file__).parent / name


def _load_config(filepath: Path | None = None) -> dict:
    if filepath is None:
        filepath = _get_config_path()

    if not filepath.exists():
        with open(filepath, "w") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    with open(filepath, "r") as f:
        return json.load(f)


_config_data = _load_config()

inference_timeout_sec: int = _config_data["inference_timeout_sec"]
model: str = _config_data["model"]
