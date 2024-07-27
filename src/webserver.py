import logging
from aiohttp import web
import aiohttp
import base64
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from models.dpt import process_image as process_depth_image
from models.yolov8_face import detect_faces, draw_boxes

logging.basicConfig(level=logging.INFO)

async def handle_post(request):
    data = await request.post()
    img_data = data['image'].file.read()

    try:
        # Process the image for depth estimation
        depth_base64_output, img_data = process_depth_image(img_data)
        
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
                # Process the image for depth estimation
                depth_base64_output, _ = process_depth_image(img_data)
                
                # Process the image for face detection
                img = Image.open(BytesIO(img_data)).convert("RGB")
                img = np.array(img)
                
                face_results = detect_faces(img)
                img_with_boxes = draw_boxes(img, face_results)
                
                # Convert the image with boxes to base64
                _, buffer = cv2.imencode('.png', img_with_boxes)
                face_base64_output = base64.b64encode(buffer).decode('utf-8')
                
                # Send both results back via WebSocket
                await ws.send_str(f"data:image/png;base64,{depth_base64_output}|data:image/png;base64,{face_base64_output}")

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
