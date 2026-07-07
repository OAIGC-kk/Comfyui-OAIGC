import sys
import types
import unittest


class RouteRegistrationTests(unittest.TestCase):
    def test_register_routes_waits_until_prompt_server_instance_exists(self):
        server_module = types.ModuleType("server")

        class FakePromptServer:
            pass

        server_module.PromptServer = FakePromptServer
        aiohttp_module = types.ModuleType("aiohttp")
        web_module = types.ModuleType("aiohttp.web")
        web_module.json_response = lambda *args, **kwargs: (args, kwargs)
        aiohttp_module.web = web_module

        old_server = sys.modules.get("server")
        old_aiohttp = sys.modules.get("aiohttp")
        old_web = sys.modules.get("aiohttp.web")
        sys.modules["server"] = server_module
        sys.modules["aiohttp"] = aiohttp_module
        sys.modules["aiohttp.web"] = web_module
        sys.modules.pop("oai_bridge.routes", None)
        try:
            from oai_bridge.routes import register_routes

            register_routes()
        finally:
            sys.modules.pop("oai_bridge.routes", None)
            if old_server is None:
                sys.modules.pop("server", None)
            else:
                sys.modules["server"] = old_server
            if old_aiohttp is None:
                sys.modules.pop("aiohttp", None)
            else:
                sys.modules["aiohttp"] = old_aiohttp
            if old_web is None:
                sys.modules.pop("aiohttp.web", None)
            else:
                sys.modules["aiohttp.web"] = old_web


class CostRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_cost_route_forwards_workflow_payload(self):
        server_module = types.ModuleType("server")

        class FakeRoutes:
            def __init__(self):
                self.posts = {}

            def get(self, path):
                def decorator(fn):
                    return fn
                return decorator

            def post(self, path):
                def decorator(fn):
                    self.posts[path] = fn
                    return fn
                return decorator

        class FakePromptServer:
            instance = types.SimpleNamespace(routes=FakeRoutes())

        class FakeRequest:
            async def json(self):
                return {"kind": "workflow", "payload": {"appId": "z-imagewenshengt", "parameter": {"prompt": "test"}}}

        captured = {}

        class FakeClient:
            def __init__(self, config):
                captured["config"] = config

            async def workflow_app_cost(self, payload):
                captured["workflow_payload"] = payload
                return {"code": 200, "message": "\u83b7\u53d6\u6210\u529f", "data": {"cost": 2}}

            async def seedance_cost(self, payload):
                captured["seedance_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

        responses = []
        web_module = types.ModuleType("aiohttp.web")
        web_module.json_response = lambda data, status=200: responses.append((data, status)) or {"data": data, "status": status}
        aiohttp_module = types.ModuleType("aiohttp")
        aiohttp_module.web = web_module
        server_module.PromptServer = FakePromptServer

        old_server = sys.modules.get("server")
        old_aiohttp = sys.modules.get("aiohttp")
        old_web = sys.modules.get("aiohttp.web")
        sys.modules["server"] = server_module
        sys.modules["aiohttp"] = aiohttp_module
        sys.modules["aiohttp.web"] = web_module
        sys.modules.pop("oai_bridge.routes", None)
        try:
            import oai_bridge.routes as routes
            routes._ROUTES_REGISTERED = False
            routes.OAIClient = FakeClient
            routes.register_routes()
            response = await FakePromptServer.instance.routes.posts["/oai-bridge/cost"](FakeRequest())
        finally:
            sys.modules.pop("oai_bridge.routes", None)
            if old_server is None:
                sys.modules.pop("server", None)
            else:
                sys.modules["server"] = old_server
            if old_aiohttp is None:
                sys.modules.pop("aiohttp", None)
            else:
                sys.modules["aiohttp"] = old_aiohttp
            if old_web is None:
                sys.modules.pop("aiohttp.web", None)
            else:
                sys.modules["aiohttp.web"] = old_web

        self.assertEqual(captured["workflow_payload"], {"appId": "z-imagewenshengt", "parameter": {"prompt": "test"}})
        self.assertNotIn("seedance_payload", captured)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"], {"ok": True, "cost": 2, "message": "\u83b7\u53d6\u6210\u529f"})

    async def test_cost_route_forwards_seedance_payload(self):
        server_module = types.ModuleType("server")

        class FakeRoutes:
            def __init__(self):
                self.posts = {}

            def get(self, path):
                def decorator(fn):
                    return fn
                return decorator

            def post(self, path):
                def decorator(fn):
                    self.posts[path] = fn
                    return fn
                return decorator

        class FakePromptServer:
            instance = types.SimpleNamespace(routes=FakeRoutes())

        class FakeRequest:
            async def json(self):
                return {"kind": "seedance", "payload": {"model": "seed-2", "metadata": {"duration": 4}}}

        captured = {}

        class FakeClient:
            def __init__(self, config):
                pass

            async def workflow_app_cost(self, payload):
                captured["workflow_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

            async def seedance_cost(self, payload):
                captured["seedance_payload"] = payload
                return {"code": 200, "message": "\u83b7\u53d6\u6210\u529f", "data": {"cost": 6}}

        web_module = types.ModuleType("aiohttp.web")
        web_module.json_response = lambda data, status=200: {"data": data, "status": status}
        aiohttp_module = types.ModuleType("aiohttp")
        aiohttp_module.web = web_module
        server_module.PromptServer = FakePromptServer

        old_server = sys.modules.get("server")
        old_aiohttp = sys.modules.get("aiohttp")
        old_web = sys.modules.get("aiohttp.web")
        sys.modules["server"] = server_module
        sys.modules["aiohttp"] = aiohttp_module
        sys.modules["aiohttp.web"] = web_module
        sys.modules.pop("oai_bridge.routes", None)
        try:
            import oai_bridge.routes as routes
            routes._ROUTES_REGISTERED = False
            routes.OAIClient = FakeClient
            routes.register_routes()
            response = await FakePromptServer.instance.routes.posts["/oai-bridge/cost"](FakeRequest())
        finally:
            sys.modules.pop("oai_bridge.routes", None)
            if old_server is None:
                sys.modules.pop("server", None)
            else:
                sys.modules["server"] = old_server
            if old_aiohttp is None:
                sys.modules.pop("aiohttp", None)
            else:
                sys.modules["aiohttp"] = old_aiohttp
            if old_web is None:
                sys.modules.pop("aiohttp.web", None)
            else:
                sys.modules["aiohttp.web"] = old_web

        self.assertEqual(captured["seedance_payload"], {"model": "seed-2", "metadata": {"duration": 4}})
        self.assertNotIn("workflow_payload", captured)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"], {"ok": True, "cost": 6, "message": "\u83b7\u53d6\u6210\u529f"})



    async def test_cost_route_forwards_model_payload(self):
        server_module = types.ModuleType("server")

        class FakeRoutes:
            def __init__(self):
                self.posts = {}

            def get(self, path):
                def decorator(fn):
                    return fn
                return decorator

            def post(self, path):
                def decorator(fn):
                    self.posts[path] = fn
                    return fn
                return decorator

        class FakePromptServer:
            instance = types.SimpleNamespace(routes=FakeRoutes())

        class FakeRequest:
            async def json(self):
                return {"kind": "model", "payload": {"model": "gpt-image-2"}}

        captured = {}

        class FakeClient:
            def __init__(self, config):
                pass

            async def workflow_app_cost(self, payload):
                captured["workflow_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

            async def model_cost(self, payload):
                captured["model_payload"] = payload
                return {"code": 200, "message": "ok", "data": {"cost": 2}}

            async def seedance_cost(self, payload):
                captured["seedance_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

        web_module = types.ModuleType("aiohttp.web")
        web_module.json_response = lambda data, status=200: {"data": data, "status": status}
        aiohttp_module = types.ModuleType("aiohttp")
        aiohttp_module.web = web_module
        server_module.PromptServer = FakePromptServer

        old_server = sys.modules.get("server")
        old_aiohttp = sys.modules.get("aiohttp")
        old_web = sys.modules.get("aiohttp.web")
        sys.modules["server"] = server_module
        sys.modules["aiohttp"] = aiohttp_module
        sys.modules["aiohttp.web"] = web_module
        sys.modules.pop("oai_bridge.routes", None)
        try:
            import oai_bridge.routes as routes
            routes._ROUTES_REGISTERED = False
            routes.OAIClient = FakeClient
            routes.register_routes()
            response = await FakePromptServer.instance.routes.posts["/oai-bridge/cost"](FakeRequest())
        finally:
            sys.modules.pop("oai_bridge.routes", None)
            if old_server is None:
                sys.modules.pop("server", None)
            else:
                sys.modules["server"] = old_server
            if old_aiohttp is None:
                sys.modules.pop("aiohttp", None)
            else:
                sys.modules["aiohttp"] = old_aiohttp
            if old_web is None:
                sys.modules.pop("aiohttp.web", None)
            else:
                sys.modules["aiohttp.web"] = old_web

        self.assertEqual(captured["model_payload"], {"model": "gpt-image-2"})
        self.assertNotIn("workflow_payload", captured)
        self.assertNotIn("seedance_payload", captured)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"], {"ok": True, "cost": 2, "message": "ok"})


    async def test_cost_route_forwards_gpt_image_payload(self):
        server_module = types.ModuleType("server")

        class FakeRoutes:
            def __init__(self):
                self.posts = {}

            def get(self, path):
                def decorator(fn):
                    return fn
                return decorator

            def post(self, path):
                def decorator(fn):
                    self.posts[path] = fn
                    return fn
                return decorator

        class FakePromptServer:
            instance = types.SimpleNamespace(routes=FakeRoutes())

        class FakeRequest:
            async def json(self):
                return {
                    "kind": "gpt_image",
                    "payload": {
                        "model": "gpt-image-2",
                        "fast": True,
                        "resolution": "1K",
                        "size": "1:1",
                    },
                }

        captured = {}

        class FakeClient:
            def __init__(self, config):
                pass

            async def workflow_app_cost(self, payload):
                captured["workflow_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

            async def gpt_image_cost(self, payload):
                captured["gpt_image_payload"] = payload
                return {"code": 200, "message": "ok", "data": {"cost": 18}}

            async def model_cost(self, payload):
                captured["model_payload"] = payload
                return {"code": 200, "message": "ok", "data": {"cost": 4}}

            async def seedance_cost(self, payload):
                captured["seedance_payload"] = payload
                return {"code": 200, "data": {"cost": 99}}

        web_module = types.ModuleType("aiohttp.web")
        web_module.json_response = lambda data, status=200: {"data": data, "status": status}
        aiohttp_module = types.ModuleType("aiohttp")
        aiohttp_module.web = web_module
        server_module.PromptServer = FakePromptServer

        old_server = sys.modules.get("server")
        old_aiohttp = sys.modules.get("aiohttp")
        old_web = sys.modules.get("aiohttp.web")
        sys.modules["server"] = server_module
        sys.modules["aiohttp"] = aiohttp_module
        sys.modules["aiohttp.web"] = web_module
        sys.modules.pop("oai_bridge.routes", None)
        try:
            import oai_bridge.routes as routes
            routes._ROUTES_REGISTERED = False
            routes.OAIClient = FakeClient
            routes.register_routes()
            response = await FakePromptServer.instance.routes.posts["/oai-bridge/cost"](FakeRequest())
        finally:
            sys.modules.pop("oai_bridge.routes", None)
            if old_server is None:
                sys.modules.pop("server", None)
            else:
                sys.modules["server"] = old_server
            if old_aiohttp is None:
                sys.modules.pop("aiohttp", None)
            else:
                sys.modules["aiohttp"] = old_aiohttp
            if old_web is None:
                sys.modules.pop("aiohttp.web", None)
            else:
                sys.modules["aiohttp.web"] = old_web

        self.assertEqual(captured["gpt_image_payload"], {"model": "gpt-image-2", "fast": True, "resolution": "1K", "size": "1:1"})
        self.assertNotIn("model_payload", captured)
        self.assertNotIn("workflow_payload", captured)
        self.assertNotIn("seedance_payload", captured)
        self.assertEqual(response["status"], 200)
        self.assertEqual(response["data"], {"ok": True, "cost": 18, "message": "ok"})


if __name__ == "__main__":
    unittest.main()
