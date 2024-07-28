import math
import cv2
import mediapipe as mp

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

def crop_at_pose_boundary(img, img_with_pose, results):
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        img_height, img_width, _ = img.shape
        
        # Extract x and y coordinates of landmarks
        x_coords = [int(landmark.x * img_width) for landmark in landmarks]
        y_coords = [int(landmark.y * img_height) for landmark in landmarks]

        # Determine the boundary coordinates
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        # Calculate the center and size of the original box
        center_x, center_y = (x_min + x_max) // 2, (y_min + y_max) // 2
        box_width, box_height = x_max - x_min, y_max - y_min

        # Expand the box by 1.5x multiplier
        scale_multiplier = 1.25
        new_width, new_height = int(box_width * scale_multiplier), int(box_height * scale_multiplier)
        new_x_min = max(0, center_x - new_width // 2)
        new_x_max = min(img_width, center_x + new_width // 2)
        new_y_min = max(0, center_y - new_height // 2)
        new_y_max = min(img_height, center_y + new_height // 2)

        # Crop the image at the expanded boundary
        cropped_img = img[new_y_min:new_y_max, new_x_min:new_x_max]
        cropped_img_with_pose = img_with_pose[new_y_min:new_y_max, new_x_min:new_x_max]
        return cropped_img, cropped_img_with_pose, max(new_x_min, 0), max(new_y_min, 0)

    return None, None, None, None

def process_pose_image(img):
    results = detect_pose(img)
    img_with_pose = img.copy()
    img_with_pose = draw_pose(img_with_pose, results)
    cropped_img, cropped_img_with_pose, x_offset, y_offset = crop_at_pose_boundary(img, img_with_pose, results)

    return cropped_img, cropped_img_with_pose, x_offset, y_offset
