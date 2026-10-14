"""Утилиты загрузки/сохранения изображений в градациях серого (без Tkinter)."""
from __future__ import annotations

import os

import cv2
import numpy as np

SUPPORTED_OPEN_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")
SUPPORTED_SAVE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff")


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Привести BGR/BGRA/Gray массив к uint8 HxW grayscale.

    Прозрачность сводится с чёрным фоном. Порядок каналов — BGR (OpenCV).
    """
    if image is None:
        raise ValueError("Не удалось прочитать изображение (файл пуст или повреждён).")
    if image.ndim == 2:
        gray = image
    elif image.ndim == 3:
        channels = image.shape[2]
        if channels == 4:
            # BGRA -> сводим с чёрным фоном, затем BGR -> Gray.
            b, g, r, a = cv2.split(image)
            alpha = (a.astype(np.float32) / 255.0)[..., None]
            bgr = np.dstack([b, g, r]).astype(np.float32)
            blended = (bgr * alpha).astype(np.uint8)
            gray = cv2.cvtColor(blended, cv2.COLOR_BGR2GRAY)
        elif channels == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        elif channels == 1:
            gray = image[:, :, 0]
        else:
            raise ValueError(f"Неподдерживаемое число каналов: {channels}.")
    else:
        raise ValueError("Неподдерживаемая размерность массива изображения.")
    if gray.dtype != np.uint8:
        gray = np.clip(gray, 0, 255).astype(np.uint8)
    return np.ascontiguousarray(gray)


def load_image_grayscale(path: str) -> np.ndarray:
    """Загрузить файл и вернуть uint8 HxW grayscale. Бросает ValueError при ошибке."""
    if not path or not os.path.exists(path):
        raise ValueError(f"Файл не найден: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_OPEN_EXTS:
        raise ValueError(f"Формат '{ext}' не поддерживается. Используйте PNG, JPEG, BMP или TIFF.")
    raw = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if raw is None:
        raise ValueError("Не удалось прочитать файл: возможно, он повреждён или это не изображение.")
    gray = to_grayscale(raw)
    return gray.copy()


def save_image_grayscale(path: str, image: np.ndarray) -> None:
    """Сохранить одноканальное uint8 изображение. Бросает ValueError при ошибке."""
    if image is None:
        raise ValueError("Нет изображения для сохранения.")
    if image.ndim != 2:
        raise ValueError("Сохранять можно только изображение в градациях серого (2D массив).")
    if image.dtype != np.uint8:
        raise ValueError("Внутреннее представление должно быть uint8.")
    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        raise ValueError(f"Папка не существует: {directory}")
    ok = cv2.imwrite(path, image)
    if not ok:
        raise ValueError(f"OpenCV не смог записать файл: {path}")
