"""Модель изображения: оригинал и текущий результат (без Tkinter)."""
from __future__ import annotations

import numpy as np

from app.utils.image_io import load_image_grayscale, save_image_grayscale


class ImageModel:
    def __init__(self) -> None:
        self._original: np.ndarray | None = None
        self._current: np.ndarray | None = None
        self.source_path: str | None = None

    @property
    def has_image(self) -> bool:
        return self._current is not None

    @property
    def original(self) -> np.ndarray | None:
        return None if self._original is None else self._original.copy()

    @property
    def current(self) -> np.ndarray | None:
        return None if self._current is None else self._current.copy()

    def _require_image(self) -> np.ndarray:
        if self._current is None:
            raise ValueError("Сначала откройте изображение (Файл → Открыть).")
        return self._current

    def load(self, path: str) -> np.ndarray:
        gray = load_image_grayscale(path)
        self._original = gray.copy()
        self._current = gray.copy()
        self.source_path = path
        return self.current

    def set_current(self, image: np.ndarray) -> np.ndarray:
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Некорректное изображение для установки.")
        if image.ndim != 2:
            raise ValueError("Изображение должно быть в градациях серого (2D).")
        img = image.copy()
        if img.dtype != np.uint8:
            img = np.clip(img, 0, 255).astype(np.uint8)
        self._current = img
        return self.current

    def reset_to_original(self) -> np.ndarray:
        if self._original is None:
            raise ValueError("Нет исходного изображения.")
        self._current = self._original.copy()
        return self.current

    def clear(self) -> None:
        self._original = None
        self._current = None
        self.source_path = None

    def require_current_copy(self) -> np.ndarray:
        return self._require_image().copy()

    def shape(self) -> tuple[int, int] | None:
        if self._current is None:
            return None
        h, w = self._current.shape
        return (h, w)

    def save_current(self, path: str) -> None:
        save_image_grayscale(path, self._require_image())
