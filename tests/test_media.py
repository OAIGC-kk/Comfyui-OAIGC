import asyncio
import types
import unittest
from io import BytesIO
from unittest.mock import patch


class MediaTests(unittest.TestCase):
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
