"""Главное окно: тёмная тема, sidebar, параметры, 2 просмотра, история, статус."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views.history_view import HistoryPanel
from app.views.image_view import ImagePanel

BG = "#1e222c"
PANEL = "#262c38"
FG = "#e8eaf0"
ACCENT = "#3b6fd4"

CATEGORIES = [
    ("morph", "Морфология"),
    ("filters", "Фильтры"),
    ("conv", "Свёртка"),
    ("history", "История"),
]


class MainView:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Морфология изображений")
        self.root.geometry("1280x780")
        self.root.minsize(980, 620)
        self.callbacks: dict = {}
        self._build_style()
        self._build_menu()
        self._build_layout()

    def _build_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=BG, foreground=FG, fieldbackground="#161a22")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=FG,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Dim.TLabel", background=PANEL, foreground="#9aa3b5",
                        font=("Segoe UI", 9))
        style.configure("TButton", background="#333b4d", foreground=FG,
                        font=("Segoe UI", 10), padding=5)
        style.map("TButton", background=[("active", "#3f4a61"), ("disabled", "#232936")])
        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("active", "#4d82e6")])
        style.configure("TEntry", fieldbackground="#161a22", foreground=FG)
        style.configure("TCombobox", fieldbackground="#161a22", foreground=FG,
                        background="#161a22", arrowcolor=FG)
        style.configure("TSpinbox", fieldbackground="#161a22", foreground=FG,
                        background="#161a22")
        style.configure("TCheckbutton", background=PANEL, foreground=FG)
        style.configure("TRadiobutton", background=PANEL, foreground=FG)
        style.configure("Category.TButton", background=PANEL, foreground=FG,
                        font=("Segoe UI", 11), padding=8, anchor="w")
        self.root.configure(bg=BG)

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root, bg=PANEL, fg=FG, activebackground=ACCENT)
        file_menu = tk.Menu(menu, tearoff=0, bg=PANEL, fg=FG, activebackground=ACCENT)
        file_menu.add_command(label="Открыть изображение...",
                              command=lambda: self.emit("open_image"))
        file_menu.add_command(label="Сохранить результат...",
                              command=lambda: self.emit("save_image"))
        file_menu.add_separator()
        file_menu.add_command(label="Сбросить к оригиналу",
                              command=lambda: self.emit("reset_original"))
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.destroy)
        menu.add_cascade(label="Файл", menu=file_menu)
        edit = tk.Menu(menu, tearoff=0, bg=PANEL, fg=FG, activebackground=ACCENT)
        edit.add_command(label="Отменить", command=lambda: self.emit("undo"))
        edit.add_command(label="Повторить", command=lambda: self.emit("redo"))
        menu.add_cascade(label="Правка", menu=edit)
        tools = tk.Menu(menu, tearoff=0, bg=PANEL, fg=FG, activebackground=ACCENT)
        tools.add_command(label="Редактор структурного элемента...",
                          command=lambda: self.emit("open_se_editor"))
        tools.add_command(label="Редактор ядра свёртки...",
                          command=lambda: self.emit("open_kernel_editor"))
        menu.add_cascade(label="Инструменты", menu=tools)
        self.root.configure(menu=menu)
    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self.root, style="Panel.TFrame")
        toolbar.pack(fill="x", padx=6, pady=6)
        self.btn_open = ttk.Button(toolbar, text="Открыть",
                                   command=lambda: self.emit("open_image"))
        self.btn_open.pack(side="left", padx=2)
        self.btn_save = ttk.Button(toolbar, text="Сохранить",
                                   command=lambda: self.emit("save_image"))
        self.btn_save.pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        self.btn_undo = ttk.Button(toolbar, text="Отменить",
                                   command=lambda: self.emit("undo"))
        self.btn_undo.pack(side="left", padx=2)
        self.btn_redo = ttk.Button(toolbar, text="Повторить",
                                   command=lambda: self.emit("redo"))
        self.btn_redo.pack(side="left", padx=2)
        self.btn_reset = ttk.Button(toolbar, text="К оригиналу",
                                    command=lambda: self.emit("reset_original"))
        self.btn_reset.pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        self.btn_se = ttk.Button(toolbar, text="Структурный элемент...",
                                 command=lambda: self.emit("open_se_editor"))
        self.btn_se.pack(side="left", padx=2)
        self.btn_kernel = ttk.Button(toolbar, text="Ядро свёртки...",
                                     command=lambda: self.emit("open_kernel_editor"))
        self.btn_kernel.pack(side="left", padx=2)
        self.busy_label = ttk.Label(toolbar, text="", style="Dim.TLabel")
        self.busy_label.pack(side="right", padx=6)
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        sidebar = ttk.Frame(main, style="Panel.TFrame", width=190)
        sidebar.pack(side="left", fill="y", padx=(0, 6))
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="Категории", style="PanelTitle.TLabel").pack(
            anchor="w", padx=8, pady=(8, 4))
        self.category_buttons: dict = {}
        for key, title in CATEGORIES:
            b = ttk.Button(sidebar, text=title, style="Category.TButton",
                           command=lambda k=key: self.emit("category", k))
            b.pack(fill="x", padx=6, pady=2)
            self.category_buttons[key] = b
        center = ttk.Frame(main)
        center.pack(side="left", fill="both", expand=True)
        views = ttk.Frame(center, style="Panel.TFrame")
        views.pack(fill="both", expand=True)
        self.original_panel = ImagePanel(views, "Исходное изображение")
        self.original_panel.pack(side="left", fill="both", expand=True,
                                 padx=(6, 3), pady=6)
        self.result_panel = ImagePanel(views, "Результат")
        self.result_panel.pack(side="left", fill="both", expand=True,
                               padx=(3, 6), pady=6)

        right = ttk.Frame(main, style="Panel.TFrame", width=340)
        right.pack(side="left", fill="y", padx=(6, 0))
        right.pack_propagate(False)
        ttk.Label(right, text="Параметры", style="PanelTitle.TLabel").pack(
            anchor="w", padx=8, pady=(8, 2))
        outer = ttk.Frame(right, style="Panel.TFrame")
        outer.pack(fill="both", expand=True, padx=6, pady=4)
        self.params_canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        self.params_scroll = ttk.Scrollbar(outer, orient="vertical",
                                           command=self.params_canvas.yview)
        self.params_canvas.configure(yscrollcommand=self.params_scroll.set)
        self.params_canvas.pack(side="left", fill="both", expand=True)
        self.params_scroll.pack(side="right", fill="y")
        self.params_frame = ttk.Frame(self.params_canvas, style="Panel.TFrame")
        self._params_window = self.params_canvas.create_window(
            (0, 0), window=self.params_frame, anchor="nw")
        self.params_frame.bind("<Configure>", lambda _e: self.params_canvas.configure(
            scrollregion=self.params_canvas.bbox("all")))
        self.params_canvas.bind("<Configure>", lambda e: self.params_canvas.itemconfigure(
            self._params_window, width=e.width))
        self.history_panel = HistoryPanel(right, on_select=self._on_history_pick)
        self.history_panel.pack(fill="both", expand=True, padx=0, pady=(4, 0))
        self.status = ttk.Label(self.root, text="Готово. Откройте изображение.",
                                style="Dim.TLabel", anchor="w")
        self.status.pack(fill="x", padx=8, pady=(0, 6))

    def on(self, event: str, callback) -> None:
        self.callbacks[event] = callback

    def emit(self, event: str, *args):
        cb = self.callbacks.get(event)
        if cb is not None:
            cb(*args)

    def _on_history_pick(self, index: int) -> None:
        self.emit("history_jump", index)

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def set_busy(self, busy: bool, text: str = "Обработка...") -> None:
        self.busy_label.configure(text=text if busy else "")
        state = "disabled" if busy else "normal"
        for b in (self.btn_open, self.btn_save, self.btn_undo, self.btn_redo,
                  self.btn_reset, self.btn_se, self.btn_kernel):
            try:
                b.configure(state=state)
            except tk.TclError:
                pass

    def set_undo_redo(self, can_undo: bool, can_redo: bool) -> None:
        try:
            self.btn_undo.configure(state="normal" if can_undo else "disabled")
            self.btn_redo.configure(state="normal" if can_redo else "disabled")
        except tk.TclError:
            pass

    def set_category(self, key: str) -> None:
        for k, b in self.category_buttons.items():
            b.configure(style="Accent.TButton" if k == key else "Category.TButton")

    def clear_params(self):
        for child in self.params_frame.winfo_children():
            child.destroy()
        return self.params_frame

