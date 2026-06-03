# SafeLicensing

**License plate detection and chaotic-map encryption for images and videos.**

Detect vehicle license plates with YOLOv8 and encrypt only the sensitive regions using a dual-pass chaotic XOR scheme, leaving the rest of the image or video completely intact.

Built on the research published at IEEE ECCE 2024:
> *Vehicle Number Plate Detection and Encryption in Digital Images Using YOLOv8 and Chaotic-Based Encryption Scheme* - [View on IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/10534375/)

---

## Features

- **One-call API**: `protect_image()` and `protect_video()` handle detection and encryption end-to-end
- **Bundled model**: 6 MB YOLOv8 weights ship with the package; no separate download needed
- **Programmable low-level API**: exposes `logistic_map`, `generate_key`, `shuffle_pixels`, `encrypt_image` for research use
- **Streamlit UI**: launch a full browser-based interface with a single command
- **Video support**: frame-by-frame plate detection and encryption with audio preservation

---

## Installation

### From PyPI

```bash
pip install safelicensing
```

### From source

```bash
git clone https://github.com/FahimFBA/safelicensing-pypi.git
cd safelicensing-pypi
pip install -r requirements.txt
pip install -e .
```

Python 3.8+ required.

---

## Quick Start

### CLI - Streamlit web app

```bash
safelicensing
```

Opens a browser UI where you can upload images or videos, tune the encryption seed, and download protected output.

### Protect an image

```python
import safelicensing as sl
from PIL import Image

model = sl.load_model()                          # loads bundled best.pt
image = Image.open("car.jpg")

result = sl.protect_image(image, seed=0.42, model=model)

result.original.show()                           # original image
result.detected.show()                           # plates highlighted in red
result.encrypted.save("car_protected.jpg")       # plates encrypted

print(f"Plates found : {len(result.bboxes)}")
print(f"Elapsed      : {result.elapsed:.2f}s")
```

### Protect a video

```python
import safelicensing as sl

model = sl.load_model()

result = sl.protect_video(
    "dashcam.mp4",
    seed=0.42,
    model=model,
    output_path="dashcam_protected.mp4",
)

print(f"Output  : {result.output_path}")
print(f"Frames  : {result.frame_count}")
print(f"FPS     : {result.fps:.2f}")
print(f"Elapsed : {result.elapsed:.2f}s")
```

---

## API Reference

### High-level

#### `sl.protect_image(image, seed=0.5, model=None, model_path=None) -> ProtectImageResult`

Detect and encrypt all license plates in a PIL image.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image` | `PIL.Image.Image` | Input image (any colour mode). |
| `seed` | `float` | Encryption seed in `(0.0, 1.0)`. Default `0.5`. |
| `model` | YOLO instance | Pre-loaded model. Loads bundled model when `None`. |
| `model_path` | `str` | Path to custom `.pt` weights. Ignored when `model` is given. |

**Returns** `ProtectImageResult`:

| Field | Type | Description |
|-------|------|-------------|
| `original` | `PIL.Image.Image` | Unmodified RGB input. |
| `detected` | `PIL.Image.Image` | Input with red bounding boxes. |
| `encrypted` | `PIL.Image.Image` | Plate regions encrypted. |
| `bboxes` | `list[tuple]` | `(x1, y1, x2, y2)` per detected plate. |
| `elapsed` | `float` | Processing time in seconds. |

---

#### `sl.protect_video(video_path, seed=0.5, output_path=None, model=None, model_path=None, progress_callback=None) -> ProtectVideoResult`

Detect and encrypt license plates in every frame of a video.

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_path` | `str` | Path to input video (mp4, avi, mov). |
| `seed` | `float` | Encryption seed in `(0.0, 1.0)`. Default `0.5`. |
| `output_path` | `str` | Output path. Defaults to `<stem>_encrypted.mp4`. |
| `model` | YOLO instance | Pre-loaded model. Loads bundled model when `None`. |
| `model_path` | `str` | Custom weights path. Ignored when `model` is given. |
| `progress_callback` | `callable` | Receives a `float` in `[0.0, 1.0]` per frame. |

