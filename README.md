# screen-scanner
Scans the screen and renders bounding box on top of recognized objects.

## Installation
The app can use CUDA to utilize the GPU to run the YOLO model

If you don't want to install the CUDA binaries and prefer to run the model on the CPU
install the [requirements-cpu.txt](requirements-cpu.txt) dependencies.

If you do want to utilize the GPU for this app
install the [requirements-gpu.txt](requirements-gpu.txt) dependencies.

You can then run [main.py](src/screen_scanner/main.py).

## Bundling
To bundle the app into an executable run the following commands:
* For CPU build: `pip install -r requirements-cpu.txt`
* For GPU build: `pip install -r requirements-gpu.txt`
* `pip install -e .[build]`
* `pyinstaller screen-scanner.spec`
