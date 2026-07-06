from __future__ import annotations

from comfy_api.latest import IO

from .client import OAIAPIError, OAIClient
from .media import upload_image_tensor

IMAGE_FIELD = "\u56fe\u50cf"
ASSET_NAME_FIELD = "\u8d44\u4ea7\u540d\u79f0"


def _extract_asset_id(response: dict) -> str:
    data = response.get("data")
    if isinstance(data, dict):
        return str(data.get("id") or data.get("asset_id") or data.get("assetId") or "")
    if data:
        return str(data)
    return ""


async def upload_seedance_asset(client: OAIClient, url: str, asset_type: str, name: str) -> str:
    response = await client.seedance_upload_asset({"url": url, "asset_type": asset_type, "name": name})
    asset_id = _extract_asset_id(response)
    if not asset_id:
        raise OAIAPIError("Seedance \u8d44\u4ea7\u4e0a\u4f20\u6210\u529f\uff0c\u4f46\u540e\u7aef\u6ca1\u6709\u8fd4\u56de\u8d44\u4ea7 ID\u3002")
    return asset_id


class OAISeedanceAssetNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OAISeedanceAssetNode",
            display_name="OAI Seedance \u56fe\u50cf\u8d44\u4ea7",
            category="OAI Bridge/\u89c6\u9891",
            description="\u628a ComfyUI \u56fe\u50cf\u8f93\u5165\u4e0a\u4f20\u5e76\u6ce8\u518c\u4e3a Seedance \u56fe\u50cf\u8d44\u4ea7\uff0c\u8f93\u51fa\u8d44\u4ea7 ID \u4f9b\u89c6\u9891\u8282\u70b9\u5f15\u7528\u3002",
            inputs=[
                IO.Image.Input(IMAGE_FIELD, tooltip="\u9700\u8981\u6ce8\u518c\u6210 Seedance \u8d44\u4ea7\u7684\u56fe\u50cf\u3002"),
                IO.String.Input(ASSET_NAME_FIELD, default="", tooltip="\u8d44\u4ea7\u540d\u79f0\uff0c\u4fbf\u4e8e\u5728\u63d0\u793a\u8bcd\u91cc\u6309\u987a\u5e8f\u63cf\u8ff0\u3002"),
            ],
            outputs=[IO.String.Output(display_name="\u8d44\u4ea7ID")],
        )

    @classmethod
    async def execute(cls, **kwargs):
        image = kwargs.get(IMAGE_FIELD)
        if image is None:
            raise ValueError("\u56fe\u50cf\u4e0d\u80fd\u4e3a\u7a7a\u3002")
        client = OAIClient()
        image_url = await upload_image_tensor(client, image, "seedance_asset_image.png")
        name = (kwargs.get(ASSET_NAME_FIELD) or "Seedance \u56fe\u50cf\u8d44\u4ea7").strip() or "Seedance \u56fe\u50cf\u8d44\u4ea7"
        asset_id = await upload_seedance_asset(client, image_url, "Image", name)
        return IO.NodeOutput(asset_id)
