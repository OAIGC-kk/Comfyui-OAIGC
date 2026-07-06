import unittest
from unittest.mock import patch


class FakeGPTClient:
    async def gpt_image_generate(self, payload):
        self.payload = payload
        return {"code": 200, "data": {"imageUrl": "https://example.test/gpt.png"}}


class FakeAgnesClient:
    async def image_generations(self, payload):
        self.payload = payload
        return {"created": 1783310000, "data": [{"url": "https://example.test/agnes.png"}]}


class GPTImageTaskTests(unittest.IsolatedAsyncioTestCase):
    async def test_gpt_image_mode_returns_image_url(self):
        from oai_bridge import tasks

        client = FakeGPTClient()
        with patch.object(tasks, "OAIClient", return_value=client):
            url = await tasks.run_app({"id": "gpt-image", "mode": "gpt_image"}, {"prompt": "\u6d4b\u8bd5"})

        self.assertEqual(url, "https://example.test/gpt.png")
        self.assertEqual(client.payload, {"prompt": "\u6d4b\u8bd5"})

    async def test_agnes_image_mode_returns_openai_style_image_url(self):
        from oai_bridge import tasks

        client = FakeAgnesClient()
        payload = {"model": "agnes-image-2.1-flash", "prompt": "\u6d4b\u8bd5", "response_format": "url"}
        with patch.object(tasks, "OAIClient", return_value=client):
            url = await tasks.run_app({"id": "agnes-image-2.1-flash", "mode": "agnes_image"}, payload)

        self.assertEqual(url, "https://example.test/agnes.png")
        self.assertEqual(client.payload, payload)


if __name__ == "__main__":
    unittest.main()