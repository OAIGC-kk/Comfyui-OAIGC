import asyncio
import sys
import types
import unittest


def _install_fake_comfy_io():
    class FakeInput:
        def __init__(self, name, options=None, **kwargs):
            self.name = name
            self.options = options
            self.kwargs = kwargs

    class FakeOutput:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeSchema:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeNodeOutput:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class FakeIO:
        class ComfyNode:
            pass

        class Schema(FakeSchema):
            pass

        NodeOutput = FakeNodeOutput

        class Combo:
            Input = FakeInput

        class String:
            Input = FakeInput
            Output = FakeOutput

        class Image:
            Input = FakeInput

        class Int:
            Input = FakeInput

        class Video:
            Input = FakeInput
            Output = FakeOutput

        class Audio:
            Input = FakeInput

    comfy_api = types.ModuleType("comfy_api")
    latest = types.ModuleType("comfy_api.latest")
    latest.IO = FakeIO
    sys.modules["comfy_api"] = comfy_api
    sys.modules["comfy_api.latest"] = latest
    sys.modules.pop("oai_bridge.nodes_video", None)
    sys.modules.pop("oai_bridge.nodes_seedance_asset", None)


async def _run_seedance_case(nodes_video, execute_kwargs, captured, fake_uploads=True):
    from oai_bridge.nodes_video import OAIVideoNode

    async def fake_run_app(app, parameter):
        captured["app"] = app
        captured["parameter"] = parameter
        return "https://example.test/video.mp4"

    async def fake_download_video_url(url):
        return "video-result"

    async def fake_upload_video_input(client, video, filename):
        captured.setdefault("video_uploads", []).append((video, filename))
        return f"https://example.test/{filename}"

    async def fake_upload_audio_input(client, audio, filename):
        captured.setdefault("audio_uploads", []).append((audio, filename))
        return f"https://example.test/{filename}"

    original_find = nodes_video._find_video_app
    original_run = nodes_video.run_app
    original_download = nodes_video.download_video_url
    original_upload_video = nodes_video.upload_video_input
    original_upload_audio = nodes_video.upload_audio_input
    nodes_video._find_video_app = lambda label: {"id": "seedance", "mode": "seedance", "output": "video"}
    nodes_video.run_app = fake_run_app
    nodes_video.download_video_url = fake_download_video_url
    if fake_uploads:
        nodes_video.upload_video_input = fake_upload_video_input
        nodes_video.upload_audio_input = fake_upload_audio_input
    try:
        return await OAIVideoNode.execute(**execute_kwargs)
    finally:
        nodes_video._find_video_app = original_find
        nodes_video.run_app = original_run
        nodes_video.download_video_url = original_download
        nodes_video.upload_video_input = original_upload_video
        nodes_video.upload_audio_input = original_upload_audio


