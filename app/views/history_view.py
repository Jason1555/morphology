"""Панель истории обработки. Только View."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


BG = "#1b202b"
CANVAS_BG = "#11151d"
TEXT = "#edf1f7"
MUTED = "#929cad"
ACCENT = "#7c9cff"
BORDER = "#303847"


class HistoryPanel(ttk.Frame):
    def __init__(self, parent, on_select=None) -> None:
        super().__init__(parent, style="Panel.TFrame")

        self._on_select = on_select
        self._entries: list[dict] = []
        self._active_index = -1
        self._updating = False

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        header.columnconfigure(0, weight=1)

        ttk.Label(
            header,
            text="ИСТОРИЯ ОБРАБОТКИ",
            style="Muted.TLabel",
        ).grid(row=0, column=0, sticky="w")

        self.count_badge = ttk.Label(
            header,
            text="0 шагов",
            style="Muted.TLabel",
        )
        self.count_badge.grid(row=0, column=1, sticky="e")

        body = ttk.Frame(self, style="Panel.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            body,
            bg=CANVAS_BG,
            fg=TEXT,
            selectbackground=ACCENT,
            selectforeground="#111722",
            font=("Segoe UI", 9),
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            bd=0,
            relief="flat",
            activestyle="none",
            borderwidth=0,
            selectborderwidth=0,
            exportselection=False,
        )
        self.listbox.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(
            body,
            orient="vertical",
            command=self.listbox.yview,
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.bind(
            "<<ListboxSelect>>",
            self._handle_selection,
        )

        self.empty_label = ttk.Label(
            self,
            text="После первой операции\nздесь появится история.",
            style="Muted.TLabel",
            justify="center",
        )

    def _handle_selection(self, _event=None) -> None:
        if self._updating or self._on_select is None:
            return

        selection = self.listbox.curselection()
        if not selection:
            return

        index = selection[0]
        if index != self._active_index:
            self._on_select(index)

    def set_entries(
        self,
        entries: list[dict],
        active_index: int,
    ) -> None:
        """Обновить список шагов и выделить текущее состояние."""
        self._updating = True

        try:
            self._entries = list(entries)
            self._active_index = active_index

            self.listbox.delete(0, tk.END)

            count = len(self._entries)
            self.count_badge.configure(
                text=f"{count} шагов"
            )

            if count == 0:
                self.empty_label.grid(
                    row=2,
                    column=0,
                    sticky="ew",
                    pady=(6, 0),
                )
            else:
                self.empty_label.grid_remove()

            for index, entry in enumerate(self._entries):
                marker = "●" if index == active_index else "○"
                label = str(entry.get("label", "Операция"))
                params = str(entry.get("params", ""))

                line = f" {marker}  {index + 1:02d}  {label}"
                if params:
                    line += f"\n      {params}"

                self.listbox.insert(tk.END, line)

                if index == active_index:
                    self.listbox.itemconfigure(
                        index,
                        fg=ACCENT,
                    )

            if 0 <= active_index < count:
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(active_index)
                self.listbox.activate(active_index)
                self.listbox.see(active_index)

        finally:
            self._updating = False
