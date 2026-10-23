from ultralytics import YOLO
import cv2
import time
try:
    import winsound
except ImportError:
    winsound = None

model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

cv2.namedWindow("GAUD - Road Safety AI", cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    "GAUD - Road Safety AI",
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

road_objects = [
    "person",
    "car",
    "motorcycle",
    "bus",
    "truck",
    "bicycle"
]

last_beep = 0

while True:

    ret, frame = cap.read()

    if not ret:
        time.sleep(0.01)
        continue

    h, w = frame.shape[:2]

    results = model(frame, verbose=False)

    # Danger Zone
    zone_x1 = int(w * 0.30)
    zone_x2 = int(w * 0.70)
    zone_y1 = int(h * 0.60)
    zone_y2 = h

    cv2.rectangle(
        frame,
        (zone_x1, zone_y1),
        (zone_x2, zone_y2),
        (0, 0, 255),
        3
    )

    risk_score = 0
    status = "SAFE"
    distance = "FAR"

    for box in results[0].boxes:

        cls = int(box.cls[0])
        name = model.names[cls]

        if name not in road_objects:
            continue

        conf = float(box.conf[0])

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        cv2.rectangle(
            frame,
            (x1, y1), 

            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{name} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        if zone_x1 < cx < zone_x2 and zone_y1 < cy < zone_y2:

            box_area = (x2 - x1) * (y2 - y1)
            frame_area = w * h

            size_risk = int((box_area / frame_area) * 200)
            position_risk = int((cy / h) * 100)

            current_risk = min(
                100,
                int((size_risk + position_risk) / 2)
            )

            if current_risk > risk_score:
                risk_score = current_risk

    # Status
    if risk_score < 30:
        status = "SAFE"
        distance = "FAR"
        color = (0, 255, 0)

    elif risk_score < 70:
        status = "WARNING"
        distance = "MEDIUM"
        color = (0, 255, 255)

    else:
        status = "DANGER"
        distance = "NEAR"
        color = (0, 0, 255)

        if time.time() - last_beep > 1:
            if winsound:
                winsound.Beep(1500, 300)
            else:
                print("\a", end="", flush=True)
            last_beep = time.time()

    # Dashboard background
    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (10, 10),
        (500, 180),
        (0, 0, 0),
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.45,
        frame,
        0.55,
        0
    )

    cv2.putText(
        frame,
        f"Risk: {risk_score}%",
        (25, 55),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        color,
        3
    )

    cv2.putText(
        frame,
        f"Status: {status}",
        (25, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        color,
        3
    )

    cv2.putText(
        frame,
        f"Distance: {distance}",
        (25, 155),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        color,
        3
    )

    # Danger Banner
    if status == "DANGER":

        cv2.rectangle(
            frame,
            (20, 220),
            (650, 300),
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            "COLLISION RISK!",
            (40, 280),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.8,
            (255, 255, 255),
            4
        )

    cv2.imshow(
        "GAUD - Road Safety AI",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()