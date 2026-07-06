from __future__ import annotations

from comfy_api.latest import IO

from .client import OAIClient
from .media import upload_image_tensor
from .tasks import run_dialogue

MODEL_FIELD = "\u6a21\u578b"
SYSTEM_PROMPT_FIELD = "\u524d\u7f6e\u63d0\u793a\u8bcd"
USER_INPUT_FIELD = "\u7528\u6237\u8f93\u5165\u63d0\u793a\u8bcd"
IMAGE_FIELDS = [f"\u56fe\u7247{index}" for index in range(1, 7)]
LLM_MODEL_OPTIONS = ["gpt-5.4", "gpt-5.5", "claude-opus-4-8", "claude-opus-4-7", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
DEFAULT_MODEL = "gpt-5.5"


class OAILLMNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OAILLMNode",
            display_name="OAI LLM \u5bf9\u8bdd",
            category="OAI Bridge/\u6587\u672c",
            description="\u8c03\u7528 OAI \u540e\u7aef LLM \u5bf9\u8bdd\u63a5\u53e3\uff0c\u652f\u6301\u6587\u672c\u548c\u56fe\u7247\u8f93\u5165\u3002",
            inputs=[
                IO.Combo.Input(MODEL_FIELD, options=LLM_MODEL_OPTIONS, default=DEFAULT_MODEL, tooltip="\u9009\u62e9\u5bf9\u8bdd\u6a21\u578b\u3002"),
                IO.String.Input(SYSTEM_PROMPT_FIELD, multiline=True, default="", tooltip="\u5bf9\u5e94\u6587\u6863\u4e2d\u7684 system_prompt\u3002"),
                IO.String.Input(USER_INPUT_FIELD, multiline=True, default="", tooltip="\u5bf9\u5e94\u6587\u6863\u4e2d\u7684 user_input\u3002"),
                *[
                    IO.Image.Input(
                        field,
                        optional=True,
                        tooltip="\u53ef\u9009\u56fe\u7247\u8f93\u5165\uff0c\u672c\u5730\u56fe\u7247\u4f1a\u5148\u4e0a\u4f20\u4e3a URL \u540e\u653e\u5165 images \u6570\u7ec4\u3002"
                        if index == 1
                        else f"\u7b2c {index} \u5f20\u53ef\u9009\u56fe\u7247\uff0c\u4f1a\u4e0a\u4f20\u540e\u8ffd\u52a0\u5230 images \u6570\u7ec4\u3002",
                    )
                    for index, field in enumerate(IMAGE_FIELDS, start=1)
                ],
            ],
            outputs=[IO.String.Output(display_name="\u56de\u590d\u5185\u5bb9")],
        )

    @classmethod
    async def execute(cls, **kwargs):
        images = [kwargs.get(field) for field in IMAGE_FIELDS if kwargs.get(field) is not None]
        image_urls = []
        if images:
            client = OAIClient()
            image_urls = [await upload_image_tensor(client, img, f"image_{index + 1}.png") for index, img in enumerate(images)]

        parameter = {
            "model": (kwargs.get(MODEL_FIELD) or DEFAULT_MODEL).strip() or DEFAULT_MODEL,
            "system_prompt": kwargs.get(SYSTEM_PROMPT_FIELD, "") or "",
            "user_input": kwargs.get(USER_INPUT_FIELD, "") or "",
            "images": image_urls,
            "video": "",
        }
        content = await run_dialogue(parameter)
        return IO.NodeOutput(content)