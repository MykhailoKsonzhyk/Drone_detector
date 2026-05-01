# app/camera.py — повна заміна

import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np


class CameraThread(QThread):
    frame_ready   = pyqtSignal(object)
    fps_updated   = pyqtSignal(float)
    error_occurred = pyqtSignal(str)
    finished      = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.source    = None
        self.is_running = False
        self.is_paused  = False
        self.detector   = None
        self._cap_ref   = None   # посилання на cap для перемотки

    def set_source(self, source):
        self.source = source

    def set_detector(self, detector):
        self.detector = detector

    def run(self):
        if self.source is None:
            self.error_occurred.emit("Джерело не вказано")
            return

        cap = cv2.VideoCapture(self.source)
        if not cap.isOpened():
            self.error_occurred.emit(
                f"Не вдалось відкрити: {self.source}"
            )
            return

        self._cap_ref = cap   # зберігаємо для зовнішнього доступу

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if video_fps <= 0 or video_fps > 120:
            video_fps = 30.0
        frame_delay = 1.0 / video_fps

        self.is_running = True
        prev_time = time.time()

        while self.is_running:
            if self.is_paused:
                time.sleep(0.05)
                continue

            loop_start = time.time()
            ret, frame = cap.read()

            if not ret:
                if self.source != 0:
                    self.finished.emit()
                break

            original = frame.copy()

            if self.detector is not None:
                annotated, counts = self.detector.detect(frame)
            else:
                annotated = frame
                counts    = {}

            current_time = time.time()
            fps = 1.0 / (current_time - prev_time + 1e-9)
            prev_time = current_time

            self.frame_ready.emit((original, annotated, counts))
            self.fps_updated.emit(fps)

            elapsed    = time.time() - loop_start
            sleep_time = frame_delay - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        self._cap_ref = None
        cap.release()

    def stop(self):
        self.is_running = False
        self.is_paused  = False
        self.wait()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False
