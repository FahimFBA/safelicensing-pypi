"""
SafeLicensing — License plate detection and chaotic-map encryption.

Provides both a high-level API for one-call image/video protection and
low-level building blocks for research use.

Quick start
-----------
::

    import safelicensing as sl
    from PIL import Image

    model = sl.load_model()                         # bundled best.pt
    image = Image.open("car.jpg")

    result = sl.protect_image(image, seed=0.42, model=model)
    result.encrypted.save("car_protected.jpg")

    video_result = sl.protect_video("dashcam.mp4", seed=0.42, model=model)
    print(video_result.output_path)

Research use
------------
::

    from safelicensing.encryption import logistic_map, generate_key, shuffle_pixels
    from safelicensing.detection import detect_license_plates

References
----------
Vehicle Number Plate Detection and Encryption in Digital Images Using YOLOv8
and Chaotic-Based Encryption Scheme, IEEE 2024.
https://ieeexplore.ieee.org/abstract/document/10534375/
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import numpy as np
from PIL import Image

from safelicensing.detection import detect_license_plates, load_model
from safelicensing.encryption import (
    encrypt_image,
    generate_key,
    logistic_map,
    shuffle_pixels,
)

__version__ = "1.0.0"
__author__ = "Md. Fahim Bin Amin, Israt Jahan Khan"
__license__ = "Apache-2.0"

__all__ = [
    "protect_image",
    "protect_video",
    "load_model",
    "detect_license_plates",
    "encrypt_image",
    "generate_key",
    "logistic_map",
    "shuffle_pixels",
    "ProtectImageResult",
    "ProtectVideoResult",
]


@dataclass
class ProtectImageResult:
    """
    Container for the output of :func:`protect_image`.

    Attributes
    ----------
    original : PIL.Image.Image
        The RGB input image, unchanged.
    detected : PIL.Image.Image
        Copy of the input with red bounding boxes around detected plates.
    encrypted : PIL.Image.Image
        Full image with every detected plate region encrypted.
    bboxes : list of (x1, y1, x2, y2) tuples
        Bounding box coordinates for each detected plate.
    elapsed : float
        Wall-clock processing time in seconds.
    """

    original: Image.Image
    detected: Image.Image
    encrypted: Image.Image
    bboxes: List[Tuple[int, int, int, int]] = field(default_factory=list)
    elapsed: float = 0.0


@dataclass
class ProtectVideoResult:
    """
    Container for the output of :func:`protect_video`.

    Attributes
    ----------
    output_path : str
        Absolute path to the encrypted output video file.
    frame_count : int
        Total number of frames that were processed.
    fps : float
        Frame rate of the output video.
    elapsed : float
        Wall-clock processing time in seconds.
    """

    output_path: str
    frame_count: int = 0
    fps: float = 0.0
    elapsed: float = 0.0


def protect_image(
    image: Image.Image,
    seed: float = 0.5,
    model=None,
    model_path: Optional[str] = None,
) -> ProtectImageResult:
    """
    Detect and encrypt all license plates found in a PIL image.

    Combines detection and encryption into a single call. The ``original``
    image is never mutated; all outputs are independent copies.

    :param image: Input image as a ``PIL.Image.Image``. Any colour mode is
                  accepted and internally converted to RGB.
    :param seed: Chaotic encryption seed in ``(0.0, 1.0)`` exclusive.
                 The same seed on the same image always produces the same
                 encrypted output. Default is ``0.5``.
    :param model: A pre-loaded YOLO model instance. When ``None``, the bundled
                  model is loaded automatically (one-time cost per process).
    :param model_path: Path to custom YOLOv8 ``.pt`` weights. Ignored when
                       ``model`` is provided explicitly.
    :return: A :class:`ProtectImageResult` with ``original``, ``detected``,
             ``encrypted`` images, ``bboxes`` list, and ``elapsed`` time.
    :raises TypeError: If ``image`` is not a ``PIL.Image.Image``.
    :raises ValueError: If ``seed`` is not strictly inside ``(0.0, 1.0)``.
    """
    if not isinstance(image, Image.Image):
        raise TypeError(
            f"image must be a PIL.Image.Image instance, got {type(image).__name__}"
        )
    if not (0.0 < seed < 1.0):
        raise ValueError(f"seed must be in (0.0, 1.0) exclusive, got {seed!r}")

    if model is None:
        model = load_model(model_path)

    rgb_image = image.convert("RGB")
    start = time.perf_counter()

    annotated, bboxes = detect_license_plates(model, rgb_image.copy())

    encrypted_np = np.array(rgb_image, dtype=np.uint8)
    img_height, img_width = encrypted_np.shape[:2]

    for (x1, y1, x2, y2) in bboxes:
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, img_width)
        y2 = min(y2, img_height)
        region = encrypted_np[y1:y2, x1:x2]
        if region.size > 0:
            encrypted_np[y1:y2, x1:x2] = encrypt_image(region, seed)

    elapsed = time.perf_counter() - start

    return ProtectImageResult(
        original=rgb_image,
        detected=annotated,
        encrypted=Image.fromarray(encrypted_np),
        bboxes=bboxes,
        elapsed=elapsed,
    )


def protect_video(
    video_path: str,
    seed: float = 0.5,
    output_path: Optional[str] = None,
    model=None,
    model_path: Optional[str] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> ProtectVideoResult:
    """
    Detect and encrypt license plates across all frames of a video file.

    Reads the source video, encrypts every detected plate region per frame,
    then encodes the result as an mp4 with the original audio re-attached.

    :param video_path: Path to the input video file. Common formats supported
                       by OpenCV (mp4, avi, mov) are accepted.
    :param seed: Chaotic encryption seed in ``(0.0, 1.0)`` exclusive. Default ``0.5``.
    :param output_path: Destination path for the encrypted video. When ``None``,
                        the file is written as ``<stem>_encrypted.mp4`` in the
                        same directory as the source video.
    :param model: Pre-loaded YOLO model instance. Loads bundled model when ``None``.
    :param model_path: Path to custom YOLOv8 weights. Ignored when ``model`` is given.
    :param progress_callback: Optional callable receiving a ``float`` in ``[0.0, 1.0]``
                              after each processed frame.
    :return: A :class:`ProtectVideoResult` with ``output_path``, ``frame_count``,
             ``fps``, and ``elapsed`` processing time.
    :raises FileNotFoundError: If ``video_path`` does not exist.
    :raises ValueError: If ``seed`` is not strictly inside ``(0.0, 1.0)``.
    """
    from safelicensing.video import create_video_from_frames, process_video

    if not (0.0 < seed < 1.0):
        raise ValueError(f"seed must be in (0.0, 1.0) exclusive, got {seed!r}")

    source = Path(video_path)
    if not source.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path!r}")

    resolved_output = (
        str(source.parent / f"{source.stem}_encrypted.mp4")
        if output_path is None
        else output_path
    )

    if model is None:
        model = load_model(model_path)

    start = time.perf_counter()
    frames, fps, _ = process_video(str(source), model, seed, progress_callback)
    create_video_from_frames(frames, fps, resolved_output, audio_path=str(source))
    elapsed = time.perf_counter() - start

    return ProtectVideoResult(
        output_path=str(Path(resolved_output).resolve()),
        frame_count=len(frames),
        fps=fps,
        elapsed=elapsed,
    )
