# 🛸 Drone Detector

Інформаційна система для виявлення та класифікації повітряних 
об'єктів на основі YOLOv8 і комп'ютерного зору.

## Можливості

- Детекція в реальному часі через камеру
- Аналіз відеофайлів з перемоткою
- Аналіз фотографій
- Розпізнавання 4 класів: дрон, літак, гелікоптер, птах
- Запис відео з детекцією і статистикою
- Перегляд збережених записів і фото

## Результати навчання

| Клас | Precision | Recall | mAP50 |
|------|-----------|--------|-------|
| Drone | 0.942 | 0.927 | 0.958 |
| Airplane | 0.930 | 0.833 | 0.893 |
| Helicopter | 0.976 | 0.906 | 0.968 |
| Bird | 0.854 | 0.883 | 0.903 |
| **Всього** | **0.925** | **0.887** | **0.930** |

## Стек технологій

- Python 3.13
- YOLOv8s (Ultralytics)
- PyTorch + CUDA
- OpenCV
- PyQt6

## Встановлення на різних системах

### Windows
```bash
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
cd app
python main.py
```

### Linux
```bash
pip3 install -r requirements.txt
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
cd app
python3 main.py
```

### macOS
```bash
pip install -r requirements.txt
pip install torch torchvision
cd app
python main.py
```

> **Примітка:** CUDA підтримується тільки на Windows і Linux з GPU Nvidia.
> На macOS використовується CPU або Apple MPS.

## Структура проекту

```
Drone_detector/
├── app/                    ← додаток
│   ├── main.py             ← точка входу
│   ├── detector.py         ← логіка детекції
│   ├── camera.py           ← потік камери
│   ├── video_writer.py     ← запис відео
│   ├── assets/
│   │   └── model/
│   │       └── best.pt     ← навчена модель
│   └── ui/
│       └── main_window.py  ← інтерфейс
├── dataset/                ← датасети (не включені в репо)
├── scripts/                ← утиліти підготовки даних
├── training/               ← скрипти навчання моделі
├── requirements.txt
└── README.md
```

## Примітки

- Датасет не включено в репозиторій через великий розмір
- Для навчання використовувалось 6689 зображень 4 класів
- Модель навчена на GPU з підтримкою CUDA

## Автор

Михайло Ксьонжик Національний університет "Львівська політхніка" — 2026