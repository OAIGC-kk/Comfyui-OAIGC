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
        return web.json_response({"ok": True, "message": "配置已保存。", "config": cfg.to_public_dict()})

    @routes.post("/oai-bridge/test")
    async def test_connection(request):
        try:
            await OAIClient(load_config()).get_model_list()
            return web.json_response({"ok": True, "message": "连接成功。"})
        except Exception as exc:
            return web.json_response({"ok": False, "message": f"连接失败：{exc}"}, status=400)

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
            return web.json_response({"ok": True, "message": "应用列表已刷新。", "metadata": data})
        except Exception as exc:
            return web.json_response(
                {"ok": False, "message": f"刷新失败：{exc}", "metadata": read_metadata_cache()},
                status=400,
            )

    @routes.post("/oai-bridge/cost")
    async def post_cost(request):
        try:
            payload = await request.json()
            kind = payload.get("kind", "workflow")
            cost_payload = payload.get("payload") or {}
            client = OAIClient(load_config())
            if kind == "seedance":
                response = await client.seedance_cost(cost_payload)
            elif kind == "gpt_image":
                response = await client.gpt_image_cost(cost_payload)
            elif kind == "model":
                response = await client.model_cost(cost_payload)
            else:
                response = await client.workflow_app_cost(cost_payload)
            data = response.get("data") or {}
            return web.json_response({"ok": True, "cost": data.get("cost"), "message": response.get("message", "获取成功")})
        except Exception as exc:
            return web.json_response({"ok": False, "message": f"获取价格失败：{exc}"}, status=400)

    @routes.get("/oai-bridge/tasks/recent")
    async def get_recent_tasks(request):
        return web.json_response({"ok": True, "tasks": []})
