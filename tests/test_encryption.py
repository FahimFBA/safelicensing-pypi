"""
Tests for safelicensing.encryption — logistic map, key generation,
pixel shuffling, and image encryption.
"""

import numpy as np
import pytest

from safelicensing.encryption import (
    encrypt_image,
    generate_key,
    logistic_map,
    shuffle_pixels,
)


# ---------------------------------------------------------------------------
# logistic_map
# ---------------------------------------------------------------------------

class TestLogisticMap:
    def test_known_value(self):
        result = logistic_map(3.9, 0.5)
        assert abs(result - 0.975) < 1e-9

    def test_output_in_unit_interval(self):
        x = 0.3
        for _ in range(100):
            x = logistic_map(3.9, x)
            assert 0.0 <= x <= 1.0

    def test_boundary_zero_stays_zero(self):
        assert logistic_map(3.9, 0.0) == 0.0

    def test_boundary_one_stays_zero(self):
        assert logistic_map(3.9, 1.0) == 0.0

    def test_return_type_is_float(self):
        assert isinstance(logistic_map(3.9, 0.5), float)


# ---------------------------------------------------------------------------
# generate_key
# ---------------------------------------------------------------------------

class TestGenerateKey:
    def test_output_length(self, valid_seed):
        key = generate_key(valid_seed, 100)
        assert len(key) == 100

    def test_output_dtype(self, valid_seed):
        key = generate_key(valid_seed, 10)
        assert key.dtype == np.uint8

    def test_output_shape(self, valid_seed):
        key = generate_key(valid_seed, 20)
        assert key.shape == (20,)

    def test_deterministic(self, valid_seed):
        key1 = generate_key(valid_seed, 50)
        key2 = generate_key(valid_seed, 50)
        np.testing.assert_array_equal(key1, key2)

    def test_different_seeds_produce_different_keys(self):
        key1 = generate_key(0.3, 50)
        key2 = generate_key(0.7, 50)
        assert not np.array_equal(key1, key2)

    def test_invalid_seed_zero_raises(self):
        with pytest.raises(ValueError, match="seed"):
            generate_key(0.0, 10)

    def test_invalid_seed_one_raises(self):
        with pytest.raises(ValueError, match="seed"):
            generate_key(1.0, 10)

    def test_invalid_seed_negative_raises(self):
        with pytest.raises(ValueError, match="seed"):
            generate_key(-0.1, 10)

    def test_invalid_seed_above_one_raises(self):
        with pytest.raises(ValueError, match="seed"):
            generate_key(1.5, 10)

    def test_invalid_n_zero_raises(self, valid_seed):
        with pytest.raises(ValueError, match="n"):
            generate_key(valid_seed, 0)

    def test_invalid_n_negative_raises(self, valid_seed):
        with pytest.raises(ValueError, match="n"):
            generate_key(valid_seed, -5)

    def test_all_values_in_byte_range(self, valid_seed):
        key = generate_key(valid_seed, 1000)
        assert key.min() >= 0
        assert key.max() <= 255


# ---------------------------------------------------------------------------
# shuffle_pixels
# ---------------------------------------------------------------------------

