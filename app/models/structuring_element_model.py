"""Модель структурного элемента: бинарная маска + якорь (без Tkinter)."""
from __future__ import annotations

import json
import os

import numpy as np

from app.utils.validators import validate_anchor, validate_se_size

PRESET_ORDER = [
    ("square", "Квадрат"), ("rect", "Прямоугольник"), ("circle", "Круг"),
    ("ellipse", "Эллипс"), ("diamond", "Ромб"), ("cross", "Крест"),
    ("line_h", "Горизонтальная линия"), ("line_v", "Вертикальная линия"),
    ("diag", "Диагональ"), ("adiag", "Обратная диагональ"), ("x", "X"),
    ("plus", "Плюс"), ("ring", "Кольцо"), ("ellipse_h", "Горизонтальный эллипс"),
    ("ellipse_v", "Вертикальный эллипс"), ("empty", "Пустой"),
    ("filled", "Полностью заполненный"),
]


def build_preset(name: str, width: int, height: int) -> np.ndarray:
    """Построить бинарную маску предустановки под размеры WxH (расчёт, не картинки)."""
    w, h = validate_se_size(width, height)
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    mask = np.zeros((h, w), dtype=np.uint8)
    if name in ("filled", "rect"):
        mask[:, :] = 1
    elif name == "square":
        side = min(w, h)
        x0, y0 = (w - side) // 2, (h - side) // 2
        mask[y0:y0 + side, x0:x0 + side] = 1
    elif name == "empty":
        pass
    elif name in ("circle", "ellipse"):
        rx, ry = max(cx, 0.5), max(cy, 0.5)
        mask[((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0] = 1
    elif name == "ellipse_h":
        rx = max(w / 2.0 * 0.95, 0.5)
        ry = max(min(w, h) / 2.0 * 0.55, 0.5)
        mask[((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0] = 1
    elif name == "ellipse_v":
        rx = max(min(w, h) / 2.0 * 0.55, 0.5)
        ry = max(h / 2.0 * 0.95, 0.5)
        mask[((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0] = 1
    elif name == "diamond":
        dx = np.abs(xx - cx) / (cx if cx > 0 else 0.5)
        dy = np.abs(yy - cy) / (cy if cy > 0 else 0.5)
        mask[(dx + dy) <= 1.0] = 1
    elif name in ("cross", "plus"):
        mask[int(cy), :] = 1
        mask[:, int(cx)] = 1
    elif name == "x":
        n = min(w, h)
        x0, y0 = (w - n) // 2, (h - n) // 2
        for i in range(n):
            mask[y0 + i, x0 + i] = 1
            mask[y0 + i, x0 + n - 1 - i] = 1
    elif name == "diag":
        n = min(w, h)
        x0, y0 = (w - n) // 2, (h - n) // 2
        for i in range(n):
            mask[y0 + i, x0 + i] = 1
    elif name == "adiag":
        n = min(w, h)
        x0, y0 = (w - n) // 2, (h - n) // 2
        for i in range(n):
            mask[y0 + i, x0 + n - 1 - i] = 1
    elif name == "line_h":
        mask[int(cy), :] = 1
    elif name == "line_v":
        mask[:, int(cx)] = 1
    elif name == "ring":
        rx, ry = max(cx, 0.5), max(cy, 0.5)
        r2 = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        mask[(r2 <= 1.0) & (r2 > 0.42)] = 1
    else:
        raise ValueError(f"Неизвестная предустановка: {name}.")
    if name != "empty" and not mask.any():
        mask[int(cy), int(cx)] = 1
    return mask
class StructuringElementModel:
    """Бинарная маска HxW (0/1) + якорь (ax, ay)."""

    def __init__(self, width: int = 3, height: int = 3) -> None:
        w, h = validate_se_size(width, height)
        self._mask = np.ones((h, w), dtype=np.uint8)
        self._anchor = (w // 2, h // 2)

    @property
    def width(self) -> int:
        return self._mask.shape[1]

    @property
    def height(self) -> int:
        return self._mask.shape[0]

    @property
    def anchor(self) -> tuple[int, int]:
        return self._anchor

    @property
    def mask(self) -> np.ndarray:
        return self._mask.copy()

    @property
    def active_count(self) -> int:
        return int(self._mask.sum())

    def _fix_anchor(self) -> None:
        ax, ay = self._anchor
        self._anchor = (min(max(ax, 0), self.width - 1), min(max(ay, 0), self.height - 1))

    def set_anchor(self, ax: int, ay: int) -> tuple[int, int]:
        self._anchor = validate_anchor(ax, ay, self.width, self.height)
        return self._anchor

    def center_anchor(self) -> tuple[int, int]:
        self._anchor = (self.width // 2, self.height // 2)
        return self._anchor

    def resize(self, width: int, height: int) -> np.ndarray:
        w, h = validate_se_size(width, height)
        new_mask = np.zeros((h, w), dtype=np.uint8)
        mh, mw = min(h, self.height), min(w, self.width)
        new_mask[:mh, :mw] = self._mask[:mh, :mw]
        self._mask = new_mask
        self._fix_anchor()
        return self.mask

    def set_cell(self, x: int, y: int, value: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mask[y, x] = 1 if value else 0

    def toggle_cell(self, x: int, y: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self._mask[y, x] ^= 1

    def set_mask(self, mask: np.ndarray) -> np.ndarray:
        arr = np.asarray(mask)
        if arr.ndim != 2:
            raise ValueError("Маска должна быть двумерной.")
        h, w = arr.shape
        validate_se_size(w, h)
        self._mask = (arr != 0).astype(np.uint8)
        self._fix_anchor()
        return self.mask

    def clear(self) -> None:
        self._mask[:, :] = 0

    def fill(self) -> None:
        self._mask[:, :] = 1

    def invert(self) -> None:
        self._mask ^= 1

    def apply_preset(self, name: str) -> np.ndarray:
        self._mask = build_preset(name, self.width, self.height)
        self._fix_anchor()
        return self.mask

    def flip_horizontal(self) -> None:
        self._mask = np.fliplr(self._mask).copy()
        ax, ay = self._anchor
        self._anchor = (self.width - 1 - ax, ay)

    def flip_vertical(self) -> None:
        self._mask = np.flipud(self._mask).copy()
        ax, ay = self._anchor
        self._anchor = (ax, self.height - 1 - ay)

    def rotate(self, angle: int) -> None:
        if angle not in (90, 180, 270):
            raise ValueError("Поворот: только 90, 180 или 270 градусов.")
        w_old, h_old = self.width, self.height
        ax, ay = self._anchor
        if angle == 90:
            self._mask = np.rot90(self._mask, k=3).copy()
            self._anchor = (h_old - 1 - ay, ax)
        elif angle == 180:
            self._mask = np.rot90(self._mask, k=2).copy()
            self._anchor = (w_old - 1 - ax, h_old - 1 - ay)
        else:
            self._mask = np.rot90(self._mask, k=1).copy()
            self._anchor = (ay, w_old - 1 - ax)
        self._fix_anchor()

    def shift(self, dx: int, dy: int) -> None:
        """Обычный (не циклический) сдвиг маски с заполнением нулями.

        Якорь остаётся на месте: двигается содержимое маски относительно
        фиксированной опорной точки. Размеры маски сохраняются.
        """
        try:
            dx, dy = int(dx), int(dy)
        except (TypeError, ValueError) as exc:
            raise ValueError("Сдвиг должен быть целым числом.") from exc
        if dx == 0 and dy == 0:
            return
        h, w = self._mask.shape
        moved = np.zeros_like(self._mask)
        src_y0, src_y1 = max(0, -dy), min(h, h - dy)
        src_x0, src_x1 = max(0, -dx), min(w, w - dx)
        dst_y0, dst_y1 = max(0, dy), min(h, h + dy)
        dst_x0, dst_x1 = max(0, dx), min(w, w + dx)
        if src_y1 > src_y0 and src_x1 > src_x0:
            moved[dst_y0:dst_y1, dst_x0:dst_x1] = self._mask[src_y0:src_y1, src_x0:src_x1]
        self._mask = moved

    def copy(self) -> "StructuringElementModel":
        clone = StructuringElementModel(self.width, self.height)
        clone._mask = self._mask.copy()
        clone._anchor = self._anchor
        return clone

    def to_opencv_kernel(self) -> np.ndarray:
        if not self._mask.any():
            raise ValueError("Структурный элемент пуст: включите хотя бы одну ячейку.")
        return self._mask.astype(np.uint8).copy()

    def opencv_anchor(self) -> tuple[int, int]:
        return (self._anchor[0], self._anchor[1])

    def to_dict(self) -> dict:
        return {"width": self.width, "height": self.height,
                "anchor": [self._anchor[0], self._anchor[1]],
                "mask": self._mask.astype(int).tolist()}

    def from_dict(self, data: dict) -> None:
        try:
            w, h = int(data["width"]), int(data["height"])
            ax, ay = int(data["anchor"][0]), int(data["anchor"][1])
            mask = np.asarray(data["mask"], dtype=np.uint8)
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            raise ValueError("Файл структурного элемента повреждён.") from exc
        validate_se_size(w, h)
        if mask.shape != (h, w):
            raise ValueError("Размер маски не совпадает с метаданными.")
        self._mask = (mask != 0).astype(np.uint8)
        self._anchor = validate_anchor(ax, ay, w, h)

    def save(self, path: str) -> None:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        elif ext == ".npz":
            np.savez_compressed(path, mask=self._mask.astype(np.uint8),
                                width=np.int32(self.width), height=np.int32(self.height),
                                anchor=np.int32([self._anchor[0], self._anchor[1]]))
        else:
            raise ValueError("Сохранять структурный элемент можно в JSON или NPZ.")

    def load(self, path: str) -> None:
        if not os.path.exists(path):
            raise ValueError(f"Файл не найден: {path}")
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".json":
                with open(path, "r", encoding="utf-8") as f:
                    self.from_dict(json.load(f))
            elif ext == ".npz":
                with np.load(path) as z:
                    mask = np.asarray(z["mask"], dtype=np.uint8)
                    w, h = int(z["width"]), int(z["height"])
                    ax, ay = int(z["anchor"][0]), int(z["anchor"][1])
                    validate_se_size(w, h)
                    if mask.shape != (h, w):
                        raise ValueError("Размер маски в NPZ не совпадает.")
                    self._mask = (mask != 0).astype(np.uint8)
                    self._anchor = validate_anchor(ax, ay, w, h)
            else:
                raise ValueError("Загружать структурный элемент можно из JSON или NPZ.")
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Не удалось загрузить структурный элемент: {exc}") from exc

