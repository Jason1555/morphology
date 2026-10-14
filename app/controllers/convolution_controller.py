"""Контроллер свёртки: панель + запуск ConvolutionModel."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views import dialogs


class ConvolutionController:
    def __init__(self, app) -> None:
        self.app = app
        self.info_var = tk.StringVar(value="")

    def build_panel(self, frame) -> None:
        ttk.Label(frame, text="Пользовательская свёртка",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(6, 0))
        ttk.Label(frame, textvariable=self.info_var, wraplength=300).pack(
            anchor="w", pady=4)
        ttk.Button(frame, text="Открыть редактор ядра...",
                   command=self.app.open_kernel_editor).pack(fill="x", pady=2)
        ttk.Button(frame, text="Применить текущее ядро",
                   style="Accent.TButton",
                   command=self.apply_kernel).pack(fill="x", pady=6)
        ttk.Label(frame, wraplength=300, justify="left",
                  text="Ядро, делитель, bias и граница задаются "
                       "в редакторе ядра. Результат применяется "
                       "к текущему изображению.").pack(anchor="w", pady=4)
        self.refresh_info()

    def refresh_info(self) -> None:
        try:
            self.info_var.set(self.app.kernel_model.summary())
        except (tk.TclError, ValueError):
            pass

    def apply_kernel(self) -> None:
        if not self.app.image_model.has_image:
            dialogs.show_error(self.app.view.root, "Сначала откройте изображение.")
            return
        km = self.app.kernel_model

        def job(src):
            return self.app.conv_model.apply_kernel_model(src, km)[0]

        try:
            _, info = self.app.conv_model.apply_kernel_model(
                self.app.image_model.require_current_copy(), km)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.run_async("Свёртка: пользовательское ядро", job, info)
