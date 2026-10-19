"""Компонент просмотра grayscale-изображения. Только View."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


BG = "#151a23"
CANVAS_BG = "#0b0e13"
BORDER = "#303847"
TEXT = "#edf1f7"
MUTED = "#929cad"
ACCENT = "#7c9cff"


class ImagePanel(ttk.Frame):
    """Панель изображения с масштабированием и прокруткой."""

    def __init__(self, parent, title: str) -> None:
        super().__init__(
            parent,
            style="Panel.TFrame",
            padding=(10, 10),
        )

        self._pil: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._zoom = 1.0
        self._fit = True
        self._render_job = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        header = ttk.Frame(self, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text=title,
            style="Title.TLabel",
        ).grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(header, style="Panel.TFrame")
        controls.grid(row=0, column=1, sticky="e")

        ttk.Button(
            controls,
            text="−",
            width=3,
            style="Small.TButton",
            command=self.zoom_out,
        ).pack(side="left", padx=1)

        self.zoom_label = ttk.Label(
            controls,
            text="Вписать",
            style="Muted.TLabel",
            width=7,
            anchor="center",
        )
        self.zoom_label.pack(side="left", padx=3)

        ttk.Button(
            controls,
            text="+",
            width=3,
            style="Small.TButton",
            command=self.zoom_in,
        ).pack(side="left", padx=1)

        ttk.Button(
            controls,
            text="Вписать",
            style="Small.TButton",
            command=self.zoom_fit,
        ).pack(side="left", padx=(5, 0))

        info_row = ttk.Frame(self, style="Panel.TFrame")
        info_row.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        info_row.columnconfigure(0, weight=1)

        self.info_label = ttk.Label(
            info_row,
            text="Изображение не загружено",
            style="Muted.TLabel",
        )
        self.info_label.grid(row=0, column=0, sticky="w")

        self.mode_label = ttk.Label(
            info_row,
            text="GRAY · 8 BIT",
            style="Muted.TLabel",
        )
        self.mode_label.grid(row=0, column=1, sticky="e")

        body = ttk.Frame(self, style="Panel.TFrame")
        body.grid(row=2, column=0, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            body,
            bg=CANVAS_BG,
            highlightthickness=1,
            highlightbackground=BORDER,
            borderwidth=0,
            relief="flat",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self.canvas.yview,
        )
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.hbar = ttk.Scrollbar(
            body,
            orient="horizontal",
            command=self.canvas.xview,
        )
        self.hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            xscrollcommand=self.hbar.set,
            yscrollcommand=self.vbar.set,
        )

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda _e: self.zoom_in())
        self.canvas.bind("<Button-5>", lambda _e: self.zoom_out())

        self.canvas.bind("<ButtonPress-2>", self._pan_start)
        self.canvas.bind("<B2-Motion>", self._pan_move)
        self.canvas.bind("<ButtonPress-3>", self._pan_start)
        self.canvas.bind("<B3-Motion>", self._pan_move)

        self._show_placeholder()

    def set_image(
        self,
        pil_image: Image.Image | None,
        info: str = "",
    ) -> None:
        """Установить изображение из контроллера."""
        self._pil = pil_image
        self._photo = None

        if pil_image is None:
            self._zoom = 1.0
            self._fit = True
            self.info_label.configure(text="Изображение не загружено")
            self.mode_label.configure(text="GRAY · 8 BIT")
            self._show_placeholder()
            self.zoom_label.configure(text="Вписать")
            return

        self.info_label.configure(
            text=info or (
                f"{pil_image.width} × {pil_image.height} пикс."
            )
        )
        self.mode_label.configure(text="GRAYSCALE")
        self._fit = True
        self._schedule_render()

    def zoom_in(self) -> None:
        if self._pil is None:
            return
        self._fit = False
        self._zoom = min(self._zoom * 1.25, 16.0)
        self._render()

    def zoom_out(self) -> None:
        if self._pil is None:
            return
        self._fit = False
        self._zoom = max(self._zoom / 1.25, 0.03)
        self._render()

    def zoom_fit(self) -> None:
        self._fit = True
        self._render()

    def _on_canvas_resize(self, _event=None) -> None:
        if self._fit or self._pil is None:
            self._schedule_render()

    def _schedule_render(self) -> None:
        if self._render_job is not None:
            try:
                self.after_cancel(self._render_job)
            except tk.TclError:
                pass
        try:
            self._render_job = self.after_idle(self._render)
        except tk.TclError:
            self._render_job = None

    def _on_wheel(self, event) -> None:
        # Ctrl + колесо меняет масштаб; обычное колесо прокручивает изображение.
        if event.state & 0x4:
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            return

        direction = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(direction * 3, "units")

    def _pan_start(self, event) -> None:
        self.canvas.scan_mark(event.x, event.y)

    def _pan_move(self, event) -> None:
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _show_placeholder(self) -> None:
        self.canvas.delete("all")
        self.canvas.configure(scrollregion=(0, 0, 1, 1))

        width = max(self.canvas.winfo_width(), 100)
        height = max(self.canvas.winfo_height(), 100)

        self.canvas.create_text(
            width // 2,
            height // 2 - 14,
            text="Нет изображения",
            fill=TEXT,
            font=("Segoe UI", 13, "bold"),
            justify="center",
        )
        self.canvas.create_text(
            width // 2,
            height // 2 + 15,
            text="Откройте файл, чтобы начать работу",
            fill=MUTED,
            font=("Segoe UI", 10),
            justify="center",
        )

    def _render(self) -> None:
        self._render_job = None
        self.canvas.delete("all")

        image = self._pil
        if image is None:
            self._show_placeholder()
            return

        canvas_width = max(self.canvas.winfo_width(), 80)
        canvas_height = max(self.canvas.winfo_height(), 80)
        image_width, image_height = image.size

        if self._fit:
            available_width = max(1, canvas_width - 28)
            available_height = max(1, canvas_height - 28)

            self._zoom = min(
                available_width / image_width,
                available_height / image_height,
                16.0,
            )
            self._zoom = max(self._zoom, 0.01)

        display_width = max(
            1, round(image_width * self._zoom)
        )
        display_height = max(
            1, round(image_height * self._zoom)
        )

        resampling = (
            Image.Resampling.NEAREST
            if self._zoom >= 1.0
            else Image.Resampling.LANCZOS
        )

        try:
            shown = image.resize(
                (display_width, display_height),
                resampling,
            )
        except (ValueError, OSError):
            shown = image.resize(
                (display_width, display_height)
            )

        self._photo = ImageTk.PhotoImage(shown)

        offset_x = max(12, (canvas_width - display_width) // 2)
        offset_y = max(12, (canvas_height - display_height) // 2)

        self.canvas.create_rectangle(
            offset_x - 1,
            offset_y - 1,
            offset_x + display_width + 1,
            offset_y + display_height + 1,
            outline=BORDER,
        )
        self.canvas.create_image(
            offset_x,
            offset_y,
            anchor="nw",
            image=self._photo,
        )

        scroll_width = max(
            canvas_width,
            display_width + offset_x * 2,
        )
        scroll_height = max(
            canvas_height,
            display_height + offset_y * 2,
        )

        self.canvas.configure(
            scrollregion=(0, 0, scroll_width, scroll_height)
        )
        self.zoom_label.configure(
            text=f"{round(self._zoom * 100)}%"
        )
