"""Виджет просмотра изображения: масштаб, прокрутка, пропорции (только View)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk


class ImagePanel(ttk.Frame):
    """Панель с заголовком, Canvas + скроллбары и кнопками масштаба."""

    def __init__(self, parent, title: str) -> None:
        super().__init__(parent)
        self._pil: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._zoom: float = 1.0
        self._fit: bool = True

        header = ttk.Frame(self)
        header.pack(fill="x", padx=4, pady=(4, 0))
        ttk.Label(header, text=title, style="PanelTitle.TLabel").pack(side="left")
        btns = ttk.Frame(header)
        btns.pack(side="right")
        ttk.Button(btns, text="−", width=2, command=self.zoom_out).pack(side="left", padx=1)
        ttk.Button(btns, text="+", width=2, command=self.zoom_in).pack(side="left", padx=1)
        ttk.Button(btns, text="Вписать", width=7, command=self.zoom_fit).pack(side="left", padx=1)
        self.zoom_label = ttk.Label(btns, text="100%", width=6, anchor="e")
        self.zoom_label.pack(side="left", padx=2)
        self.info_label = ttk.Label(self, text="Нет изображения", style="Dim.TLabel")
        self.info_label.pack(fill="x", padx=6)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=4, pady=4)
        self.canvas = tk.Canvas(body, bg="#161a22", highlightthickness=1,
                                highlightbackground="#2c3342")
        self.vbar = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.hbar = ttk.Scrollbar(body, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", lambda _e: self._render() if self._fit else None)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", lambda _e: self.zoom_in())
        self.canvas.bind("<Button-5>", lambda _e: self.zoom_out())

    # --- API для контроллера ---
    def set_image(self, pil_image: "Image.Image | None", info: str = "") -> None:
        self._pil = pil_image
        if info:
            self.info_label.configure(text=info)
        elif pil_image is not None:
            self.info_label.configure(text=f"{pil_image.width}×{pil_image.height}")
        else:
            self.info_label.configure(text="Нет изображения")
        self._render()

    def zoom_in(self) -> None:
        self._fit = False
        self._zoom = min(self._zoom * 1.25, 16.0)
        self._render()

    def zoom_out(self) -> None:
        self._fit = False
        self._zoom = max(self._zoom / 1.25, 0.05)
        self._render()

    def zoom_fit(self) -> None:
        self._fit = True
        self._render()

    # --- внутреннее ---
    def _on_wheel(self, event) -> None:
        if event.state & 0x4:  # Ctrl+колесо — масштаб
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

    def _render(self) -> None:
        self.canvas.delete("all")
        if self._pil is None:
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            self.zoom_label.configure(text="—")
            return
        cw, ch = max(self.canvas.winfo_width(), 50), max(self.canvas.winfo_height(), 50)
        iw, ih = self._pil.size
        if self._fit:
            scale = min(cw / iw, ch / ih)
            scale = max(min(scale, 16.0), 0.02)
            self._zoom = scale
        dw, dh = max(1, int(iw * self._zoom)), max(1, int(ih * self._zoom))
        try:
            shown = self._pil.resize((dw, dh), Image.NEAREST if self._zoom >= 1 else Image.LANCZOS)
        except Exception:
            shown = self._pil.resize((dw, dh))
        self._photo = ImageTk.PhotoImage(shown)
        self.canvas.create_image(0, 0, anchor="nw", image=self._photo)
        self.canvas.configure(scrollregion=(0, 0, dw, dh))
        self.zoom_label.configure(text=f"{int(self._zoom * 100)}%")
