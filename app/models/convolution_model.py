"""Пользовательская свёртка: divisor/bias/border, float-промежуток (без Tkinter)."""
from __future__ import annotations

import cv2
import numpy as np

from app.models.kernel_model import KernelModel
from app.utils.validators import validate_bias, validate_border, validate_divisor

BORDER_MAP = {
    "default": cv2.BORDER_DEFAULT,
    "replicate": cv2.BORDER_REPLICATE,
    "reflect": cv2.BORDER_REFLECT,
    "isolated": cv2.BORDER_ISOLATED,
    "constant": cv2.BORDER_CONSTANT,
}

BORDER_TITLES = {
    "default": "Default (отражение 101)",
    "replicate": "Replicate (копия края)",
    "reflect": "Reflect (отражение)",
    "isolated": "Isolated (без выхода за край)",
    "constant": "Constant (чёрная рамка)",
}


class ConvolutionModel:
    @staticmethod
    def _check(image: np.ndarray) -> np.ndarray:
        if image is None:
            raise ValueError("Нет изображения для обработки.")
        arr = np.asarray(image)
        if arr.ndim != 2:
            raise ValueError("Свёртка работает только с grayscale (2D).")
        if arr.dtype != np.uint8:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        return np.ascontiguousarray(arr)

    def apply(self, image: np.ndarray, kernel: np.ndarray, divisor: float = 1.0,
              bias: float = 0.0, border: str = "default",
              auto_normalize: bool = False) -> np.ndarray:
        src = self._check(image)
        mat = np.asarray(kernel, dtype=np.float64)
        if mat.ndim != 2:
            raise ValueError("Ядро свёртки должно быть двумерной матрицей.")
        if mat.shape[0] > 31 or mat.shape[1] > 31 or mat.shape[0] < 1 or mat.shape[1] < 1:
            raise ValueError("Размер ядра: от 1x1 до 31x31.")
        if not np.all(np.isfinite(mat)):
            raise ValueError("Ядро содержит некорректные значения.")
        d = validate_divisor(divisor, auto_normalize, float(mat.sum()))
        b = validate_bias(bias)
        border = validate_border(border)
        normed = (mat / d).astype(np.float32)
        try:
            convo = cv2.filter2D(src.astype(np.float32), ddepth=cv2.CV_32F,
                                 kernel=normed, borderType=BORDER_MAP[border])
        except cv2.error as exc:
            raise ValueError(f"OpenCV не смог выполнить свёртку: {exc}") from exc
        # Смещение применяется после свёртки, клип — только в самом конце.
        convo = convo + float(b)
        return np.clip(convo, 0, 255).astype(np.uint8)

    def apply_kernel_model(self, image: np.ndarray, km: KernelModel) -> tuple[np.ndarray, str]:
        d, how = km.effective_divisor()
        out = self.apply(image, km.matrix, divisor=d, bias=km.bias,
                         border=km.border, auto_normalize=False)
        info = f"делитель={d:.4g} ({how}), bias={km.bias:.4g}, граница={km.border}"
        return out, info
