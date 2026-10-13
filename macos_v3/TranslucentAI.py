"""TranslucentAI macOS v3: the PyQt overlay backed by OpenRouter free models.

Set OPENROUTER_API_KEY in the environment (or a .env file in this directory)
before starting the app. The app keeps the original hotkeys:

    Ctrl+Alt+S  type a short answer into the active app
    Ctrl+Alt+D  show multiple-choice answer numbers in the overlay
    Ctrl+Alt+A  send answer-number progress notifications (optional Pushover)
    Ctrl+Alt+M  open settings
    Escape      quit
"""

from __future__ import annotations

import os
import sys
import threading
import time

import pyperclip
from dotenv import load_dotenv
from PyQt5.QtCore import QObject, QPoint, QSettings, QTimer, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QMainWindow,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPainter, QPen

from openrouter_client import OpenRouterClient, answer_numbers

try:
    from pynput import keyboard as pynput_keyboard
except ImportError:  # Allows the client/parser to be tested without global hotkeys.
    pynput_keyboard = None


class Spinner(QWidget):
    """Small animated circular progress indicator."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.setFixedSize(22, 22)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.hide()

    def start(self):
        self.angle = 0
        self.show()
        self.timer.start(80)

    def stop(self):
        self.timer.stop()
        self.hide()

    def advance(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(Qt.white, 2)
        painter.setPen(pen)
        painter.drawArc(self.rect().adjusted(3, 3, -3, -3), self.angle * 16, 270 * 16)


def apply_native_window_level(window, all_spaces: bool):
    """Keep a Qt overlay above normal macOS windows and optionally across Spaces."""
    try:
        from AppKit import NSApp, NSFloatingWindowLevel
        from AppKit import NSWindowCollectionBehaviorCanJoinAllSpaces
        from AppKit import NSWindowCollectionBehaviorFullScreenAuxiliary
        from AppKit import NSWindowCollectionBehaviorStationary

        behavior = (NSWindowCollectionBehaviorCanJoinAllSpaces |
                    NSWindowCollectionBehaviorStationary |
                    NSWindowCollectionBehaviorFullScreenAuxiliary) if all_spaces else 0
        for native in NSApp.windows():
            if (int(native.windowNumber()) == int(window.winId()) or
                    str(native.title()) == window.windowTitle()):
                native.setLevel_(NSFloatingWindowLevel)
                native.setHidesOnDeactivate_(False)
                native.setCanHide_(False)
                native.setCollectionBehavior_(behavior)
                native.orderFrontRegardless()
                break
    except Exception:
        pass


def fit_to_screen(x: int, y: int, width: int, height: int):
    """Keep a saved overlay rectangle visible on the monitor under its position."""
    screen = QApplication.screenAt(QPoint(x, y)) or QApplication.primaryScreen()
    geometry = screen.availableGeometry()
    width = min(max(width, 40), max(40, geometry.width() - 20))
    height = min(max(height, 28), max(28, geometry.height() - 20))
    x = max(geometry.left(), min(x, geometry.right() - width + 1))
    y = max(geometry.top(), min(y, geometry.bottom() - height + 1))
    return x, y, width, height


class Overlay(QMainWindow):
    updated = pyqtSignal(str)
    loading_changed = pyqtSignal(bool)
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.preferences = QSettings("TranslucentAI", "macos_v3")
        self.drag_offset = QPoint()
        self.setWindowTitle("TranslucentAI")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool |
                            Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel("AI", self)
        self.text_shadow = QGraphicsDropShadowEffect(self.label)
        self.text_shadow.setBlurRadius(4)
        self.text_shadow.setOffset(0, 0)
        self.text_shadow.setColor(Qt.black)
        self.label.setGraphicsEffect(self.text_shadow)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setCentralWidget(self.label)
        self.updated.connect(self.label.setText)
        self.load_preferences()

    def load_preferences(self):
        x, y, width, height = fit_to_screen(
            self.preferences.value("x", 50, type=int),
            self.preferences.value("y", 100, type=int),
            min(self.preferences.value("width", 400, type=int), 600),
            min(self.preferences.value("height", 120, type=int), 200),
        )
        self.resize(width, height)
        self.move(x, y)
        self.setWindowOpacity(self.preferences.value("opacity", 0.92, type=float))
        self.set_font_size(self.preferences.value("font_size", 24, type=int))
        # Persist any migration/clamping so the next launch uses the corrected
        # visible rectangle rather than the legacy oversized geometry.
        self.save_preferences()

    def save_preferences(self):
        self.preferences.setValue("x", self.x())
        self.preferences.setValue("y", self.y())
        self.preferences.setValue("width", self.width())
        self.preferences.setValue("height", self.height())
        self.preferences.sync()

    def closeEvent(self, event):
        self.save_preferences()
        super().closeEvent(event)

    def set_font_size(self, value: int):
        self.label.setStyleSheet(
            f"font-size: {value}px; color: white; background: transparent; "
            "border: none; padding: 0px;"
        )
        self.preferences.setValue("font_size", value)

    def set_opacity(self, value: float):
        self.setWindowOpacity(value)
        self.preferences.setValue("opacity", value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.settings_requested.emit()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            self.save_preferences()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_preferences()
            event.accept()

    def move_to_primary_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.left() + 40, screen.top() + 100)
        self.save_preferences()

    def set_all_spaces(self, enabled: bool):
        apply_native_window_level(self, enabled)


class SpinnerOverlay(QMainWindow):
    """Independent, draggable loading indicator window."""

    settings_requested = pyqtSignal()

    def __init__(self, preferences: QSettings):
        super().__init__()
        self.preferences = preferences
        self.drag_offset = QPoint()
        self.setWindowTitle("TranslucentAI Loading")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool |
                            Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.spinner = Spinner(self)
        self.spinner.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setCentralWidget(self.spinner)
        self.resize(28, 28)
        x, y, width, height = fit_to_screen(
            self.preferences.value("spinner_x", 470, type=int),
            self.preferences.value("spinner_y", 100, type=int),
            28,
            28,
        )
        self.resize(width, height)
        self.move(x, y)
        self.setWindowOpacity(self.preferences.value("spinner_opacity", 0.92, type=float))
        self.hide()

    def set_loading(self, loading: bool):
        if loading:
            self.show()
            self.spinner.start()
            apply_native_window_level(self, self.preferences.value("all_spaces", False, type=bool))
        else:
            self.spinner.stop()
            self.hide()

    def set_opacity(self, value: float):
        self.setWindowOpacity(value)
        self.preferences.setValue("spinner_opacity", value)

    def save_preferences(self):
        self.preferences.setValue("spinner_x", self.x())
        self.preferences.setValue("spinner_y", self.y())
        self.preferences.sync()

    def closeEvent(self, event):
        self.save_preferences()
        super().closeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.settings_requested.emit()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            self.save_preferences()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_preferences()
            event.accept()

    def set_all_spaces(self, enabled: bool):
        apply_native_window_level(self, enabled)


class SettingsDialog(QDialog):
    def __init__(self, overlay: Overlay, spinner: SpinnerOverlay):
        super().__init__(overlay)
        self.overlay = overlay
        self.spinner = spinner
        self.setWindowTitle("TranslucentAI Settings")
        self.setWindowFlags(Qt.Tool)
        form = QFormLayout()

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 96)
        self.font_size.setValue(overlay.preferences.value("font_size", 24, type=int))
        form.addRow("Text size", self.font_size)

        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.2, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setValue(overlay.windowOpacity())
        form.addRow("Text opacity", self.opacity)

        self.x_position = QSpinBox()
        self.x_position.setRange(-10000, 10000)
        self.x_position.setValue(overlay.x())
        form.addRow("X position", self.x_position)

        self.y_position = QSpinBox()
        self.y_position.setRange(-10000, 10000)
        self.y_position.setValue(overlay.y())
        form.addRow("Y position", self.y_position)

        self.spinner_opacity = QDoubleSpinBox()
        self.spinner_opacity.setRange(0.2, 1.0)
        self.spinner_opacity.setSingleStep(0.05)
        self.spinner_opacity.setValue(spinner.windowOpacity())
        form.addRow("Loading circle opacity", self.spinner_opacity)

        self.spinner_x = QSpinBox()
        self.spinner_x.setRange(-10000, 10000)
        self.spinner_x.setValue(spinner.x())
        form.addRow("Loading circle X", self.spinner_x)

        self.spinner_y = QSpinBox()
        self.spinner_y.setRange(-10000, 10000)
        self.spinner_y.setValue(spinner.y())
        form.addRow("Loading circle Y", self.spinner_y)

        self.all_spaces = QCheckBox("Show overlay on every macOS Space")
        self.all_spaces.setChecked(overlay.preferences.value("all_spaces", False, type=bool))
        form.addRow(self.all_spaces)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.apply)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(QLabel("Left-drag the text or loading circle independently; right-click either one for settings."))
        layout.addWidget(buttons)

    def apply(self):
        self.overlay.set_font_size(self.font_size.value())
        self.overlay.set_opacity(self.opacity.value())
        self.overlay.move(self.x_position.value(), self.y_position.value())
        self.spinner.set_opacity(self.spinner_opacity.value())
        self.spinner.move(self.spinner_x.value(), self.spinner_y.value())
        self.overlay.preferences.setValue("all_spaces", self.all_spaces.isChecked())
        self.overlay.set_all_spaces(self.all_spaces.isChecked())
        self.spinner.set_all_spaces(self.all_spaces.isChecked())
        self.overlay.save_preferences()
        self.spinner.save_preferences()
        self.accept()


class AppController(QObject):
    def __init__(self, overlay: Overlay, spinner: SpinnerOverlay, client: OpenRouterClient):
        super().__init__()
        self.overlay = overlay
        self.spinner = spinner
        self.client = client

    def _clipboard(self) -> str:
        return pyperclip.paste().strip()

    def show_settings(self):
        SettingsDialog(self.overlay, self.spinner).exec_()

    def _run(self, work) -> None:
        self.overlay.loading_changed.emit(True)

        def worker():
            try:
                self.overlay.updated.emit(work())
            except Exception as exc:  # Surface errors in the overlay instead of killing the hotkey thread.
                self.overlay.updated.emit(f"Error: {exc}")
            finally:
                self.overlay.loading_changed.emit(False)
        threading.Thread(target=worker, daemon=True).start()

    def type_answer(self) -> None:
        prompt = self._clipboard()
        if not prompt:
            self.overlay.updated.emit("Clipboard is empty")
            return

        def work():
            response = self.client.chat(
                "Answer the following question in 10-20 words, like a student. "
                f"Question: {prompt}"
            )
            if pynput_keyboard is None:
                return response
            pynput_keyboard.Controller().write(response, interval=0.01)
            return "Typed answer"

        self._run(work)

    def show_numbers(self) -> None:
        prompt = self._clipboard()
        if not prompt:
            self.overlay.updated.emit("Clipboard is empty")
            return
        self._run(lambda: ", ".join(answer_numbers(self.client.chat(
            "For this multiple-choice question, output ONLY the correct answer "
            "number(s), separated by commas. If options are labeled A, B, C, "
            "D, convert them to 1, 2, 3, 4. Question: " + prompt
        ))) or "No answer numbers")

    def notify_numbers(self) -> None:
        """Optional v1-compatible Pushover mode; inactive unless configured."""
        prompt = self._clipboard()
        if not prompt:
            self.overlay.updated.emit("Clipboard is empty")
            return
        self._run(lambda: self._notify(answer_numbers(self.client.chat(
            "For this multiple-choice question, output ONLY the correct answer "
            "number(s), separated by commas. If options are labeled A, B, C, "
            "D, convert them to 1, 2, 3, 4. Question: " + prompt
        ))))

    def _notify(self, numbers: list[str]) -> str:
        token = os.getenv("PUSHOVER_API_TOKEN", "")
        user = os.getenv("PUSHOVER_USER_KEY", "")
        if not token or not user:
            return ", ".join(numbers) or "No answer numbers"
        import requests

        for number in numbers:
            for index in range(int(number)):
                requests.post(
                    "https://api.pushover.net/1/messages.json",
                    data={"token": token, "user": user, "title": "TranslucentAI", "message": f"{index + 1}/{number}"},
                    timeout=15,
                ).raise_for_status()
                time.sleep(1)
        return "Notifications sent"


def main() -> int:
    load_dotenv()
    if pynput_keyboard is None:
        raise RuntimeError("Install pynput to use the global hotkeys")

    app = QApplication(sys.argv)
    overlay = Overlay()
    spinner = SpinnerOverlay(overlay.preferences)
    overlay.show()
    # Persist state before Qt tears down either overlay, including Escape and
    # other normal application shutdown paths.
    app.aboutToQuit.connect(overlay.save_preferences)
    app.aboutToQuit.connect(spinner.save_preferences)
    configured_models = tuple(
        model.strip() for model in os.getenv("OPENROUTER_MODELS", "").split(",") if model.strip()
    )
    controller = AppController(
        overlay,
        spinner,
        OpenRouterClient(os.getenv("OPENROUTER_API_KEY", ""), models=configured_models or None),
    )
    overlay.settings_requested.connect(controller.show_settings)
    spinner.settings_requested.connect(controller.show_settings)
    overlay.loading_changed.connect(spinner.set_loading)
    overlay.set_all_spaces(overlay.preferences.value("all_spaces", False, type=bool))
    spinner.set_all_spaces(overlay.preferences.value("all_spaces", False, type=bool))
    # Re-assert the native level after macOS changes the active application or Space.
    native_level_timer = QTimer(overlay)
    native_level_timer.timeout.connect(
        lambda: overlay.set_all_spaces(overlay.preferences.value("all_spaces", False, type=bool))
    )
    native_level_timer.timeout.connect(
        lambda: spinner.set_all_spaces(overlay.preferences.value("all_spaces", False, type=bool))
    )
    native_level_timer.start(1000)

    # These QObject slots are queued back onto Qt's GUI thread when emitted by
    # pynput's listener thread.
    overlay.quit_requested.connect(overlay.close)
    overlay.quit_requested.connect(spinner.close)
    overlay.quit_requested.connect(app.quit)

    pressed_keys = set()

    def key_name(key):
        if key in (pynput_keyboard.Key.ctrl, pynput_keyboard.Key.ctrl_l, pynput_keyboard.Key.ctrl_r):
            return "ctrl"
        if key in (pynput_keyboard.Key.alt, pynput_keyboard.Key.alt_l, pynput_keyboard.Key.alt_r):
            return "alt"
        if key == pynput_keyboard.Key.esc:
            return "esc"
        return getattr(key, "char", None)

    def on_press(key):
        name = key_name(key)
        if name == "esc":
            overlay.quit_requested.emit()
            return
        if not name:
            return
        pressed_keys.add(name.lower())
        if not {"ctrl", "alt"}.issubset(pressed_keys):
            return
        actions = {
            "s": controller.type_answer,
            "d": controller.show_numbers,
            "a": controller.notify_numbers,
            "m": lambda: overlay.settings_requested.emit(),
        }
        action = actions.get(name.lower())
        if action:
            action()

    def on_release(key):
        name = key_name(key)
        if name:
            pressed_keys.discard(name.lower())

    keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    print("Ctrl+Alt+S: type answer | Ctrl+Alt+D: show numbers | Ctrl+Alt+A: notify | Ctrl+Alt+M: settings | Esc: quit")
    result = app.exec_()
    keyboard_listener.stop()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
