"""
Chaotic-map encryption utilities for license plate privacy protection.

Implements a two-layer encryption scheme combining XOR with a logistic-map
chaotic key and pixel shuffling, as described in:

    Vehicle Number Plate Detection and Encryption in Digital Images Using
    YOLOv8 and Chaotic-Based Encryption Scheme (IEEE, 2024).
    https://ieeexplore.ieee.org/abstract/document/10534375/
"""

import random

import numpy as np


def logistic_map(r: float, x: float) -> float:
    """
    Compute a single step of the logistic map: ``r * x * (1 - x)``.

    For chaotic behaviour use ``r`` in the range ``(3.57, 4.0]``.

    :param r: Growth rate parameter.
    :param x: Current state value, expected in ``(0.0, 1.0)``.
    :return: Next state value.
    """
    return r * x * (1.0 - x)


def generate_key(seed: float, n: int) -> np.ndarray:
    """
    Generate a pseudo-random chaotic key array using the logistic map.

    Iterates the logistic map ``n`` times starting from ``seed``, mapping
    each floating-point state to a byte value in ``[0, 255]``.

    :param seed: Initial condition for the logistic map. Must be in ``(0.0, 1.0)`` exclusive.
    :param n: Number of key bytes to produce. Must be a positive integer.
    :return: NumPy array of shape ``(n,)`` with dtype ``uint8``.
    :raises ValueError: If ``seed`` is not strictly inside ``(0.0, 1.0)`` or ``n <= 0``.
    """
    if not (0.0 < seed < 1.0):
        raise ValueError(f"seed must be in (0.0, 1.0) exclusive, got {seed!r}")
    if n <= 0:
        raise ValueError(f"n must be a positive integer, got {n!r}")

    key = []
    x = seed
    for _ in range(n):
        x = logistic_map(3.9, x)
        key.append(int(x * 255) % 256)
    return np.array(key, dtype=np.uint8)


def shuffle_pixels(img_array: np.ndarray, seed: float):
    """
    Shuffle the pixels of an image using a seeded random permutation.

    The permutation is reproducible: the same ``seed`` always produces the
    same shuffling order, which is required for correct decryption.

    :param img_array: Input image as a NumPy array of shape ``(H, W, C)`` with dtype ``uint8``.
    :param seed: Seed for the random permutation. Must be in ``(0.0, 1.0)`` exclusive.
    :return: Tuple ``(shuffled_array, indices)`` where ``shuffled_array`` has the same
             shape and dtype as ``img_array``, and ``indices`` is an integer permutation
             array of length ``H * W`` that maps original pixel positions to new positions.
    :raises ValueError: If ``img_array`` is not a 3-D uint8 array, or ``seed`` is out of range.
    """
    if img_array.ndim != 3:
        raise ValueError(
            f"img_array must be a 3-D array (H, W, C), got shape {img_array.shape}"
        )
    if img_array.dtype != np.uint8:
        raise ValueError(
            f"img_array must have dtype uint8, got {img_array.dtype}"
        )
    if not (0.0 < seed < 1.0):
        raise ValueError(f"seed must be in (0.0, 1.0) exclusive, got {seed!r}")

    h, w, c = img_array.shape
    num_pixels = h * w
    flattened = img_array.reshape(-1, c)
    indices = np.arange(num_pixels)
    random.seed(seed)
    random.shuffle(indices)
    shuffled = flattened[indices]
    return shuffled.reshape(h, w, c), indices


def encrypt_image(img_array: np.ndarray, seed: float) -> np.ndarray:
    """
    Encrypt an image region using dual-pass chaotic XOR and pixel shuffling.

    Encryption pipeline:

    1. XOR every byte with a logistic-map chaotic key derived from ``seed``.
    2. Randomly shuffle all pixels using a permutation seeded by ``seed``.
    3. XOR every byte of the shuffled result with a second chaotic key
       derived from a perturbed seed ``min(seed * 1.1, 0.9999)``.

    :param img_array: Image region as a NumPy array of shape ``(H, W, C)``, dtype ``uint8``.
                      Typically a cropped license plate region extracted from a larger image.
    :param seed: Encryption seed in ``(0.0, 1.0)`` exclusive. Different seeds produce
                 different chaotic sequences and therefore different encrypted outputs.
    :return: Encrypted image as a NumPy array with the same shape and dtype as ``img_array``.
    :raises ValueError: If ``img_array`` is not a valid 3-D uint8 array, or ``seed`` is out of range.
    """
    if img_array.ndim != 3:
        raise ValueError(
            f"img_array must be a 3-D array (H, W, C), got shape {img_array.shape}"
        )
    if img_array.dtype != np.uint8:
        raise ValueError(
            f"img_array must have dtype uint8, got {img_array.dtype}"
        )
    if not (0.0 < seed < 1.0):
        raise ValueError(f"seed must be in (0.0, 1.0) exclusive, got {seed!r}")

    h, w, c = img_array.shape
    flat_image = img_array.flatten()

    chaotic_key_1 = generate_key(seed, len(flat_image))
    encrypted_layer_1 = (flat_image ^ chaotic_key_1).reshape(h, w, c)

    shuffled_array, _ = shuffle_pixels(encrypted_layer_1, seed)

    second_seed = min(seed * 1.1, 0.9999)
    chaotic_key_2 = generate_key(second_seed, len(flat_image))
    encrypted_layer_2 = (shuffled_array.flatten() ^ chaotic_key_2).reshape(h, w, c)

    return encrypted_layer_2
