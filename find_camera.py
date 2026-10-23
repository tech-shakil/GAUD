import cv2

for i in range(10):
    cap = cv2.VideoCapture(i)

    if cap.isOpened():
        ret, frame = cap.read()
        print(f"Camera {i}: {ret}")

    cap.release()