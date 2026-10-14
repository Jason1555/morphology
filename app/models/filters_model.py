"""Фильтры изображений: резкость, motion blur, emboss, медиана (без Tkinter)."""
from __future__ import annotations

import cv2
import numpy as np

from app.utils.validators import (
    validate_median_ksize,
    validate_motion_params,
    validate_sharpen_strength,
)

FILTERS = [
    ("sharpen", "Резкость"),
    ("motion", "Размытие в движении"),
    ("emboss", "Тиснение (Emboss)"),
    ("median", "Медианный фильтр"),
]


def build_motion_kernel(length: int, angle_deg: float) -> np.ndarray:
    length, angle = validate_motion_params(length, angle_deg)
    size = length
    kernel = np.zeros((size, size), dtype=np.float64)
    kernel[size // 2, :] = 1.0
    center = (size / 2 - 0.5, size / 2 - 0.5)
    rot = cv2.getRotationMatrix2D(center, angle, 1.0)
    kernel = cv2.warpAffine(kernel, rot, (size, size), flags=cv2.INTER_LINEAR)
    total = kernel.sum()
    if abs(total) < 1e-12:
        kernel[size // 2, size // 2] = 1.0
        total = 1.0
    return (kernel / total).astype(np.float64)


def build_sharpen_kernel(strength: float) -> np.ndarray:
    k = validate_sharpen_strength(strength)
    kernel = np.array([[0, -k, 0], [-k, 1 + 4 * k, -k], [0, -k, 0]], dtype=np.float64)
    return kernel


EMBOSS_KERNEL = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]], dtype=np.float64)
EMBOSS_BIAS = 128.0


class FiltersModel:
    @staticmethod
    def _check(image: np.ndarray) -> np.ndarray:
        if image is None:
            raise ValueError("Нет изображения для обработки.")
        arr = np.asarray(image)
        if arr.ndim != 2:
            raise ValueError("Фильтры работают только с grayscale (2D).")
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(arr)

    @staticmethod
    def _filter2d(src: np.ndarray, kernel: np.ndarray, bias: float = 0.0) -> np.ndarray:
        try:
            convo = cv2.filter2D(src.astype(np.float32), ddepth=cv2.CV_32F,
                                 kernel=kernel.astype(np.float32))
        except cv2.error as exc:
            raise ValueError(f"OpenCV не смог выполнить фильтрацию: {exc}") from exc
        convo = convo + float(bias)
        return np.clip(convo, 0, 255).astype(np.uint8)

    def sharpen(self, image: np.ndarray, strength: float = 1.0) -> np.ndarray:
        src = self._check(image)
        return self._filter2d(src, build_sharpen_kernel(strength))

    def motion_blur(self, image: np.ndarray, length: int = 9, angle: float = 0.0) -> np.ndarray:
        src = self._check(image)
        return self._filter2d(src, build_motion_kernel(length, angle))

    def emboss(self, image: np.ndarray) -> np.ndarray:
        src = self._check(image)
        return self._filter2d(src, EMBOSS_KERNEL, EMBOSS_BIAS)

    def emboss_kernel_info(self) -> tuple[np.ndarray, float]:
        return EMBOSS_KERNEL.copy(), EMBOSS_BIAS

    def median(self, image: np.ndarray, ksize: int = 3) -> np.ndarray:
        src = self._check(image)
        k = validate_median_ksize(ksize)
        try:
            return cv2.medianBlur(src, k)
        except cv2.error as exc:
            raise ValueError(f"OpenCV не смог выполнить медианную фильтрацию: {exc}") from exc
