import logging
from aiohttp import web
import aiohttp
import base64
from models.dpt import process_image
from io import BytesIO

logging.basicConfig(level=logging.INFO)

async def handle_post(request):
    data = await request.post()
    img_data = data['image'].file.read()

    try:
        base64_output, img_data = process_image(img_data)
    except ValueError as e:
        return web.Response(text=str(e), status=400)

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
                base64_output, _ = process_image(img_data)
            except ValueError as e:
                await ws.send_str(str(e))
                continue

            await ws.send_str(f"data:image/png;base64,{base64_output}")

    return ws

def init_func(argv):
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_post("/upload", handle_post)
    app.router.add_get("/ws", websocket_handler)
    return app

if __name__ == "__main__":
    # Start the web server
    app = init_func(None)
    web.run_app(app)
