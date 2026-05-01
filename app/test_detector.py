# app/test_detector.py

from detector import DroneDetector
import cv2

if __name__ == '__main__':
    detector = DroneDetector("assets/model/best.pt")

    test_image = cv2.imread("../dataset/final/images/test/test_00004.jpg")

    if test_image is None:
        print("Фото не знайдено")
    else:
        result_frame, counts = detector.detect(test_image)

        print("Знайдено об'єктів:")
        for cls, count in counts.items():
            if count > 0:
                print(f"  {cls}: {count}")

        # Зберігаємо результат замість показу вікна
        cv2.imwrite("test_result.jpg", result_frame)
        print("Результат збережено: app/test_result.jpg")
