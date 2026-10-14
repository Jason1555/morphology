"""Контроллер изображений: открытие/сохранение/сброс (связывает Model и View)."""
from __future__ import annotations

import os

from PIL import Image

from app.views import dialogs


class ImageController:
    def __init__(self, app) -> None:
        self.app = app

    def _to_pil(self, arr):
        if arr is None:
            return None
        return Image.fromarray(arr, mode="L")

    def open_image(self) -> None:
        path = dialogs.ask_open_image(self.app.view.root)
        if not path:
            return
        try:
            self.app.image_model.load(path)
            self.app.history.initialize(self.app.image_model.require_current_copy(),
                                        label=f"Открыто: {os.path.basename(path)}")
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Открыто: {os.path.basename(path)}")

    def save_image(self) -> None:
        if not self.app.image_model.has_image:
            dialogs.show_error(self.app.view.root, "Нет изображения для сохранения.")
            return
        path = dialogs.ask_save_image(self.app.view.root)
        if not path:
            return
        try:
            self.app.image_model.save_current(path)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.view.set_status(f"Сохранено: {path}")

    def reset_to_original(self) -> None:
        try:
            img = self.app.image_model.reset_to_original()
            self.app.history.push(img, "Возврат к оригиналу", "")
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images("Возврат к исходному изображению.")
