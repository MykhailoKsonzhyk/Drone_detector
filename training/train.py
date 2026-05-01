# training/train.py

from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("yolov8s.pt")

    results = model.train(
        data="dataset/final/data.yaml",
        epochs=100,
        imgsz=640,
        batch=8,
        device=0,
        patience=20,
        workers=0,        # ← додай це для Windows
        save=True,
        project="training/runs",
        name="drone_detector"
    )

    print("Навчання завершено!")
    print("Найкраща модель: training/runs/drone_detector/weights/best.pt")
