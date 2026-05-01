# app/video_writer.py

import cv2
import os
import json
import queue
import threading
from datetime import datetime


class VideoWriter:
    def __init__(self, output_dir: str = "recordings"):
        self.output_dir = output_dir
        self.writer = None
        self.is_recording = False
        self.current_path = None
        self.current_name = None
        os.makedirs(output_dir, exist_ok=True)

        # Статистика поточного запису
        self._stats = {
            'drone': 0, 'airplane': 0,
            'helicopter': 0, 'bird': 0
        }
        self._frame_count = 0

        # Черга для асинхронного запису
        self._queue = queue.Queue(maxsize=60)
        self._thread = None

    def start(self, frame_width: int, frame_height: int,
              fps: float = 30.0, name: str = None):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Якщо назва не задана — генеруємо автоматично
        safe_name = name.strip().replace(" ", "_") if name else None
        filename = f"{safe_name}_{timestamp}.mp4" \
                   if safe_name else f"detection_{timestamp}.mp4"

        self.current_path = os.path.join(self.output_dir, filename)
        self.current_name = name or filename

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            self.current_path, fourcc, fps,
            (frame_width, frame_height)
        )
        self.is_recording = True

        # Скидаємо статистику
        self._stats = {
            'drone': 0, 'airplane': 0,
            'helicopter': 0, 'bird': 0
        }
        self._frame_count = 0

        # Запускаємо потік запису
        self._thread = threading.Thread(
            target=self._write_loop, daemon=True
        )
        self._thread.start()

        print(f"Запис розпочато: {self.current_path}")
        return filename

    def _write_loop(self):
        while self.is_recording or not self._queue.empty():
            try:
                frame = self._queue.get(timeout=0.5)
                if self.writer:
                    self.writer.write(frame)
            except queue.Empty:
                continue

    def write(self, frame, counts: dict = None):
        """Записуємо кадр і оновлюємо статистику"""
        if self.is_recording:
            try:
                self._queue.put_nowait(frame.copy())
                self._frame_count += 1
            except queue.Full:
                pass

            # Оновлюємо максимальні значення статистики
            if counts:
                for cls, count in counts.items():
                    if cls in self._stats:
                        self._stats[cls] = max(
                            self._stats[cls], count
                        )

    def stop(self):
        self.is_recording = False

        if self._thread:
            self._thread.join(timeout=5.0)

        if self.writer:
            self.writer.release()
            self.writer = None

        path = self.current_path

        # Зберігаємо статистику в JSON
        if path:
            self._save_stats(path)

        self.current_path = None
        self.current_name = None
        print(f"Запис збережено: {path}")
        return path

    def _save_stats(self, video_path: str):
        """Зберігаємо статистику поруч з відео як .json"""
        stats_path = video_path.replace('.mp4', '_stats.json')
        data = {
            'name': self.current_name,
            'path': video_path,
            'frames': self._frame_count,
            'detections': self._stats,
            'date': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_stats(video_path: str) -> dict:
        """Завантажити статистику для відео"""
        stats_path = video_path.replace('.mp4', '_stats.json')
        if os.path.exists(stats_path):
            with open(stats_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    @property
    def recording(self):
        return self.is_recording
