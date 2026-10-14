"""Диалоги открытия/сохранения и уведомлений (только View, без математики)."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox

IMAGE_OPEN_TYPES = [
    ("Изображения", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
    ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"),
    ("BMP", "*.bmp"), ("TIFF", "*.tif *.tiff"),
    ("Все файлы", "*.*"),
]

IMAGE_SAVE_TYPES = [
    ("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"),
    ("BMP", "*.bmp"), ("TIFF", "*.tif *.tiff"),
]

SE_TYPES = [("JSON", "*.json"), ("NumPy", "*.npz")]


def ask_open_image(parent) -> str | None:
    return filedialog.askopenfilename(parent=parent, title="Открыть изображение",
                                      filetypes=IMAGE_OPEN_TYPES)


def ask_save_image(parent) -> str | None:
    return filedialog.asksaveasfilename(parent=parent, title="Сохранить результат",
                                        defaultextension=".png", filetypes=IMAGE_SAVE_TYPES)


def ask_save_se(parent) -> str | None:
    return filedialog.asksaveasfilename(parent=parent, title="Сохранить структурный элемент",
                                        defaultextension=".json", filetypes=SE_TYPES)


def ask_open_se(parent) -> str | None:
    return filedialog.askopenfilename(parent=parent, title="Загрузить структурный элемент",
                                      filetypes=SE_TYPES + [("Все файлы", "*.*")])


def show_error(parent, message: str) -> None:
    messagebox.showerror("Ошибка", str(message), parent=parent)


def show_info(parent, message: str) -> None:
    messagebox.showinfo("Информация", str(message), parent=parent)


def confirm(parent, message: str) -> bool:
    return messagebox.askyesno("Подтверждение", message, parent=parent)
