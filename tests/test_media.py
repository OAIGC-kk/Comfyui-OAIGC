import asyncio
import types
import unittest
from io import BytesIO
from unittest.mock import patch


class MediaTests(unittest.TestCase):
    def test_result_download_uses_twenty_minute_timeout(self):
        from oai_bridge import media

        captured = {}

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return b"result-bytes"

        def fake_urlopen(url, timeout):
            captured["timeout"] = timeout
            return FakeResponse()

        with patch.object(media, "urlopen", fake_urlopen):
            result = media._download_bytes_sync("https://example.test/result.bin")

        self.assertEqual(result, b"result-bytes")
        self.assertEqual(captured["timeout"], 1200)

    def test_download_image_url_preserves_rgba_alpha_channel(self):
        from PIL import Image
        from oai_bridge import media

        image = Image.new("RGBA", (1, 1), (255, 0, 0, 0))
        data = BytesIO()
        image.save(data, format="PNG")
        fake_torch = types.SimpleNamespace(from_numpy=lambda arr: types.SimpleNamespace(unsqueeze=lambda dim: arr[None, ...]))

        async def run_case():
            with patch.dict("sys.modules", {"torch": fake_torch}):
                with patch.object(media, "_download_bytes", return_value=data.getvalue()):
                    return await media.download_image_url("https://example.test/cutout.png")

        tensor = asyncio.run(run_case())

        self.assertEqual(tuple(tensor.shape), (1, 1, 1, 4))
        self.assertEqual(float(tensor[0, 0, 0, 3]), 0.0)
        self.assertEqual(float(tensor[0, 0, 0, 0]), 1.0)


if __name__ == "__main__":
    unittest.main()
