"""Главное окно приложения. Только представление (MVC)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.views.history_view import HistoryPanel
from app.views.image_view import ImagePanel


COLORS = {
    "bg": "#101319",
    "sidebar": "#171b24",
    "panel": "#1b202b",
    "card": "#222936",
    "canvas": "#0b0e13",
    "border": "#303847",
    "text": "#edf1f7",
    "muted": "#929cad",
    "accent": "#7c9cff",
    "accent_hover": "#91adff",
    "danger": "#f07878",
    "button": "#2b3342",
    "button_hover": "#394458",
}

CATEGORIES = [
    ("morph", "Морфология", "M"),
    ("filters", "Фильтры", "F"),
    ("conv", "Свёртка", "K"),
    ("history", "История", "H"),
]


class MainView:
    """Главное окно: навигация, рабочая область, параметры и история."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.callbacks: dict[str, object] = {}
        self.category_buttons: dict[str, ttk.Button] = {}

        self.root.title("GrayLab — обработка изображений")
        self.root.geometry("1440x900")
        self.root.minsize(1080, 680)
        self.root.configure(bg=COLORS["bg"])

        self._configure_styles()
        self._build_menu()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.option_add(
            "*TCombobox*Listbox.background", COLORS["card"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.foreground", COLORS["text"]
        )
        self.root.option_add(
            "*TCombobox*Listbox.selectBackground", COLORS["accent"]
        )

        style.configure(
            ".",
            font=("Segoe UI", 10),
            background=COLORS["bg"],
            foreground=COLORS["text"],
        )
        style.configure("TFrame", background=COLORS["bg"])
        style.configure(
            "Sidebar.TFrame", background=COLORS["sidebar"]
        )
        style.configure(
            "Panel.TFrame", background=COLORS["panel"]
        )
        style.configure(
            "Card.TFrame", background=COLORS["card"]
        )

        style.configure(
            "TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
        )
        style.configure(
            "Panel.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
        )
        style.configure(
            "Card.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
        )
        style.configure(
            "CardDim.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Section.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Dim.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Muted.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "CardMuted.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Title.TLabel",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "AppTitle.TLabel",
            background=COLORS["sidebar"],
            foreground=COLORS["text"],
            font=("Segoe UI", 16, "bold"),
        )
        style.configure(
            "AppSubtitle.TLabel",
            background=COLORS["sidebar"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Section.TLabel",
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Badge.TLabel",
            background=COLORS["card"],
            foreground=COLORS["muted"],
            font=("Segoe UI", 9),
        )

        style.configure(
            "TButton",
            background=COLORS["button"],
            foreground=COLORS["text"],
            borderwidth=0,
            padding=(10, 7),
            font=("Segoe UI", 9),
        )
        style.map(
            "TButton",
            background=[
                ("active", COLORS["button_hover"]),
                ("disabled", COLORS["panel"]),
            ],
            foreground=[("disabled", COLORS["muted"])],
        )
        style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#111722",
            padding=(12, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_hover"]),
                ("disabled", COLORS["button"]),
            ],
        )
        style.configure(
            "Small.TButton",
            padding=(6, 4),
            font=("Segoe UI", 9),
        )
        style.configure(
            "Nav.TButton",
            background=COLORS["sidebar"],
            foreground=COLORS["muted"],
            padding=(12, 11),
            anchor="w",
            font=("Segoe UI", 10),
        )
        style.map(
            "Nav.TButton",
            background=[("active", COLORS["button_hover"])],
            foreground=[("active", COLORS["text"])],
        )
        style.configure(
            "NavActive.TButton",
            background=COLORS["accent"],
            foreground="#111722",
            padding=(12, 11),
            anchor="w",
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "NavActive.TButton",
            background=[("active", COLORS["accent_hover"])],
            foreground=[("active", "#111722")],
        )

        style.configure(
            "TEntry",
            fieldbackground=COLORS["canvas"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            padding=5,
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["canvas"],
            foreground=COLORS["text"],
            background=COLORS["button"],
            arrowcolor=COLORS["text"],
            padding=4,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["canvas"])],
            foreground=[("readonly", COLORS["text"])],
        )
        style.configure(
            "TSpinbox",
            fieldbackground=COLORS["canvas"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            padding=4,
        )
        style.configure(
            "TCheckbutton",
            background=COLORS["card"],
            foreground=COLORS["text"],
        )
        style.configure(
            "TRadiobutton",
            background=COLORS["card"],
            foreground=COLORS["text"],
        )
        style.configure(
            "TScrollbar",
            background=COLORS["button"],
            troughcolor=COLORS["panel"],
            bordercolor=COLORS["panel"],
            arrowcolor=COLORS["muted"],
        )
        style.configure(
            "Horizontal.TSeparator",
            background=COLORS["border"],
        )
        style.configure(
            "Vertical.TSeparator",
            background=COLORS["border"],
        )

    def _build_menu(self) -> None:
        menu = tk.Menu(
            self.root,
            tearoff=False,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
            activeforeground="#111722",
        )

        file_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
        )
        file_menu.add_command(
            label="Открыть изображение...",
            command=lambda: self.emit("open_image"),
        )
        file_menu.add_command(
            label="Сохранить результат...",
            command=lambda: self.emit("save_image"),
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Вернуться к оригиналу",
            command=lambda: self.emit("reset_original"),
        )
        file_menu.add_separator()
        file_menu.add_command(
            label="Выход", command=self.root.destroy
        )
        menu.add_cascade(label="Файл", menu=file_menu)

        edit_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
        )
        edit_menu.add_command(
            label="Отменить",
            command=lambda: self.emit("undo"),
        )
        edit_menu.add_command(
            label="Повторить",
            command=lambda: self.emit("redo"),
        )
        menu.add_cascade(label="Правка", menu=edit_menu)

        tools_menu = tk.Menu(
            menu,
            tearoff=False,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            activebackground=COLORS["accent"],
        )
        tools_menu.add_command(
            label="Структурный элемент...",
            command=lambda: self.emit("open_se_editor"),
        )
        tools_menu.add_command(
            label="Ядро свёртки...",
            command=lambda: self.emit("open_kernel_editor"),
        )
        menu.add_cascade(label="Инструменты", menu=tools_menu)

        self.root.configure(menu=menu)

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        shell = ttk.Frame(self.root)
        shell.grid(row=0, column=0, sticky="nsew")
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(0, weight=1)

        self._build_sidebar(shell)
        self._build_workspace(shell)

    def _build_sidebar(self, parent) -> None:
        sidebar = ttk.Frame(
            parent,
            style="Sidebar.TFrame",
            width=205,
            padding=(14, 18, 14, 12),
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(8, weight=1)

        ttk.Label(
            sidebar,
            text="GrayLab",
            style="AppTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            sidebar,
            text="IMAGE PROCESSING",
            style="AppSubtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(2, 24))

        ttk.Label(
            sidebar,
            text="РАБОЧЕЕ ПРОСТРАНСТВО",
            style="AppSubtitle.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(0, 8))

        for index, (key, title, shortcut) in enumerate(CATEGORIES, start=3):
            button = ttk.Button(
                sidebar,
                text=f"{shortcut}     {title}",
                style="Nav.TButton",
                command=lambda k=key: self.emit("category", k),
            )
            button.grid(
                row=index,
                column=0,
                sticky="ew",
                pady=3,
            )
            self.category_buttons[key] = button

        ttk.Separator(sidebar).grid(
            row=7, column=0, sticky="ew", pady=18
        )

        tools = ttk.Frame(
            sidebar,
            style="Sidebar.TFrame",
        )
        tools.grid(row=9, column=0, sticky="sew")
        tools.columnconfigure(0, weight=1)

        ttk.Label(
            tools,
            text="ИНСТРУМЕНТЫ",
            style="AppSubtitle.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Button(
            tools,
            text="Структурный элемент",
            command=lambda: self.emit("open_se_editor"),
        ).grid(row=1, column=0, sticky="ew", pady=3)

        ttk.Button(
            tools,
            text="Ядро свёртки",
            command=lambda: self.emit("open_kernel_editor"),
        ).grid(row=2, column=0, sticky="ew", pady=3)

        ttk.Label(
            tools,
            text="Grayscale · MVC · OpenCV",
            style="AppSubtitle.TLabel",
        ).grid(row=3, column=0, sticky="w", pady=(18, 0))

    def _build_workspace(self, parent) -> None:
        workspace = ttk.Frame(parent, padding=(12, 12, 12, 10))
        workspace.grid(row=0, column=1, sticky="nsew")
        workspace.columnconfigure(0, weight=1)
        workspace.rowconfigure(1, weight=1)

        self._build_toolbar(workspace)

        content = ttk.Frame(workspace)
        content.grid(row=1, column=0, sticky="nsew", pady=(12, 10))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=0)
        content.rowconfigure(0, weight=1)

        viewer_area = ttk.Frame(content)
        viewer_area.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        viewer_area.columnconfigure(0, weight=1, uniform="image")
        viewer_area.columnconfigure(1, weight=1, uniform="image")
        viewer_area.rowconfigure(0, weight=1)

        self.original_panel = ImagePanel(
            viewer_area, "01  /  ОРИГИНАЛ"
        )
        self.original_panel.grid(
            row=0, column=0, sticky="nsew", padx=(0, 5)
        )

        self.result_panel = ImagePanel(
            viewer_area, "02  /  РЕЗУЛЬТАТ"
        )
        self.result_panel.grid(
            row=0, column=1, sticky="nsew", padx=(5, 0)
        )

        inspector = ttk.Frame(
            content,
            style="Panel.TFrame",
            width=320,
            padding=(12, 12, 10, 8),
        )
        inspector.grid(row=0, column=1, sticky="ns")
        inspector.grid_propagate(False)
        inspector.columnconfigure(0, weight=1)
        inspector.rowconfigure(1, weight=1)
        inspector.rowconfigure(3, weight=1)

        ttk.Label(
            inspector,
            text="ПАРАМЕТРЫ",
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        params_outer = ttk.Frame(
            inspector,
            style="Panel.TFrame",
        )
        params_outer.grid(row=1, column=0, sticky="nsew")
        params_outer.columnconfigure(0, weight=1)
        params_outer.rowconfigure(0, weight=1)

        self.params_canvas = tk.Canvas(
            params_outer,
            bg=COLORS["panel"],
            highlightthickness=0,
            borderwidth=0,
        )
        self.params_scroll = ttk.Scrollbar(
            params_outer,
            orient="vertical",
            command=self.params_canvas.yview,
        )
        self.params_canvas.configure(
            yscrollcommand=self.params_scroll.set
        )
        self.params_canvas.grid(row=0, column=0, sticky="nsew")
        self.params_scroll.grid(row=0, column=1, sticky="ns")

        self.params_frame = ttk.Frame(
            self.params_canvas,
            style="Panel.TFrame",
        )
        self._params_window = self.params_canvas.create_window(
            (0, 0),
            window=self.params_frame,
            anchor="nw",
        )

        self.params_frame.bind(
            "<Configure>",
            lambda _event: self.params_canvas.configure(
                scrollregion=self.params_canvas.bbox("all")
            ),
        )
        self.params_canvas.bind(
            "<Configure>",
            lambda event: self.params_canvas.itemconfigure(
                self._params_window,
                width=event.width,
            ),
        )

        ttk.Separator(inspector).grid(
            row=2, column=0, sticky="ew", pady=(12, 8)
        )

        self.history_panel = HistoryPanel(
            inspector,
            on_select=self._on_history_pick,
        )
        self.history_panel.grid(
            row=3, column=0, sticky="nsew"
        )

        status_bar = ttk.Frame(
            workspace,
            style="Panel.TFrame",
            padding=(12, 9),
        )
        status_bar.grid(row=2, column=0, sticky="ew")
        status_bar.columnconfigure(1, weight=1)

        self.status_dot = tk.Label(
            status_bar,
            text="●",
            bg=COLORS["panel"],
            fg="#73d6a2",
            font=("Segoe UI", 9),
        )
        self.status_dot.grid(row=0, column=0, padx=(0, 8))

        self.status = ttk.Label(
            status_bar,
            text="Готово. Откройте изображение.",
            style="Muted.TLabel",
            anchor="w",
        )
        self.status.grid(row=0, column=1, sticky="ew")

        self.busy_label = ttk.Label(
            status_bar,
            text="",
            style="Muted.TLabel",
        )
        self.busy_label.grid(row=0, column=2, padx=(10, 0))

    # API, используемый контроллерами

    def on(self, event: str, callback) -> None:
        self.callbacks[event] = callback

    def emit(self, event: str, *args):
        callback = self.callbacks.get(event)
        if callback is not None:
            return callback(*args)
        return None

    def _on_history_pick(self, index: int) -> None:
        self.emit("history_jump", index)

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def set_busy(self, busy: bool, text: str = "Обработка...") -> None:
        self.busy_label.configure(text=text if busy else "")
        state = "disabled" if busy else "normal"

        for button in (
            self.btn_open,
            self.btn_save,
            self.btn_undo,
            self.btn_redo,
            self.btn_reset,
            self.btn_se,
            self.btn_kernel,
        ):
            try:
                button.configure(state=state)
            except tk.TclError:
                pass

        self.status_dot.configure(
            fg="#e6b567" if busy else "#73d6a2"
        )

    def set_undo_redo(
        self,
        can_undo: bool,
        can_redo: bool,
    ) -> None:
        try:
            self.btn_undo.configure(
                state="normal" if can_undo else "disabled"
            )
            self.btn_redo.configure(
                state="normal" if can_redo else "disabled"
            )
        except tk.TclError:
            pass

    def set_category(self, key: str) -> None:
        for category, button in self.category_buttons.items():
            button.configure(
                style=(
                    "NavActive.TButton"
                    if category == key
                    else "Nav.TButton"
                )
            )

    def clear_params(self):
        for child in self.params_frame.winfo_children():
            child.destroy()
        self.params_canvas.yview_moveto(0)
        return self.params_frame

    def _build_toolbar(self, parent) -> None:
        toolbar = ttk.Frame(
            parent,
            style="Panel.TFrame",
            padding=(10, 9),
        )
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(8, weight=1)

        self.btn_open = ttk.Button(
            toolbar,
            text="Открыть изображение",
            style="Accent.TButton",
            command=lambda: self.emit("open_image"),
        )
        self.btn_open.grid(row=0, column=0, padx=(0, 6))

        self.btn_save = ttk.Button(
            toolbar,
            text="Сохранить",
            command=lambda: self.emit("save_image"),
        )
        self.btn_save.grid(row=0, column=1, padx=3)

        ttk.Separator(
            toolbar,
            orient="vertical",
        ).grid(row=0, column=2, sticky="ns", padx=9)

        self.btn_undo = ttk.Button(
            toolbar,
            text="↶  Отменить",
            command=lambda: self.emit("undo"),
        )
        self.btn_undo.grid(row=0, column=3, padx=3)

        self.btn_redo = ttk.Button(
            toolbar,
            text="↷  Повторить",
            command=lambda: self.emit("redo"),
        )
        self.btn_redo.grid(row=0, column=4, padx=3)

        self.btn_reset = ttk.Button(
            toolbar,
            text="К оригиналу",
            command=lambda: self.emit("reset_original"),
        )
        self.btn_reset.grid(row=0, column=5, padx=3)

        ttk.Separator(
            toolbar,
            orient="vertical",
        ).grid(row=0, column=6, sticky="ns", padx=9)

        self.btn_se = ttk.Button(
            toolbar,
            text="Структурный элемент",
            command=lambda: self.emit("open_se_editor"),
        )
        self.btn_se.grid(row=0, column=7, padx=3)

        self.btn_kernel = ttk.Button(
            toolbar,
            text="Ядро",
            command=lambda: self.emit("open_kernel_editor"),
        )
        self.btn_kernel.grid(row=0, column=8, padx=3, sticky="w")
