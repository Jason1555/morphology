"""Редактор структурного элемента: Canvas-сетка, якорь, пресеты (только View)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.models.structuring_element_model import PRESET_ORDER, StructuringElementModel

CELL_MIN, CELL_MAX = 4, 28


class StructuringElementEditor(tk.Toplevel):
    """Диалог редактирования SE. Работает с копией модели; результат через on_accept."""

    def __init__(self, parent, se: StructuringElementModel, on_accept=None) -> None:
        super().__init__(parent)
        self.title("Редактор структурного элемента")
        self.geometry("980x680")
        self.minsize(800, 540)
        self.configure(bg="#141821")
        self.transient(parent)
        self.grab_set()
        self.se = se.copy()
        self.on_accept = on_accept
        self.tool = tk.StringVar(value="toggle")
        self.cell_size = 18
        self._rects: dict = {}
        self._build_top()
        self._build_middle()
        self._build_bottom()
        self._rebuild_grid()
        self._refresh_info()

    def _build_top(self) -> None:
        top = ttk.Frame(self, padding=(12, 10))
        top.configure(style="Panel.TFrame")
        top.pack(fill="x", padx=10, pady=(10, 4))
        ttk.Label(top, text="Ширина:").pack(side="left")
        self.width_var = tk.StringVar(value=str(self.se.width))
        ttk.Spinbox(top, from_=1, to=101, width=5, textvariable=self.width_var).pack(
            side="left", padx=(4, 10))
        ttk.Label(top, text="Высота:").pack(side="left")
        self.height_var = tk.StringVar(value=str(self.se.height))
        ttk.Spinbox(top, from_=1, to=101, width=5, textvariable=self.height_var).pack(
            side="left", padx=(4, 10))
        ttk.Button(top, text="Применить размер", command=self._apply_size).pack(
            side="left", padx=4)
        ttk.Label(top, text="Масштаб:").pack(side="left", padx=(12, 4))
        ttk.Button(top, text="−", width=3, command=self._zoom_out).pack(side="left", padx=1)
        ttk.Button(top, text="+", width=3, command=self._zoom_in).pack(side="left", padx=1)
        self.info_var = tk.StringVar(value="")
        info = ttk.Label(self, textvariable=self.info_var)
        info.configure(style="Dim.TLabel")
        info.pack(fill="x", padx=14, pady=(0, 4))

    def _build_middle(self) -> None:
        mid = ttk.Frame(self)
        mid.configure(style="Panel.TFrame")
        mid.pack(fill="both", expand=True, padx=10, pady=4)
        cframe = ttk.Frame(mid)
        cframe.configure(style="Panel.TFrame")
        cframe.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(cframe, bg="#10141c", highlightthickness=1,
                                highlightbackground="#2f394d")
        self.vbar = ttk.Scrollbar(cframe, orient="vertical", command=self.canvas.yview)
        self.hbar = ttk.Scrollbar(cframe, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        cframe.rowconfigure(0, weight=1)
        cframe.columnconfigure(0, weight=1)
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<Motion>", self._on_hover)
        side = ttk.Frame(mid, width=260)
        side.configure(style="Card.TFrame")
        side.pack(side="right", fill="y", padx=(10, 0))
        side.pack_propagate(False)
        self.side = side
        ttk.Label(side, text="Инструмент рисования:", style="Section.TLabel").pack(anchor="w", pady=(8, 4))
        for val, txt in (("toggle", "Переключение"), ("draw", "Рисование"),
                         ("erase", "Стирание"), ("anchor", "Якорь")):
            ttk.Radiobutton(side, text=txt, value=val, variable=self.tool).pack(
                anchor="w", padx=10)
        ttk.Separator(side, orient="horizontal").pack(fill="x", padx=10, pady=8)
        ttk.Label(side, text="Предустановка:", style="CardDim.TLabel").pack(
            anchor="w", padx=10)
        self.preset_var = tk.StringVar()
        self.preset_box = ttk.Combobox(side, textvariable=self.preset_var,
                                       state="readonly", width=26)
        self.preset_box["values"] = [t for _, t in PRESET_ORDER]
        self.preset_box.current(0)
        self.preset_box.pack(fill="x", padx=10, pady=2)
        ttk.Button(side, text="Применить форму", command=self._apply_preset).pack(
            fill="x", padx=10, pady=2)
        ttk.Separator(side, orient="horizontal").pack(fill="x", padx=10, pady=8)
        row1 = ttk.Frame(side, style="Card.TFrame")
        row1.pack(fill="x", padx=10, pady=1)
        ttk.Button(row1, text="Очистить", command=self._do_clear).pack(
            side="left", fill="x", expand=True, padx=1)
        ttk.Button(row1, text="Заполнить", command=self._do_fill).pack(
            side="left", fill="x", expand=True, padx=1)
        ttk.Button(side, text="Инвертировать", command=self._do_invert).pack(
            fill="x", padx=10, pady=1)
        ttk.Button(side, text="Якорь в центр", command=self._do_center).pack(
            fill="x", padx=10, pady=1)
        ttk.Separator(side, orient="horizontal").pack(fill="x", padx=10, pady=8)
        ttk.Label(side, text="Отразить / повернуть:", style="CardDim.TLabel").pack(
            anchor="w", padx=10)
        row2 = ttk.Frame(side, style="Card.TFrame")
        row2.pack(fill="x", padx=10, pady=1)
        ttk.Button(row2, text="Зеркало ↔", command=self._flip_h).pack(
            side="left", fill="x", expand=True, padx=1)
        ttk.Button(row2, text="Зеркало ↕", command=self._flip_v).pack(
            side="left", fill="x", expand=True, padx=1)
        row3 = ttk.Frame(side, style="Card.TFrame")
        row3.pack(fill="x", padx=10, pady=1)
        for ang in (90, 180, 270):
            ttk.Button(row3, text=f"{ang}°",
                       command=lambda a=ang: self._rotate(a)).pack(
                side="left", fill="x", expand=True, padx=1)
        ttk.Separator(side, orient="horizontal").pack(fill="x", padx=10, pady=8)
        ttk.Label(side, text="Сдвиг (dx, dy):", style="CardDim.TLabel").pack(
            anchor="w", padx=10)
        srow = ttk.Frame(side, style="Card.TFrame")
        srow.pack(fill="x", padx=10, pady=2)
        self.dx_var = tk.StringVar(value="1")
        self.dy_var = tk.StringVar(value="0")
        ttk.Entry(srow, textvariable=self.dx_var, width=6).pack(side="left", padx=1)
        ttk.Entry(srow, textvariable=self.dy_var, width=6).pack(side="left", padx=1)
        ttk.Button(srow, text="Сдвинуть", command=self._shift).pack(side="left", padx=2)
        ttk.Separator(side, orient="horizontal").pack(fill="x", padx=10, pady=8)
        ttk.Button(side, text="Сохранить в файл...",
                   command=lambda: self.event_generate("<<SESave>>")).pack(
            fill="x", padx=10, pady=1)
        ttk.Button(side, text="Загрузить из файла...",
                   command=lambda: self.event_generate("<<SELoad>>")).pack(
            fill="x", padx=10, pady=1)
        self.cursor_var = tk.StringVar(value="Курсор: —")
        cur = ttk.Label(side, textvariable=self.cursor_var)
        cur.configure(style="CardDim.TLabel")
        cur.pack(anchor="w", padx=10, pady=(8, 10))

    def _build_bottom(self) -> None:
        bot = ttk.Frame(self, padding=(12, 8))
        bot.configure(style="Panel.TFrame")
        bot.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(bot, text="OK", style="Accent.TButton",
                   command=self._accept).pack(side="right", padx=4)
        ttk.Button(bot, text="Отмена", command=self.destroy).pack(side="right")
    # --- отрисовка сетки на Canvas (без виджетов на ячейку) ---
    def _rebuild_grid(self) -> None:
        self.canvas.delete("all")
        self._rects = {}
        # Адаптивная клетка: интерфейс не раздувается даже на 101×101.
        eff = self.cell_size
        for dim in (self.se.width, self.se.height):
            if dim * eff > 1600:
                eff = max(4, 1600 // dim)
        self._eff_cell = eff
        for y in range(self.se.height):
            for x in range(self.se.width):
                x0, y0 = x * eff, y * eff
                r = self.canvas.create_rectangle(x0, y0, x0 + eff, y0 + eff,
                                                 outline="#2f394d", width=1)
                self._rects[(x, y)] = r
        self.canvas.configure(scrollregion=(0, 0, self.se.width * eff, self.se.height * eff))
        self._paint_all()
        self.width_var.set(str(self.se.width))
        self.height_var.set(str(self.se.height))

    def _paint_all(self) -> None:
        mask = self.se.mask
        ax, ay = self.se.anchor
        for (x, y), r in self._rects.items():
            fill = "#4f8cff" if mask[y, x] else "#1c2331"
            self.canvas.itemconfigure(r, fill=fill)
        self._paint_anchor(ax, ay)

    def _paint_cell(self, x: int, y: int) -> None:
        r = self._rects.get((x, y))
        if r is None:
            return
        fill = "#4f8cff" if self.se.mask[y, x] else "#1c2331"
        self.canvas.itemconfigure(r, fill=fill)
        if (x, y) == self.se.anchor:
            self._paint_anchor(x, y)

    def _paint_anchor(self, ax: int, ay: int) -> None:
        self.canvas.delete("anchor_mark")
        s = getattr(self, "_eff_cell", self.cell_size)
        self.canvas.create_oval(ax * s + s * 0.2, ay * s + s * 0.2,
                                ax * s + s * 0.8, ay * s + s * 0.8,
                                fill="#ffca3a", outline="#8a6100",
                                tags=("anchor_mark",))

    def _cell_from_event(self, event) -> tuple[int, int] | None:
        s = getattr(self, "_eff_cell", self.cell_size)
        x = int(self.canvas.canvasx(event.x) // s)
        y = int(self.canvas.canvasy(event.y) // s)
        if 0 <= x < self.se.width and 0 <= y < self.se.height:
            return x, y
        return None

    def _on_press(self, event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            return
        self._apply_tool(*cell)
        self._last_cell = cell

    def _on_drag(self, event) -> None:
        cell = self._cell_from_event(event)
        if cell is None or getattr(self, "_last_cell", None) == cell:
            return
        if self.tool.get() == "anchor":
            return
        self._apply_tool(*cell)
        self._last_cell = cell

    def _on_hover(self, event) -> None:
        cell = self._cell_from_event(event)
        if cell is None:
            self.cursor_var.set("Курсор: —")
        else:
            self.cursor_var.set(f"Курсор: ({cell[0]}, {cell[1]})")

    def _apply_tool(self, x: int, y: int) -> None:
        t = self.tool.get()
        if t == "toggle":
            self.se.toggle_cell(x, y)
            self._paint_cell(x, y)
        elif t == "draw":
            self.se.set_cell(x, y, 1)
            self._paint_cell(x, y)
        elif t == "erase":
            self.se.set_cell(x, y, 0)
            self._paint_cell(x, y)
        elif t == "anchor":
            self.se.set_anchor(x, y)
            self._paint_all()
        self._refresh_info()

    def _refresh_info(self) -> None:
        ax, ay = self.se.anchor
        self.info_var.set(f"Размер: {self.se.width}×{self.se.height}   "
                          f"Активных ячеек: {self.se.active_count}   "
                          f"Якорь: ({ax}, {ay})")

    # --- действия (View только меняет копию модели и перерисовывает) ---
    def _apply_size(self) -> None:
        try:
            self.se.resize(self.width_var.get(), self.height_var.get())
        except ValueError as exc:
            self.info_var.set(f"Ошибка размера: {exc}")
            return
        self._rebuild_grid()
        self._refresh_info()

    def _zoom_in(self) -> None:
        self.cell_size = min(self.cell_size + 2, CELL_MAX)
        self._rebuild_grid()

    def _zoom_out(self) -> None:
        self.cell_size = max(self.cell_size - 2, CELL_MIN)
        self._rebuild_grid()

    def _apply_preset(self) -> None:
        idx = self.preset_box.current()
        if idx < 0:
            return
        name = PRESET_ORDER[idx][0]
        try:
            self.se.apply_preset(name)
        except ValueError as exc:
            self.info_var.set(f"Ошибка: {exc}")
            return
        self._paint_all()
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
            self.info_var.set(f"Ошибка: {exc}")
            return
        self._rebuild_grid()
        self._refresh_info()

    def _shift(self) -> None:
        try:
            self.se.shift(self.dx_var.get(), self.dy_var.get())
        except ValueError as exc:
            self.info_var.set(f"Ошибка сдвига: {exc}")
            return
        self._paint_all()
        self._refresh_info()

    def refresh_from_model(self) -> None:
        self._rebuild_grid()
        self._refresh_info()

    def _accept(self) -> None:
        if self.on_accept is not None:
            self.on_accept(self.se.copy())
        self.destroy()

