"""Контроллер истории: Undo/Redo/переход (без математики обработки)."""
from __future__ import annotations

from app.views import dialogs


class HistoryController:
    def __init__(self, app) -> None:
        self.app = app

    def undo(self) -> None:
        try:
            img, label = self.app.history.undo()
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Отмена: {label}")

    def redo(self) -> None:
        try:
            img, label = self.app.history.redo()
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Повтор: {label}")

    def jump(self, index: int) -> None:
        try:
            img, label = self.app.history.jump_to(index)
            self.app.image_model.set_current(img)
        except ValueError as exc:
            dialogs.show_error(self.app.view.root, str(exc))
            return
        self.app.refresh_images(f"Переход к состоянию {index}: {label}")
