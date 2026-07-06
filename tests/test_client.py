import json
import ssl
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError


class FakeJSONResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"code": 200, "data": {"ok": True}}).encode("utf-8")


class ClientTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_json_retries_ssl_unexpected_eof(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        attempts = {"count": 0}

        def fake_urlopen(request, timeout, context=None):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise ssl.SSLError("UNEXPECTED_EOF_WHILE_READING")
            return FakeJSONResponse()

        client = OAIClient(OAIConfig(token="secret"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            with patch("oai_bridge.client.time.sleep", return_value=None):
                data = await client.request_json("POST", "/v1/test", {"hello": "world"})

        self.assertEqual(data["data"], {"ok": True})
        self.assertEqual(attempts["count"], 2)

    async def test_request_json_uses_ssl_context_for_https(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        captured = {}

        def fake_urlopen(request, timeout, context=None):
            captured["context"] = context
            return FakeJSONResponse()

        client = OAIClient(OAIConfig(token="secret"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            await client.request_json("POST", "/v1/test", {})

        self.assertIsNotNone(captured["context"])


    async def test_request_json_includes_http_error_response_message(self):
        from oai_bridge.client import OAIAPIError, OAIClient
        from oai_bridge.config import OAIConfig

        def fake_urlopen(request, timeout, context=None):
            body = json.dumps({"code": 500, "message": "尺寸参数不支持"}).encode("utf-8")
            raise HTTPError(request.full_url, 500, "Internal Server Error", {}, BytesIO(body))

        client = OAIClient(OAIConfig(token="secret"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            with patch("oai_bridge.client.time.sleep", return_value=None):
                with self.assertRaises(OAIAPIError) as raised:
                    await client.request_json("POST", "/v1/test", {"hello": "world"})

        message = str(raised.exception)
        self.assertIn("HTTP 500", message)
        self.assertIn("尺寸参数不支持", message)


    async def test_request_json_includes_http_error_response_details(self):
        from oai_bridge.client import OAIAPIError, OAIClient
        from oai_bridge.config import OAIConfig

        def fake_urlopen(request, timeout, context=None):
            body = json.dumps({"code": 500, "message": "参数错误", "err": {"Offset": 2}}).encode("utf-8")
            raise HTTPError(request.full_url, 500, "Internal Server Error", {}, BytesIO(body))

        client = OAIClient(OAIConfig(token="secret"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            with patch("oai_bridge.client.time.sleep", return_value=None):
                with self.assertRaises(OAIAPIError) as raised:
                    await client.request_json("POST", "/v1/test", {"hello": "world"})

        message = str(raised.exception)
        self.assertIn("HTTP 500", message)
        self.assertIn("参数错误", message)
        self.assertIn("Offset", message)
    async def test_request_json_includes_api_error_details(self):
        from oai_bridge.client import OAIAPIError, OAIClient
        from oai_bridge.config import OAIConfig

        class ErrorResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({"code": 500, "message": "参数错误", "err": {"Offset": 2}}).encode("utf-8")

        def fake_urlopen(request, timeout, context=None):
            return ErrorResponse()

        client = OAIClient(OAIConfig(token="secret"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            with self.assertRaises(OAIAPIError) as raised:
                await client.request_json("POST", "/v1/test", {"hello": "world"})

        message = str(raised.exception)
        self.assertIn("参数错误", message)
        self.assertIn("Offset", message)
    async def test_submit_task_http_error_includes_payload_without_token(self):
        from oai_bridge.client import OAIAPIError, OAIClient
        from oai_bridge.config import OAIConfig

        def fake_urlopen(request, timeout, context=None):
            body = json.dumps({"code": 500, "message": "参数错误", "err": {"Offset": 2}}).encode("utf-8")
            raise HTTPError(request.full_url, 500, "Internal Server Error", {}, BytesIO(body))

        client = OAIClient(OAIConfig(token="secret-token"))
        parameter = {"prompt": "测试", "num": 1, "magnification": 1.1, "aspect_ratio": "1:1", "use_pre_llm": True}

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            with patch("oai_bridge.client.time.sleep", return_value=None):
                with self.assertRaises(OAIAPIError) as raised:
                    await client.submit_task("z-imagewenshengt", parameter)

        message = str(raised.exception)
        self.assertIn('"appId": "z-imagewenshengt"', message)
        self.assertIn('"parameter":', message)
        self.assertIn('"aspect_ratio": "1:1"', message)
        self.assertNotIn("secret-token", message)
        self.assertNotIn("Bearer", message)
    async def test_submit_task_wraps_general_task_parameters(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        captured = {}

        async def fake_request_json(method, path, json_data=None):
            captured.update({"method": method, "path": path, "json_data": json_data})
            return {"code": 200, "data": {"taskId": "task-1"}}

        client = OAIClient(OAIConfig(token="secret"))
        client.request_json = fake_request_json

        await client.submit_task("qwenedit", {"prompt": "test"})

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/v1/task/submit")
        self.assertEqual(captured["json_data"], {"appId": "qwenedit", "parameter": {"prompt": "test"}})

    async def test_submit_task_wraps_ali_text_image_parameters(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        captured = {}
        parameter = {"prompt": "测试", "num": 1, "magnification": 1.1, "aspect_ratio": "9:16", "use_pre_llm": True}

        async def fake_request_json(method, path, json_data=None):
            captured.update({"method": method, "path": path, "json_data": json_data})
            return {"code": 200, "data": {"taskId": "task-1"}}

        client = OAIClient(OAIConfig(token="secret"))
        client.request_json = fake_request_json

        await client.submit_task("z-imagewenshengt", parameter)

        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/v1/task/submit")
        self.assertEqual(captured["json_data"], {"appId": "z-imagewenshengt", "parameter": parameter})

    async def test_submit_task_logs_payload_without_token(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        logs = []
        parameter = {"prompt": "测试", "num": 1, "magnification": 1.1, "aspect_ratio": "1:1", "use_pre_llm": True}

        async def fake_request_json(method, path, json_data=None):
            return {"code": 200, "data": {"taskId": "task-1"}}

        client = OAIClient(OAIConfig(token="secret-token"))
        client.request_json = fake_request_json

        with patch("builtins.print", lambda *args, **kwargs: logs.append(" ".join(str(arg) for arg in args))):
            await client.submit_task("z-imagewenshengt", parameter)

        joined = "\n".join(logs)
        self.assertIn("[OAI Bridge] /v1/task/submit payload:", joined)
        self.assertIn('"appId": "z-imagewenshengt"', joined)
        self.assertIn('"aspect_ratio": "1:1"', joined)
        self.assertNotIn("secret-token", joined)
        self.assertNotIn("Bearer", joined)

    async def test_dialogue_execute_posts_documented_payload(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        captured = {}
        payload = {
            "model": "gpt-4o",
            "system_prompt": "你是助手",
            "user_input": "你好",
            "images": ["https://example.test/a.png"],
            "video": "https://example.test/a.mp4",
        }

        async def fake_request_json(method, path, json_data=None):
            captured.update({"method": method, "path": path, "json_data": json_data})
            return {"code": 200, "data": {"content": "你好呀"}}

        client = OAIClient(OAIConfig(token="secret"))
        client.request_json = fake_request_json

        response = await client.dialogue_execute(payload)

        self.assertEqual(response["data"]["content"], "你好呀")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["path"], "/v1/dialogue/execute")
        self.assertEqual(captured["json_data"], payload)
if __name__ == "__main__":
    unittest.main()








