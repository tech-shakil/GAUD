import cv2

for i in range(10):
    print(f"\nTesting Camera {i}")

    cap = cv2.VideoCapture(i)

    if not cap.isOpened():
        print("Not opened")
        continue

    ret, frame = cap.read()

    print("Frame:", ret)

    if ret:
        cv2.imshow(f"Camera {i}", frame)
        cv2.waitKey(3000)
        cv2.destroyAllWindows()

    cap.release()