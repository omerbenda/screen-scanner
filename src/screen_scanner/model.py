import sys
from pathlib import Path
from ultralytics import YOLO
import config


def _get_models_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "models"

    return Path(__file__).resolve().parents[2] / "models"


def load_model() -> YOLO:
    _model_path: Path = _get_models_dir() / config.model

    return YOLO(str(_model_path))


if __name__ == "__main__":
    load_model()
