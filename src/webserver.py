import logging
from aiohttp import web
import aiohttp
import base64
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from models.dpt import process_depth_image
from models.yolov8_face import detect_faces, draw_boxes
from models.pose import process_pose_image

logging.basicConfig(level=logging.INFO)

async def handle_post(request):
    data = await request.post()
    img_data = data['image'].file.read()

    try:
        # Process the image for depth estimation
        depth_output, img_data = process_depth_image(img_data)
        
        # Convert depth output to base64
        _, buffer = cv2.imencode('.png', depth_output)
        depth_base64_output = base64.b64encode(buffer).decode('utf-8')

        # Process the image for face detection
        img = Image.open(BytesIO(img_data)).convert("RGB")
        img = np.array(img)
        
        face_results = detect_faces(img)
        img_with_boxes = draw_boxes(img, face_results)
        
        # Convert the image with boxes to base64
        _, buffer = cv2.imencode('.png', img_with_boxes)
        face_base64_output = base64.b64encode(buffer).decode('utf-8')

    except ValueError as e:
        return web.Response(text=str(e), status=400)

    html_content = f"""
    <html>
    <body>
        <h2>Original Image</h2>
        <img src="data:image/png;base64,{base64.b64encode(img_data).decode('utf-8')}" alt="Original Image"/>
        <h2>Depth Map</h2>
        <img src="data:image/png;base64,{depth_base64_output}" alt="Depth Map"/>
        <h2>Face Detection</h2>
        <img src="data:image/png;base64,{face_base64_output}" alt="Face Detection"/>
        <br><br>
        <a href="/">Upload Another Image</a>
    </body>
    </html>
    """

    return web.Response(text=html_content, content_type='text/html')

async def index(request):
    return web.FileResponse('./static/index.html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data_url = msg.data
            header, encoded = data_url.split(",", 1)
            img_data = base64.b64decode(encoded)

            try:
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
                    cropped_pose_raw, cropped_pose = process_pose_image(cropped_face)
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

                # Convert the image with boxes to base64
                face_with_boxes = cv2.cvtColor(face_with_boxes, cv2.COLOR_RGB2BGR)
                _, buffer = cv2.imencode('.png', face_with_boxes)
                face_base64_output = base64.b64encode(buffer).decode('utf-8')
                
                # Send results back via WebSocket
                await ws.send_json({
                    "original_image": encoded,
                    "depth_image": depth_base64_output,
                    "face_image": face_base64_output,
                    "boxes": boxes,
                    "cropped_faces": cropped_faces,
                    "cropped_poses": cropped_poses,
                    "cropped_poses_raw": cropped_poses_raw,
                    "cropped_depths": cropped_depths
                })

            except ValueError as e:
                await ws.send_str(str(e))
                continue

    return ws

def init_func(argv):
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_post("/upload", handle_post)
    app.router.add_get("/ws", websocket_handler)
    return app

if __name__ == "__main__":
    app = init_func(None)
    web.run_app(app)
