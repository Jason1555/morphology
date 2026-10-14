"""История обработки: Undo/Redo/переход к состоянию (без Tkinter)."""
from __future__ import annotations

import numpy as np


class HistoryModel:
    def __init__(self, max_states: int = 30) -> None:
        if max_states < 2:
            max_states = 2
        self.max_states = max_states
        self._states: list[dict] = []
        self._index: int = -1

    def __len__(self) -> int:
        return len(self._states)

    @property
    def index(self) -> int:
        return self._index

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._states) - 1

    def entries(self) -> list[dict]:
        return [
            {"label": s["label"], "params": s.get("params", ""), "active": i == self._index}
            for i, s in enumerate(self._states)
        ]

    def initialize(self, image: np.ndarray, label: str = "Исходное изображение") -> np.ndarray:
        self._states = [{"label": label, "params": "", "image": image.copy()}]
        self._index = 0
        return image.copy()

    def clear(self) -> None:
        self._states = []
        self._index = -1

    def push(self, image: np.ndarray, label: str, params: str = "") -> np.ndarray:
        if image.ndim != 2:
            raise ValueError("В историю можно сохранять только grayscale-изображения.")
        # Новая ветка: отбрасываем redo-хвост.
        if self._index < len(self._states) - 1:
            self._states = self._states[: self._index + 1]
        self._states.append({"label": label, "params": params, "image": image.copy()})
        # Ограничение памяти: выбрасываем самые старые (кроме нулевого, если возможно).
        while len(self._states) > self.max_states:
            self._states.pop(1)
        self._index = len(self._states) - 1
        return image.copy()

    def undo(self) -> tuple[np.ndarray, str]:
        if not self.can_undo():
            raise ValueError("Нечего отменять.")
        self._index -= 1
        s = self._states[self._index]
        return s["image"].copy(), s["label"]

    def redo(self) -> tuple[np.ndarray, str]:
        if not self.can_redo():
            raise ValueError("Нечего повторять.")
        self._index += 1
        s = self._states[self._index]
        return s["image"].copy(), s["label"]

    def jump_to(self, idx: int) -> tuple[np.ndarray, str]:
        if not (0 <= idx < len(self._states)):
            raise ValueError("Некорректный индекс истории.")
        self._index = idx
        s = self._states[idx]
        return s["image"].copy(), s["label"]

    def current(self) -> np.ndarray:
        if not self._states or self._index < 0:
            raise ValueError("История пуста.")
        return self._states[self._index]["image"].copy()
