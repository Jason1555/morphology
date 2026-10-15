"""Список истории обработки (только View)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class HistoryPanel(ttk.Frame):
    def __init__(self, parent, on_select=None) -> None:
        super().__init__(parent, style="Panel.TFrame")
        self._on_select = on_select
        header = ttk.Frame(self, style="Panel.TFrame")
        header.pack(fill="x", padx=6, pady=(6, 4))
        ttk.Label(header, text="История состояний", style="PanelTitle.TLabel").pack(side="left")
        self.count_badge = ttk.Label(header, text="0", style="Badge.TLabel")
        self.count_badge.pack(side="right")

        body = ttk.Frame(self, style="Panel.TFrame")
        body.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.listbox = tk.Listbox(
            body,
            bg="#10141c",
            fg="#eef2f8",
            font=("Segoe UI", 9),
            selectbackground="#4f8cff",
            selectforeground="#ffffff",
            highlightthickness=1,
            highlightbackground="#2f394d",
            highlightcolor="#4f8cff",
            bd=0,
            relief="flat",
            activestyle="none",
        )
        bar = ttk.Scrollbar(body, orient="vertical", command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=bar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        bar.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self._handle)

    def _handle(self, _event=None) -> None:
        if self._on_select is None:
            return
        sel = self.listbox.curselection()
        if sel:
            self._on_select(sel[0])

    def set_entries(self, entries: list[dict], active_index: int) -> None:
        self.listbox.delete(0, "end")
        self.count_badge.configure(text=f"шагов: {len(entries)}")
        for i, e in enumerate(entries):
            mark = "● " if i == active_index else "   "
            params = f"  ({e['params']})" if e.get("params") else ""
            self.listbox.insert("end", f" {mark}{i}. {e['label']}{params}")
        if 0 <= active_index < len(entries):
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(active_index)
            self.listbox.see(active_index)

