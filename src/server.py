from aiohttp import web

async def hello(request):
    return web.Response(text="Hello, world")

def init_func(argv):
    app = web.Application()
    app.router.add_get("/", hello)
    return app

app = init_func(None)
web.run_app(app)