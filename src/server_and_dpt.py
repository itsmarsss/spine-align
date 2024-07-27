import cv2
import torch
from midas.dpt_depth import DPTDepthModel
from torchvision.transforms import Compose
from aiohttp import web
import numpy as np
import base64
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import aiohttp
import logging

logging.basicConfig(level=logging.INFO)

# Load the MiDaS model architecture
model_path = "./models/dpt_large_384.pt"
midas = DPTDepthModel(
    path=model_path,
    backbone="vitl16_384",
    non_negative=True,
)

# Use GPU if available
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(device)
midas.eval()

# Use transforms to resize and normalize the image
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform

async def handle_post(request):
    data = await request.post()
    img_data = data['image'].file.read()

    try:
        img = Image.open(BytesIO(img_data)).convert("RGB")
    except UnidentifiedImageError:
        return web.Response(text="Error: Uploaded file is not a valid image.", status=400)

    img = np.array(img)

    # Transform input for midas
    imgbatch = transform(img).to(device)

    # Make a prediction
    with torch.no_grad():
        prediction = midas(imgbatch)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

        output = prediction.cpu().numpy()

    # Normalize the output for visualization
    output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    _, buffer = cv2.imencode('.png', output)
    base64_output = base64.b64encode(buffer).decode('utf-8')

    html_content = f"""
    <html>
    <body>
        <h2>Original Image</h2>
        <img src="data:image/png;base64,{base64.b64encode(img_data).decode('utf-8')}" alt="Original Image"/>
        <h2>Depth Map</h2>
        <img src="data:image/png;base64,{base64_output}" alt="Depth Map"/>
        <br><br>
        <a href="/">Upload Another Image</a>
    </body>
    </html>
    """

    return web.Response(text=html_content, content_type='text/html')

async def hello(request):
    html_content = """
    <html>
    <body>
        <h2>Upload an Image</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*">
            <input type="submit" value="Upload">
        </form>
        <h2>Stream Webcam</h2>
        <button onclick="startWebcam()">Start Webcam</button>
        <br><br>
        <video id="webcam" autoplay></video>
        <div id="depth-map-container"></div>
        <script>
            const video = document.getElementById('webcam');
            const startWebcam = async () => {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;
                const ws = new WebSocket('ws://' + window.location.host + '/ws');
                ws.onopen = () => {
                    setInterval(async () => {
                        const canvas = document.createElement('canvas');
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        const context = canvas.getContext('2d');
                        context.drawImage(video, 0, 0, canvas.width, canvas.height);
                        const dataURL = canvas.toDataURL('image/jpeg');
                        ws.send(dataURL);
                    }, 100);
                };
                ws.onmessage = (event) => {
                    const img = new Image();
                    img.src = event.data;
                    const container = document.getElementById('depth-map-container');
                    container.innerHTML = '';
                    container.appendChild(img);
                };
            };
        </script>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data_url = msg.data
            header, encoded = data_url.split(",", 1)
            img_data = base64.b64decode(encoded)

            try:
                img = Image.open(BytesIO(img_data)).convert("RGB")
            except UnidentifiedImageError:
                await ws.send_str("Error: Uploaded file is not a valid image.")
                continue

            img = np.array(img)

            # Transform input for midas
            imgbatch = transform(img).to(device)

            # Make a prediction
            with torch.no_grad():
                prediction = midas(imgbatch)
                prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
                ).squeeze()

                output = prediction.cpu().numpy()

            # Normalize the output for visualization
            output = cv2.normalize(output, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

            _, buffer = cv2.imencode('.png', output)
            base64_output = base64.b64encode(buffer).decode('utf-8')

            await ws.send_str(f"data:image/png;base64,{base64_output}")

    return ws

def init_func(argv):
    app = web.Application()
    app.router.add_get("/", hello)
    app.router.add_post("/upload", handle_post)
    app.router.add_get("/ws", websocket_handler)
    return app

if __name__ == "__main__":
    # Start the web server
    app = init_func(None)
    web.run_app(app)
