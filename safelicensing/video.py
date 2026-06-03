"""
Video processing utilities for license plate encryption.

Provides frame-by-frame detection and encryption of license plates in video
files, plus helpers for assembling processed frames back into a video container
with optional audio preservation.
"""

from pathlib import Path
from typing import Callable, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from safelicensing.detection import detect_license_plates
from safelicensing.encryption import encrypt_image


def process_video(
    video_path: str,
    model,
    key_seed: float,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Tuple[List[np.ndarray], float, Tuple[int, int]]:
    """
    Process a video file frame-by-frame, detecting and encrypting license plates.

    Each frame is decoded, run through the YOLO detector, and any detected plate
    regions are encrypted in-place using :func:`~safelicensing.encryption.encrypt_image`.
    The modified frame is appended to the returned list as an RGB NumPy array.

    :param video_path: Absolute or relative path to the input video file.
                       Common formats (mp4, avi, mov) are supported via OpenCV.
    :param model: A loaded YOLO model instance from :func:`~safelicensing.detection.load_model`.
    :param key_seed: Chaotic encryption seed in ``(0.0, 1.0)`` exclusive.
    :param progress_callback: Optional callable that receives a ``float`` in ``[0.0, 1.0]``
                              after each frame is processed. Useful for progress bars.
                              Pass ``None`` to disable.
    :return: Tuple ``(processed_frames, fps, (width, height))`` where:

             - ``processed_frames`` is a list of RGB NumPy arrays (one per frame).
             - ``fps`` is the source frame rate as a ``float``.
             - ``(width, height)`` are the frame dimensions in pixels.

    :raises FileNotFoundError: If ``video_path`` does not point to an existing file.
    :raises ValueError: If OpenCV cannot open the video at ``video_path``.
    """
    source = Path(video_path)
    if not source.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path!r}")

    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise ValueError(f"OpenCV cannot open video: {video_path!r}")

    fps: float = cap.get(cv2.CAP_PROP_FPS)
    width: int = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height: int = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames: int = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    processed_frames: List[np.ndarray] = []
    frame_count = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            _, bboxes = detect_license_plates(model, pil_image)

            for (x1, y1, x2, y2) in bboxes:
                x1 = max(x1, 0)
                y1 = max(y1, 0)
                x2 = min(x2, width)
                y2 = min(y2, height)
                plate_region = frame[y1:y2, x1:x2]
                if plate_region.size > 0:
                    frame[y1:y2, x1:x2] = encrypt_image(plate_region, key_seed)

            processed_frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            frame_count += 1

            if progress_callback is not None and total_frames > 0:
                progress_callback(frame_count / total_frames)
    finally:
        cap.release()

    return processed_frames, fps, (width, height)


def create_video_from_frames(
    frames: List[np.ndarray],
    fps: float,
    output_path: str,
    audio_path: Optional[str] = None,
) -> str:
    """
    Assemble processed RGB frames into a video file.

    Uses MoviePy to encode the frame list and optionally re-attaches the
    audio track from a source file (e.g. the original input video).

    :param frames: Non-empty list of RGB NumPy arrays, all with identical dimensions.
    :param fps: Output frame rate in frames per second. Must be a positive number.
    :param output_path: Destination file path for the encoded video (e.g. ``"out.mp4"``).
    :param audio_path: Optional path to a video file whose audio track will be
                       attached to the output. Pass ``None`` for a silent video.
    :return: Resolved absolute path to the created video file as a ``str``.
    :raises ValueError: If ``frames`` is empty or ``fps`` is not a positive number.
    :raises FileNotFoundError: If ``audio_path`` is provided but does not exist.
    """
    from moviepy.editor import ImageSequenceClip, VideoFileClip  # lazy import

    if not frames:
        raise ValueError("frames must not be empty")
    if fps <= 0:
        raise ValueError(f"fps must be a positive number, got {fps!r}")
    if audio_path is not None and not Path(audio_path).is_file():
        raise FileNotFoundError(f"audio_path not found: {audio_path!r}")

    clip = ImageSequenceClip(frames, fps=fps)

    if audio_path is not None:
        source_clip = VideoFileClip(audio_path)
        if source_clip.audio is not None:
            clip = clip.set_audio(source_clip.audio)

    clip.write_videofile(output_path, codec="libx264", logger=None)
    return str(Path(output_path).resolve())
