"""Редактор ядра свёртки: матрица коэффициентов + divisor/bias/border (View)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.convolution_model import BORDER_TITLES
from app.models.kernel_model import KERNEL_PRESETS, KernelModel


class KernelEditorView(tk.Toplevel):
    def __init__(self, parent, kernel: KernelModel, on_accept=None) -> None:
        super().__init__(parent)
        self.title("Редактор ядра свёртки")
        self.geometry("720x600")
        self.minsize(620, 480)
        self.transient(parent)
        self.grab_set()
        self.kernel = kernel
        self.on_accept = on_accept
        self._cells: list = []
        self.summary_var = tk.StringVar(value="")
        self.error_var = tk.StringVar(value="")
        self._build_top()
        self._build_mid()
        self._build_side()
        self._build_bottom()
        self._rebuild_matrix()
        self._refresh_summary()
    def _build_top(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="Строки:").pack(side="left")
        self.rows_var = tk.StringVar(value=str(self.kernel.rows))
        ttk.Spinbox(top, from_=1, to=31, width=4,
                    textvariable=self.rows_var).pack(side="left", padx=(2, 8))
        ttk.Label(top, text="Столбцы:").pack(side="left")
        self.cols_var = tk.StringVar(value=str(self.kernel.cols))
        ttk.Spinbox(top, from_=1, to=31, width=4,
                    textvariable=self.cols_var).pack(side="left", padx=(2, 8))
        ttk.Button(top, text="Применить размер",
                   command=self._apply_size).pack(side="left", padx=4)
        ttk.Label(top, text="Предустановка:").pack(side="left", padx=(10, 2))
        self.preset_names = list(KERNEL_PRESETS.keys())
        self.preset_box = ttk.Combobox(top, state="readonly", width=22)
        self.preset_box["values"] = [KERNEL_PRESETS[k][0] for k in self.preset_names]
        self.preset_box.current(0)
        self.preset_box.pack(side="left", padx=2)
        ttk.Button(top, text="Применить", command=self._apply_preset).pack(
            side="left", padx=2)

    def _build_mid(self) -> None:
        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=8, pady=4)
        mframe = ttk.Frame(mid)
        mframe.pack(side="left", fill="both", expand=True)
        self.holder = mframe
        self.mcanvas = tk.Canvas(mframe, bg="#10141b", highlightthickness=1,
                                 highlightbackground="#2c3342")
        self.mv = ttk.Scrollbar(mframe, orient="vertical", command=self.mcanvas.yview)
        self.mh = ttk.Scrollbar(mframe, orient="horizontal", command=self.mcanvas.xview)
        self.mcanvas.configure(yscrollcommand=self.mv.set, xscrollcommand=self.mh.set)
        self.mcanvas.grid(row=0, column=0, sticky="nsew")
        self.mv.grid(row=0, column=1, sticky="ns")
        self.mh.grid(row=1, column=0, sticky="ew")
        mframe.rowconfigure(0, weight=1)
        mframe.columnconfigure(0, weight=1)
        self.minner = ttk.Frame(self.mcanvas)
        self.mcanvas.create_window((0, 0), window=self.minner, anchor="nw")
        self.minner.bind("<Configure>", lambda _e: self.mcanvas.configure(
            scrollregion=self.mcanvas.bbox("all")))

    def _build_side(self) -> None:
        mid_children = self.mcanvas.master.master
        side = ttk.Frame(mid_children, width=230)
        side.pack(side="right", fill="y", padx=(8, 0))
        side.pack_propagate(False)
        ttk.Label(side, text="Делитель (divisor):").pack(anchor="w")
        self.divisor_var = tk.StringVar(value=str(self.kernel.divisor))
        ttk.Entry(side, textvariable=self.divisor_var).pack(fill="x", pady=2)
        self.auto_var = tk.BooleanVar(value=self.kernel.auto_normalize)
        ttk.Checkbutton(side, text="Автонормализация (сумма)",
                        variable=self.auto_var,
                        command=self._refresh_summary).pack(anchor="w", pady=2)
        ttk.Label(side, text="Смещение (bias):").pack(anchor="w", pady=(6, 0))
        self.bias_var = tk.StringVar(value=str(self.kernel.bias))
        ttk.Entry(side, textvariable=self.bias_var).pack(fill="x", pady=2)
        ttk.Label(side, text="Граница:").pack(anchor="w", pady=(6, 0))
        self.border_box = ttk.Combobox(side, state="readonly", width=26)
        self.border_box["values"] = list(BORDER_TITLES.values())
        order = list(BORDER_TITLES.keys())
        self.border_box.current(order.index(self.kernel.border))
        self.border_box.pack(fill="x", pady=2)
        ttk.Separator(side, orient="horizontal").pack(fill="x", pady=6)
        ttk.Button(side, text="Очистить (нули)",
                   command=self._do_clear).pack(fill="x", pady=1)
        ttk.Button(side, text="Заполнить единицами",
                   command=self._do_ones).pack(fill="x", pady=1)
        ttk.Label(side, textvariable=self.summary_var, wraplength=215).pack(
            anchor="w", pady=(8, 0))

    def _build_bottom(self) -> None:
        ttk.Label(self, textvariable=self.error_var,
                  foreground="#ff7b7b").pack(fill="x", padx=8)
        bot = ttk.Frame(self)
        bot.pack(fill="x", padx=8, pady=8)
        ttk.Button(bot, text="Применить", style="Accent.TButton",
                   command=self._accept).pack(side="right", padx=4)
        ttk.Button(bot, text="Отмена", command=self.destroy).pack(side="right")

    def _rebuild_matrix(self) -> None:
        for child in self.minner.winfo_children():
            child.destroy()
        self._cells = []
        mat = self.kernel.matrix
        for r in range(self.kernel.rows):
            row_vars = []
            for c in range(self.kernel.cols):
                var = tk.StringVar(value=f"{mat[r, c]:.6g}")
                e = ttk.Entry(self.minner, textvariable=var, width=8, justify="center")
                e.grid(row=r, column=c, padx=1, pady=1)
                var.trace_add("write", lambda *_a: self._on_cell_change())
                row_vars.append(var)
            self._cells.append(row_vars)

    def _on_cell_change(self) -> None:
        self._refresh_summary(silent=True)

    def _read_matrix(self):
        from app.utils.validators import parse_float_cell
        return [[parse_float_cell(v.get()) for v in row] for row in self._cells]

    def _apply_size(self) -> None:
        try:
            values = self._read_matrix()
            self.kernel.set_matrix(values)
            self.kernel.resize(self.rows_var.get(), self.cols_var.get())
        except ValueError as exc:
            self.error_var.set(str(exc))
            return
        self.error_var.set("")
        self.rows_var.set(str(self.kernel.rows))
        self.cols_var.set(str(self.kernel.cols))
        self._rebuild_matrix()
        self._refresh_summary()

    def _apply_preset(self) -> None:
        name = self.preset_names[self.preset_box.current()]
        try:
            self.kernel.apply_preset(name)
        except ValueError as exc:
            self.error_var.set(str(exc))
            return
        self.bias_var.set(str(self.kernel.bias))
        self.rows_var.set(str(self.kernel.rows))
        self.cols_var.set(str(self.kernel.cols))
        self._rebuild_matrix()
        self._refresh_summary()

    def _do_clear(self) -> None:
        self.kernel.clear()
        self._rebuild_matrix()
        self._refresh_summary()

    def _do_ones(self) -> None:
        self.kernel.fill_ones()
        self._rebuild_matrix()
        self._refresh_summary()

    def _refresh_summary(self, silent: bool = False) -> None:
        try:
            self.kernel.set_matrix(self._read_matrix())
        except ValueError as exc:
            if not silent:
                self.error_var.set(str(exc))
            return
        order = list(BORDER_TITLES.keys())
        try:
            self.kernel.set_border(order[self.border_box.current()])
            self.kernel.set_bias(self.bias_var.get())
            if not self.auto_var.get():
                self.kernel.set_divisor(self.divisor_var.get())
            self.kernel.set_auto_normalize(self.auto_var.get())
            d, how = self.kernel.effective_divisor()
            self.summary_var.set(
                f"Сумма: {float(self.kernel.matrix.sum()):.4g}\n"
                f"Делитель: {d:.4g} ({how})\nBias: {self.kernel.bias:.4g}\n"
                f"Граница: {self.kernel.border}")
            self.error_var.set("")
        except ValueError as exc:
            self.error_var.set(str(exc))

    def _accept(self) -> None:
        self._refresh_summary()
        if self.error_var.get():
            return
        if self.on_accept is not None:
            self.on_accept()
        self.destroy()

