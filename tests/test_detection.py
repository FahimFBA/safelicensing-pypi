"""
Tests for safelicensing.detection — model loading and license plate detection.

Model-dependent tests (those requiring actual YOLO inference) are marked with
``pytest.mark.integration`` and skipped in environments where the bundled
weights file or ultralytics is unavailable.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

from safelicensing.detection import BUNDLED_MODEL_PATH, detect_license_plates, load_model


# ---------------------------------------------------------------------------
# load_model
# ---------------------------------------------------------------------------

class TestLoadModel:
    def test_missing_custom_path_raises_file_not_found(self, tmp_path):
        nonexistent = str(tmp_path / "no_such_model.pt")
        with pytest.raises(FileNotFoundError, match="not found"):
            load_model(nonexistent)

    def test_missing_bundled_model_raises_file_not_found(self, monkeypatch):
        fake_path = Path("/nonexistent/path/best.pt")
        monkeypatch.setattr(
            "safelicensing.detection.BUNDLED_MODEL_PATH", fake_path
        )
        with pytest.raises(FileNotFoundError):
            load_model()

    def test_yolo_runtime_error_is_wrapped(self, tmp_path):
        weights = tmp_path / "dummy.pt"
        weights.write_bytes(b"not a real model")
        with pytest.raises(RuntimeError, match="Failed to load"):
            load_model(str(weights))

    @pytest.mark.integration
    def test_bundled_model_loads_when_present(self):
        if not BUNDLED_MODEL_PATH.is_file():
            pytest.skip("Bundled best.pt not present — skipping integration test")
        model = load_model()
        assert model is not None

    @pytest.mark.integration
    def test_custom_path_loads_when_present(self):
        if not BUNDLED_MODEL_PATH.is_file():
            pytest.skip("Bundled best.pt not present — skipping integration test")
        model = load_model(str(BUNDLED_MODEL_PATH))
        assert model is not None


# ---------------------------------------------------------------------------
# detect_license_plates
# ---------------------------------------------------------------------------

class TestDetectLicensePlates:
    def test_invalid_input_type_raises(self):
        mock_model = MagicMock()
        with pytest.raises(TypeError, match="PIL.Image.Image"):
            detect_license_plates(mock_model, np.zeros((4, 4, 3), dtype=np.uint8))

    def test_returns_tuple(self, tiny_pil_image):
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        result = detect_license_plates(mock_model, tiny_pil_image)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_pil_image_and_list(self, tiny_pil_image):
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        annotated, bboxes = detect_license_plates(mock_model, tiny_pil_image)
        assert isinstance(annotated, Image.Image)
        assert isinstance(bboxes, list)

    def test_no_detection_returns_empty_bboxes(self, tiny_pil_image):
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        _, bboxes = detect_license_plates(mock_model, tiny_pil_image)
        assert bboxes == []

    def test_original_image_not_mutated(self, tiny_pil_image):
        original_pixels = list(tiny_pil_image.getdata())
        mock_model = MagicMock()
        mock_model.predict.return_value = []
        detect_license_plates(mock_model, tiny_pil_image)
        assert list(tiny_pil_image.getdata()) == original_pixels

    def test_detection_with_mock_boxes(self, tiny_pil_image):
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock()]
        mock_box.xyxy[0].tolist.return_value = [0.0, 0.0, 2.0, 2.0]
        mock_box.cls = [MagicMock()]
        mock_box.cls[0].item.return_value = 0

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]

        mock_model = MagicMock()
        mock_model.predict.return_value = [mock_result]
        mock_model.names = {0: "licenseplate"}

        annotated, bboxes = detect_license_plates(mock_model, tiny_pil_image)
        assert len(bboxes) == 1
        assert bboxes[0] == (0, 0, 2, 2)

    def test_non_plate_class_excluded(self, tiny_pil_image):
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock()]
        mock_box.xyxy[0].tolist.return_value = [0.0, 0.0, 2.0, 2.0]
        mock_box.cls = [MagicMock()]
        mock_box.cls[0].item.return_value = 1

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]

        mock_model = MagicMock()
        mock_model.predict.return_value = [mock_result]
        mock_model.names = {1: "car"}

        _, bboxes = detect_license_plates(mock_model, tiny_pil_image)
        assert bboxes == []

    def test_none_boxes_returns_empty(self, tiny_pil_image):
        mock_result = MagicMock()
        mock_result.boxes = None

        mock_model = MagicMock()
        mock_model.predict.return_value = [mock_result]

        _, bboxes = detect_license_plates(mock_model, tiny_pil_image)
        assert bboxes == []