**Returns** `ProtectVideoResult`:

| Field | Type | Description |
|-------|------|-------------|
| `output_path` | `str` | Absolute path to the encrypted video. |
| `frame_count` | `int` | Total frames processed. |
| `fps` | `float` | Output frame rate. |
| `elapsed` | `float` | Processing time in seconds. |

---

#### `sl.load_model(weights_path=None) -> YOLO`

Load a YOLOv8 model. Uses the bundled `best.pt` when `weights_path` is `None`.

---

### Mid-level

```python
from safelicensing import detect_license_plates, encrypt_image

annotated, bboxes = detect_license_plates(model, pil_image)
encrypted_region  = encrypt_image(np_array, seed=0.42)
```

---

### Low-level (research)

```python
from safelicensing.encryption import logistic_map, generate_key, shuffle_pixels
from safelicensing.detection  import load_model, detect_license_plates
from safelicensing.video      import process_video, create_video_from_frames
```

#### `logistic_map(r, x) -> float`
Single step of the logistic map: `r * x * (1 - x)`.

#### `generate_key(seed, n) -> np.ndarray`
Generates a chaotic byte key of length `n` using the logistic map seeded at `seed`.

#### `shuffle_pixels(img_array, seed) -> (np.ndarray, np.ndarray)`
Shuffles pixels of a `(H, W, C)` uint8 array. Returns `(shuffled, indices)`.

#### `encrypt_image(img_array, seed) -> np.ndarray`
Full two-layer encryption: XOR -> shuffle -> XOR. Returns encrypted array, same shape.

#### `process_video(video_path, model, key_seed, progress_callback=None)`
Frame-by-frame detection and encryption. Returns `(frames, fps, (width, height))`.

#### `create_video_from_frames(frames, fps, output_path, audio_path=None) -> str`
Encodes a list of RGB frames into a video file. Returns absolute output path.

---

## Custom model

Bring your own YOLOv8 weights trained for license plate detection:

```python
model = sl.load_model("path/to/my_model.pt")
result = sl.protect_image(image, seed=0.5, model=model)
```

---

## Encryption details

The scheme applies two passes per region:

1. **XOR pass 1**: every pixel byte is XOR'd with a chaotic key generated by iterating the logistic map at `r = 3.9` from the given seed.
2. **Pixel shuffle**: all pixels are randomly permuted using a seed-reproducible permutation.
3. **XOR pass 2**: the shuffled bytes are XOR'd with a second chaotic key derived from a perturbed seed (`min(seed * 1.1, 0.9999)`).

The same seed always produces the same encrypted output, making the process deterministic and auditable.

---

## Development setup

```bash
git clone https://github.com/FahimFBA/safelicensing-pypi.git
cd safelicensing-pypi
pip install -r requirements-dev.txt
pip install -e .
```

`requirements-dev.txt` includes all runtime dependencies plus `pytest` and `pytest-cov`.

## Running tests

```bash
pytest                              # unit tests only (no model or video files needed)
pytest -m integration               # also run integration tests
pytest --cov=safelicensing          # with coverage report
```

---

## Authors

- [Md. Fahim Bin Amin](https://www.fahimbinamin.com)
- [Israt Jahan Khan](https://www.isratjahankhan.com)

---

## Citation

If you use SafeLicensing in your research, please cite:

```bibtex
@inproceedings{amin2024safelicensing,
  title     = {Vehicle Number Plate Detection and Encryption in Digital Images
               Using YOLOv8 and Chaotic-Based Encryption Scheme},
  author    = {Amin, Md. Fahim Bin and Khan, Israt Jahan},
  booktitle = {2024 International Conference on Electrical, Computer and
               Communication Engineering (ECCE)},
  year      = {2024},
  publisher = {IEEE},
  url       = {https://ieeexplore.ieee.org/abstract/document/10534375/}
}
```

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.
