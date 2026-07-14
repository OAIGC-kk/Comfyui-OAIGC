import json
import unittest
from unittest.mock import patch


class FakeUploadResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps({"code": 200, "message": "图片上传成功", "data": "https://tu.oaigc.cn/test.png"}).encode(
            "utf-8"
        )


class UploadTests(unittest.IsolatedAsyncioTestCase):
    async def test_upload_file_posts_multipart_and_returns_url(self):
        from oai_bridge.client import OAIClient
        from oai_bridge.config import OAIConfig

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["headers"] = dict(request.header_items())
            captured["data"] = request.data
            return FakeUploadResponse()

        client = OAIClient(OAIConfig(token="secret", upload_url="https://oaigc.cn/api/file/tool/upload"))

        with patch("oai_bridge.client.urlopen", fake_urlopen):
            url = await client.upload_file("test.png", b"image-bytes", "image/png")

        self.assertEqual(url, "https://tu.oaigc.cn/test.png")
        self.assertEqual(captured["url"], "https://oaigc.cn/api/file/tool/upload")
        self.assertEqual(captured["timeout"], 1200)
        self.assertIn("multipart/form-data", captured["headers"]["Content-type"])
        self.assertIn(b'name="file"; filename="test.png"', captured["data"])
        self.assertIn(b"image-bytes", captured["data"])



    async def test_upload_video_input_saves_mp4_and_uploads_file(self):
        from oai_bridge.media import upload_video_input

        class FakeVideo:
            def save_to(self, out, format=None):
                self.format = format
                out.write(b"mp4-bytes")

        class FakeClient:
            async def upload_file(self, filename, content, content_type):
                self.filename = filename
                self.content = content
                self.content_type = content_type
                return "https://tu.oaigc.cn/reference.mp4"

        video = FakeVideo()
        client = FakeClient()

        url = await upload_video_input(client, video, "reference_video_1.mp4")

        self.assertEqual(url, "https://tu.oaigc.cn/reference.mp4")
        self.assertEqual(client.filename, "reference_video_1.mp4")
        self.assertEqual(client.content, b"mp4-bytes")
        self.assertEqual(client.content_type, "video/mp4")


    async def test_upload_audio_input_writes_wav_and_uploads_file(self):
        import wave
        from io import BytesIO

        import numpy as np

        from oai_bridge.media import upload_audio_input

        class FakeWaveform:
            shape = (1, 1, 4)

            def __getitem__(self, index):
                return self

            def detach(self):
                return self

            def cpu(self):
                return self

            def numpy(self):
                return np.array([[0.0, 0.5, -0.5, 1.0]], dtype=np.float32)

        class FakeClient:
            async def upload_file(self, filename, content, content_type):
                self.filename = filename
                self.content = content
                self.content_type = content_type
                return "https://tu.oaigc.cn/reference.wav"

        client = FakeClient()

        url = await upload_audio_input(
            client,
            {"waveform": FakeWaveform(), "sample_rate": 16000},
            "reference_audio_1.wav",
        )

        self.assertEqual(url, "https://tu.oaigc.cn/reference.wav")
        self.assertEqual(client.filename, "reference_audio_1.wav")
        self.assertEqual(client.content_type, "audio/wav")
        with wave.open(BytesIO(client.content), "rb") as wav:
            self.assertEqual(wav.getnchannels(), 1)
            self.assertEqual(wav.getframerate(), 16000)
            self.assertEqual(wav.getnframes(), 4)

if __name__ == "__main__":
    unittest.main()


