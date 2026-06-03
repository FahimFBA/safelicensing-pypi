"""
License plate detection utilities using YOLOv8.

Wraps Ultralytics YOLO inference and returns both an annotated copy of the
input image and a list of bounding box coordinates for downstream encryption.
"""

from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw


BUNDLED_MODEL_PATH: Path = Path(__file__).parent / "best.pt"


def load_model(weights_path: str = None):
    """
    Load a YOLOv8 model from the specified weights file.

    When no path is given the bundled ``best.pt`` that ships with the package
    is used, so callers do not need to supply weights for the default pipeline.

    :param weights_path: Absolute or relative path to a ``.pt`` weights file.
                         Pass ``None`` (default) to use the bundled model.
    :return: A loaded ``ultralytics.YOLO`` model instance ready for inference.
    :raises FileNotFoundError: If the resolved weights file does not exist on disk.
    :raises RuntimeError: If YOLO fails to load or initialise the model.
    """
    from ultralytics import YOLO  # lazy import — heavy dependency

    resolved = Path(weights_path) if weights_path is not None else BUNDLED_MODEL_PATH

    if not resolved.is_file():
        raise FileNotFoundError(f"Model weights not found: {resolved}")

    try:
        return YOLO(str(resolved))
    except Exception as exc:
        raise RuntimeError(
            f"Failed to load YOLO model from '{resolved}': {exc}"
        ) from exc


def detect_license_plates(
    model,
    pil_image: Image.Image,
) -> Tuple[Image.Image, List[Tuple[int, int, int, int]]]:
    """
    Run YOLOv8 license plate detection on a PIL image.

    Returns a copy of the input image with red bounding boxes drawn around
    every detected plate, alongside a list of the box coordinates. The original
    ``pil_image`` is never mutated.

    :param model: A loaded YOLO model instance obtained from :func:`load_model`.
    :param pil_image: Input image as a ``PIL.Image.Image`` in any mode;
                      conversion to a NumPy array is handled internally.
    :return: Tuple ``(annotated_image, bboxes)`` where ``annotated_image`` is a
             ``PIL.Image.Image`` copy with red bounding boxes, and ``bboxes`` is
             a list of ``(x1, y1, x2, y2)`` integer tuples — one per detected plate.
             Returns an unannotated copy and an empty list when no plates are found.
    :raises TypeError: If ``pil_image`` is not a ``PIL.Image.Image`` instance.
    """
    if not isinstance(pil_image, Image.Image):
        raise TypeError(
            f"pil_image must be a PIL.Image.Image instance, got {type(pil_image).__name__}"
        )

    annotated = pil_image.copy()
    np_image = np.array(pil_image)
    results = model.predict(np_image, verbose=False)

    if not results or len(results) == 0:
        return annotated, []

    result = results[0]
    if not hasattr(result, "boxes") or result.boxes is None or len(result.boxes) == 0:
        return annotated, []

    bboxes: List[Tuple[int, int, int, int]] = []
    draw = ImageDraw.Draw(annotated)

    for box in result.boxes:
        coords = box.xyxy[0].tolist()
        cls_id = int(box.cls[0].item())
        cls_name = model.names.get(cls_id, "unknown")

        if cls_name.lower() == "licenseplate" or cls_id == 0:
            x1, y1, x2, y2 = map(int, coords)
            bboxes.append((x1, y1, x2, y2))
            draw.rectangle([x1, y1, x2, y2], outline="red", width=2)

    return annotated, bboxes