class TestShufflePixels:
    def test_output_shape_preserved(self, tiny_rgb_array, valid_seed):
        shuffled, _ = shuffle_pixels(tiny_rgb_array, valid_seed)
        assert shuffled.shape == tiny_rgb_array.shape

    def test_output_dtype_preserved(self, tiny_rgb_array, valid_seed):
        shuffled, _ = shuffle_pixels(tiny_rgb_array, valid_seed)
        assert shuffled.dtype == np.uint8

    def test_all_pixels_preserved(self, tiny_rgb_array, valid_seed):
        shuffled, _ = shuffle_pixels(tiny_rgb_array, valid_seed)
        original_flat = np.sort(tiny_rgb_array.reshape(-1, 3), axis=0)
        shuffled_flat = np.sort(shuffled.reshape(-1, 3), axis=0)
        np.testing.assert_array_equal(original_flat, shuffled_flat)

    def test_indices_length(self, tiny_rgb_array, valid_seed):
        h, w, _ = tiny_rgb_array.shape
        _, indices = shuffle_pixels(tiny_rgb_array, valid_seed)
        assert len(indices) == h * w

    def test_indices_are_permutation(self, tiny_rgb_array, valid_seed):
        h, w, _ = tiny_rgb_array.shape
        _, indices = shuffle_pixels(tiny_rgb_array, valid_seed)
        assert sorted(indices) == list(range(h * w))

    def test_deterministic(self, tiny_rgb_array, valid_seed):
        shuffled1, idx1 = shuffle_pixels(tiny_rgb_array, valid_seed)
        shuffled2, idx2 = shuffle_pixels(tiny_rgb_array, valid_seed)
        np.testing.assert_array_equal(shuffled1, shuffled2)
        np.testing.assert_array_equal(idx1, idx2)

    def test_invalid_2d_array_raises(self, valid_seed):
        arr = np.zeros((4, 4), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-D"):
            shuffle_pixels(arr, valid_seed)

    def test_invalid_dtype_raises(self, valid_seed):
        arr = np.zeros((4, 4, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            shuffle_pixels(arr, valid_seed)

    def test_invalid_seed_zero_raises(self, tiny_rgb_array):
        with pytest.raises(ValueError, match="seed"):
            shuffle_pixels(tiny_rgb_array, 0.0)

    def test_invalid_seed_one_raises(self, tiny_rgb_array):
        with pytest.raises(ValueError, match="seed"):
            shuffle_pixels(tiny_rgb_array, 1.0)


# ---------------------------------------------------------------------------
# encrypt_image
# ---------------------------------------------------------------------------

class TestEncryptImage:
    def test_output_shape_preserved(self, tiny_rgb_array, valid_seed):
        result = encrypt_image(tiny_rgb_array, valid_seed)
        assert result.shape == tiny_rgb_array.shape

    def test_output_dtype_preserved(self, tiny_rgb_array, valid_seed):
        result = encrypt_image(tiny_rgb_array, valid_seed)
        assert result.dtype == np.uint8

    def test_output_differs_from_input(self, tiny_rgb_array, valid_seed):
        result = encrypt_image(tiny_rgb_array, valid_seed)
        assert not np.array_equal(result, tiny_rgb_array)

    def test_deterministic(self, tiny_rgb_array, valid_seed):
        result1 = encrypt_image(tiny_rgb_array, valid_seed)
        result2 = encrypt_image(tiny_rgb_array, valid_seed)
        np.testing.assert_array_equal(result1, result2)

    def test_different_seeds_produce_different_ciphertext(self, tiny_rgb_array):
        enc1 = encrypt_image(tiny_rgb_array, 0.3)
        enc2 = encrypt_image(tiny_rgb_array, 0.7)
        assert not np.array_equal(enc1, enc2)

    def test_seed_near_upper_boundary_safe(self, tiny_rgb_array):
        result = encrypt_image(tiny_rgb_array, 0.95)
        assert result.shape == tiny_rgb_array.shape

    def test_seed_near_lower_boundary_safe(self, tiny_rgb_array):
        result = encrypt_image(tiny_rgb_array, 0.01)
        assert result.shape == tiny_rgb_array.shape

    def test_invalid_2d_array_raises(self, valid_seed):
        arr = np.zeros((4, 4), dtype=np.uint8)
        with pytest.raises(ValueError, match="3-D"):
            encrypt_image(arr, valid_seed)

    def test_invalid_dtype_raises(self, valid_seed):
        arr = np.zeros((4, 4, 3), dtype=np.float32)
        with pytest.raises(ValueError, match="uint8"):
            encrypt_image(arr, valid_seed)

    def test_invalid_seed_zero_raises(self, tiny_rgb_array):
        with pytest.raises(ValueError, match="seed"):
            encrypt_image(tiny_rgb_array, 0.0)

    def test_invalid_seed_one_raises(self, tiny_rgb_array):
        with pytest.raises(ValueError, match="seed"):
            encrypt_image(tiny_rgb_array, 1.0)

    def test_invalid_seed_above_one_raises(self, tiny_rgb_array):
        with pytest.raises(ValueError, match="seed"):
            encrypt_image(tiny_rgb_array, 1.1)

    def test_single_pixel_image(self, valid_seed):
        arr = np.array([[[128, 64, 32]]], dtype=np.uint8)
        result = encrypt_image(arr, valid_seed)
        assert result.shape == (1, 1, 3)
        assert result.dtype == np.uint8
