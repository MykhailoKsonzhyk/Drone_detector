# scripts/extract_frames.py

import cv2
import os

def extract_frames(video_path, output_dir, every_n_frames=15):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Помилка: не можу відкрити {video_path}")
        return
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Відео: {total_frames} кадрів, {fps} FPS")
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_count % every_n_frames == 0:
            filename = f"{output_dir}/frame_{saved_count:05d}.jpg"
            cv2.imwrite(filename, frame)
            saved_count += 1
            
        frame_count += 1
    
    cap.release()
    print(f"Збережено {saved_count} кадрів в {output_dir}")


# Запускаємо для кожного відео окремо
extract_frames(
    video_path=r"dataset/raw/7438336-uhd_4096_1974_30fps.mp4",
    output_dir="dataset/raw/my_frames/drone_video_1",
    every_n_frames=15  # кожен 15-й кадр = 2 кадри/сек для 30fps відео
)

extract_frames(
    video_path=r"dataset/raw/8459631-hd_1920_1080_30fps.mp4",
    output_dir="dataset/raw/my_frames/drone_video_2",
    every_n_frames=15
)

extract_frames(
    video_path=r"dataset/raw/15155238_3840_2160_30fps.mp4",
    output_dir="dataset/raw/my_frames/helicopter_video",
    every_n_frames=15
)
