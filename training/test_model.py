# training/test_model.py

from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("app/assets/model/best.pt")
    
    # Тест на тестовому датасеті — побачиш метрики
    metrics = model.val(
        data="dataset/final/data.yaml",
        split='test'
    )
    
    print(f"mAP50: {metrics.box.map50:.3f}")
    print(f"mAP50-95: {metrics.box.map:.3f}")
