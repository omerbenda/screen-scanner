from typing import Iterator
from torch import Tensor
from ultralytics import YOLO
from ultralytics.engine.results import Results

_model = YOLO("yolo26n.pt")

def process_frame() -> Iterator[Results | Tensor] | list[Results] | list[Tensor]:
    return _model([""], stream=False)
