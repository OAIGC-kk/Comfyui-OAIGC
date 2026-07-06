from __future__ import annotations

from typing import Any

ALI_TEXT_IMAGE_LABEL = "\u963f\u91cc\u9020\u76f8-\u6587\u751f\u56fe"
BANANA_IMAGE_LABEL = "Banana\u751f\u56fe"
GPT_IMAGE_LABEL = "GPT \u751f\u56fe"
AGNES_IMAGE_LABEL = "Agnes Image 2.1 Flash"
CUTOUT_LABEL = "AI\u6263\u56fe"
OUTPAINT_LABEL = "AI\u6269\u56fe"

IMAGE_MODEL_LABELS = [
    GPT_IMAGE_LABEL,
    BANANA_IMAGE_LABEL,
    AGNES_IMAGE_LABEL,
    CUTOUT_LABEL,
    OUTPAINT_LABEL,
    ALI_TEXT_IMAGE_LABEL,
]

ASPECT_RATIO_OPTIONS = [
    "1:1",
    "9:16",
    "16:9",
    "2:3",
    "3:2",
    "21:9",
    "4:3",
    "3:4",
    "3:1",
    "9:21",
    "2:1",
    "4:5",
    "1:2",
    "1:3",
]
BANANA_MODEL_OPTIONS = ["banana", "banana2", "banana-pro"]
GPT_MODEL_OPTIONS = ["gpt-image-2", "gpt-image-1.5", "gpt-image-1"]
IMAGE_SIZE_OPTIONS = ["1k"]
RESOLUTION_OPTIONS = ["1K", "2K", "3K", "4K"]
YES_NO_OPTIONS = ["\u662f", "\u5426"]
ALI_ASPECT_RATIO_OPTIONS = ["9:16", "2:3", "1:1", "4:3", "3:2", "16:9"]



def _validate_ali_aspect_ratio(value: str) -> None:
    if value not in ALI_ASPECT_RATIO_OPTIONS:
        supported = "、".join(ALI_ASPECT_RATIO_OPTIONS)
        raise ValueError(f"阿里造相-文生图当前仅支持画面比例 {supported}，请把画面比例改为 {supported}。")
def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip() not in {"\u5426", "false", "False", "0", "no", "No"}


def _first_image(image_urls: list[str], extra: dict[str, Any]) -> str:
    image = image_urls[0] if image_urls else extra.get("image")
    if not image:
        raise ValueError("\u8bf7\u8fde\u63a5\u56fe\u72471\uff0c\u6216\u5728\u9ad8\u7ea7\u53c2\u6570JSON \u4e2d\u4f20\u5165 image\u3002")
    return image


def build_image_app_and_parameter(
    model_label: str,
    *,
    prompt: str = "",
    image_urls: list[str] | None = None,
    aspect_ratio: str = "1:1",
    count: int = 1,
    magnification: float = 1.1,
    use_pre_llm: bool | str = True,
    banana_model: str = "banana2",
    image_size: str = "1k",
    hd: bool | str = False,
    fast: bool | str = True,
    gpt_model: str = "gpt-image-2",
    resolution: str = "1K",
    expand_top: str = "1",
    expand_bottom: str = "1",
    expand_left: str = "1",
    expand_right: str = "1",
    extra: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    image_urls = image_urls or []
    extra = dict(extra or {})

    if model_label == ALI_TEXT_IMAGE_LABEL:
        parameter = {
            "prompt": prompt,
            "num": int(count),
            "magnification": float(magnification),
            "aspect_ratio": aspect_ratio,
            "use_pre_llm": _as_bool(use_pre_llm),
        }
        parameter.update(extra)
        _validate_ali_aspect_ratio(str(parameter.get("aspect_ratio", "")))
        return {"id": "z-imagewenshengt", "mode": "task_submit"}, parameter

    if model_label == BANANA_IMAGE_LABEL:
        parameter = {
            "prompt": prompt,
            "model": banana_model,
            "size": aspect_ratio,
            "image_size": image_size,
            "fast": _as_bool(fast),
        }
        if banana_model == "banana":
            parameter["hd"] = _as_bool(hd)
        images = image_urls or extra.get("images")
        if images:
            parameter["images"] = images
        parameter.update(extra)
        if banana_model != "banana":
            parameter.pop("hd", None)
        return {"id": "banana", "mode": "banana_sync"}, parameter

    if model_label == GPT_IMAGE_LABEL:
        parameter = {
            "prompt": prompt,
            "model": gpt_model,
            "size": aspect_ratio,
            "fast": _as_bool(fast),
            "resolution": resolution,
        }
        images = image_urls or extra.get("images")
        if images:
            parameter["images"] = images
        parameter.update(extra)
        return {"id": "gpt-image", "mode": "gpt_image"}, parameter

    if model_label == AGNES_IMAGE_LABEL:
        parameter = {
            "model": "agnes-image-2.1-flash",
            "prompt": prompt,
            "size": resolution,
            "ratio": aspect_ratio,
            "images": image_urls or extra.get("images", []),
            "n": int(count),
            "response_format": "url",
        }
        parameter.update(extra)
        return {"id": "agnes-image-2.1-flash", "mode": "agnes_image"}, parameter

    if model_label == CUTOUT_LABEL:
        parameter = {"image": _first_image(image_urls, extra)}
        parameter.update(extra)
        return {"id": "tupiankoutu", "mode": "task_submit"}, parameter

    if model_label == OUTPAINT_LABEL:
        parameter = {
            "image": _first_image(image_urls, extra),
            "top": str(expand_top),
            "bottom": str(expand_bottom),
            "left": str(expand_left),
            "right": str(expand_right),
        }
        parameter.update(extra)
        return {"id": "kuotu", "mode": "task_submit"}, parameter

    raise ValueError(f"\u672a\u652f\u6301\u7684\u56fe\u50cf\u6a21\u578b\uff1a{model_label}")




