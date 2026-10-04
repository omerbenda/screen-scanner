# screen-scanner
Scans the screen and renders bounding box on top of recognized objects.

## Installation
The app can use CUDA to utilize the GPU to run the YOLO model

If you don't want to install the CUDA binaries and prefer to run the model on the CPU
install the [requirements-cpu.txt](requirements-cpu.txt) dependencies.

If you do want to utilize the GPU for this app
install the [requirements-gpu.txt](requirements-gpu.txt) dependencies.

You can then run [main.py](main.py).
