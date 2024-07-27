import cvzone
from ultralytics import YOLO
import cv2


cap = cv2.VideoCapture(0)

facemodel = YOLO("yolov8n-face.pt")

prev_time = cv2.getTickCount()
while cap.isOpened():
    rt, video = cap.read()
    # video = cv2.resize(video, (700, 500))
    
    # Calculate the FPS
    current_time = cv2.getTickCount()
    time_diff = (current_time - prev_time) / cv2.getTickFrequency()
    prev_time = current_time
    fps = 1 / time_diff

    face_result = facemodel.predict(video, conf=0.40)
    for info in face_result:
        parameters = info.boxes
        for box in parameters:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            h, w = y2 - y1, x2 - x1
            cvzone.cornerRect(video, [x1, y1, w, h], l=1, rt=1)

    # Display the FPS on the frame
    cv2.putText(video, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("frame", video)
    if cv2.waitKey(1) & 0xFF == ord("t"):
        break

cap.release()
cv2.destroyAllWindows()