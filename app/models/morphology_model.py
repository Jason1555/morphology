"""Математика морфологических операций через OpenCV (без Tkinter)."""
from __future__ import annotations

import cv2
import numpy as np

from app.models.structuring_element_model import StructuringElementModel
from app.utils.validators import validate_iterations

MORPH_OPS = [
    ("erosion", "Эрозия (Erosion)"),
    ("dilation", "Дилатация (Dilation)"),
    ("opening", "Открытие (Opening)"),
    ("closing", "Закрытие (Closing)"),
    ("gradient", "Морфологический градиент"),
    ("tophat", "Top Hat"),
    ("blackhat", "Black Hat"),
]

_ITERATED_OPS = {"erosion", "dilation"}


class MorphologyModel:
    @staticmethod
    def _check_image(image: np.ndarray) -> np.ndarray:
        if image is None:
            raise ValueError("Нет изображения для обработки.")
        arr = np.asarray(image)
        if arr.ndim != 2:
            raise ValueError("Морфология работает только с grayscale (2D).")
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(arr)

    @staticmethod
    def _check_se(se: StructuringElementModel) -> tuple[np.ndarray, tuple[int, int]]:
        if se is None:
            raise ValueError("Не задан структурный элемент.")
        kernel = se.to_opencv_kernel()
        return kernel, se.opencv_anchor()

    def apply(self, image: np.ndarray, op: str, se: StructuringElementModel,
              iterations: int = 1) -> np.ndarray:
        src = self._check_image(image)
        kernel, anchor = self._check_se(se)
        valid = {key for key, _ in MORPH_OPS}
        if op not in valid:
            raise ValueError(f"Неизвестная морфологическая операция: {op}.")
        it = validate_iterations(iterations) if op in _ITERATED_OPS else 1
        try:
            if op == "erosion":
                return cv2.erode(src, kernel, anchor=anchor, iterations=it)
            if op == "dilation":
                return cv2.dilate(src, kernel, anchor=anchor, iterations=it)
            if op == "opening":
                return cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel, anchor=anchor)
            if op == "closing":
                return cv2.morphologyEx(src, cv2.MORPH_CLOSE, kernel, anchor=anchor)
            if op == "gradient":
                return cv2.morphologyEx(src, cv2.MORPH_GRADIENT, kernel, anchor=anchor)
            if op == "tophat":
                return cv2.morphologyEx(src, cv2.MORPH_TOPHAT, kernel, anchor=anchor)
            return cv2.morphologyEx(src, cv2.MORPH_BLACKHAT, kernel, anchor=anchor)
        except cv2.error as exc:
            raise ValueError(f"OpenCV не смог выполнить операцию: {exc}") from exc
