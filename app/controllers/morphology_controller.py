"""Контроллер морфологии: параметры View -> вызов MorphologyModel."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.morphology_model import MORPH_OPS
from app.models.structuring_element_model import PRESET_ORDER
from app.views import dialogs


class MorphologyController:
    def __init__(self, app) -> None:
        self.app = app
        self.width_var = tk.StringVar(value="3")
        self.height_var = tk.StringVar(value="3")
        self.ax_var = tk.StringVar(value="1")
        self.ay_var = tk.StringVar(value="1")
        self.iter_var = tk.StringVar(value="1")
        self._preset_names = [n for n, _ in PRESET_ORDER]
        self._preset_titles = {n: t for n, t in PRESET_ORDER}
        self._op_titles = {k: t for k, t in MORPH_OPS}

    def build_panel(self, frame) -> None:
        ttk.Label(frame, text="Операция:").pack(anchor="w", pady=(6, 0))
        self.op_box = ttk.Combobox(frame, state="readonly", width=30,
                                   values=[t for _, t in MORPH_OPS])
        self.op_box.current(0)
        self.op_box.pack(fill="x", pady=2)
        ttk.Label(frame, text="Форма элемента:").pack(anchor="w", pady=(6, 0))
        self.preset_box = ttk.Combobox(frame, state="readonly", width=30,
                                       values=[t for _, t in PRESET_ORDER])
        self.preset_box.current(3)
        self.preset_box.pack(fill="x", pady=2)
        ttk.Button(frame, text="Применить форму к редактору",
                   command=self._use_preset).pack(fill="x", pady=2)
        ttk.Button(frame, text="Открыть редактор элемента...",
                   command=self.app.open_se_editor).pack(fill="x", pady=2)
        size_row = ttk.Frame(frame)
        size_row.pack(fill="x", pady=(6, 0))
        ttk.Label(size_row, text="W:").pack(side="left")
        ttk.Entry(size_row, textvariable=self.width_var, width=5).pack(
            side="left", padx=(2, 6))
        ttk.Label(size_row, text="H:").pack(side="left")
        ttk.Entry(size_row, textvariable=self.height_var, width=5).pack(
            side="left", padx=(2, 6))
        ttk.Button(size_row, text="Размер", command=self._apply_size).pack(
            side="left", padx=2)
        anch_row = ttk.Frame(frame)
        anch_row.pack(fill="x", pady=(4, 0))
        ttk.Label(anch_row, text="Якорь X:").pack(side="left")
        ttk.Entry(anch_row, textvariable=self.ax_var, width=5).pack(
            side="left", padx=(2, 6))
        ttk.Label(anch_row, text="Y:").pack(side="left")
        ttk.Entry(anch_row, textvariable=self.ay_var, width=5).pack(
            side="left", padx=(2, 6))
        ttk.Button(anch_row, text="Якорь", command=self._apply_anchor).pack(
            side="left", padx=2)
        ttk.Button(frame, text="Якорь в центр",
                   command=self._center_anchor).pack(fill="x", pady=2)
        ttk.Label(frame, text="Итерации (эрозия/дилатация):").pack(
            anchor="w", pady=(6, 0))
        ttk.Spinbox(frame, from_=1, to=100, width=6,
                    textvariable=self.iter_var).pack(anchor="w", pady=2)
        self.se_info = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.se_info, wraplength=300).pack(
            anchor="w", pady=(6, 2))
        ttk.Button(frame, text="Применить операцию", style="Accent.TButton",
                   command=self.apply_operation).pack(fill="x", pady=6)
        self.sync_se_fields()
    def sync_se_fields(self) -> None:
        se = self.app.se_model
        for var, val in ((self.width_var, se.width), (self.height_var, se.height),
                         (self.ax_var, se.anchor[0]), (self.ay_var, se.anchor[1])):
            try:
                var.set(str(val))
            except tk.TclError:
                pass
        try:
            self.se_info.set(f"Элемент: {se.width}×{se.height}, "
                             f"активных: {se.active_count}, якорь: {se.anchor}")
        except tk.TclError:
            pass

    def _use_preset(self) -> None:
        try:
            name = self._preset_names[self.preset_box.current()]
            self.app.se_model.apply_preset(name)
            self.app.se_model.center_anchor()
        except (ValueError, IndexError) as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.sync_se_fields()
        self.app.view.set_status(
            f"Форма '{self._preset_titles.get(name, name)}' применена к элементу.")

    def _apply_size(self) -> None:
        try:
            self.app.se_model.resize(self.width_var.get(), self.height_var.get())
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.sync_se_fields()

    def _apply_anchor(self) -> None:
        try:
            self.app.se_model.set_anchor(self.ax_var.get(), self.ay_var.get())
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.sync_se_fields()

    def _center_anchor(self) -> None:
        self.app.se_model.center_anchor()
        self.sync_se_fields()

    def apply_operation(self) -> None:
        if not self.app.image_model.has_image:
            dialogs.show_error(self.app.view.root, "Сначала откройте изображение.")
            return
        op_keys = [k for k, _ in MORPH_OPS]
        cur = self.op_box.current()
        op = op_keys[cur] if 0 <= cur < len(op_keys) else "erosion"
        se = self.app.se_model
        desc = (f"SE {se.width}×{se.height}, якорь {se.anchor}, "
                f"итераций {self.iter_var.get()}")
        self.app.run_async(
            f"Морфология: {self._op_titles.get(op, op)}",
            lambda src: self.app.morph_model.apply(src, op, se, self.iter_var.get()),
            desc)

