import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, UnidentifiedImageError
from io import BytesIO

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, model_complexity=1, smooth_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

def detect_pose(img):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)
    return results

def draw_pose(img, results):
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return img

def process_image(img_data):
    try:
        img = Image.open(BytesIO(img_data)).convert("RGB")
    except UnidentifiedImageError:
        raise ValueError("Uploaded file is not a valid image.")

    img = np.array(img)

    results = detect_pose(img)
    img_with_pose = draw_pose(img, results)

    return img_with_pose, img_data
