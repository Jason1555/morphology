"""Точка входа: только создание объектов и запуск (MVC: main.py минимальный)."""
from __future__ import annotations

import tkinter as tk

from app.controllers.main_controller import MainController


def main() -> None:
    root = tk.Tk()
    app = MainController(root)
    app.run()


if __name__ == "__main__":
    main()
