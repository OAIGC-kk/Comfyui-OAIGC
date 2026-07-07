from __future__ import annotations

from comfy_api.latest import IO, UI

from .client import OAIClient
from .image_models import (
    ASPECT_RATIO_OPTIONS,
    BANANA_MODEL_OPTIONS,
    GPT_MODEL_OPTIONS,
    IMAGE_MODEL_LABELS,
    IMAGE_SIZE_OPTIONS,
    RESOLUTION_OPTIONS,
    YES_NO_OPTIONS,
    build_image_app_and_parameter,
)
from .media import download_image_url, upload_image_tensor
from .tasks import run_app

MODEL_FIELD = "\u6a21\u578b"
PROMPT_FIELD = "\u63d0\u793a\u8bcd"
IMAGE_FIELDS = [f"\u56fe\u7247{index}" for index in range(1, 13)]
ASPECT_FIELD = "\u753b\u9762\u6bd4\u4f8b"
COUNT_FIELD = "\u6570\u91cf"
MAGNIFICATION_FIELD = "\u653e\u5927\u500d\u6570"
PRE_LLM_FIELD = "\u63d0\u793a\u8bcd\u4f18\u5316"
BANANA_MODEL_FIELD = "Banana\u6a21\u578b"
IMAGE_SIZE_FIELD = "\u56fe\u50cf\u89c4\u683c"
HD_FIELD = "\u9ad8\u6e05\u6a21\u5f0f"
FAST_FIELD = "\u5feb\u901f\u6a21\u5f0f"
GPT_MODEL_FIELD = "GPT\u6a21\u578b"
RESOLUTION_FIELD = "\u5206\u8fa8\u7387"
EXPAND_TOP_FIELD = "\u5411\u4e0a\u6269\u5c55"
EXPAND_BOTTOM_FIELD = "\u5411\u4e0b\u6269\u5c55"
EXPAND_LEFT_FIELD = "\u5411\u5de6\u6269\u5c55"
EXPAND_RIGHT_FIELD = "\u5411\u53f3\u6269\u5c55"
EXTRA_FIELD = "\u9ad8\u7ea7\u53c2\u6570JSON"


class OAIImageNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OAIImageNode",
            display_name="OAI \u56fe\u50cf",
            category="OAI Bridge/\u56fe\u50cf",
            description="\u8c03\u7528 OAI \u540e\u7aef\u7684\u56fe\u50cf\u751f\u6210\u3001\u6263\u56fe\u548c\u6269\u56fe\u6a21\u578b\u3002",
            has_intermediate_output=True,
            inputs=[
                IO.Combo.Input(MODEL_FIELD, options=IMAGE_MODEL_LABELS, default=IMAGE_MODEL_LABELS[0], tooltip="\u9009\u62e9\u8981\u8c03\u7528\u7684\u56fe\u50cf\u6a21\u578b\u3002"),
                IO.String.Input(PROMPT_FIELD, multiline=True, default="", tooltip="\u6587\u751f\u56fe\u3001Banana \u751f\u56fe\u548c GPT \u751f\u56fe\u4f7f\u7528\u3002"),
                *[
                    IO.Image.Input(
                        field,
                        optional=True,
                        tooltip="\u53c2\u8003\u56fe\u6216\u5de5\u5177\u8f93\u5165\u56fe\uff0c\u672c\u5730\u56fe\u7247\u4f1a\u5148\u4e0a\u4f20\u4e3a URL\u3002"
                        if index == 1
                        else f"\u7b2c {index} \u5f20\u53c2\u8003\u56fe\uff0c\u7528\u4e8e\u652f\u6301\u591a\u56fe\u7684\u56fe\u50cf\u6a21\u578b\u3002",
                    )
                    for index, field in enumerate(IMAGE_FIELDS, start=1)
                ],
                IO.Combo.Input(ASPECT_FIELD, options=ASPECT_RATIO_OPTIONS, default="1:1", optional=True, tooltip="\u5bf9\u5e94\u6587\u6863\u4e2d\u7684 aspect_ratio/size\u3002"),
                IO.Int.Input(COUNT_FIELD, default=1, min=1, max=8, step=1, optional=True, tooltip="\u963f\u91cc\u9020\u76f8\u7684\u751f\u6210\u6570\u91cf num\u3002"),
                IO.Float.Input(MAGNIFICATION_FIELD, default=1.1, min=1.1, max=2.5, step=0.1, optional=True, tooltip="\u963f\u91cc\u9020\u76f8\u7684 magnification\u3002"),
                IO.Combo.Input(PRE_LLM_FIELD, options=YES_NO_OPTIONS, default="\u662f", optional=True, tooltip="\u963f\u91cc\u9020\u76f8\u7684 use_pre_llm\u3002"),
                IO.Combo.Input(BANANA_MODEL_FIELD, options=BANANA_MODEL_OPTIONS, default="banana2", optional=True, tooltip="Banana \u751f\u56fe\u7684 model\u3002"),
                IO.Combo.Input(IMAGE_SIZE_FIELD, options=IMAGE_SIZE_OPTIONS, default="1k", optional=True, tooltip="Banana \u751f\u56fe\u7684 image_size\u3002"),
                IO.Combo.Input(HD_FIELD, options=YES_NO_OPTIONS, default="\u5426", optional=True, tooltip="Banana \u751f\u56fe\u7684 hd\u3002"),
                IO.Combo.Input(FAST_FIELD, options=YES_NO_OPTIONS, default="\u662f", optional=True, tooltip="Banana/GPT \u751f\u56fe\u7684 fast\u3002"),
                IO.Combo.Input(GPT_MODEL_FIELD, options=GPT_MODEL_OPTIONS, default="gpt-image-2", optional=True, tooltip="GPT \u751f\u56fe\u7684 model\u3002"),
                IO.Combo.Input(RESOLUTION_FIELD, options=RESOLUTION_OPTIONS, default="1K", optional=True, tooltip="GPT \u751f\u56fe\u7684 resolution\u3002"),
                IO.String.Input(EXPAND_TOP_FIELD, default="1", optional=True, tooltip="AI\u6269\u56fe\u7684 top\u3002"),
                IO.String.Input(EXPAND_BOTTOM_FIELD, default="1", optional=True, tooltip="AI\u6269\u56fe\u7684 bottom\u3002"),
                IO.String.Input(EXPAND_LEFT_FIELD, default="1", optional=True, tooltip="AI\u6269\u56fe\u7684 left\u3002"),
                IO.String.Input(EXPAND_RIGHT_FIELD, default="1", optional=True, tooltip="AI\u6269\u56fe\u7684 right\u3002"),
            ],
            outputs=[IO.Image.Output()],
        )

    @classmethod
    async def execute(cls, **kwargs):
        extra = {}


        images = [kwargs.get(field) for field in IMAGE_FIELDS if kwargs.get(field) is not None]
        image_urls = []
        if images:
            client = OAIClient()
            image_urls = [await upload_image_tensor(client, img, f"image_{index + 1}.png") for index, img in enumerate(images)]

        app, parameter = build_image_app_and_parameter(
            kwargs[MODEL_FIELD],
            prompt=kwargs.get(PROMPT_FIELD, ""),
            image_urls=image_urls,
            aspect_ratio=kwargs.get(ASPECT_FIELD, "1:1"),
            count=kwargs.get(COUNT_FIELD, 1),
            magnification=kwargs.get(MAGNIFICATION_FIELD, 1.1),
            use_pre_llm=kwargs.get(PRE_LLM_FIELD, "\u662f"),
            banana_model=kwargs.get(BANANA_MODEL_FIELD, "banana2"),
            image_size=kwargs.get(IMAGE_SIZE_FIELD, "1k"),
            hd=kwargs.get(HD_FIELD, "\u5426"),
            fast=kwargs.get(FAST_FIELD, "\u662f"),
            gpt_model=kwargs.get(GPT_MODEL_FIELD, "gpt-image-2"),
            resolution=kwargs.get(RESOLUTION_FIELD, "1K"),
            expand_top=kwargs.get(EXPAND_TOP_FIELD, "1"),
            expand_bottom=kwargs.get(EXPAND_BOTTOM_FIELD, "1"),
            expand_left=kwargs.get(EXPAND_LEFT_FIELD, "1"),
            expand_right=kwargs.get(EXPAND_RIGHT_FIELD, "1"),
            extra=extra,
        )
        url = await run_app(app, parameter)
        image = await download_image_url(url)
        return IO.NodeOutput(image, ui=UI.ImageSaveHelper.get_save_images_ui(image, filename_prefix="OAI_Bridge", cls=cls))






