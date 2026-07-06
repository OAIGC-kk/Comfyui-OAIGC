from __future__ import annotations

from aiohttp import web
from server import PromptServer

from .client import OAIClient
from .config import load_config, save_config
from .metadata import read_metadata_cache, refresh_metadata
from .panel import get_project_nodes

_ROUTES_REGISTERED = False


def register_routes() -> None:
    global _ROUTES_REGISTERED
    if _ROUTES_REGISTERED:
        return
    prompt_server = getattr(PromptServer, "instance", None)
    if prompt_server is None:
        return
    routes = prompt_server.routes
    _ROUTES_REGISTERED = True

    @routes.get("/oai-bridge/config")
    async def get_config(request):
        return web.json_response({"ok": True, "config": load_config().to_public_dict()})

    @routes.post("/oai-bridge/config")
    async def post_config(request):
        payload = await request.json()
        cfg = save_config(payload)
        return web.json_response({"ok": True, "message": "\u914d\u7f6e\u5df2\u4fdd\u5b58\u3002", "config": cfg.to_public_dict()})

    @routes.post("/oai-bridge/test")
    async def test_connection(request):
        try:
            await OAIClient(load_config()).get_model_list()
            return web.json_response({"ok": True, "message": "\u8fde\u63a5\u6210\u529f\u3002"})
        except Exception as exc:
            return web.json_response({"ok": False, "message": f"\u8fde\u63a5\u5931\u8d25\uff1a{exc}"}, status=400)

    @routes.get("/oai-bridge/nodes")
    async def get_nodes(request):
        return web.json_response({"ok": True, "nodes": get_project_nodes()})

    @routes.get("/oai-bridge/metadata")
    async def get_metadata(request):
        return web.json_response({"ok": True, "metadata": read_metadata_cache()})

    @routes.post("/oai-bridge/metadata/refresh")
    async def post_metadata_refresh(request):
        try:
            data = await refresh_metadata()
            return web.json_response({"ok": True, "message": "\u5e94\u7528\u5217\u8868\u5df2\u5237\u65b0\u3002", "metadata": data})
        except Exception as exc:
            return web.json_response(
                {"ok": False, "message": f"\u5237\u65b0\u5931\u8d25\uff1a{exc}", "metadata": read_metadata_cache()},
                status=400,
            )

    @routes.get("/oai-bridge/tasks/recent")
    async def get_recent_tasks(request):
        return web.json_response({"ok": True, "tasks": []})