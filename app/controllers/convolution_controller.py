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
        card = ttk.Frame(frame, style="Card.TFrame", padding=10)
        card.pack(fill="x", pady=(2, 8))
        ttk.Label(card, text="Пользовательская свёртка",
                  style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        ttk.Label(card, textvariable=self.info_var, style="Card.TLabel",
                  wraplength=290).pack(anchor="w", pady=(0, 8))
        ttk.Button(card, text="⌗ Открыть редактор ядра...",
                   command=self.app.open_kernel_editor).pack(fill="x", pady=(0, 6))
        ttk.Button(card, text="▶ Применить текущее ядро",
                   style="Accent.TButton",
                   command=self.apply_kernel).pack(fill="x", pady=(0, 8))
        ttk.Label(card, style="CardDim.TLabel", wraplength=290, justify="left",
                  text="Матрица коэффициентов, делитель, смещение (bias) и "
                       "режим обработки границ настраиваются в редакторе ядра.").pack(anchor="w")
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
        # Snapshot prevents edits in the kernel editor from changing an in-flight job.
        km = self.app.kernel_model.copy()
        try:
            info = km.summary()
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return

        def job(src):
            return self.app.conv_model.apply_kernel_model(src, km)[0]

        self.app.run_async("Свёртка: пользовательское ядро", job, info)
