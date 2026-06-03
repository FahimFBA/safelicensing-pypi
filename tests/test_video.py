"""
Tests for safelicensing.video — video processing and frame assembly.

Tests that require writing real video files are marked ``pytest.mark.integration``
and depend on OpenCV, MoviePy, and a writable temp directory.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, call
import os

import numpy as np
import pytest

from safelicensing.video import create_video_from_frames, process_video


# ---------------------------------------------------------------------------
# create_video_from_frames
# ---------------------------------------------------------------------------

class TestCreateVideoFromFrames:
    def test_empty_frames_raises(self, tmp_path):
        with pytest.raises(ValueError, match="empty"):
            create_video_from_frames([], 25.0, str(tmp_path / "out.mp4"))

    def test_invalid_fps_zero_raises(self, tiny_rgb_array, tmp_path):
        frames = [tiny_rgb_array]
        with pytest.raises(ValueError, match="fps"):
            create_video_from_frames(frames, 0.0, str(tmp_path / "out.mp4"))

    def test_invalid_fps_negative_raises(self, tiny_rgb_array, tmp_path):
        frames = [tiny_rgb_array]
        with pytest.raises(ValueError, match="fps"):
            create_video_from_frames(frames, -1.0, str(tmp_path / "out.mp4"))

    def test_nonexistent_audio_path_raises(self, tiny_rgb_array, tmp_path):
        frames = [tiny_rgb_array]
        with pytest.raises(FileNotFoundError, match="audio_path"):
            create_video_from_frames(
                frames, 25.0, str(tmp_path / "out.mp4"),
                audio_path=str(tmp_path / "no_audio.mp4"),
            )

    @pytest.mark.integration
    def test_creates_output_file(self, tiny_rgb_array, tmp_path):
        frames = [tiny_rgb_array] * 5
        output = str(tmp_path / "out.mp4")
        result = create_video_from_frames(frames, 25.0, output)
        assert Path(result).is_file()

    @pytest.mark.integration
    def test_returns_absolute_path(self, tiny_rgb_array, tmp_path):
        frames = [tiny_rgb_array] * 3
        output = str(tmp_path / "out.mp4")
        result = create_video_from_frames(frames, 25.0, output)
        assert os.path.isabs(result)


# ---------------------------------------------------------------------------
# process_video
# ---------------------------------------------------------------------------

class TestProcessVideo:
    def test_nonexistent_file_raises(self, tmp_path):
        mock_model = MagicMock()
        with pytest.raises(FileNotFoundError, match="not found"):
            process_video(str(tmp_path / "missing.mp4"), mock_model, 0.5)

    def test_unopenable_file_raises(self, tmp_path):
        fake_video = tmp_path / "fake.mp4"
        fake_video.write_bytes(b"not a video")
        mock_model = MagicMock()
        with pytest.raises((ValueError, Exception)):
            process_video(str(fake_video), mock_model, 0.5)

    def test_progress_callback_called(self, tmp_path):
        import cv2

        output_path = str(tmp_path / "test_progress.mp4")
        height, width = 8, 8
        fps = 5

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for _ in range(3):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            writer.write(frame)
        writer.release()

        mock_model = MagicMock()
        mock_model.predict.return_value = []

        calls = []
        process_video(output_path, mock_model, 0.5, progress_callback=calls.append)

        assert len(calls) == 3
        assert all(0.0 <= v <= 1.0 for v in calls)

    def test_returns_correct_types(self, tmp_path):
        import cv2

        output_path = str(tmp_path / "test_types.mp4")
        height, width = 8, 8

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, 5.0, (width, height))
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        writer.write(frame)
        writer.release()

        mock_model = MagicMock()
        mock_model.predict.return_value = []

        frames, fps, size = process_video(output_path, mock_model, 0.5)

        assert isinstance(frames, list)
        assert isinstance(fps, float)
        assert isinstance(size, tuple) and len(size) == 2

    def test_encrypts_detected_plates(self, tmp_path):
        import cv2
        from safelicensing.detection import detect_license_plates

        output_path = str(tmp_path / "test_encrypt.mp4")
        height, width = 16, 32

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, 5.0, (width, height))
        frame = np.full((height, width, 3), 128, dtype=np.uint8)
        writer.write(frame)
        writer.release()

        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock()]
        mock_box.xyxy[0].tolist.return_value = [0.0, 0.0, 8.0, 8.0]
        mock_box.cls = [MagicMock()]
        mock_box.cls[0].item.return_value = 0

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]

        mock_model = MagicMock()
        mock_model.predict.return_value = [mock_result]
        mock_model.names = {0: "licenseplate"}

        frames, _, _ = process_video(output_path, mock_model, 0.42)

        assert len(frames) == 1
        plate_region = frames[0][0:8, 0:8]
        assert not np.all(plate_region == 128)
