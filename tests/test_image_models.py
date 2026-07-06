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

        class Image:
            Input = FakeInput
            Output = FakeOutput

        class Int:
            Input = FakeInput

        class Float:
            Input = FakeInput

    class FakeUI:
        class PreviewImage:
            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

    comfy_api = types.ModuleType("comfy_api")
    latest = types.ModuleType("comfy_api.latest")
    latest.IO = FakeIO
    latest.UI = FakeUI
    sys.modules["comfy_api"] = comfy_api
    sys.modules["comfy_api.latest"] = latest


class ImageModelTests(unittest.TestCase):
    def test_image_model_list_is_limited_to_requested_models(self):
        from oai_bridge.image_models import IMAGE_MODEL_LABELS

        self.assertEqual(
            IMAGE_MODEL_LABELS,
            [
                "GPT \u751f\u56fe",
                "Banana\u751f\u56fe",
                "Agnes Image 2.1 Flash",
                "AI\u6263\u56fe",
                "AI\u6269\u56fe",
                "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe",
            ],
        )

    def test_schema_default_model_uses_gpt_image(self):
        _install_fake_comfy_io()

        from oai_bridge.image_models import GPT_IMAGE_LABEL
        from oai_bridge.nodes_image import OAIImageNode

        schema = OAIImageNode.define_schema()
        model_input = next(item for item in schema.inputs if item.name == "\u6a21\u578b")

        self.assertEqual(model_input.kwargs.get("default"), GPT_IMAGE_LABEL)

    def test_schema_declares_intermediate_preview_output(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_image import OAIImageNode

        schema = OAIImageNode.define_schema()

        self.assertTrue(schema.has_intermediate_output)

    def test_execute_returns_preview_image_metadata(self):
        _install_fake_comfy_io()

        import oai_bridge.nodes_image as nodes_image
        from oai_bridge.nodes_image import OAIImageNode

        async def fake_run_app(app, parameter):
            return "https://example.test/generated.png"

        async def fake_download_image_url(url):
            return "image-tensor"

        async def run_case():
            original_run_app = nodes_image.run_app
            original_download_image_url = nodes_image.download_image_url
            nodes_image.run_app = fake_run_app
            nodes_image.download_image_url = fake_download_image_url
            try:
                return await OAIImageNode.execute(**{nodes_image.MODEL_FIELD: "GPT 生图", nodes_image.PROMPT_FIELD: "test"})
            finally:
                nodes_image.run_app = original_run_app
                nodes_image.download_image_url = original_download_image_url

        output = asyncio.run(run_case())

        self.assertEqual(output.args, ("image-tensor",))
        self.assertIn("ui", output.kwargs)
        self.assertEqual(output.kwargs["ui"].__class__.__name__, "PreviewImage")
        self.assertEqual(output.kwargs["ui"].args, ("image-tensor",))
        self.assertEqual(output.kwargs["ui"].kwargs, {"cls": OAIImageNode})


    def test_schema_does_not_expose_advanced_json_input(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_image import EXTRA_FIELD, OAIImageNode

        schema = OAIImageNode.define_schema()
        input_names = [item.name for item in schema.inputs]

        self.assertNotIn(EXTRA_FIELD, input_names)
    def test_schema_model_combo_uses_requested_models(self):
        _install_fake_comfy_io()

        from oai_bridge.image_models import IMAGE_MODEL_LABELS
        from oai_bridge.nodes_image import OAIImageNode

        schema = OAIImageNode.define_schema()
        model_input = next(item for item in schema.inputs if item.name == "\u6a21\u578b")

        self.assertEqual(model_input.options, IMAGE_MODEL_LABELS)

    def test_schema_sets_banana_hd_default_off(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_image import OAIImageNode

        schema = OAIImageNode.define_schema()
        hd_input = next(item for item in schema.inputs if item.name == "\u9ad8\u6e05\u6a21\u5f0f")

        self.assertEqual(hd_input.kwargs.get("default"), "\u5426")

    def test_schema_exposes_twelve_optional_image_inputs(self):
        _install_fake_comfy_io()

        from oai_bridge.nodes_image import OAIImageNode

        schema = OAIImageNode.define_schema()
        image_inputs = [item for item in schema.inputs if item.name.startswith("\u56fe\u7247")]

        self.assertEqual([item.name for item in image_inputs], [f"\u56fe\u7247{index}" for index in range(1, 13)])
        self.assertTrue(all(item.kwargs.get("optional") for item in image_inputs))

    def test_ali_text_to_image_payload_contains_all_documented_parameters(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe",
            prompt="\u4e00\u53ea\u767d\u8272\u676f\u5b50",
            image_urls=[],
            aspect_ratio="1:1",
            count=2,
            magnification=1.5,
            use_pre_llm=False,
        )

        self.assertEqual(app, {"id": "z-imagewenshengt", "mode": "task_submit"})
        self.assertEqual(
            parameter,
            {
                "prompt": "\u4e00\u53ea\u767d\u8272\u676f\u5b50",
                "num": 2,
                "magnification": 1.5,
                "aspect_ratio": "1:1",
                "use_pre_llm": False,
            },
        )

    def test_ali_text_to_image_accepts_supported_aspect_ratios(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        for aspect_ratio in ("9:16", "2:3", "1:1", "4:3", "3:2", "16:9"):
            with self.subTest(aspect_ratio=aspect_ratio):
                app, parameter = build_image_app_and_parameter(
                    "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe",
                    prompt="\u4e00\u4e2a\u4e2d\u56fd\u7f8e\u5973",
                    image_urls=[],
                    aspect_ratio=aspect_ratio,
                )

                self.assertEqual(parameter["aspect_ratio"], aspect_ratio)

    def test_ali_text_to_image_rejects_unsupported_aspect_ratio(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        with self.assertRaisesRegex(ValueError, "9:16"):
            build_image_app_and_parameter(
                "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe",
                prompt="\u4e00\u4e2a\u4e2d\u56fd\u7f8e\u5973",
                image_urls=[],
                aspect_ratio="21:9",
            )
    def test_banana2_and_banana_pro_payload_omit_hd(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        for banana_model in ("banana2", "banana-pro"):
            with self.subTest(banana_model=banana_model):
                app, parameter = build_image_app_and_parameter(
                    "Banana\u751f\u56fe",
                    prompt="\u4ea7\u54c1\u6d77\u62a5",
                    image_urls=["https://example.test/a.png", "https://example.test/b.png"],
                    aspect_ratio="9:16",
                    banana_model=banana_model,
                    image_size="1k",
                    hd=True,
                    fast=False,
                )

                self.assertEqual(app, {"id": "banana", "mode": "banana_sync"})
                self.assertEqual(
                    parameter,
                    {
                        "prompt": "\u4ea7\u54c1\u6d77\u62a5",
                        "model": banana_model,
                        "size": "9:16",
                        "image_size": "1k",
                        "fast": False,
                        "images": ["https://example.test/a.png", "https://example.test/b.png"],
                    },
                )

    def test_banana_payload_includes_hd_default_off(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "Banana\u751f\u56fe",
            prompt="\u4ea7\u54c1\u6d77\u62a5",
            banana_model="banana",
        )

        self.assertEqual(app, {"id": "banana", "mode": "banana_sync"})
        self.assertEqual(parameter["model"], "banana")
        self.assertEqual(parameter["hd"], False)

    def test_gpt_image_payload_contains_all_documented_parameters(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "GPT \u751f\u56fe",
            prompt="\u7535\u5f71\u611f\u4eba\u50cf",
            image_urls=["https://example.test/ref.png"],
            aspect_ratio="3:2",
            gpt_model="gpt-image-1.5",
            fast=True,
            resolution="4K",
        )

        self.assertEqual(app, {"id": "gpt-image", "mode": "gpt_image"})
        self.assertEqual(
            parameter,
            {
                "prompt": "\u7535\u5f71\u611f\u4eba\u50cf",
                "model": "gpt-image-1.5",
                "size": "3:2",
                "fast": True,
                "resolution": "4K",
                "images": ["https://example.test/ref.png"],
            },
        )

    def test_agnes_payload_uses_recommended_image_generations_endpoint(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "Agnes Image 2.1 Flash",
            prompt="\u672a\u6765\u57ce\u5e02\u6d77\u62a5",
            image_urls=["https://example.test/ref.png"],
            aspect_ratio="21:9",
            count=1,
            resolution="3K",
        )

        self.assertEqual(app, {"id": "agnes-image-2.1-flash", "mode": "agnes_image"})
        self.assertEqual(
            parameter,
            {
                "model": "agnes-image-2.1-flash",
                "prompt": "\u672a\u6765\u57ce\u5e02\u6d77\u62a5",
                "size": "3K",
                "ratio": "21:9",
                "images": ["https://example.test/ref.png"],
                "n": 1,
                "response_format": "url",
            },
        )

    def test_cutout_payload_uses_uploaded_image(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "AI\u6263\u56fe",
            prompt="",
            image_urls=["https://example.test/input.png"],
        )

        self.assertEqual(app, {"id": "tupiankoutu", "mode": "task_submit"})
        self.assertEqual(parameter, {"image": "https://example.test/input.png"})

    def test_outpaint_payload_contains_all_documented_parameters(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        app, parameter = build_image_app_and_parameter(
            "AI\u6269\u56fe",
            prompt="",
            image_urls=["https://example.test/input.png"],
            expand_top="2",
            expand_bottom="3",
            expand_left="4",
            expand_right="5",
        )

        self.assertEqual(app, {"id": "kuotu", "mode": "task_submit"})
        self.assertEqual(
            parameter,
            {
                "image": "https://example.test/input.png",
                "top": "2",
                "bottom": "3",
                "left": "4",
                "right": "5",
            },
        )

    def test_image_tools_require_uploaded_image(self):
        from oai_bridge.image_models import build_image_app_and_parameter

        with self.assertRaisesRegex(ValueError, "\u8bf7\u8fde\u63a5\u56fe\u72471"):
            build_image_app_and_parameter("AI\u6263\u56fe", prompt="", image_urls=[])


if __name__ == "__main__":
    unittest.main()











