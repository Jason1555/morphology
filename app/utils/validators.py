"""Проверка корректности параметров на уровне логики (без Tkinter)."""
from __future__ import annotations

import numpy as np

SE_MIN = 1
SE_MAX = 101

BORDER_NAMES = ("default", "replicate", "reflect", "isolated", "constant")


def validate_se_size(width: int, height: int) -> tuple[int, int]:
    try:
        w, h = int(width), int(height)
    except (TypeError, ValueError) as exc:
        raise ValueError("Ширина и высота структурного элемента должны быть целыми числами.") from exc
    for v, name in ((w, "Ширина"), (h, "Высота")):
        if not (SE_MIN <= v <= SE_MAX):
            raise ValueError(f"{name} должна быть от {SE_MIN} до {SE_MAX}.")
    return w, h


def validate_anchor(ax: int, ay: int, width: int, height: int) -> tuple[int, int]:
    try:
        ax, ay = int(ax), int(ay)
    except (TypeError, ValueError) as exc:
        raise ValueError("Координаты якоря должны быть целыми числами.") from exc
    if not (0 <= ax < width and 0 <= ay < height):
        raise ValueError(f"Якорь ({ax}, {ay}) вне элемента {width}x{height}.")
    return ax, ay


def validate_iterations(n) -> int:
    try:
        n = int(n)
    except (TypeError, ValueError) as exc:
        raise ValueError("Количество итераций должно быть целым числом.") from exc
    if not (1 <= n <= 100):
        raise ValueError("Количество итераций должно быть от 1 до 100.")
    return n


def validate_median_ksize(k) -> int:
    try:
        k = int(k)
    except (TypeError, ValueError) as exc:
        raise ValueError("Размер ядра медианного фильтра должен быть целым числом.") from exc
    if k < 1 or k > 101 or k % 2 == 0:
        raise ValueError("Размер ядра медианного фильтра: нечётное число от 1 до 101.")
    return k


def validate_motion_params(length, angle) -> tuple[int, float]:
    try:
        length = int(length)
    except (TypeError, ValueError) as exc:
        raise ValueError("Длина ядра размытия должна быть целым числом.") from exc
    try:
        angle = float(angle)
    except (TypeError, ValueError) as exc:
        raise ValueError("Угол размытия должен быть числом.") from exc
    if not (1 <= length <= 101):
        raise ValueError("Длина ядра размытия: от 1 до 101.")
    if not (0.0 <= angle < 360.0):
        raise ValueError("Угол размытия: от 0 до 360 градусов.")
    return length, angle


def validate_sharpen_strength(value) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Сила резкости должна быть числом.") from exc
    if not (0.0 <= v <= 5.0):
        raise ValueError("Сила резкости: от 0.0 до 5.0.")
    return v


def validate_kernel_matrix(values) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("Ядро свёртки должно быть двумерной матрицей.")
    h, w = arr.shape
    if not (1 <= w <= 31 and 1 <= h <= 31):
        raise ValueError("Размер ядра: от 1x1 до 31x31.")
    if not np.all(np.isfinite(arr)):
        raise ValueError("Ядро содержит некорректные значения (NaN/inf).")
    return arr


def validate_divisor(divisor, auto: bool, kernel_sum: float) -> float:
    if auto:
        if abs(kernel_sum) < 1e-12:
            raise ValueError("Автонормализация невозможна: сумма коэффициентов равна нулю.")
        return float(kernel_sum)
    try:
        d = float(divisor)
    except (TypeError, ValueError) as exc:
        raise ValueError("Делитель должен быть числом.") from exc
    if not np.isfinite(d):
        raise ValueError("Делитель некорректен.")
    if abs(d) < 1e-12:
        raise ValueError("Делитель не должен быть равен нулю.")
    return d


def validate_bias(bias) -> float:
    try:
        b = float(bias)
    except (TypeError, ValueError) as exc:
        raise ValueError("Смещение (bias) должно быть числом.") from exc
    if not np.isfinite(b):
        raise ValueError("Смещение некорректно.")
    return b


def validate_border(name: str) -> str:
    if name not in BORDER_NAMES:
        raise ValueError(f"Неизвестный тип границы: {name}.")
    return name


def parse_float_cell(text: str) -> float:
    try:
        v = float(str(text).replace(",", ".").strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Некорректный коэффициент: {text!r}.") from exc
    if not np.isfinite(v):
        raise ValueError(f"Некорректный коэффициент: {text!r}.")
    return v
