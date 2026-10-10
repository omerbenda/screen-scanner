# screen-scanner
Scans the screen and renders bounding box on top of recognized objects.

## Installation
The app can use CUDA to utilize the GPU to run the YOLO model

If you don't want to install the CUDA binaries and prefer to run the model on the CPU
install the [requirements-cpu.txt](requirements-cpu.txt) dependencies.

If you do want to utilize the GPU for this app
install the [requirements-gpu.txt](requirements-gpu.txt) dependencies.

You can then run [main.py](src/screen_scanner/main.py).

## Configuring the app
The config JSON is created when running either
[main.py](src/screen_scanner/main.py), [model.py](src/screen_scanner/model.py) and [config.py](src/screen_scanner/config.py)

The JSON contains the following fields:

| Field Name           | Type   | Description                                                  |
|:---------------------|:-------|:-------------------------------------------------------------|
| inference_timeout_ms | number | The time in milliseconds between each inference              |
| model                | string | model name, decides which model in the models folder is used |


## Packaging
To package the app into a standalone executable:

**Install runtime dependencies:**
* For CPU build: `pip install -r requirements-cpu.txt`
* For GPU build: `pip install -r requirements-gpu.txt`

**Install packaging tool:**
* `pip install -e .[build]`

**Fetch Model:**
* Fetch the model currently in config: `python src/screen_scanner/model.py`

If the model specified in config is not found in the models folder, the app will try to fetch the model.

**Package:**
* `pyinstaller screen-scanner.spec`
