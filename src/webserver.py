import logging
import math
import aiohttp
from aiohttp import web
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from models.dpt import process_depth_image
from models.yolov8_face import detect_faces
from models.pose import process_pose_image
from models.openAI import query_gpt

logging.basicConfig(level=logging.INFO)

def find_closest_key(positions, target_x, target_y):
    closest_key = None
    min_distance = float('inf')

    for key, (x, y) in positions.items():
        distance = math.sqrt((x - target_x) ** 2 + (y - target_y) ** 2)
        if distance < min_distance:
            min_distance = distance
            closest_key = key

    return closest_key, min_distance

async def index(request):
    return web.FileResponse('./static/index.html')

async def post_handler(request):
    try:
        data = await request.json()
        data_url = data['data_url']
        positions = data['positions']

        print(positions)
        print({
    "0": [1, 2],
    "1": [4, 6],
    "2": [5, 7],
    "3": [2, 3]
})

        header, encoded = data_url.split(",", 1)
        img_data = base64.b64decode(encoded)

        # Process the image data for image
        img = Image.open(BytesIO(img_data)).convert("RGB")
        img = np.array(img)

        # Process the image for depth estimation
        depth_output = process_depth_image(img)
        _, buffer = cv2.imencode('.png', depth_output)
        depth_base64_output = base64.b64encode(buffer).decode('utf-8')
        
        # Process the image data for face detection
        face_with_boxes, face_results = detect_faces(img)
        
        # Constants for scaling
        scale_upward_factor = 1/2
        scale_downward_factor = 7
        scale_leftward_factor = 1.5
        scale_rightward_factor = 1.5
        
        # Extract bounding box coordinates and cropped faces
        boxes = []
        cropped_faces = []
        cropped_depths = []
        cropped_poses = []
        cropped_poses_raw = []
        gpt_responses = []
        center_xs = []
        center_ys = []
        cropped_widths = []
        cropped_heights = []
        for box in face_results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Ensure x1 < x2 and y1 < y2
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1

            # Calculate the face box dimensions
            face_height = y2 - y1
            face_width = x2 - x1
            
            # Extend the bounding box
            new_y1 = max(0, y1 - int(face_height * scale_upward_factor))
            new_y2 = min(img.shape[0], y2 + int(face_height * scale_downward_factor))
            new_x1 = max(0, x1 - int(face_width * scale_leftward_factor))
            new_x2 = min(img.shape[1], x2 + int(face_width * scale_rightward_factor))

            boxes.append({"x1": new_x1, "y1": new_y1, "x2": new_x2, "y2": new_y2})
            
            cropped_face = img[new_y1:new_y2, new_x1:new_x2]
            
            # Convert cropped face from RGB to BGR
            cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2BGR)
            _, buffer = cv2.imencode('.png', cropped_face)
            cropped_faces.append(base64.b64encode(buffer).decode('utf-8'))

            # Process cropped face for pose detection
            cropped_pose_raw, cropped_pose, offset_x, offset_y = process_pose_image(cropped_face)
            if cropped_pose_raw is None or cropped_pose is None:
                continue

            # Raw
            _, buffer = cv2.imencode('.png', cropped_pose_raw)
            cropped_poses_raw.append(base64.b64encode(buffer).decode('utf-8'))
            # Drawn
            _, buffer = cv2.imencode('.png', cropped_pose)
            cropped_poses.append(base64.b64encode(buffer).decode('utf-8'))

            # Process cropped pose for depth estimation
            cropped_depth_output = process_depth_image(cropped_pose_raw)
            _, buffer = cv2.imencode('.png', cropped_depth_output)
            cropped_depths.append(base64.b64encode(buffer).decode('utf-8'))

            gpt_response = query_gpt(cropped_pose_raw, cropped_depth_output)
            gpt_responses.append(gpt_response)

            # Get the original dimensions
            cropped_height, cropped_width = cropped_pose_raw.shape[:2]

            # Calculate center coordinates
            center_x = new_x1 + offset_x/2 + cropped_width / 2
            center_y = new_y1 + offset_y/2 + cropped_height / 2

            center_xs.append(center_x)
            center_ys.append(center_y)
            cropped_widths.append(cropped_width)
            cropped_heights.append(cropped_height)

            print(find_closest_key(positions, center_x, center_y))

        final_output = img.copy()

        for x, y, width, height in zip(center_xs, center_ys, cropped_widths, cropped_heights):
            x1 = int(x - width / 2)
            y1 = int(y - height / 2)
            x2 = int(x + width / 2)
            y2 = int(y + height / 2)

            final_output = cv2.circle(final_output, (int(x), int(y)), 5, (0, 255, 0), -1)
            final_output = cv2.rectangle(final_output, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Convert the final image with boxes to base64
        final_output = cv2.cvtColor(final_output, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', final_output)
        final_base64_output = base64.b64encode(buffer).decode('utf-8')

        # Convert the image with boxes to base64
        face_with_boxes = cv2.cvtColor(face_with_boxes, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode('.png', face_with_boxes)
        face_base64_output = base64.b64encode(buffer).decode('utf-8')
        
        # Send results back as JSON response
        return web.json_response({
            "original_image": encoded,
            "depth_image": depth_base64_output,
            "face_image": face_base64_output,
            "boxes": boxes,
            "cropped_faces": cropped_faces,
            "cropped_poses": cropped_poses,
            "cropped_poses_raw": cropped_poses_raw,
            "cropped_depths": cropped_depths,
            "gpt_responses": gpt_responses,
            "final_output": final_base64_output
        })

    except ValueError as e:
        print(e)
        return web.Response(text=str(e), status=500)

app = web.Application()
app.router.add_get("/", index)
app.router.add_post("/process_image", post_handler)

if __name__ == '__main__':
    web.run_app(app)
