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
        # 1. Резкость
        c1 = ttk.Frame(frame, style="Card.TFrame", padding=10)
        c1.pack(fill="x", pady=(2, 8))
        ttk.Label(c1, text="Повышение резкости", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6))
        row1 = ttk.Frame(c1, style="Card.TFrame")
        row1.pack(fill="x")
        ttk.Label(row1, text="Сила (0–5):", style="Card.TLabel").pack(side="left")
        ttk.Entry(row1, textvariable=self.strength_var, width=7,
                  justify="center").pack(side="left", padx=6)
        ttk.Button(row1, text="Применить", style="Accent.TButton",
                   command=self.apply_sharpen).pack(side="right")

        # 2. Размытие в движении
        c2 = ttk.Frame(frame, style="Card.TFrame", padding=10)
        c2.pack(fill="x", pady=(0, 8))
        ttk.Label(c2, text="Размытие в движении", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6))
        row2 = ttk.Frame(c2, style="Card.TFrame")
        row2.pack(fill="x", pady=(0, 6))
        ttk.Label(row2, text="Длина:", style="Card.TLabel").pack(side="left")
        ttk.Entry(row2, textvariable=self.length_var, width=6,
                  justify="center").pack(side="left", padx=(4, 10))
        ttk.Label(row2, text="Угол (°):", style="Card.TLabel").pack(side="left")
        ttk.Entry(row2, textvariable=self.angle_var, width=6,
                  justify="center").pack(side="left", padx=4)
        ttk.Button(c2, text="Применить размытие",
                   command=self.apply_motion).pack(fill="x")

        # 3. Тиснение
        c3 = ttk.Frame(frame, style="Card.TFrame", padding=10)
        c3.pack(fill="x", pady=(0, 8))
        ttk.Label(c3, text="Тиснение (Emboss)", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6))
        ttk.Button(c3, text="Применить тиснение",
                   command=self.apply_emboss).pack(fill="x", pady=(0, 4))
        ttk.Button(c3, text="⌗ Открыть ядро тиснения в редакторе...",
                   command=self.app.open_emboss_in_kernel_editor).pack(fill="x")

        # 4. Медианный фильтр
        c4 = ttk.Frame(frame, style="Card.TFrame", padding=10)
        c4.pack(fill="x", pady=(0, 4))
        ttk.Label(c4, text="Медианный фильтр", style="Section.TLabel").pack(
            anchor="w", pady=(0, 6))
        row3 = ttk.Frame(c4, style="Card.TFrame")
        row3.pack(fill="x")
        ttk.Label(row3, text="Окно (нечётн.):", style="Card.TLabel").pack(side="left")
        ttk.Entry(row3, textvariable=self.median_var, width=7,
                  justify="center").pack(side="left", padx=6)
        ttk.Button(row3, text="Применить",
                   command=self.apply_median).pack(side="right")

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
