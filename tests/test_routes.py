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


if __name__ == "__main__":
    unittest.main()