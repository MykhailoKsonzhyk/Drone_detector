# scripts/prepare_dataset.py

import os, shutil, random

# ============================================
# КРОК 1 — РЕМАППІНГ
# ============================================

def remap_labels(input_dir, output_dir, class_mapping):
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    for filename in os.listdir(input_dir):
        if not filename.endswith('.txt'):
            continue
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        with open(input_path, 'r') as f:
            lines = f.readlines()
        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue
            old_class = int(parts[0])
            if old_class in class_mapping:
                new_class = class_mapping[old_class]
                new_lines.append(f"{new_class} {' '.join(parts[1:])}\n")
        if new_lines:
            with open(output_path, 'w') as f:
                f.writelines(new_lines)
            count += 1
    print(f"  Оброблено файлів: {count}")


print("=== РЕМАППІНГ ===")

# Датасет A: birds=0, drone=1, helicopter=2, plane=3
print("Датасет A...")
for split in ['train', 'valid', 'test']:
    remap_labels(
        input_dir=f"dataset/raw/Drone detection.v4i.yolov8_1/{split}/labels",
        output_dir=f"dataset/raw/Drone detection.v4i.yolov8_1/{split}/labels_fixed",
        class_mapping={0: 3, 1: 0, 2: 2, 3: 1}
    )

# Датасет B: Bird=0, Drone=1, Plane=2
print("Датасет B...")
for split in ['train', 'valid', 'test']:
    remap_labels(
        input_dir=f"dataset/raw/Drone detection.v4i.yolov8_2/{split}/labels",
        output_dir=f"dataset/raw/Drone detection.v4i.yolov8_2/{split}/labels_fixed",
        class_mapping={0: 3, 1: 0, 2: 1}
    )

# Датасет C: AirPlane=0, Drone=1, Helicopter=2
print("Датасет C...")
for split in ['train', 'valid', 'test']:
    remap_labels(
        input_dir=f"dataset/raw/Drone Detection.v1i.yolov8_3/{split}/labels",
        output_dir=f"dataset/raw/Drone Detection.v1i.yolov8_3/{split}/labels_fixed",
        class_mapping={0: 1, 1: 0, 2: 2}
    )

# Свої кадри: drone=0, helicopter=1
print("Свої кадри...")
remap_labels(
    input_dir="dataset/raw/my_frames/final/labels",
    output_dir="dataset/raw/my_frames/final/labels_fixed",
    class_mapping={0: 0, 1: 2}
)

print("Ремаппінг завершено!\n")


# ============================================
# КРОК 2 — ЗЛИТТЯ
# ============================================

def merge_and_split(sources, output_dir, split_ratio=(0.7, 0.2, 0.1), seed=42):
    random.seed(seed)
    all_pairs = []

    for source in sources:
        img_dir = source["images"]
        lbl_dir = source["labels"]

        if not os.path.exists(img_dir) or not os.path.exists(lbl_dir):
            print(f"  Пропускаю (не існує): {img_dir}")
            continue

        for img_filename in os.listdir(img_dir):
            if not img_filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            base = os.path.splitext(img_filename)[0]
            label_path = os.path.join(lbl_dir, base + '.txt')
            if os.path.exists(label_path):
                all_pairs.append({
                    "img": os.path.join(img_dir, img_filename),
                    "lbl": label_path,
                    "ext": os.path.splitext(img_filename)[1]
                })

    print(f"Всього пар фото+анотація: {len(all_pairs)}")
    random.shuffle(all_pairs)

    total = len(all_pairs)
    train_end = int(total * split_ratio[0])
    val_end = train_end + int(total * split_ratio[1])

    splits = {
        "train": all_pairs[:train_end],
        "val":   all_pairs[train_end:val_end],
        "test":  all_pairs[val_end:]
    }

    for split_name, pairs in splits.items():
        img_out = os.path.join(output_dir, "images", split_name)
        lbl_out = os.path.join(output_dir, "labels", split_name)
        os.makedirs(img_out, exist_ok=True)
        os.makedirs(lbl_out, exist_ok=True)

        for i, pair in enumerate(pairs):
            new_name = f"{split_name}_{i:05d}"
            shutil.copy(pair["img"], os.path.join(img_out, new_name + pair["ext"]))
            shutil.copy(pair["lbl"], os.path.join(lbl_out, new_name + ".txt"))

        print(f"  {split_name}: {len(pairs)} зображень")


print("=== ЗЛИТТЯ ===")

sources = [
    # Датасет A
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_1/train/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_1/train/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_1/valid/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_1/valid/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_1/test/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_1/test/labels_fixed"
    },
    # Датасет B
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_2/train/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_2/train/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_2/valid/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_2/valid/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone detection.v4i.yolov8_2/test/images",
        "labels": "dataset/raw/Drone detection.v4i.yolov8_2/test/labels_fixed"
    },
    # Датасет C
    {
        "images": "dataset/raw/Drone Detection.v1i.yolov8_3/train/images",
        "labels": "dataset/raw/Drone Detection.v1i.yolov8_3/train/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone Detection.v1i.yolov8_3/valid/images",
        "labels": "dataset/raw/Drone Detection.v1i.yolov8_3/valid/labels_fixed"
    },
    {
        "images": "dataset/raw/Drone Detection.v1i.yolov8_3/test/images",
        "labels": "dataset/raw/Drone Detection.v1i.yolov8_3/test/labels_fixed"
    },
    # Свої кадри
    {
        "images": "dataset/raw/my_frames/final/images",
        "labels": "dataset/raw/my_frames/final/labels_fixed"
    },
]

merge_and_split(sources, output_dir="dataset/final")


# ============================================
# КРОК 3 — СТВОРЕННЯ data.yaml
# ============================================

yaml_content = f"""path: {os.path.abspath("dataset/final")}
train: images/train
val: images/val
test: images/test

nc: 4
names: ['drone', 'airplane', 'helicopter', 'bird']
"""

with open("dataset/final/data.yaml", 'w') as f:
    f.write(yaml_content)

print("\ndata.yaml створено!")
print("✅ Датасет готовий до навчання!")
