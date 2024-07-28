import cv2
from ultralytics import YOLO
import cvzone

# Load the YOLOv8 face detection model
model_path = "./models/pretrained/yolov8n-face.pt"
face_model = YOLO(model_path)

def detect_faces(frame, conf_threshold=0.1):
    results = face_model.predict(frame, conf=conf_threshold)
    return results

def draw_boxes(frame, results):
    for info in results:
        parameters = info.boxes
        for box in parameters:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            h, w = y2 - y1, x2 - x1
            cvzone.cornerRect(frame, [x1, y1, w, h], l=1, rt=1)
    return frame