"""Редактор ядра свёртки. Только View."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.convolution_model import BORDER_TITLES
from app.models.kernel_model import KERNEL_PRESETS, KernelModel
from app.utils.validators import parse_float_cell


BG = "#151a23"
PANEL = "#1b202b"
CARD = "#222936"
CANVAS_BG = "#0b0e13"
TEXT = "#edf1f7"
MUTED = "#929cad"
ACCENT = "#7c9cff"
BORDER = "#303847"
ERROR = "#f07878"


class KernelEditorView(tk.Toplevel):
    """Модальный редактор матрицы ядра и её параметров."""

    def __init__(
        self,
        parent,
        kernel: KernelModel,
        on_accept=None,
    ) -> None:
        super().__init__(parent)

        self.title("GrayLab — редактор ядра")
        self.geometry("900x680")
        self.minsize(720, 520)
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()

        self._target = kernel
        self.kernel = kernel.copy()
        self.on_accept = on_accept
        self._cells: list[list[tk.StringVar]] = []
        self._syncing = False

        self.rows_var = tk.StringVar(value=str(self.kernel.rows))
        self.cols_var = tk.StringVar(value=str(self.kernel.cols))
        self.divisor_var = tk.StringVar(value=str(self.kernel.divisor))
        self.bias_var = tk.StringVar(value=str(self.kernel.bias))
        self.auto_var = tk.BooleanVar(
            value=self.kernel.auto_normalize
        )
        self.summary_var = tk.StringVar(value="")
        self.error_var = tk.StringVar(value="")

        self._build_ui()
        self._rebuild_matrix()
        self._refresh_summary()

        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-Return>", lambda _event: self._accept())

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Panel.TFrame", padding=14)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="ЯДРО СВЁРТКИ",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Настройте коэффициенты и параметры фильтра",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        body = ttk.Frame(self, padding=(12, 0))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        matrix_panel = ttk.Frame(
            body,
            style="Panel.TFrame",
            padding=12,
        )
        matrix_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        matrix_panel.columnconfigure(0, weight=1)
        matrix_panel.rowconfigure(2, weight=1)

        ttk.Label(
            matrix_panel,
            text="Матрица коэффициентов",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        size_row = ttk.Frame(
            matrix_panel,
            style="Panel.TFrame",
        )
        size_row.grid(row=1, column=0, sticky="ew", pady=(10, 10))

        ttk.Label(
            size_row,
            text="Строки",
            style="Muted.TLabel",
        ).pack(side="left")

        ttk.Spinbox(
            size_row,
            from_=1,
            to=31,
            width=4,
            textvariable=self.rows_var,
        ).pack(side="left", padx=(5, 12))

        ttk.Label(
            size_row,
            text="Столбцы",
            style="Muted.TLabel",
        ).pack(side="left")

        ttk.Spinbox(
            size_row,
            from_=1,
            to=31,
            width=4,
            textvariable=self.cols_var,
        ).pack(side="left", padx=5)

        ttk.Button(
            size_row,
            text="Изменить размер",
            command=self._apply_size,
        ).pack(side="right")

        grid_holder = ttk.Frame(
            matrix_panel,
            style="Panel.TFrame",
        )
        grid_holder.grid(row=2, column=0, sticky="nsew")
        grid_holder.rowconfigure(0, weight=1)
        grid_holder.columnconfigure(0, weight=1)

        self.mcanvas = tk.Canvas(
            grid_holder,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=BORDER,
            borderwidth=0,
        )
        self.mcanvas.grid(row=0, column=0, sticky="nsew")

        self.mscroll_y = ttk.Scrollbar(
            grid_holder,
            orient="vertical",
            command=self.mcanvas.yview,
        )
        self.mscroll_y.grid(row=0, column=1, sticky="ns")

        self.mscroll_x = ttk.Scrollbar(
            grid_holder,
            orient="horizontal",
            command=self.mcanvas.xview,
        )
        self.mscroll_x.grid(row=1, column=0, sticky="ew")

        self.mcanvas.configure(
            yscrollcommand=self.mscroll_y.set,
            xscrollcommand=self.mscroll_x.set,
        )

        self.minner = ttk.Frame(
            self.mcanvas,
            style="Panel.TFrame",
        )
        self._matrix_window = self.mcanvas.create_window(
            (8, 8),
            window=self.minner,
            anchor="nw",
        )
        self.minner.bind(
            "<Configure>",
            lambda _event: self.mcanvas.configure(
                scrollregion=self.mcanvas.bbox("all")
            ),
        )

        settings = ttk.Frame(
            body,
            style="Panel.TFrame",
            width=260,
            padding=12,
        )
        settings.grid(row=0, column=1, sticky="ns")
        settings.grid_propagate(False)
        settings.columnconfigure(0, weight=1)

        ttk.Label(
            settings,
            text="ПАРАМЕТРЫ",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        self._section_label(settings, "Предустановка", 1)

        self.preset_names = list(KERNEL_PRESETS.keys())
        self.preset_box = ttk.Combobox(
            settings,
            state="readonly",
            values=[
                KERNEL_PRESETS[name][0]
                for name in self.preset_names
            ],
        )
        self.preset_box.current(0)
        self.preset_box.grid(
            row=2, column=0, sticky="ew", pady=(4, 5)
        )

        ttk.Button(
            settings,
            text="Применить шаблон",
            command=self._apply_preset,
        ).grid(row=3, column=0, sticky="ew", pady=(0, 14))

        self._section_label(settings, "Нормализация", 4)

        ttk.Label(
            settings,
            text="Делитель",
            style="Muted.TLabel",
        ).grid(row=5, column=0, sticky="w", pady=(7, 2))

        self.divisor_entry = ttk.Entry(
            settings,
            textvariable=self.divisor_var,
        )
        self.divisor_entry.grid(row=6, column=0, sticky="ew")

        ttk.Checkbutton(
            settings,
            text="Автоматический делитель",
            variable=self.auto_var,
            command=self._refresh_summary,
        ).grid(row=7, column=0, sticky="w", pady=(6, 0))

        self._section_label(settings, "Дополнительные настройки", 8)

        ttk.Label(
            settings,
            text="Смещение (bias)",
            style="Muted.TLabel",
        ).grid(row=9, column=0, sticky="w", pady=(7, 2))

        ttk.Entry(
            settings,
            textvariable=self.bias_var,
        ).grid(row=10, column=0, sticky="ew")

        ttk.Label(
            settings,
            text="Обработка границ",
            style="Muted.TLabel",
        ).grid(row=11, column=0, sticky="w", pady=(10, 2))

        self.border_keys = list(BORDER_TITLES.keys())
        self.border_box = ttk.Combobox(
            settings,
            state="readonly",
            values=[
                BORDER_TITLES[key]
                for key in self.border_keys
            ],
        )
        self.border_box.current(
            self.border_keys.index(self.kernel.border)
        )
        self.border_box.grid(
            row=12, column=0, sticky="ew"
        )

        ttk.Separator(settings).grid(
            row=13, column=0, sticky="ew", pady=12
        )

        ttk.Label(
            settings,
            text="Сводка",
            style="Muted.TLabel",
        ).grid(row=14, column=0, sticky="w")

        ttk.Label(
            settings,
            textvariable=self.summary_var,
            style="Card.TLabel",
            wraplength=225,
            justify="left",
        ).grid(row=15, column=0, sticky="ew", pady=(5, 10))

        actions = ttk.Frame(
            settings,
            style="Panel.TFrame",
        )
        actions.grid(row=16, column=0, sticky="ew", pady=(4, 0))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        ttk.Button(
            actions,
            text="Обнулить",
            command=self._do_clear,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 3))

        ttk.Button(
            actions,
            text="Единицы",
            command=self._do_ones,
        ).grid(row=0, column=1, sticky="ew", padx=(3, 0))

        footer = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=(12, 9),
        )
        footer.grid(
            row=2, column=0, sticky="ew", padx=12, pady=12
        )
        footer.columnconfigure(0, weight=1)

        self.error_label = ttk.Label(
            footer,
            textvariable=self.error_var,
            foreground=ERROR,
            background="#1b202b",
            wraplength=500,
        )
        self.error_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer,
            text="Отмена",
            command=self.destroy,
        ).grid(row=0, column=1, padx=(8, 4))

        ttk.Button(
            footer,
            text="Применить",
            style="Accent.TButton",
            command=self._accept,
        ).grid(row=0, column=2)

    @staticmethod
    def _section_label(parent, text: str, row: int) -> None:
        ttk.Label(
            parent,
            text=text.upper(),
            style="Muted.TLabel",
        ).grid(row=row, column=0, sticky="w")

    def _rebuild_matrix(self) -> None:
        for child in self.minner.winfo_children():
            child.destroy()

        self._cells = []
        matrix = self.kernel.matrix

        for row in range(self.kernel.rows):
            row_vars = []

            for col in range(self.kernel.cols):
                variable = tk.StringVar(
                    value=f"{matrix[row, col]:.6g}"
                )
                entry = ttk.Entry(
                    self.minner,
                    textvariable=variable,
                    width=8,
                    justify="center",
                )
                entry.grid(
                    row=row,
                    column=col,
                    padx=2,
                    pady=2,
                    ipady=3,
                )
                variable.trace_add(
                    "write",
                    lambda *_args: self._refresh_summary(silent=True),
                )
                row_vars.append(variable)

            self._cells.append(row_vars)

        self._refresh_summary(silent=True)

    def _read_matrix(self):
        return [
            [parse_float_cell(cell.get()) for cell in row]
            for row in self._cells
        ]

    def _apply_size(self) -> None:
        try:
            matrix = self._read_matrix()
            self.kernel.set_matrix(matrix)
            self.kernel.resize(
                self.rows_var.get(),
                self.cols_var.get(),
            )
        except ValueError as exc:
            self.error_var.set(str(exc))
            return

        self.rows_var.set(str(self.kernel.rows))
        self.cols_var.set(str(self.kernel.cols))
        self.error_var.set("")
        self._rebuild_matrix()
        self._refresh_summary()

    def _apply_preset(self) -> None:
        index = self.preset_box.current()
        if not 0 <= index < len(self.preset_names):
            return

        name = self.preset_names[index]

        try:
            self.kernel.apply_preset(name)
        except ValueError as exc:
            self.error_var.set(str(exc))
            return

        self.rows_var.set(str(self.kernel.rows))
        self.cols_var.set(str(self.kernel.cols))
        self.bias_var.set(str(self.kernel.bias))
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
        if self._syncing:
            return

        try:
            matrix = self._read_matrix()
            self.kernel.set_matrix(matrix)

            border_index = self.border_box.current()
            if border_index < 0:
                border_index = 0
            self.kernel.set_border(self.border_keys[border_index])

            self.kernel.set_bias(self.bias_var.get())
            self.kernel.set_auto_normalize(self.auto_var.get())

            if not self.auto_var.get():
                self.kernel.set_divisor(self.divisor_var.get())

            divisor, method = self.kernel.effective_divisor()

            self.summary_var.set(
                f"Размер: {self.kernel.rows} × {self.kernel.cols}\n"
                f"Сумма коэффициентов: {self.kernel.matrix.sum():.5g}\n"
                f"Делитель: {divisor:.5g}\n"
                f"Режим: {method}\n"
                f"Bias: {self.kernel.bias:.5g}"
            )
            self.error_var.set("")

        except ValueError as exc:
            if not silent:
                self.error_var.set(str(exc))

    def _copy_to_target(self) -> None:
        """Перенести проверенные настройки в исходную модель."""
        self._target.set_matrix(self.kernel.matrix)
        self._target.set_auto_normalize(self.kernel.auto_normalize)
        self._target.set_divisor(self.kernel.divisor)
        self._target.set_bias(self.kernel.bias)
        self._target.set_border(self.kernel.border)

    def _accept(self) -> None:
        self._refresh_summary()

        if self.error_var.get():
            return

        try:
            self._copy_to_target()
        except ValueError as exc:
            self.error_var.set(str(exc))
            return

        if self.on_accept is not None:
            self.on_accept()

        self.destroy()
