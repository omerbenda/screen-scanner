import sys
from pathlib import Path
from ultralytics import YOLO
import screen_scanner.config as config


def get_model_path() -> Path:
    if getattr(sys, "frozen", False):
        models_dir = Path(sys.executable).parent / "models"
    else:
        models_dir = Path(__file__).resolve().parents[2] / "models"

    return models_dir / config.model


def load_model() -> YOLO:
    model_path = get_model_path()

    return YOLO(str(model_path))


if __name__ == "__main__":
    load_model()
