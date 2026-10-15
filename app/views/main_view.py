"""Главное окно: тёмная тема, sidebar, параметры, 2 просмотра, история, статус."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views.history_view import HistoryPanel
from app.views.image_view import ImagePanel

BG = "#141821"
PANEL = "#1d2330"
CARD = "#242c3d"
SURFACE = "#10141c"
BORDER = "#2f394d"
FG = "#eef2f8"
MUTED = "#94a0b8"
ACCENT = "#4f8cff"
ACCENT_HOVER = "#6aa0ff"
BTN_BG = "#2a3346"
BTN_HOVER = "#364259"

CATEGORIES = [
    ("morph", "❖  Морфология"),
    ("filters", "✦  Фильтры"),
    ("conv", "⊞  Свёртка"),
    ("history", "🕘  История"),
]


class MainView:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Морфология и фильтрация")
        self.root.geometry("1340x820")
        self.root.minsize(1020, 640)
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
        self.root.option_add("*TCombobox*Listbox.background", SURFACE)
        self.root.option_add("*TCombobox*Listbox.foreground", FG)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        style.configure(".", background=BG, foreground=FG, fieldbackground=SURFACE)
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=CARD, foreground=FG)
        style.configure("CardDim.TLabel", background=CARD, foreground=MUTED)
        style.configure("PanelTitle.TLabel", background=PANEL, foreground=FG,
                        font=("Segoe UI", 11, "bold"))
        style.configure("Section.TLabel", background=CARD, foreground="#dbe4f5",
                        font=("Segoe UI", 10, "bold"))
        style.configure("Dim.TLabel", background=PANEL, foreground=MUTED,
                        font=("Segoe UI", 9))
        style.configure("Badge.TLabel", background=CARD, foreground=MUTED,
                        font=("Segoe UI", 9))
        style.configure("TButton", background=BTN_BG, foreground=FG,
                        font=("Segoe UI", 10), padding=(10, 6))
        style.map("TButton", background=[("active", BTN_HOVER), ("disabled", "#1b202c")])
        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(12, 7))
        style.configure("Small.TButton", background=BTN_BG, foreground=FG,
                        font=("Segoe UI", 9), padding=(6, 3))
        style.configure("TEntry", fieldbackground=SURFACE, foreground=FG)
        style.configure("TCombobox", fieldbackground=SURFACE, foreground=FG,
                        background=BTN_BG, arrowcolor=FG)
        style.configure("TSpinbox", fieldbackground=SURFACE, foreground=FG,
                        background=BTN_BG)
        style.configure("TCheckbutton", background=CARD, foreground=FG)
        style.configure("TRadiobutton", background=CARD, foreground=FG)
        style.configure("Category.TButton", background=PANEL, foreground=MUTED,
                        font=("Segoe UI", 10), padding=(12, 9), anchor="w")
        style.configure("CategoryActive.TButton", background=ACCENT, foreground="white",
                        font=("Segoe UI", 10, "bold"), padding=(12, 9), anchor="w")
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
        toolbar = ttk.Frame(self.root, padding=(10, 7))
        toolbar.configure(style="Panel.TFrame")
        toolbar.pack(fill="x", padx=10, pady=(8, 6))
        self.btn_open = ttk.Button(toolbar, text="📂 Открыть", style="Accent.TButton",
                                   command=lambda: self.emit("open_image"))
        self.btn_open.pack(side="left", padx=(0, 4))
        self.btn_save = ttk.Button(toolbar, text="💾 Сохранить",
                                   command=lambda: self.emit("save_image"))
        self.btn_save.pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        self.btn_undo = ttk.Button(toolbar, text="↶ Отменить",
                                   command=lambda: self.emit("undo"))
        self.btn_undo.pack(side="left", padx=2)
        self.btn_redo = ttk.Button(toolbar, text="↷ Повторить",
                                   command=lambda: self.emit("redo"))
        self.btn_redo.pack(side="left", padx=2)
        self.btn_reset = ttk.Button(toolbar, text="↺ К оригиналу",
                                    command=lambda: self.emit("reset_original"))
        self.btn_reset.pack(side="left", padx=2)
        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=6)
        self.btn_se = ttk.Button(toolbar, text="⊞ Элемент...",
                                 command=lambda: self.emit("open_se_editor"))
        self.btn_se.pack(side="left", padx=2)
        self.btn_kernel = ttk.Button(toolbar, text="⌗ Ядро...",
                                     command=lambda: self.emit("open_kernel_editor"))
        self.btn_kernel.pack(side="left", padx=2)
        self.busy_label = ttk.Label(toolbar, text="", style="Dim.TLabel")
        self.busy_label.pack(side="right", padx=6)
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        sidebar = ttk.Frame(main, width=200)
        sidebar.configure(style="Panel.TFrame")
        sidebar.pack(side="left", fill="y", padx=(0, 6))
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="РЕЖИМЫ РАБОТЫ", style="Dim.TLabel").pack(
            anchor="w", padx=14, pady=(14, 6))
        self.category_buttons: dict = {}
        for key, title in CATEGORIES:
            b = ttk.Button(sidebar, text=title, style="Category.TButton",
                           command=lambda k=key: self.emit("category", k))
            b.pack(fill="x", padx=8, pady=3)
            self.category_buttons[key] = b
        center = ttk.Frame(main)
        center.pack(side="left", fill="both", expand=True)
        views = ttk.Frame(center)
        views.configure(style="Panel.TFrame")
        views.pack(fill="both", expand=True)
        self.original_panel = ImagePanel(views, "Исходное изображение")
        self.original_panel.pack(side="left", fill="both", expand=True,
                                 padx=(6, 3), pady=6)
        self.result_panel = ImagePanel(views, "Результат обработки")
        self.result_panel.pack(side="left", fill="both", expand=True,
                               padx=(3, 6), pady=6)

        right = ttk.Frame(main, width=360)
        right.configure(style="Panel.TFrame")
        right.pack(side="left", fill="y", padx=(8, 0))
        right.pack(side="left", fill="y", padx=(6, 0))
        right.pack_propagate(False)
        ttk.Label(right, text="Параметры операции", style="PanelTitle.TLabel").pack(
            anchor="w", padx=12, pady=(12, 4))
        outer = ttk.Frame(right)
        outer.configure(style="Panel.TFrame")
        outer.pack(fill="both", expand=True, padx=10, pady=(2, 6))
        self.params_canvas = tk.Canvas(outer, bg=PANEL, highlightthickness=0)
        self.params_scroll = ttk.Scrollbar(outer, orient="vertical",
                                           command=self.params_canvas.yview)
        self.params_canvas.configure(yscrollcommand=self.params_scroll.set)
        self.params_canvas.pack(side="left", fill="both", expand=True)
        self.params_scroll.pack(side="right", fill="y")
        self.params_frame = ttk.Frame(self.params_canvas)
        self.params_frame.configure(style="Panel.TFrame")
        self._params_window = self.params_canvas.create_window(
            (0, 0), window=self.params_frame, anchor="nw")
        self.params_frame.bind("<Configure>", lambda _e: self.params_canvas.configure(
            scrollregion=self.params_canvas.bbox("all")))
        self.params_canvas.bind("<Configure>", lambda e: self.params_canvas.itemconfigure(
            self._params_window, width=e.width))
        self.history_panel = HistoryPanel(right, on_select=self._on_history_pick)
        self.history_panel.pack(fill="both", expand=True, padx=6, pady=(0, 8))
        status_bar = ttk.Frame(self.root, padding=(12, 5))
        status_bar.configure(style="Panel.TFrame")
        status_bar.pack(fill="x", padx=10, pady=(0, 8))
        self.status = ttk.Label(status_bar, text="Готово. Откройте изображение.",
                                style="Dim.TLabel", anchor="w")
        self.status.pack(fill="x")

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

    def set_busy(self, busy: bool, text: str = "⏳ Обработка...") -> None:
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
            b.configure(style="CategoryActive.TButton" if k == key else "Category.TButton")

    def clear_params(self):
        for child in self.params_frame.winfo_children():
            child.destroy()
        return self.params_frame

