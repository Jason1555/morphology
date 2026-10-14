"""Контроллер фильтров: резкость, motion, emboss, медиана."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views import dialogs


class FiltersController:
    def __init__(self, app) -> None:
        self.app = app
        self.strength_var = tk.StringVar(value="1.0")
        self.length_var = tk.StringVar(value="9")
        self.angle_var = tk.StringVar(value="0")
        self.median_var = tk.StringVar(value="3")

    def build_panel(self, frame) -> None:
        ttk.Label(frame, text="Резкость", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(6, 0))
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=2)
        ttk.Label(row, text="Сила (0–5):").pack(side="left")
        ttk.Entry(row, textvariable=self.strength_var, width=6).pack(
            side="left", padx=4)
        ttk.Button(row, text="Применить", command=self.apply_sharpen).pack(
            side="left", padx=4)
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(frame, text="Размытие в движении",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row2 = ttk.Frame(frame)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="Длина:").pack(side="left")
        ttk.Entry(row2, textvariable=self.length_var, width=6).pack(
            side="left", padx=4)
        ttk.Label(row2, text="Угол:").pack(side="left")
        ttk.Entry(row2, textvariable=self.angle_var, width=6).pack(
            side="left", padx=4)
        ttk.Button(frame, text="Применить размытие",
                   command=self.apply_motion).pack(fill="x", pady=2)
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(frame, text="Тиснение (Emboss)",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Button(frame, text="Применить тиснение",
                   command=self.apply_emboss).pack(fill="x", pady=2)
        ttk.Button(frame, text="Открыть ядро тиснения в редакторе...",
                   command=self.app.open_emboss_in_kernel_editor).pack(
            fill="x", pady=2)
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=6)
        ttk.Label(frame, text="Медианный фильтр",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w")
        row3 = ttk.Frame(frame)
        row3.pack(fill="x", pady=2)
        ttk.Label(row3, text="Размер (нечётн.):").pack(side="left")
        ttk.Entry(row3, textvariable=self.median_var, width=6).pack(
            side="left", padx=4)
        ttk.Button(row3, text="Применить", command=self.apply_median).pack(
            side="left", padx=4)

    def _need_image(self) -> bool:
        if not self.app.image_model.has_image:
            dialogs.show_error(self.app.view.root, "Сначала откройте изображение.")
            return False
        return True

    def apply_sharpen(self) -> None:
        if not self._need_image():
            return
        s = self.strength_var.get()
        self.app.run_async("Фильтр: резкость",
                           lambda src: self.app.filters_model.sharpen(src, s),
                           f"сила {s}")

    def apply_motion(self) -> None:
        if not self._need_image():
            return
        ln, an = self.length_var.get(), self.angle_var.get()
        self.app.run_async("Фильтр: размытие в движении",
                           lambda src: self.app.filters_model.motion_blur(src, ln, an),
                           f"длина {ln}, угол {an}")

    def apply_emboss(self) -> None:
        if not self._need_image():
            return
        self.app.run_async("Фильтр: тиснение",
                           lambda src: self.app.filters_model.emboss(src),
                           "ядро emboss + bias 128")

    def apply_median(self) -> None:
        if not self._need_image():
            return
        k = self.median_var.get()
        self.app.run_async("Фильтр: медианный",
                           lambda src: self.app.filters_model.median(src, k),
                           f"ядро {k}")
