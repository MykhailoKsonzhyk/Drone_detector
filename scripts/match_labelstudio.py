# scripts/match_labelstudio.py

import os
import shutil

# Шляхи
frames_dirs = [
    r"dataset/raw/my_frames/drone_video_1",
    r"dataset/raw/my_frames/drone_video_2",
    r"dataset/raw/my_frames/helicopter_video",
]
labels_dir = r"dataset\raw\my_frames\project-3-at-2026-04-07-15-37-9a770637\labels"
output_dir = r"dataset/raw/my_frames/final"

os.makedirs(f"{output_dir}/images", exist_ok=True)
os.makedirs(f"{output_dir}/labels", exist_ok=True)

# Збираємо всі оригінальні кадри в один словник
# ключ = "frame_00008", значення = повний шлях до фото
all_frames = {}
for frames_dir in frames_dirs:
    for filename in os.listdir(frames_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            # frame_00008.jpg → frame_00008
            base = os.path.splitext(filename)[0]
            all_frames[base] = os.path.join(frames_dir, filename)

print(f"Знайдено кадрів: {len(all_frames)}")

# Проходимо по всіх .txt файлах з Label Studio
matched = 0
not_matched = []

for label_filename in os.listdir(labels_dir):
    if not label_filename.endswith('.txt'):
        continue
    
    # "0fe8c419-frame_00008.txt" → шукаємо частину після "-"
    # яка відповідає оригінальній назві кадру
    base = os.path.splitext(label_filename)[0]  # без .txt
    
    # Шукаємо оригінальний кадр
    found_key = None
    for frame_key in all_frames:
        if frame_key in base:  # frame_00008 є в 0fe8c419-frame_00008
            found_key = frame_key
            break
    
    if found_key:
        # Копіюємо фото
        src_img = all_frames[found_key]
        ext = os.path.splitext(src_img)[1]
        dst_img = f"{output_dir}/images/{found_key}{ext}"
        shutil.copy(src_img, dst_img)
        
        # Копіюємо анотацію з новою правильною назвою
        src_lbl = os.path.join(labels_dir, label_filename)
        dst_lbl = f"{output_dir}/labels/{found_key}.txt"
        shutil.copy(src_lbl, dst_lbl)
        
        matched += 1
    else:
        not_matched.append(label_filename)

print(f"Успішно зіставлено: {matched}")
print(f"Не знайдено пару: {len(not_matched)}")
if not_matched:
    print("Файли без пари:", not_matched)
