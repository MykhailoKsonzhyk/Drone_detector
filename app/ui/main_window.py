# app/ui/main_window.py

import os
import cv2
import json
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from detector import DroneDetector
from camera import CameraThread
from video_writer import VideoWriter

PHOTOS_DIR = "photos"

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0d0d;
    color: #e8e8e8;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QTabWidget::pane {
    border: none;
    background-color: #0d0d0d;
}
QTabBar::tab {
    background-color: #1e1e1e;
    color: #aaaaaa;
    border: none;
    border-right: 1px solid #2a2a2a;
    padding: 13px 36px;
    font-size: 13px;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #ffffff;
    border-bottom: 2px solid #00d4ff;
    background-color: #0d0d0d;
}
QTabBar::tab:hover:!selected {
    color: #cccccc;
    background-color: #252525;
}
QPushButton {
    background-color: #383838;
    color: #e8e8e8;
    border: 1px solid #505050;
    border-radius: 7px;
    padding: 9px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #444444;
    border-color: #00d4ff;
    color: #ffffff;
}
QPushButton:disabled {
    color: #505050;
    border-color: #2e2e2e;
    background-color: #222222;
}
QPushButton#btn_record {
    background-color: #2a1515;
    border-color: #5a2020;
    color: #cc4444;
}
QPushButton#btn_record:hover {
    background-color: #c0392b;
    border-color: #e74c3c;
    color: #ffffff;
}
QPushButton#btn_record:disabled {
    background-color: #1a0a0a;
    border-color: #2a1515;
    color: #553333;
}
QPushButton#btn_exit {
    background-color: #252525;
    border-color: #383838;
    color: #666666;
    padding: 8px 16px;
    font-size: 12px;
}
QPushButton#btn_exit:hover {
    border-color: #ff4444;
    color: #ff4444;
    background-color: #1e1010;
}
QPushButton#btn_delete {
    color: #cc4444;
    border-color: #5a1a1a;
    background-color: #2a1515;
}
QPushButton#btn_delete:hover {
    background-color: #c0392b;
    color: white;
    border-color: #e74c3c;
}
QPushButton#btn_save_photo {
    background-color: #0d2233;
    border-color: #00d4ff;
    color: #00d4ff;
}
QPushButton#btn_save_photo:hover {
    background-color: #00d4ff;
    color: #000000;
}
QPushButton#btn_retry {
    background-color: #1a2a1a;
    border-color: #2ecc71;
    color: #2ecc71;
}
QPushButton#btn_retry:hover {
    background-color: #2ecc71;
    color: #000000;
}
QListWidget {
    background-color: #161616;
    border: 1px solid #252525;
    border-radius: 8px;
    color: #cccccc;
    font-size: 12px;
    outline: none;
}
QListWidget::item {
    padding: 10px 14px;
    border-bottom: 1px solid #1e1e1e;
}
QListWidget::item:hover { background-color: #1e1e1e; }
QListWidget::item:selected {
    background-color: #0d2233;
    color: #00d4ff;
}
QSlider::groove:horizontal {
    background: #2e2e2e;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #00d4ff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #00d4ff;
    border-radius: 2px;
}
QLineEdit {
    background-color: #1e1e1e;
    border: 1px solid #333333;
    border-radius: 6px;
    color: #ffffff;
    padding: 9px 13px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #00d4ff; }
QScrollBar:vertical {
    background: #161616;
    width: 5px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #333333;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #00d4ff; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0px; }
"""

CLASS_COLORS = {
    'drone':      '#00d4ff',
    'airplane':   '#2ecc71',
    'helicopter': '#f39c12',
    'bird':       '#ff69b4',
}
CLASS_ICONS = {
    'drone':      '🛸',
    'airplane':   '✈️',
    'helicopter': '🚁',
    'bird':       '🐦',
}

PANEL_STYLE = """
    QWidget {
        background-color: #1c1c1c;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
    }
"""


class NameDialog(QDialog):
    def __init__(self, parent=None, current_name="",
                 title="Назва", placeholder="Введіть назву"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 155)
        self.setStyleSheet(STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        label = QLabel("Введіть назву:")
        label.setStyleSheet("color: #999999; font-size: 13px;")
        layout.addWidget(label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(placeholder)
        self.name_input.setText(current_name)
        self.name_input.selectAll()
        layout.addWidget(self.name_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_cancel = QPushButton("Скасувати")
        btn_ok = QPushButton("Підтвердити")
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #0d2233;
                border: 1px solid #00d4ff;
                color: #00d4ff;
                border-radius: 7px;
                padding: 9px 20px;
            }
            QPushButton:hover {
                background-color: #00d4ff;
                color: #000000;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def get_name(self) -> str:
        return self.name_input.text().strip()


class DetectionTab(QWidget):
    def __init__(self, detector, video_writer, parent=None):
        super().__init__(parent)
        self.detector          = detector
        self.video_writer      = video_writer
        self.camera_thread     = None
        self._want_record      = False
        self._record_ready     = False
        self._current_source   = None
        self._total_frames     = 0
        self._is_paused        = False
        self._is_video_mode    = False
        self._last_photo       = None
        self._last_photo_path  = None
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        root.addLayout(self._build_video_panel(), stretch=3)
        root.addLayout(self._build_right_panel(), stretch=1)

    def _build_video_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        video_wrapper = QWidget()
        video_wrapper.setStyleSheet("""
            QWidget {
                background-color: #111111;
                border: 1px solid #1e1e1e;
                border-radius: 10px;
            }
        """)
        vw_layout = QVBoxLayout(video_wrapper)
        vw_layout.setContentsMargins(0, 0, 0, 0)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(720, 460)
        self._show_placeholder()
        vw_layout.addWidget(self.video_label)
        layout.addWidget(video_wrapper)

        # Прогрес бар
        self.detect_progress = QSlider(Qt.Orientation.Horizontal)
        self.detect_progress.setRange(0, 100)
        self.detect_progress.setValue(0)
        self.detect_progress.setEnabled(False)
        self.detect_progress.sliderPressed.connect(self._on_progress_pressed)
        self.detect_progress.sliderReleased.connect(self._on_progress_released)
        layout.addWidget(self.detect_progress)

        # Кнопки під відео
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        self.btn_restart = QPushButton("⏮")
        self.btn_restart.setFixedWidth(44)
        self.btn_restart.setToolTip("Почати з початку")
        self.btn_restart.setEnabled(False)
        self.btn_restart.setVisible(False)
        self.btn_restart.clicked.connect(self._restart_video)

        self.btn_play_pause = QPushButton("⏸")
        self.btn_play_pause.setFixedWidth(44)
        self.btn_play_pause.setToolTip("Пауза / Відтворити")
        self.btn_play_pause.setEnabled(False)
        self.btn_play_pause.setVisible(False)
        self.btn_play_pause.clicked.connect(self._toggle_pause)

        self.btn_save_photo = QPushButton("💾  Зберегти фото")
        self.btn_save_photo.setObjectName("btn_save_photo")
        self.btn_save_photo.setVisible(False)
        self.btn_save_photo.clicked.connect(self._save_photo)

        self.btn_retry_photo = QPushButton("🔄  Повторити")
        self.btn_retry_photo.setObjectName("btn_retry")
        self.btn_retry_photo.setVisible(False)
        self.btn_retry_photo.clicked.connect(self._retry_photo)

        self.btn_record = QPushButton("⏺  Записати")
        self.btn_record.setObjectName("btn_record")
        self.btn_record.setEnabled(False)
        self.btn_record.setVisible(False)
        self.btn_record.clicked.connect(self.toggle_record)

        self.btn_stop = QPushButton("Зупинити детекцію")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_stream)

        bottom_row.addWidget(self.btn_restart)
        bottom_row.addWidget(self.btn_play_pause)
        bottom_row.addWidget(self.btn_save_photo)
        bottom_row.addWidget(self.btn_retry_photo)
        bottom_row.addStretch()
        bottom_row.addWidget(self.btn_record)
        bottom_row.addWidget(self.btn_stop)
        layout.addLayout(bottom_row)

        # Слайдер впевненості
        conf_wrap = QWidget()
        conf_wrap.setStyleSheet("""
            QWidget {
                background-color: #1c1c1c;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
        """)
        conf_wrap.setFixedHeight(36)
        conf_layout = QHBoxLayout(conf_wrap)
        conf_layout.setContentsMargins(12, 0, 12, 0)
        conf_layout.setSpacing(10)

        lbl = QLabel("Поріг впевненості:")
        lbl.setStyleSheet("color: #ffffff; font-size: 12px;")
        self.conf_val = QLabel("45%")
        self.conf_val.setStyleSheet(
            "color: #00d4ff; font-size: 12px; min-width: 34px;"
        )
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setRange(10, 95)
        self.conf_slider.setValue(45)
        self.conf_slider.valueChanged.connect(self._on_conf)
        conf_layout.addWidget(lbl)
        conf_layout.addWidget(self.conf_slider)
        conf_layout.addWidget(self.conf_val)
        layout.addWidget(conf_wrap)

        return layout

    def _build_right_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        src_title = QLabel("Джерело")
        src_title.setStyleSheet(
            "font-size: 13px; font-weight: 600; color: #666666;"
        )
        layout.addWidget(src_title)

        self.btn_camera = QPushButton("📷  Камера")
        self.btn_file   = QPushButton("📂  Відкрити відео")
        self.btn_photo  = QPushButton("🖼️  Відкрити фото")
        self.btn_camera.clicked.connect(self.start_camera)
        self.btn_file.clicked.connect(lambda: self.open_file())
        self.btn_photo.clicked.connect(self.open_photo)
        for btn in [self.btn_camera, self.btn_file, self.btn_photo]:
            layout.addWidget(btn)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #1e1e1e; margin: 4px 0;")
        layout.addWidget(line)

        stats_title = QLabel("Детекція")
        stats_title.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #ffffff;"
        )
        layout.addWidget(stats_title)

        self.counters = {}
        for cls in ['drone', 'airplane', 'helicopter', 'bird']:
            layout.addWidget(self._make_counter_card(cls))

        layout.addSpacing(4)

        info = QWidget()
        info.setStyleSheet(PANEL_STYLE)
        info_l = QVBoxLayout(info)
        info_l.setContentsMargins(12, 8, 12, 8)
        info_l.setSpacing(3)
        self.fps_label = QLabel("FPS: —")
        self.fps_label.setStyleSheet("color: #444444; font-size: 11px;")
        self.status_label = QLabel("Очікування...")
        self.status_label.setStyleSheet("color: #00d4ff; font-size: 11px;")
        info_l.addWidget(self.fps_label)
        info_l.addWidget(self.status_label)
        layout.addWidget(info)

        layout.addStretch()

        btn_exit = QPushButton("✕  Вийти")
        btn_exit.setObjectName("btn_exit")
        btn_exit.clicked.connect(QApplication.instance().quit)
        layout.addWidget(btn_exit)

        return layout

    def _make_counter_card(self, cls):
        card = QWidget()
        card.setStyleSheet(PANEL_STYLE)
        row = QHBoxLayout(card)
        row.setContentsMargins(12, 8, 12, 8)
        icon = QLabel(CLASS_ICONS[cls])
        icon.setFixedWidth(22)
        icon.setStyleSheet("font-size: 15px;")
        name = QLabel(cls.capitalize())
        name.setStyleSheet(f"color: {CLASS_COLORS[cls]}; font-size: 12px;")
        count = QLabel("0")
        count.setAlignment(Qt.AlignmentFlag.AlignRight)
        count.setStyleSheet(f"""
            color: {CLASS_COLORS[cls]};
            font-size: 26px;
            font-weight: bold;
        """)
        row.addWidget(icon)
        row.addWidget(name)
        row.addWidget(count)
        self.counters[cls] = count
        return card

    def _show_placeholder(self):
        self.video_label.clear()
        self.video_label.setText(
            "📷\n\nОберіть джерело відео або фото\nдля початку детекції"
        )
        self.video_label.setStyleSheet("""
            background-color: transparent;
            font-size: 16px;
            color: #ffffff;
            border-radius: 10px;
        """)

    def _set_video_controls_visible(self, visible: bool):
        self.btn_restart.setVisible(visible)
        self.btn_play_pause.setVisible(visible)
        self.detect_progress.setEnabled(visible)
        self.btn_record.setVisible(visible)

    def _make_thread(self, source, with_detector=True):
        t = CameraThread()
        t.set_source(source)
        if with_detector:
            t.set_detector(self.detector)
        t.frame_ready.connect(self._on_frame)
        t.fps_updated.connect(self._on_fps)
        t.error_occurred.connect(self._on_error)
        t.finished.connect(self._on_finished)
        return t

    def _stop_thread_only(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        self._is_paused = False

    def start_camera(self):
        self.stop_stream()
        self._current_source = 0
        self._is_video_mode  = False
        self._set_video_controls_visible(False)
        self.btn_save_photo.setVisible(False)
        self.btn_retry_photo.setVisible(False)
        self.btn_record.setVisible(True)
        self.btn_record.setEnabled(True)
        self.camera_thread = self._make_thread(0)
        self.camera_thread.start()
        self.btn_stop.setEnabled(True)
        self._set_active("Камера активна...")

    def open_file(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "Відкрити відео", "",
                "Відео файли (*.mp4 *.avi *.mov *.mkv)"
            )
        if not path:
            return
        self.stop_stream()
        self._current_source = path
        self._is_video_mode  = True
        self._is_paused      = False

        cap = cv2.VideoCapture(path)
        self._total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        self.detect_progress.setRange(0, max(1, self._total_frames))
        self.detect_progress.setValue(0)

        self._set_video_controls_visible(True)
        self.btn_restart.setEnabled(True)
        self.btn_play_pause.setEnabled(True)
        self.btn_play_pause.setText("⏸")
        self.btn_save_photo.setVisible(False)
        self.btn_retry_photo.setVisible(False)
        self.btn_record.setEnabled(True)

        self.camera_thread = self._make_thread(path)
        self.camera_thread.start()
        self.btn_stop.setEnabled(True)
        self._set_active(f"▶ {os.path.basename(path)}")

    def open_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Відкрити фото", "",
            "Зображення (*.jpg *.jpeg *.png *.bmp *.webp)"
        )
        if not path:
            return
        self.stop_stream()
        frame = cv2.imread(path)
        if frame is None:
            QMessageBox.warning(self, "Помилка", "Не вдалось відкрити фото")
            return

        self._last_photo_path = path
        annotated, counts = self.detector.detect(frame)
        self._last_photo = annotated.copy()

        for cls, count in counts.items():
            if cls in self.counters:
                self.counters[cls].setText(str(count))

        self._show_annotated(annotated)

        self._is_video_mode = False
        self._set_video_controls_visible(False)
        self.btn_save_photo.setVisible(True)
        self.btn_retry_photo.setVisible(True)
        self.btn_stop.setEnabled(True)

        found = [f"{v} {k}" for k, v in counts.items() if v > 0]
        if found:
            msg = ", ".join(found)
            self.status_label.setText(f"Фото: {msg}")
        else:
            self.status_label.setText(
                "Нічого не знайдено — спробуйте понизити поріг впевненості"
            )
        self.fps_label.setText("")

    def _retry_photo(self):
        """Повторна детекція фото з поточним порогом впевненості"""
        if not self._last_photo_path:
            return
        frame = cv2.imread(self._last_photo_path)
        if frame is None:
            return

        annotated, counts = self.detector.detect(frame)
        self._last_photo = annotated.copy()

        for cls, count in counts.items():
            if cls in self.counters:
                self.counters[cls].setText(str(count))

        self._show_annotated(annotated)

        found = [f"{v} {k}" for k, v in counts.items() if v > 0]
        if found:
            msg = ", ".join(found)
            self.status_label.setText(f"Фото: {msg}")
        else:
            self.status_label.setText(
                "Нічого не знайдено — спробуйте понизити поріг впевненості"
            )

    def _show_annotated(self, annotated):
        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
        self.video_label.setStyleSheet(
            "background-color: transparent; border-radius: 10px;"
        )

    def _save_photo(self):
        if self._last_photo is None:
            return
        dialog = NameDialog(
            self, title="Зберегти фото",
            placeholder="Наприклад: Дрон над полем"
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        os.makedirs(PHOTOS_DIR, exist_ok=True)
        name = dialog.get_name()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = name.replace(" ", "_") if name else ""
        filename = f"{safe_name}_{timestamp}.jpg" \
                   if safe_name else f"photo_{timestamp}.jpg"
        path = os.path.join(PHOTOS_DIR, filename)

        cv2.imwrite(path, self._last_photo)
        meta_path = path.replace('.jpg', '_meta.json')
        counts = {cls: int(self.counters[cls].text())
                  for cls in self.counters}
        meta = {
            'name': name or filename,
            'path': path,
            'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'detections': counts
        }
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        self.status_label.setText(f"Фото збережено: {filename}")
        self.window().refresh_recordings()

    def open_recording(self, path: str):
        self.open_file(path)

    def _set_active(self, status):
        self.status_label.setText(status)
        self.video_label.setStyleSheet(
            "background-color: transparent; border-radius: 10px;"
        )

    def _toggle_pause(self):
        if not self.camera_thread:
            return
        if self._is_paused:
            self.camera_thread.resume()
            self._is_paused = False
            self.btn_play_pause.setText("⏸")
        else:
            self.camera_thread.pause()
            self._is_paused = True
            self.btn_play_pause.setText("▶")

    def _restart_video(self):
        if not self._current_source or self._current_source == 0:
            return
        src = self._current_source
        self._stop_thread_only()
        self.detect_progress.setValue(0)
        self._want_record  = False
        self._record_ready = False
        if self.video_writer.recording:
            self.video_writer.stop()
            self.btn_record.setText("⏺  Записати")
            self.btn_record.setStyleSheet("")

        self.camera_thread = self._make_thread(src)
        self.camera_thread.start()
        self.btn_play_pause.setText("⏸")
        self.btn_stop.setEnabled(True)
        self.btn_record.setEnabled(True)
        self.status_label.setText(f"▶ {os.path.basename(str(src))}")

    def _on_progress_pressed(self):
        if self.camera_thread and not self._is_paused:
            self.camera_thread.pause()
            self._is_paused = True
            self.btn_play_pause.setText("▶")

    def _on_progress_released(self):
        value = self.detect_progress.value()
        if self.camera_thread and \
           self.camera_thread._cap_ref is not None:
            self.camera_thread._cap_ref.set(
                cv2.CAP_PROP_POS_FRAMES, value
            )
        if self.camera_thread:
            self.camera_thread.resume()
            self._is_paused = False
            self.btn_play_pause.setText("⏸")

    def toggle_record(self):
        if not self._want_record:
            if self._is_video_mode and not self._is_paused:
                if self.camera_thread:
                    self.camera_thread.pause()
                    self._is_paused = True
                    self.btn_play_pause.setText("▶")

            dialog = NameDialog(
                self, title="Назва запису",
                placeholder="Наприклад: Тест дрона над полем"
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                if self._is_paused and self.camera_thread:
                    self.camera_thread.resume()
                    self._is_paused = False
                    self.btn_play_pause.setText("⏸")
                return

            if self._is_paused and self.camera_thread:
                self.camera_thread.resume()
                self._is_paused = False
                self.btn_play_pause.setText("⏸")

            self._record_name  = dialog.get_name() or None
            self._want_record  = True
            self._record_ready = False

            self.btn_record.setText("⏹  Зупинити запис")
            self.btn_record.setStyleSheet("""
                QPushButton {
                    background-color: #c0392b;
                    border: 1px solid #e74c3c;
                    color: #ffffff;
                    border-radius: 7px;
                    padding: 9px 16px;
                }
                QPushButton:hover { background-color: #e74c3c; }
            """)
            self.status_label.setText("⏺ Підготовка...")
        else:
            self._stop_recording()

    def _stop_recording(self):
        self._want_record  = False
        self._record_ready = False
        if self.video_writer.recording:
            self.video_writer.stop()
        self.btn_record.setText("⏺  Записати")
        self.btn_record.setStyleSheet("")
        self.btn_record.setEnabled(True)
        self.status_label.setText("Запис збережено ✓")
        self.window().refresh_recordings()

    def stop_stream(self):
        if self.video_writer.recording:
            self.video_writer.stop()
            self.window().refresh_recordings()
        self._want_record      = False
        self._record_ready     = False
        self._is_paused        = False
        self._last_photo       = None
        self._last_photo_path  = None
        self._current_source   = None

        self.btn_record.setText("⏺  Записати")
        self.btn_record.setStyleSheet("")

        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.is_running = False  # ← примусово
            self.camera_thread.is_paused  = False  # ← знімаємо паузу
            self.camera_thread.quit()              # ← зупиняємо Qt потік
            self.camera_thread.wait(2000)          # ← чекаємо max 2 сек
            self.camera_thread = None

        self.btn_record.setEnabled(False)
        self.btn_record.setVisible(False)
        self.btn_stop.setEnabled(False)
        self.btn_restart.setEnabled(False)
        self.btn_restart.setVisible(False)
        self.btn_play_pause.setEnabled(False)
        self.btn_play_pause.setVisible(False)
        self.btn_save_photo.setVisible(False)
        self.btn_retry_photo.setVisible(False)
        self.detect_progress.setEnabled(False)
        self.detect_progress.setValue(0)
        self.fps_label.setText("FPS: —")
        self.status_label.setText("Очікування...")
        for lbl in self.counters.values():
            lbl.setText("0")
        self._show_placeholder()

    def _on_frame(self, data):
        original, annotated, counts = data

        if self._is_video_mode and \
           self.camera_thread and \
           self.camera_thread._cap_ref is not None:
            try:
                pos = int(self.camera_thread._cap_ref.get(
                    cv2.CAP_PROP_POS_FRAMES
                ))
                self.detect_progress.setValue(pos)
            except Exception:
                pass

        if self._want_record:
            h, w = annotated.shape[:2]
            if not self._record_ready:
                name = getattr(self, '_record_name', None)
                self.video_writer.start(w, h, fps=30.0, name=name)
                self._record_ready = True
                self.status_label.setText("⏺ Запис...")
            self.video_writer.write(annotated, counts)

        for cls, count in counts.items():
            if cls in self.counters:
                self.counters[cls].setText(str(count))

        rgb = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def _on_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.1f}")

    def _on_error(self, msg):
        QMessageBox.warning(self, "Помилка", msg)
        self.stop_stream()

    def _on_finished(self):
        if self.video_writer.recording:
            self.video_writer.stop()
            self._want_record  = False
            self._record_ready = False
            self.window().refresh_recordings()

        self.btn_record.setText("⏺  Записати")
        self.btn_record.setStyleSheet("")
        self.btn_record.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_play_pause.setEnabled(False)
        self.status_label.setText("Завершено — можна перезапустити")

    def _on_conf(self, value):
        self.detector.set_confidence(value / 100.0)
        self.conf_val.setText(f"{value}%")


class RecordingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recordings_dir    = "recordings"
        self._cap              = None
        self.play_thread       = None
        self._is_playing       = False
        self._total_frames     = 0
        self._current_frame    = 0
        self._current_is_photo = False
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)
        root.addLayout(self._build_list_panel(), stretch=1)
        root.addLayout(self._build_player_panel(), stretch=2)

    def _build_list_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        title = QLabel("Записи")
        title.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #ffffff;"
        )
        layout.addWidget(title)

        self.recordings_list = QListWidget()
        self.recordings_list.currentRowChanged.connect(self._on_select)
        self.recordings_list.itemDoubleClicked.connect(self._rename_item)
        layout.addWidget(self.recordings_list)

        hint = QLabel("Подвійний клік — перейменувати")
        hint.setStyleSheet("color: #2e2e2e; font-size: 11px;")
        layout.addWidget(hint)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_rename = QPushButton("✏️  Перейменувати")
        self.btn_delete = QPushButton("🗑  Видалити")
        self.btn_delete.setObjectName("btn_delete")
        self.btn_rename.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_rename.clicked.connect(self._rename_selected)
        self.btn_delete.clicked.connect(self._delete_selected)
        btn_row.addWidget(self.btn_rename)
        btn_row.addWidget(self.btn_delete)
        layout.addLayout(btn_row)

        return layout

    def _build_player_panel(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)

        player_wrapper = QWidget()
        player_wrapper.setStyleSheet("""
            QWidget {
                background-color: #111111;
                border: 1px solid #1e1e1e;
                border-radius: 10px;
            }
        """)
        pw_layout = QVBoxLayout(player_wrapper)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        self.player_label = QLabel()
        self.player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_label.setMinimumSize(580, 330)
        self.player_label.setText("🎬\n\nОберіть запис зі списку")
        self.player_label.setStyleSheet(
            "font-size: 15px; color: #ffffff; background: transparent;"
        )
        pw_layout.addWidget(self.player_label)
        layout.addWidget(player_wrapper)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.setEnabled(False)
        layout.addWidget(self.progress_slider)

        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)
        self.btn_restart_rec = QPushButton("⏮")
        self.btn_restart_rec.setFixedWidth(44)
        self.btn_play_pause = QPushButton("▶  Відтворити")
        self.btn_restart_rec.setEnabled(False)
        self.btn_play_pause.setEnabled(False)
        self.btn_restart_rec.clicked.connect(self._restart)
        self.btn_play_pause.clicked.connect(self._toggle_play)
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("color: #444444; font-size: 12px;")
        ctrl_row.addWidget(self.btn_restart_rec)
        ctrl_row.addWidget(self.btn_play_pause)
        ctrl_row.addStretch()
        ctrl_row.addWidget(self.time_label)
        layout.addLayout(ctrl_row)

        stats_lbl = QLabel("Статистика детекції")
        stats_lbl.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #444444;"
        )
        layout.addWidget(stats_lbl)

        stats_widget = QWidget()
        stats_widget.setStyleSheet(PANEL_STYLE)
        stats_row = QHBoxLayout(stats_widget)
        stats_row.setContentsMargins(16, 12, 16, 12)

        self.stat_labels = {}
        for cls in ['drone', 'airplane', 'helicopter', 'bird']:
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)
            col.setSpacing(2)
            icon = QLabel(CLASS_ICONS[cls])
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon.setStyleSheet("font-size: 16px;")
            val = QLabel("—")
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val.setStyleSheet(f"""
                color: {CLASS_COLORS[cls]};
                font-size: 22px;
                font-weight: bold;
            """)
            name_lbl = QLabel(cls.capitalize())
            name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_lbl.setStyleSheet(
                f"color: {CLASS_COLORS[cls]}; font-size: 11px;"
            )
            col.addWidget(icon)
            col.addWidget(val)
            col.addWidget(name_lbl)
            stats_row.addLayout(col)
            self.stat_labels[cls] = val
        layout.addWidget(stats_widget)

        self.meta_label = QLabel("")
        self.meta_label.setStyleSheet("color: #333333; font-size: 11px;")
        layout.addWidget(self.meta_label)
        return layout

    def refresh(self):
        self.recordings_list.clear()

        # Відео — фіолетовий
        if os.path.exists(self.recordings_dir):
            files = sorted(
                [f for f in os.listdir(self.recordings_dir)
                 if f.endswith('.mp4')],
                reverse=True
            )
            for f in files:
                path = os.path.join(self.recordings_dir, f)
                stats = VideoWriter.load_stats(path)
                display = (stats['name']
                           if stats and stats.get('name') else f)
                item = QListWidgetItem(f"🎬 {display}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setData(Qt.ItemDataRole.UserRole + 1, 'video')
                item.setForeground(QColor('#a855f7'))  # фіолетовий
                self.recordings_list.addItem(item)

        # Фото — зелений
        if os.path.exists(PHOTOS_DIR):
            photos = sorted(
                [f for f in os.listdir(PHOTOS_DIR)
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
                reverse=True
            )
            for f in photos:
                path = os.path.join(PHOTOS_DIR, f)
                meta = self._load_photo_meta(path)
                display = meta.get('name', f) if meta else f
                item = QListWidgetItem(f"🖼 {display}")
                item.setData(Qt.ItemDataRole.UserRole, path)
                item.setData(Qt.ItemDataRole.UserRole + 1, 'photo')
                item.setForeground(QColor('#2ecc71'))  # зелений
                self.recordings_list.addItem(item)

    @staticmethod
    def _load_photo_meta(photo_path: str):
        for ext in ['.jpg', '.jpeg', '.png']:
            meta_path = photo_path.replace(ext, '_meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return None

    def _get_selected(self):
        row = self.recordings_list.currentRow()
        if row < 0:
            return None, None, None
        item = self.recordings_list.item(row)
        return (item,
                item.data(Qt.ItemDataRole.UserRole),
                item.data(Qt.ItemDataRole.UserRole + 1))

    def _on_select(self, row):
        if row < 0:
            return
        item = self.recordings_list.item(row)
        path  = item.data(Qt.ItemDataRole.UserRole)
        ftype = item.data(Qt.ItemDataRole.UserRole + 1)

        self.btn_rename.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self._stop_player()
        self._current_is_photo = (ftype == 'photo')

        if ftype == 'photo':
            self._load_photo_view(path)
        else:
            self._load_video_stats(path)
            self._load_video(path)

    def _load_photo_view(self, path):
        # Ховаємо кнопки відтворення для фото
        self.btn_restart_rec.setEnabled(False)
        self.btn_play_pause.setEnabled(False)
        self.progress_slider.setEnabled(False)
        self.progress_slider.setValue(0)
        self.time_label.setText("")

        frame = cv2.imread(path)
        if frame is None:
            return
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.player_label.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self.player_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

        meta = self._load_photo_meta(path)
        if meta and 'detections' in meta:
            for cls, val in meta['detections'].items():
                if cls in self.stat_labels:
                    self.stat_labels[cls].setText(str(val))
            self.meta_label.setText(
                f"📷 {meta.get('date', '')}   📁 {os.path.basename(path)}"
            )
        else:
            for lbl in self.stat_labels.values():
                lbl.setText("—")
            self.meta_label.setText(f"📷 {os.path.basename(path)}")

    def _load_video_stats(self, path):
        stats = VideoWriter.load_stats(path)
        if stats:
            for cls, val in stats['detections'].items():
                if cls in self.stat_labels:
                    self.stat_labels[cls].setText(str(val))
            self.meta_label.setText(
                f"📅 {stats.get('date', '')}   "
                f"🎞 {stats.get('frames', 0)} кадрів"
            )
        else:
            for lbl in self.stat_labels.values():
                lbl.setText("—")
            self.meta_label.setText("")

    def _load_video(self, path):
        if self._cap:
            self._cap.release()
        self._cap = cv2.VideoCapture(path)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._current_frame = 0
        self.progress_slider.setRange(0, max(1, self._total_frames))
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(True)
        self.btn_restart_rec.setEnabled(True)
        self.btn_play_pause.setEnabled(True)
        self.btn_play_pause.setText("▶  Відтворити")
        self._show_frame(0)

    def _show_frame(self, idx):
        if not self._cap:
            return
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = self._cap.read()
        if ret:
            self._current_frame = idx
            self.progress_slider.setValue(idx)
            self._update_time()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w,
                          QImage.Format.Format_RGB888)
            self.player_label.setPixmap(
                QPixmap.fromImage(qimg).scaled(
                    self.player_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

    def _update_time(self):
        if not self._cap:
            return
        fps = self._cap.get(cv2.CAP_PROP_FPS) or 30
        cur = int(self._current_frame / fps)
        tot = int(self._total_frames / fps)
        self.time_label.setText(
            f"{cur//60:02d}:{cur%60:02d} / {tot//60:02d}:{tot%60:02d}"
        )

    def _toggle_play(self):
        if self._is_playing:
            self._stop_player()
            self.btn_play_pause.setText("▶  Відтворити")
        else:
            self._start_player()
            self.btn_play_pause.setText("⏸  Пауза")

    def _restart(self):
        self._stop_player()
        self.btn_play_pause.setText("▶  Відтворити")
        self._show_frame(0)

    def _start_player(self):
        if not self._cap:
            return
        self._is_playing = True
        self.play_thread = PlaybackThread(
            self._cap, self._current_frame, self._total_frames
        )
        self.play_thread.frame_ready.connect(self._on_pb_frame)
        self.play_thread.finished.connect(self._on_pb_finished)
        self.play_thread.start()

    def _stop_player(self):
        self._is_playing = False
        if self.play_thread:
            self.play_thread.stop()
            self.play_thread = None

    def _on_slider_pressed(self):
        if self._is_playing:
            self._stop_player()
            self.btn_play_pause.setText("▶  Відтворити")

    def _on_slider_released(self):
        self._show_frame(self.progress_slider.value())

    def _on_pb_frame(self, data):
        frame, idx = data
        self._current_frame = idx
        self.progress_slider.setValue(idx)
        self._update_time()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.player_label.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                self.player_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def _on_pb_finished(self):
        self._is_playing = False
        self.btn_play_pause.setText("▶  Відтворити")

    def _rename_selected(self):
        item, path, ftype = self._get_selected()
        if item:
            self._do_rename(item, path, ftype)

    def _rename_item(self, item):
        path  = item.data(Qt.ItemDataRole.UserRole)
        ftype = item.data(Qt.ItemDataRole.UserRole + 1)
        self._do_rename(item, path, ftype)

    def _do_rename(self, item, path, ftype):
        if ftype == 'video':
            stats = VideoWriter.load_stats(path)
            current = stats.get('name', '') if stats else ''
        else:
            meta = self._load_photo_meta(path)
            current = meta.get('name', '') if meta else ''

        dialog = NameDialog(self, current_name=current,
                            title="Перейменувати")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new_name = dialog.get_name()
        if not new_name:
            return

        if ftype == 'video':
            stats_path = path.replace('.mp4', '_stats.json')
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['name'] = new_name
            else:
                data = {
                    'name': new_name, 'path': path,
                    'frames': 0, 'date': '',
                    'detections': {
                        'drone': 0, 'airplane': 0,
                        'helicopter': 0, 'bird': 0
                    }
                }
            with open(stats_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            item.setText(f"🎬 {new_name}")
        else:
            ext = os.path.splitext(path)[1]
            meta_path = path.replace(ext, '_meta.json')
            if os.path.exists(meta_path):
                with open(meta_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data['name'] = new_name
                with open(meta_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            item.setText(f"🖼 {new_name}")

    def _delete_selected(self):
        item, path, ftype = self._get_selected()
        if not item:
            return
        reply = QMessageBox.question(
            self, "Видалити", f"Видалити '{item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._stop_player()
        if self._cap:
            self._cap.release()
            self._cap = None
        if os.path.exists(path):
            os.remove(path)
        if ftype == 'video':
            sp = path.replace('.mp4', '_stats.json')
            if os.path.exists(sp):
                os.remove(sp)
        else:
            ext = os.path.splitext(path)[1]
            mp = path.replace(ext, '_meta.json')
            if os.path.exists(mp):
                os.remove(mp)
        self.refresh()
        for lbl in self.stat_labels.values():
            lbl.setText("—")
        self.meta_label.setText("")
        self.player_label.setText("🎬\n\nОберіть запис зі списку")
        self.player_label.setStyleSheet(
            "font-size: 15px; color: #ffffff; background: transparent;"
        )
        self.btn_rename.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_play_pause.setEnabled(False)
        self.btn_restart_rec.setEnabled(False)


class PlaybackThread(QThread):
    frame_ready = pyqtSignal(object)
    finished    = pyqtSignal()

    def __init__(self, cap, start_frame, total_frames):
        super().__init__()
        self.cap = cap
        self.start_frame  = start_frame
        self.total_frames = total_frames
        self._running = False

    def run(self):
        import time
        fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        delay = 1.0 / fps
        self._running = True
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_frame)
        idx = self.start_frame
        while self._running and idx < self.total_frames:
            t0 = time.time()
            ret, frame = self.cap.read()
            if not ret:
                break
            self.frame_ready.emit((frame, idx))
            idx += 1
            sleep = delay - (time.time() - t0)
            if sleep > 0:
                time.sleep(sleep)
        self.finished.emit()

    def stop(self):
        self._running = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Detector")
        self.setMinimumSize(1200, 720)
        self.setStyleSheet(STYLE)

        self.detector     = DroneDetector("assets/model/best.pt")
        self.video_writer = VideoWriter("recordings")

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)

        self.detection_tab  = DetectionTab(self.detector, self.video_writer)
        self.recordings_tab = RecordingsTab()

        self.tabs.addTab(self.detection_tab,  "  Детекція  ")
        self.tabs.addTab(self.recordings_tab, "  Записи  ")

    def refresh_recordings(self):
        self.recordings_tab.refresh()

    def open_in_detection(self, path: str):
        self.tabs.setCurrentIndex(0)
        self.detection_tab.open_recording(path)

    def closeEvent(self, event):
        self.detection_tab.stop_stream()
        event.accept()
