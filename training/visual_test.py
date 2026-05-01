# training/visual_test.py

from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("app/assets/model/best.pt")
    
    # Тест на кількох фото з тестового датасету
    results = model.predict(
        source="dataset/final/images/test",
        save=True,          # зберігає фото з рамками
        conf=0.45,
        max_det=10
    )
