"""Интерактивный редактор структурного элемента. Только View."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.structuring_element_model import (
    PRESET_ORDER,
    StructuringElementModel,
)


BG = "#101319"
PANEL = "#1b202b"
CARD = "#222936"
CANVAS_BG = "#0b0e13"
TEXT = "#edf1f7"
MUTED = "#929cad"
ACCENT = "#7c9cff"
ACTIVE = "#405d9b"
ANCHOR_COLOR = "#ffc857"
BORDER = "#303847"
ERROR = "#f07878"

CELL_MIN = 5
CELL_MAX = 28


class StructuringElementEditor(tk.Toplevel):
    """Редактирует копию SE и передаёт её контроллеру после подтверждения."""

    def __init__(
        self,
        parent,
        se: StructuringElementModel,
        on_accept=None,
    ) -> None:
        super().__init__(parent)

        self.title("GrayLab — структурный элемент")
        self.geometry("1100x760")
        self.minsize(820, 560)
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()

        self.se = se.copy()
        self.on_accept = on_accept
        self.tool = tk.StringVar(value="toggle")
        self.cell_size = 16
        self._eff_cell = 16
        self._rects: dict[tuple[int, int], int] = {}
        self._last_cell: tuple[int, int] | None = None

        self.width_var = tk.StringVar(value=str(self.se.width))
        self.height_var = tk.StringVar(value=str(self.se.height))
        self.preset_var = tk.StringVar()
        self.dx_var = tk.StringVar(value="1")
        self.dy_var = tk.StringVar(value="0")
        self.info_var = tk.StringVar(value="")
        self.cursor_var = tk.StringVar(value="Координаты: —")

        self._build_ui()
        self._rebuild_grid()
        self._refresh_info()

        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-Return>", lambda _event: self._accept())

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(
            self,
            style="Panel.TFrame",
            padding=(14, 12),
        )
        header.grid(
            row=0, column=0, sticky="ew", padx=12, pady=(12, 8)
        )
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="СТРУКТУРНЫЙ ЭЛЕМЕНТ",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            header,
            text="Левая кнопка мыши — редактирование ячеек",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        size_controls = ttk.Frame(
            header,
            style="Panel.TFrame",
        )
        size_controls.grid(row=0, column=1, rowspan=2, sticky="e")

        ttk.Label(
            size_controls,
            text="Ширина",
            style="Muted.TLabel",
        ).pack(side="left")

        ttk.Spinbox(
            size_controls,
            from_=1,
            to=101,
            width=5,
            textvariable=self.width_var,
        ).pack(side="left", padx=(5, 12))

        ttk.Label(
            size_controls,
            text="Высота",
            style="Muted.TLabel",
        ).pack(side="left")

        ttk.Spinbox(
            size_controls,
            from_=1,
            to=101,
            width=5,
            textvariable=self.height_var,
        ).pack(side="left", padx=(5, 8))

        ttk.Button(
            size_controls,
            text="Применить",
            command=self._apply_size,
        ).pack(side="left")

        body = ttk.Frame(self, padding=(12, 0))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        grid_panel = ttk.Frame(
            body,
            style="Panel.TFrame",
            padding=10,
        )
        grid_panel.grid(
            row=0, column=0, sticky="nsew", padx=(0, 8)
        )
        grid_panel.columnconfigure(0, weight=1)
        grid_panel.rowconfigure(1, weight=1)

        grid_header = ttk.Frame(
            grid_panel,
            style="Panel.TFrame",
        )
        grid_header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        grid_header.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(
            grid_header,
            textvariable=self.info_var,
            style="Muted.TLabel",
        )
        self.info_label.grid(row=0, column=0, sticky="w")

        zoom_controls = ttk.Frame(
            grid_header,
            style="Panel.TFrame",
        )
        zoom_controls.grid(row=0, column=1, sticky="e")

        ttk.Button(
            zoom_controls,
            text="−",
            width=3,
            command=self._zoom_out,
        ).pack(side="left", padx=2)

        self.zoom_label = ttk.Label(
            zoom_controls,
            text="16 px",
            style="Muted.TLabel",
            width=6,
            anchor="center",
        )
        self.zoom_label.pack(side="left", padx=2)

        ttk.Button(
            zoom_controls,
            text="+",
            width=3,
            command=self._zoom_in,
        ).pack(side="left", padx=2)

        canvas_holder = ttk.Frame(
            grid_panel,
            style="Panel.TFrame",
        )
        canvas_holder.grid(row=1, column=0, sticky="nsew")
        canvas_holder.rowconfigure(0, weight=1)
        canvas_holder.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_holder,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=BORDER,
            borderwidth=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vbar = ttk.Scrollbar(
            canvas_holder,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.hbar = ttk.Scrollbar(
            canvas_holder,
            orient="horizontal",
            command=self.canvas.xview,
        )
        self.hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
        )
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Motion>", self._on_hover)
        self.canvas.bind("<MouseWheel>", self._on_wheel)

        tools = ttk.Frame(
            body,
            style="Panel.TFrame",
            width=270,
            padding=12,
        )
        tools.grid(row=0, column=1, sticky="ns")
        tools.grid_propagate(False)
        tools.columnconfigure(0, weight=1)

        ttk.Label(
            tools,
            text="ИНСТРУМЕНТЫ",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Label(
            tools,
            text="Режим рисования",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w")

        for index, (value, label) in enumerate(
            (
                ("toggle", "Переключать ячейки"),
                ("draw", "Рисовать"),
                ("erase", "Стирать"),
                ("anchor", "Переместить якорь"),
            ),
            start=2,
        ):
            ttk.Radiobutton(
                tools,
                text=label,
                value=value,
                variable=self.tool,
            ).grid(
                row=index,
                column=0,
                sticky="w",
                pady=2,
            )

        ttk.Separator(tools).grid(
            row=6, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            tools,
            text="ФОРМЫ",
            style="Muted.TLabel",
        ).grid(row=7, column=0, sticky="w")

        self.preset_box = ttk.Combobox(
            tools,
            textvariable=self.preset_var,
            state="readonly",
            values=[title for _, title in PRESET_ORDER],
        )
        self.preset_box.current(0)
        self.preset_box.grid(
            row=8, column=0, sticky="ew", pady=(5, 4)
        )

        ttk.Button(
            tools,
            text="Применить форму",
            command=self._apply_preset,
        ).grid(row=9, column=0, sticky="ew")

        ttk.Separator(tools).grid(
            row=10, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            tools,
            text="МАСКА",
            style="Muted.TLabel",
        ).grid(row=11, column=0, sticky="w")

        mask_actions = ttk.Frame(
            tools,
            style="Panel.TFrame",
        )
        mask_actions.grid(
            row=12, column=0, sticky="ew", pady=(5, 3)
        )
        mask_actions.columnconfigure(0, weight=1)
        mask_actions.columnconfigure(1, weight=1)

        ttk.Button(
            mask_actions,
            text="Очистить",
            command=self._do_clear,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 3))

        ttk.Button(
            mask_actions,
            text="Заполнить",
            command=self._do_fill,
        ).grid(row=0, column=1, sticky="ew", padx=(3, 0))

        ttk.Button(
            tools,
            text="Инвертировать",
            command=self._do_invert,
        ).grid(row=13, column=0, sticky="ew", pady=3)

        ttk.Button(
            tools,
            text="Якорь в центр",
            command=self._do_center,
        ).grid(row=14, column=0, sticky="ew", pady=3)

        ttk.Separator(tools).grid(
            row=15, column=0, sticky="ew", pady=10
        )

        ttk.Label(
            tools,
            text="ПРЕОБРАЗОВАНИЯ",
            style="Muted.TLabel",
        ).grid(row=16, column=0, sticky="w")

        flips = ttk.Frame(
            tools,
            style="Panel.TFrame",
        )
        flips.grid(
            row=17, column=0, sticky="ew", pady=(5, 3)
        )
        flips.columnconfigure(0, weight=1)
        flips.columnconfigure(1, weight=1)

        ttk.Button(
            flips,
            text="Отразить ↔",
            command=self._flip_h,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 3))

        ttk.Button(
            flips,
            text="Отразить ↕",
            command=self._flip_v,
        ).grid(row=0, column=1, sticky="ew", padx=(3, 0))

        rotations = ttk.Frame(
            tools,
            style="Panel.TFrame",
        )
        rotations.grid(
            row=18, column=0, sticky="ew", pady=3
        )
        for col, angle in enumerate((90, 180, 270)):
            rotations.columnconfigure(col, weight=1)
            ttk.Button(
                rotations,
                text=f"{angle}°",
                command=lambda a=angle: self._rotate(a),
            ).grid(
                row=0,
                column=col,
                sticky="ew",
                padx=2,
            )

        ttk.Label(
            tools,
            text="Сдвиг содержимого (dx, dy)",
            style="Muted.TLabel",
        ).grid(row=19, column=0, sticky="w", pady=(9, 3))

        shift_row = ttk.Frame(
            tools,
            style="Panel.TFrame",
        )
        shift_row.grid(row=20, column=0, sticky="ew")
        shift_row.columnconfigure(0, weight=1)
        shift_row.columnconfigure(1, weight=1)

        ttk.Entry(
            shift_row,
            textvariable=self.dx_var,
            width=5,
            justify="center",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 3))

        ttk.Entry(
            shift_row,
            textvariable=self.dy_var,
            width=5,
            justify="center",
        ).grid(row=0, column=1, sticky="ew", padx=(3, 0))

        ttk.Button(
            tools,
            text="Выполнить сдвиг",
            command=self._shift,
        ).grid(row=21, column=0, sticky="ew", pady=(4, 0))

        ttk.Label(
            tools,
            textvariable=self.cursor_var,
            style="Muted.TLabel",
        ).grid(row=22, column=0, sticky="w", pady=(12, 0))

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
            text="",
            foreground=ERROR,
            background=PANEL,
        )
        self.error_label.grid(row=0, column=0, sticky="w")

        ttk.Button(
            footer,
            text="Сохранить в файл...",
            command=lambda: self.event_generate("<<SESave>>"),
        ).grid(row=0, column=1, padx=3)

        ttk.Button(
            footer,
            text="Загрузить из файла...",
            command=lambda: self.event_generate("<<SELoad>>"),
        ).grid(row=0, column=2, padx=3)

        ttk.Button(
            footer,
            text="Отмена",
            command=self.destroy,
        ).grid(row=0, column=3, padx=(12, 4))

        ttk.Button(
            footer,
            text="Применить",
            style="Accent.TButton",
            command=self._accept,
        ).grid(row=0, column=4)

    def _rebuild_grid(self) -> None:
        self.canvas.delete("all")
        self._rects.clear()

        effective_cell = self.cell_size
        max_canvas_dimension = 1800

        effective_cell = min(
            effective_cell,
            max_canvas_dimension // max(
                self.se.width, self.se.height
            ),
        )
        effective_cell = max(CELL_MIN, effective_cell)
        self._eff_cell = effective_cell

        for y in range(self.se.height):
            for x in range(self.se.width):
                x0 = x * effective_cell
                y0 = y * effective_cell

                rect = self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + effective_cell,
                    y0 + effective_cell,
                    fill=CANVAS_BG,
                    outline=BORDER,
                    width=1,
                )
                self._rects[(x, y)] = rect

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                self.se.width * effective_cell,
                self.se.height * effective_cell,
            )
        )

        self.width_var.set(str(self.se.width))
        self.height_var.set(str(self.se.height))
        self.zoom_label.configure(text=f"{effective_cell} px")

        self._paint_all()

    def _paint_all(self) -> None:
        mask = self.se.mask

        for (x, y), rect in self._rects.items():
            self.canvas.itemconfigure(
                rect,
                fill=ACTIVE if mask[y, x] else CANVAS_BG,
            )

        self._paint_anchor(*self.se.anchor)

    def _paint_anchor(self, ax: int, ay: int) -> None:
        self.canvas.delete("anchor_mark")

        cell = self._eff_cell
        inset = max(2, cell * 0.22)

        self.canvas.create_oval(
            ax * cell + inset,
            ay * cell + inset,
            (ax + 1) * cell - inset,
            (ay + 1) * cell - inset,
            fill=ANCHOR_COLOR,
            outline="#704b00",
            width=1,
            tags=("anchor_mark",),
        )

    def _paint_cell(self, x: int, y: int) -> None:
        rect = self._rects.get((x, y))
        if rect is None:
            return

        self.canvas.itemconfigure(
            rect,
            fill=ACTIVE if self.se.mask[y, x] else CANVAS_BG,
        )

        if (x, y) == self.se.anchor:
            self._paint_anchor(x, y)

    def _cell_from_event(self, event):
        cell = self._eff_cell
        x = int(self.canvas.canvasx(event.x) // cell)
        y = int(self.canvas.canvasy(event.y) // cell)

        if 0 <= x < self.se.width and 0 <= y < self.se.height:
            return x, y
        return None

    def _on_press(self, event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            return

        self._last_cell = cell
        self._apply_tool(*cell)

    def _on_drag(self, event) -> None:
        cell = self._cell_from_event(event)

        if cell is None or cell == self._last_cell:
            return

        if self.tool.get() == "anchor":
            return

        self._last_cell = cell
        self._apply_tool(*cell)

    def _on_release(self, _event=None) -> None:
        self._last_cell = None

    def _on_hover(self, event) -> None:
        cell = self._cell_from_event(event)

        if cell is None:
            self.cursor_var.set("Координаты: —")
        else:
            self.cursor_var.set(
                f"X: {cell[0]}    Y: {cell[1]}"
            )

    def _on_wheel(self, event) -> None:
        if event.state & 0x4:
            if event.delta > 0:
                self._zoom_in()
            else:
                self._zoom_out()
        else:
            self.canvas.yview_scroll(
                -1 if event.delta > 0 else 1,
                "units",
            )

    def _apply_tool(self, x: int, y: int) -> None:
        tool = self.tool.get()

        if tool == "toggle":
            self.se.toggle_cell(x, y)
        elif tool == "draw":
            self.se.set_cell(x, y, 1)
        elif tool == "erase":
            self.se.set_cell(x, y, 0)
        elif tool == "anchor":
            self.se.set_anchor(x, y)

        self._paint_cell(x, y)
        if tool == "anchor":
            self._paint_all()

        self._refresh_info()

    def _refresh_info(self) -> None:
        ax, ay = self.se.anchor
        self.info_var.set(
            f"{self.se.width} × {self.se.height}    "
            f"Активных ячеек: {self.se.active_count}    "
            f"Якорь: ({ax}, {ay})"
        )

    def _apply_size(self) -> None:
        try:
            self.se.resize(
                self.width_var.get(),
                self.height_var.get(),
            )
        except ValueError as exc:
            self.error_label.configure(text=str(exc))
            return

        self.error_label.configure(text="")
        self._rebuild_grid()
        self._refresh_info()

    def _zoom_in(self) -> None:
        self.cell_size = min(CELL_MAX, self.cell_size + 2)
        self._rebuild_grid()

    def _zoom_out(self) -> None:
        self.cell_size = max(CELL_MIN, self.cell_size - 2)
        self._rebuild_grid()

    def _apply_preset(self) -> None:
        index = self.preset_box.current()
        if not 0 <= index < len(PRESET_ORDER):
            return

        try:
            self.se.apply_preset(PRESET_ORDER[index][0])
        except ValueError as exc:
            self.error_label.configure(text=str(exc))
            return

        self.error_label.configure(text="")
        self._rebuild_grid()
        self._refresh_info()

    def _do_clear(self) -> None:
        self.se.clear()
        self._paint_all()
        self._refresh_info()

    def _do_fill(self) -> None:
        self.se.fill()
        self._paint_all()
        self._refresh_info()

    def _do_invert(self) -> None:
        self.se.invert()
        self._paint_all()
        self._refresh_info()

    def _do_center(self) -> None:
        self.se.center_anchor()
        self._paint_all()
        self._refresh_info()

    def _flip_h(self) -> None:
        self.se.flip_horizontal()
        self._paint_all()
        self._refresh_info()

    def _flip_v(self) -> None:
        self.se.flip_vertical()
        self._paint_all()
        self._refresh_info()

    def _rotate(self, angle: int) -> None:
        try:
            self.se.rotate(angle)
        except ValueError as exc:
            self.error_label.configure(text=str(exc))
            return

        self.error_label.configure(text="")
        self._rebuild_grid()
        self._refresh_info()

    def _shift(self) -> None:
        try:
            self.se.shift(
                self.dx_var.get(),
                self.dy_var.get(),
            )
        except ValueError as exc:
            self.error_label.configure(text=str(exc))
            return

        self.error_label.configure(text="")
        self._paint_all()
        self._refresh_info()

    def refresh_from_model(self) -> None:
        """Обновляется контроллером после загрузки файла."""
        self.error_label.configure(text="")
        self._rebuild_grid()
        self._refresh_info()

    def _accept(self) -> None:
        if self.se.active_count == 0:
            self.error_label.configure(
                text="Включите хотя бы одну ячейку."
            )
            return

        if self.on_accept is not None:
            self.on_accept(self.se.copy())

        self.destroy()