class VideoModelTests(unittest.TestCase):
    def test_schema_exposes_only_image_asset_id_inputs(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_video import (
            AUDIO_FIELDS,
            APP_FIELD,
            EXTRA_FIELD,
            IMAGE_ASSET_FIELDS,
            IMAGE_FIELDS,
            OAIVideoNode,
            VIDEO_FIELDS,
            VIDEO_MODEL_FIELD,
        )

        schema = OAIVideoNode.define_schema()
        input_names = [item.name for item in schema.inputs]
        model_input = next(item for item in schema.inputs if item.name == VIDEO_MODEL_FIELD)
        image_asset_inputs = [item for item in schema.inputs if item.name in IMAGE_ASSET_FIELDS]

        self.assertEqual(model_input.options, ["seedance2.0", "seedance2.0-fast"])
        self.assertEqual(model_input.kwargs.get("default"), "seedance2.0")
        self.assertIn(APP_FIELD, input_names)
        self.assertNotIn("\u9ad8\u7ea7\u53c2\u6570JSON", input_names)
        self.assertEqual([name for name in input_names if name in IMAGE_FIELDS], IMAGE_FIELDS)
        self.assertEqual([name for name in input_names if name in VIDEO_FIELDS], VIDEO_FIELDS)
        self.assertEqual([name for name in input_names if name in AUDIO_FIELDS], AUDIO_FIELDS)
        self.assertEqual([item.name for item in image_asset_inputs], IMAGE_ASSET_FIELDS)
        self.assertNotIn("\u89c6\u9891\u8d44\u4ea7ID1", input_names)
        self.assertNotIn("\u97f3\u9891\u8d44\u4ea7ID1", input_names)
        self.assertTrue(all(item.kwargs.get("optional") for item in image_asset_inputs))
        self.assertTrue(all(item.kwargs.get("force_input") for item in image_asset_inputs))

    def test_seedance_payload_keeps_reference_files_as_urls_without_automatic_asset_upload(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_video as nodes_video
        from oai_bridge.nodes_video import AUDIO_FIELDS, APP_FIELD, GENERATE_AUDIO_FIELD, IMAGE_FIELDS, OAIVideoNode, VIDEO_FIELDS, VIDEO_MODEL_FIELD

        captured = {"image_uploads": [], "video_uploads": [], "audio_uploads": []}

        async def fake_upload_image_tensor(client, image, filename):
            captured["image_uploads"].append((image, filename))
            return f"https://example.test/{filename}"

        async def fake_upload_video_input(client, video, filename):
            captured["video_uploads"].append((video, filename))
            return f"https://example.test/{filename}"

        async def fake_upload_audio_input(client, audio, filename):
            captured["audio_uploads"].append((audio, filename))
            return f"https://example.test/{filename}"

        async def fake_run_app(app, parameter):
            captured["app"] = app
            captured["parameter"] = parameter
            return "https://example.test/video.mp4"

        async def fake_download_video_url(url):
            return "video-result"

        async def run_case():
            original_find = nodes_video._find_video_app
            original_run = nodes_video.run_app
            original_download = nodes_video.download_video_url
            original_upload_image = nodes_video.upload_image_tensor
            original_upload_video = nodes_video.upload_video_input
            original_upload_audio = nodes_video.upload_audio_input
            nodes_video._find_video_app = lambda label: {"id": "seedance", "mode": "seedance", "output": "video"}
            nodes_video.run_app = fake_run_app
            nodes_video.download_video_url = fake_download_video_url
            nodes_video.upload_image_tensor = fake_upload_image_tensor
            nodes_video.upload_video_input = fake_upload_video_input
            nodes_video.upload_audio_input = fake_upload_audio_input
            try:
                kwargs = {
                    APP_FIELD: "Seedance Video (seedance)",
                    VIDEO_MODEL_FIELD: "seedance2.0-fast",
                    nodes_video.PROMPT_FIELD: "use video1 and audio1",
                    nodes_video.ASPECT_FIELD: "9:16",
                    nodes_video.DURATION_FIELD: 8,
                    nodes_video.RESOLUTION_FIELD: "1080p",
                    GENERATE_AUDIO_FIELD: "\u5426",
                }
                kwargs.update({field: f"image-{index}" for index, field in enumerate(IMAGE_FIELDS, start=1)})
                kwargs.update({field: f"video-{index}" for index, field in enumerate(VIDEO_FIELDS, start=1)})
                kwargs.update({field: f"audio-{index}" for index, field in enumerate(AUDIO_FIELDS, start=1)})
                return await OAIVideoNode.execute(**kwargs)
            finally:
                nodes_video._find_video_app = original_find
                nodes_video.run_app = original_run
                nodes_video.download_video_url = original_download
                nodes_video.upload_image_tensor = original_upload_image
                nodes_video.upload_video_input = original_upload_video
                nodes_video.upload_audio_input = original_upload_audio

        output = asyncio.run(run_case())

        self.assertEqual(output.args, ("video-result",))
        self.assertEqual(
            captured["parameter"],
            {
                "model": "seed-2-fast-vision",
                "prompt": "use video1 and audio1",
                "metadata": {
                    "ratio": "9:16",
                    "duration": 8,
                    "resolution": "1080p",
                    "generate_audio": False,
                    "reference_images": [f"https://example.test/reference_image_{index}.png" for index in range(1, 10)],
                    "reference_videos": [f"https://example.test/reference_video_{index}.mp4" for index in range(1, 4)],
                    "reference_audios": [f"https://example.test/reference_audio_{index}.wav" for index in range(1, 4)],
                },
            },
        )

    def test_seedance_payload_uses_explicit_image_asset_id_inputs_only(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_video as nodes_video
        from oai_bridge.nodes_video import APP_FIELD, IMAGE_ASSET_FIELDS, PROMPT_FIELD, VIDEO_MODEL_FIELD

        captured = {}
        asyncio.run(
            _run_seedance_case(
                nodes_video,
                {
                    APP_FIELD: "Seedance Video (seedance)",
                    VIDEO_MODEL_FIELD: "seedance2.0",
                    PROMPT_FIELD: "use image asset 1 and image asset 3",
                    IMAGE_ASSET_FIELDS[0]: "asset-image-1",
                    IMAGE_ASSET_FIELDS[2]: "asset-image-3",
                },
                captured,
            )
        )

        metadata = captured["parameter"]["metadata"]
        self.assertEqual(captured["parameter"]["model"], "seed-2")
        self.assertEqual(metadata["reference_image_asset_ids"], ["asset-image-1", "asset-image-3"])
        self.assertNotIn("reference_video_asset_ids", metadata)
        self.assertNotIn("reference_audio_asset_ids", metadata)
        self.assertNotIn("reference_images", metadata)
        self.assertNotIn("reference_videos", metadata)

    def test_seedance_connected_reference_video_promotes_base_model_to_visio_without_asset_upload(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_video as nodes_video
        from oai_bridge.nodes_video import APP_FIELD, OAIVideoNode, PROMPT_FIELD, VIDEO_FIELDS, VIDEO_MODEL_FIELD

        captured = {}
        fake_video = object()

        async def fake_upload_video_input(client, video, filename):
            captured["uploaded_video"] = (video, filename)
            return f"https://example.test/{filename}"

        async def fake_run_app(app, parameter):
            captured["parameter"] = parameter
            return "https://example.test/video.mp4"

        async def fake_download_video_url(url):
            return "video-result"

        async def run_case():
            original_find = nodes_video._find_video_app
            original_run = nodes_video.run_app
            original_download = nodes_video.download_video_url
            original_upload_video = nodes_video.upload_video_input
            nodes_video._find_video_app = lambda label: {"id": "seedance", "mode": "seedance", "output": "video"}
            nodes_video.run_app = fake_run_app
            nodes_video.download_video_url = fake_download_video_url
            nodes_video.upload_video_input = fake_upload_video_input
            try:
                return await OAIVideoNode.execute(
                    **{
                        APP_FIELD: "Seedance Video (seedance)",
                        VIDEO_MODEL_FIELD: "seedance2.0",
                        PROMPT_FIELD: "test video",
                        VIDEO_FIELDS[0]: fake_video,
                    }
                )
            finally:
                nodes_video._find_video_app = original_find
                nodes_video.run_app = original_run
                nodes_video.download_video_url = original_download
                nodes_video.upload_video_input = original_upload_video

        asyncio.run(run_case())

        self.assertEqual(captured["uploaded_video"], (fake_video, "reference_video_1.mp4"))
        self.assertEqual(captured["parameter"]["model"], "seed-2-visio")
        self.assertEqual(captured["parameter"]["metadata"]["reference_videos"], ["https://example.test/reference_video_1.mp4"])
        self.assertNotIn("reference_video_asset_ids", captured["parameter"]["metadata"])

    def test_seedance_fast_without_reference_video_keeps_fast_model(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_video as nodes_video
        from oai_bridge.nodes_video import APP_FIELD, PROMPT_FIELD, VIDEO_MODEL_FIELD

        captured = {}
        asyncio.run(
            _run_seedance_case(
                nodes_video,
                {
                    APP_FIELD: "Seedance Video (seedance)",
                    VIDEO_MODEL_FIELD: "seedance2.0-fast",
                    PROMPT_FIELD: "test video",
                },
                captured,
            )
        )

        self.assertEqual(captured["parameter"]["model"], "seed-2-fast")
        self.assertNotIn("reference_videos", captured["parameter"]["metadata"])

    def test_seedance_asset_node_uploads_image_input_and_returns_asset_id(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_seedance_asset as nodes_seedance_asset
        from oai_bridge.nodes_seedance_asset import OAISeedanceAssetNode

        captured = {}
        fake_image = object()

        class FakeClient:
            async def seedance_upload_asset(self, payload):
                captured["payload"] = payload
                return {"code": 200, "data": {"id": "asset-123"}}

        async def fake_upload_image_tensor(client, image, filename):
            captured["uploaded_image"] = (image, filename)
            return "https://tu3.oaigc.cn/uploaded-image.png"

        original_client = nodes_seedance_asset.OAIClient
        original_upload_image = nodes_seedance_asset.upload_image_tensor
        nodes_seedance_asset.OAIClient = lambda: FakeClient()
        nodes_seedance_asset.upload_image_tensor = fake_upload_image_tensor
        try:
            output = asyncio.run(
                OAISeedanceAssetNode.execute(
                    **{
                        "\u56fe\u50cf": fake_image,
                        "\u8d44\u4ea7\u540d\u79f0": "person image 1",
                    }
                )
            )
        finally:
            nodes_seedance_asset.OAIClient = original_client
            nodes_seedance_asset.upload_image_tensor = original_upload_image

        self.assertEqual(captured["uploaded_image"], (fake_image, "seedance_asset_image.png"))
        self.assertEqual(captured["payload"], {"url": "https://tu3.oaigc.cn/uploaded-image.png", "asset_type": "Image", "name": "person image 1"})
        self.assertEqual(output.args, ("asset-123",))

    def test_seedance_asset_node_schema_is_image_only(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_seedance_asset import OAISeedanceAssetNode

        schema = OAISeedanceAssetNode.define_schema()
        self.assertEqual(schema.display_name, "OAI Seedance \u56fe\u50cf\u8d44\u4ea7")
        self.assertEqual([item.name for item in schema.inputs], ["\u56fe\u50cf", "\u8d44\u4ea7\u540d\u79f0"])


if __name__ == "__main__":
    unittest.main()


