# app/detector.py

from ultralytics import YOLO
import cv2
import numpy as np

CLASS_COLORS = {
    'drone':      (255, 191, 0),    # блакитний
    'airplane':   (0, 200, 0),      # зелений
    'helicopter': (0, 140, 255),    # жовтогарячий
    'bird':       (180, 105, 255),  # рожевий (#ff69b4 в BGR)
}

CLASS_NAMES = ['drone', 'airplane', 'helicopter', 'bird']


class DroneDetector:
    def __init__(self, model_path: str, confidence: float = 0.45):
        print(f"Завантаження моделі: {model_path}")
        self.model = YOLO(model_path)
        self.confidence = confidence
        print("Модель завантажена!")

    def detect(self, frame: np.ndarray):
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False
        )[0]

        annotated = frame.copy()
        counts = {cls: 0 for cls in CLASS_NAMES}

        for box in results.boxes:
            cls_id   = int(box.cls[0])
            conf     = float(box.conf[0])
            cls_name = CLASS_NAMES[cls_id]
            color    = CLASS_COLORS.get(cls_name, (255, 255, 255))

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            label = f"{cls_name} {conf:.0%}"
            (text_w, text_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - text_h - 8),
                (x1 + text_w + 4, y1),
                color, -1
            )
            cv2.putText(
                annotated, label,
                (x1 + 2, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (0, 0, 0),
                1, cv2.LINE_AA
            )
            counts[cls_name] += 1

        return annotated, counts

    def set_confidence(self, value: float):
        self.confidence = value
