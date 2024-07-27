import cv2
import torch
import matplotlib.pyplot as plt
from midas.dpt_depth import DPTDepthModel
from torchvision.transforms import Compose
from aiohttp import web
import asyncio
import numpy as np
import base64
from io import BytesIO
from PIL import Image

# Load the MiDaS model architecture
model_path = "./dpt_large_384.pt"
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
    
    img = Image.open(BytesIO(img_data)).convert("RGB")
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
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type='text/html')

def init_func(argv):
    app = web.Application()
    app.router.add_get("/", hello)
    app.router.add_post("/upload", handle_post)
    return app

if __name__ == "__main__":
    # Start the web server
    app = init_func(None)
    web.run_app(app)
