"""Главный контроллер: связывает Model и View, потоки, редакторы, категории."""
from __future__ import annotations

import queue
import threading
import tkinter as tk

import numpy as np
from PIL import Image

from app.controllers.convolution_controller import ConvolutionController
from app.controllers.filters_controller import FiltersController
from app.controllers.history_controller import HistoryController
from app.controllers.image_controller import ImageController
from app.controllers.morphology_controller import MorphologyController
from app.models.convolution_model import ConvolutionModel
from app.models.filters_model import FiltersModel
from app.models.history_model import HistoryModel
from app.models.image_model import ImageModel
from app.models.kernel_model import KernelModel
from app.models.morphology_model import MorphologyModel
from app.models.structuring_element_model import StructuringElementModel
from app.views import dialogs
from app.views.kernel_editor_view import KernelEditorView
from app.views.main_view import MainView
from app.views.structuring_element_view import StructuringElementEditor


class MainController:
    def __init__(self, root: tk.Tk) -> None:
        self.image_model = ImageModel()
        self.history = HistoryModel(max_states=30)
        self.morph_model = MorphologyModel()
        self.filters_model = FiltersModel()
        self.conv_model = ConvolutionModel()
        self.se_model = StructuringElementModel(3, 3)
        self.kernel_model = KernelModel(3, 3)
        self.view = MainView(root)
        self.image_ctrl = ImageController(self)
        self.history_ctrl = HistoryController(self)
        self.morph_ctrl = MorphologyController(self)
        self.filters_ctrl = FiltersController(self)
        self.conv_ctrl = ConvolutionController(self)
        self.category = "morph"
        self._busy = False
        self._operation_source: np.ndarray | None = None
        self._worker_queue: queue.Queue[tuple] = queue.Queue()
        self._bind()
        self.show_category("morph")
        self.refresh_images("Готово. Откройте изображение.")
        # Poll from Tk's main thread; workers only put plain data in the queue.
        self.view.root.after(40, self._poll_worker_results)

    def _bind(self) -> None:
        v = self.view
        v.on("open_image", self.image_ctrl.open_image)
        v.on("save_image", self.image_ctrl.save_image)
        v.on("reset_original", self.image_ctrl.reset_to_original)
        v.on("undo", self.history_ctrl.undo)
        v.on("redo", self.history_ctrl.redo)
        v.on("history_jump", self.history_ctrl.jump)
        v.on("category", self.show_category)
        v.on("open_se_editor", self.open_se_editor)
        v.on("open_kernel_editor", self.open_kernel_editor)

    CATEGORY_KEYS = ("morph", "filters", "conv", "history")

    def show_category(self, key: str) -> None:
        if key not in self.CATEGORY_KEYS:
            try:
                self.view.set_status(f"Неизвестная категория: {key!r}.")
            except tk.TclError:
                pass
            return
        self.category = key
        try:
            self.view.set_category(key)
        except tk.TclError:
            return
        frame = self.view.clear_params()
        if key == "morph":
            self.morph_ctrl.build_panel(frame)
        elif key == "filters":
            self.filters_ctrl.build_panel(frame)
        elif key == "conv":
            self.conv_ctrl.build_panel(frame)
        else:  # history
            self.history_ctrl.build_panel(frame)
        if key == "history":
            self.history_ctrl.refresh_panel()
        # Виджеты панели параметров пересоздаются через clear_params(),
        # поэтому дубли исключены; историю переключение не трогает.
        try:
            self.morph_ctrl.sync_se_fields()
        except AttributeError:
            pass
        try:
            self.conv_ctrl.refresh_info()
        except (tk.TclError, ValueError, AttributeError):
            pass

    def _to_pil(self, arr):
        if arr is None:
            return None
        return Image.fromarray(arr, mode="L")
    def refresh_images(self, status: str = "") -> None:
        try:
            exists = self.view.root.winfo_exists()
        except tk.TclError:
            return
        if not exists:
            return
        orig = self.image_model.original
        curr = self.image_model.current
        if orig is not None:
            h, w = orig.shape
            self.view.original_panel.set_image(self._to_pil(orig), f"{w}x{h} grayscale")
        else:
            self.view.original_panel.set_image(None)
        if curr is not None:
            h, w = curr.shape
            self.view.result_panel.set_image(self._to_pil(curr), f"{w}x{h} grayscale")
        else:
            self.view.result_panel.set_image(None)
        self.view.history_panel.set_entries(self.history.entries(), self.history.index)
        try:
            self.history_ctrl.refresh_panel()
        except (AttributeError, tk.TclError):
            pass
        self.view.set_undo_redo(self.history.can_undo(), self.history.can_redo())
        if status:
            self.view.set_status(status)

    def _poll_worker_results(self) -> None:
        """Consume worker results on Tk's main thread only."""
        try:
            if not self.view.root.winfo_exists():
                return
            while True:
                try:
                    message = self._worker_queue.get_nowait()
                except queue.Empty:
                    break
                if message[0] == "ok":
                    _, label, params, result = message
                    self._finish_ok(label, params, result)
                elif message[0] == "error":
                    self._finish_error(message[1])
            self.view.root.after(40, self._poll_worker_results)
        except tk.TclError:
            # The window may have been closed between the existence check and after().
            return

    def run_async(self, label: str, func, params: str = "") -> None:
        if self._busy:
            dialogs.show_info(self.view.root, "Дождитесь завершения текущей операции.")
            return
        try:
            src = self.image_model.require_current_copy()
        except ValueError as exc:
            dialogs.show_error(self.view.root, str(exc))
            return
        self._busy = True
        self.view.set_busy(True, f"{label}...")
        self.view.set_status(f"{label}...")

        self._operation_source = src.copy()

        def worker() -> None:
            try:
                result = func(src)
            except ValueError as exc:
                self._worker_queue.put(("error", str(exc)))
                return
            except Exception as exc:
                self._worker_queue.put(("error", f"Неожиданная ошибка: {exc}"))
                return
            self._worker_queue.put(("ok", label, params, result))

        threading.Thread(target=worker, daemon=True).start()

    def _alive(self) -> bool:
        try:
            return bool(self.view.root.winfo_exists())
        except tk.TclError:
            return False

    def _finish_ok(self, label, params, result) -> None:
        self._busy = False
        if not self._alive():
            self._operation_source = None
            return
        try:
            self.view.set_busy(False)
        except tk.TclError:
            self._operation_source = None
            return
        source_snapshot = self._operation_source
        self._operation_source = None
        current = self.image_model.current
        if source_snapshot is not None and (
            current is None or not np.array_equal(current, source_snapshot)
        ):
            # A menu/history action changed the image while computation was running.
            # Never apply a stale result to a different current image.
            self.refresh_images("Результат не применён: изображение изменилось во время обработки.")
            return
        try:
            self.image_model.set_current(result)
            self.history.push(result, label, params)
        except ValueError as exc:
            dialogs.show_error(self.view.root, str(exc))
            self.refresh_images()
            return
        self.refresh_images(f"Готово: {label}. {params}")

    def _finish_error(self, message: str) -> None:
        self._busy = False
        self._operation_source = None
        if not self._alive():
            return
        try:
            self.view.set_busy(False)
        except tk.TclError:
            return
        try:
            dialogs.show_error(self.view.root, message)
        except tk.TclError:
            return
        self.refresh_images("Ошибка. История не изменена.")

    def open_se_editor(self) -> None:
        def on_accept(new_se: StructuringElementModel) -> None:
            self.se_model = new_se
            try:
                self.morph_ctrl.sync_se_fields()
            except AttributeError:
                pass
            self.view.set_status(
                f"Элемент обновлён: {new_se.width}x{new_se.height}, "
                f"якорь {new_se.anchor}.")

        dlg = StructuringElementEditor(self.view.root, self.se_model, on_accept)

        def do_save() -> None:
            path = dialogs.ask_save_se(dlg)
            if not path:
                return
            try:
                dlg.se.save(path)
            except ValueError as exc:
                dialogs.show_error(dlg, str(exc))
                return
            dialogs.show_info(dlg, f"Сохранено: {path}")

        def do_load() -> None:
            path = dialogs.ask_open_se(dlg)
            if not path:
                return
            try:
                dlg.se.load(path)
            except ValueError as exc:
                dialogs.show_error(dlg, str(exc))
                return
            dlg.refresh_from_model()

        dlg.bind("<<SESave>>", lambda _e: do_save())
        dlg.bind("<<SELoad>>", lambda _e: do_load())

    def open_kernel_editor(self) -> None:
        def on_accept() -> None:
            self.conv_ctrl.refresh_info()
            self.view.set_status(f"Ядро обновлено: {self.kernel_model.summary()}")

        KernelEditorView(self.view.root, self.kernel_model, on_accept)

    def open_emboss_in_kernel_editor(self) -> None:
        from app.models.filters_model import FiltersModel as FM
        try:
            k, b = FM().emboss_kernel_info()
            self.kernel_model.set_matrix(k)
            self.kernel_model.set_bias(b)
            self.kernel_model.set_auto_normalize(False)
            self.kernel_model.set_divisor(1.0)
            self.kernel_model.set_border("default")
        except ValueError as exc:
            dialogs.show_error(self.view.root, str(exc))
            return
        self.open_kernel_editor()

    def run(self) -> None:
        self.view.root.mainloop()

