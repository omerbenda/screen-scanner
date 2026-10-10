import sys
from pathlib import Path
from ultralytics import YOLO
import config


def _get_models_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / "models"

    return Path(__file__).resolve().parents[2] / "models"


_model_path: Path = _get_models_dir() / config.model

yolo_model: YOLO = YOLO(str(_model_path))
