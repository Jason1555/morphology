"""Контроллер истории: Undo/Redo/переход (без математики обработки)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views import dialogs


class HistoryController:
    def __init__(self, app) -> None:
        self.app = app
        self._count_var: tk.StringVar | None = None

    def build_panel(self, frame) -> None:
        """Панель категории «История»: использует существующую историю."""
        card = ttk.Frame(frame, style="Card.TFrame", padding=10)
        card.pack(fill="x", pady=(2, 8))
        ttk.Label(card, text="Управление историей",
                  style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(card, style="CardDim.TLabel", wraplength=290, justify="left",
                  text="Выберите любой шаг в списке «История состояний» ниже, "
                       "чтобы мгновенно перейти к нему. Новая операция после "
                       "отката создаст новую ветку.").pack(anchor="w", pady=(0, 8))
        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x", pady=(0, 4))
        ttk.Button(row, text="↶ Отменить",
                   command=self.undo).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(row, text="↷ Повторить",
                   command=self.redo).pack(side="left", fill="x", expand=True, padx=(2, 0))
        ttk.Button(card, text="↺ Сбросить к оригиналу",
                   command=self.app.image_ctrl.reset_to_original).pack(
            fill="x", pady=(2, 8))
        self._count_var = tk.StringVar(value="")
        ttk.Label(card, textvariable=self._count_var, style="Card.TLabel",
                  wraplength=290).pack(anchor="w")
        self.refresh_panel()

    def undo(self) -> None:
        try:
            img, label = self.app.history.undo()
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Отмена: {label}")

    def redo(self) -> None:
        try:
            img, label = self.app.history.redo()
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Повтор: {label}")

    def refresh_panel(self) -> None:
        """Обновить счётчик панели категории (безопасно при закрытом UI)."""
        var = self._count_var
        if var is None:
            return
        try:
            n = len(self.app.history)
            pos = self.app.history.index + 1 if n else 0
            var.set(f"Состояний: {n} (позиция {pos}).")
        except (tk.TclError, ValueError, AttributeError):
            pass

    def jump(self, index: int) -> None:
        try:
            img, label = self.app.history.jump_to(index)
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Переход к состоянию {index}: {label}")
