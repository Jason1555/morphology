"""Модель пользовательского ядра свёртки (без Tkinter)."""
from __future__ import annotations

import numpy as np

from app.utils.validators import validate_bias, validate_border, validate_divisor, validate_kernel_matrix

KERNEL_PRESETS = {
    "sharpen": ("Повышение резкости", [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]),
    "blur": ("Размытие", [[1, 1, 1], [1, 1, 1], [1, 1, 1]]),
    "edge_h": ("Горизонтальные границы", [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]),
    "edge_v": ("Вертикальные границы", [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]),
    "edge_d": ("Диагональные границы", [[-1, -1, 0], [-1, 0, 1], [0, 1, 1]]),
    "emboss": ("Тиснение (Emboss)", [[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]),
}


class KernelModel:
    def __init__(self, rows: int = 3, cols: int = 3) -> None:
        self._matrix = np.zeros((3, 3), dtype=np.float64)
        self._matrix[1, 1] = 1.0
        self.resize(rows, cols)
        self._divisor: float = 1.0
        self._auto_normalize: bool = False
        self._bias: float = 0.0
        self._border: str = "default"

    @property
    def rows(self) -> int:
        return self._matrix.shape[0]

    @property
    def cols(self) -> int:
        return self._matrix.shape[1]

    @property
    def matrix(self) -> np.ndarray:
        return self._matrix.copy()

    @property
    def divisor(self) -> float:
        return self._divisor

    @property
    def auto_normalize(self) -> bool:
        return self._auto_normalize

    @property
    def bias(self) -> float:
        return self._bias

    @property
    def border(self) -> str:
        return self._border

    def resize(self, rows: int, cols: int) -> np.ndarray:
        try:
            r, c = int(rows), int(cols)
        except (TypeError, ValueError) as exc:
            raise ValueError("Строки и столбцы ядра — целые числа.") from exc
        if not (1 <= r <= 31 and 1 <= c <= 31):
            raise ValueError("Размер ядра: от 1x1 до 31x31.")
        new_m = np.zeros((r, c), dtype=np.float64)
        mh, mw = min(r, self._matrix.shape[0]), min(c, self._matrix.shape[1])
        new_m[:mh, :mw] = self._matrix[:mh, :mw]
        self._matrix = new_m
        return self.matrix

    def set_value(self, row: int, col: int, value: float) -> None:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            raise ValueError("Индекс коэффициента вне ядра.")
        try:
            v = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Коэффициент должен быть числом.") from exc
        if not np.isfinite(v):
            raise ValueError("Коэффициент некорректен.")
        self._matrix[row, col] = v

    def set_matrix(self, values) -> np.ndarray:
        self._matrix = validate_kernel_matrix(values)
        return self.matrix

    def set_divisor(self, value) -> float:
        self._divisor = validate_divisor(value, False, float(self._matrix.sum()))
        return self._divisor

    def set_auto_normalize(self, flag: bool) -> None:
        self._auto_normalize = bool(flag)

    def set_bias(self, value) -> float:
        self._bias = validate_bias(value)
        return self._bias

    def set_border(self, name: str) -> str:
        self._border = validate_border(name)
        return self._border

    def clear(self) -> None:
        self._matrix[:, :] = 0.0

    def fill_ones(self) -> None:
        self._matrix[:, :] = 1.0

    def apply_preset(self, name: str) -> np.ndarray:
        if name not in KERNEL_PRESETS:
            raise ValueError(f"Неизвестная предустановка ядра: {name}.")
        title, mat = KERNEL_PRESETS[name]
        self._matrix = np.asarray(mat, dtype=np.float64)
        if name == "emboss":
            self._bias = 128.0
        return self.matrix

    def effective_divisor(self) -> tuple[float, str]:
        s = float(self._matrix.sum())
        if self._auto_normalize:
            d = validate_divisor(None, True, s)
            return d, "авто (сумма коэффициентов)"
        d = validate_divisor(self._divisor, False, s)
        return d, "вручную"

    def normalized_kernel(self) -> tuple[np.ndarray, float, str]:
        d, how = self.effective_divisor()
        return (self._matrix / d).astype(np.float64), d, how

    def copy(self) -> "KernelModel":
        """Return an independent snapshot suitable for background processing."""
        clone = KernelModel(self.rows, self.cols)
        clone._matrix = self._matrix.copy()
        clone._divisor = self._divisor
        clone._auto_normalize = self._auto_normalize
        clone._bias = self._bias
        clone._border = self._border
        return clone

    def summary(self) -> str:
        d, how = self.effective_divisor()
        return (f"Ядро {self.rows}x{self.cols}, сумма={float(self._matrix.sum()):.4g}, "
                f"делитель={d:.4g} ({how}), bias={self._bias:.4g}, граница={self._border}")
