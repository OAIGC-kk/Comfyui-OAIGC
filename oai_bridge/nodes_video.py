from __future__ import annotations

import json

from comfy_api.latest import IO

from .client import OAIClient
from .media import download_video_url, upload_audio_input, upload_image_tensor, upload_video_input
from .metadata import load_app_options
from .registry import app_label
from .tasks import run_app


APP_FIELD = "\u5e94\u7528"
PROMPT_FIELD = "\u63d0\u793a\u8bcd"
VIDEO_MODEL_FIELD = "\u89c6\u9891\u6a21\u578b"
ASPECT_FIELD = "\u753b\u9762\u6bd4\u4f8b"
DURATION_FIELD = "\u65f6\u957f"
RESOLUTION_FIELD = "\u6e05\u6670\u5ea6"
GENERATE_AUDIO_FIELD = "\u751f\u6210\u97f3\u9891"
EXTRA_FIELD = "\u9ad8\u7ea7\u53c2\u6570JSON"
IMAGE_FIELDS = [f"\u56fe\u7247{index}" for index in range(1, 10)]
VIDEO_FIELDS = [f"\u89c6\u9891{index}" for index in range(1, 4)]
AUDIO_FIELDS = [f"\u97f3\u9891{index}" for index in range(1, 4)]
IMAGE_ASSET_FIELDS = [f"\u56fe\u7247\u8d44\u4ea7ID{index}" for index in range(1, 10)]
SEEDANCE_MODEL_VALUE_BY_LABEL = {
    "seedance2.0": "seed-2",
    "seedance2.0-visio": "seed-2-visio",
    "seedance2.0-fast-vision": "seed-2-fast-vision",
    "seedance2.0-fast": "seed-2-fast",
}
SEEDANCE_MODEL_OPTIONS = ["seedance2.0", "seedance2.0-fast"]
SEEDANCE_REFERENCE_VIDEO_REQUIRED_MODELS = {"seed-2-visio", "seed-2-fast-vision"}
SEEDANCE_REFERENCE_VIDEO_MODEL_BY_BASE = {
    "seed-2": "seed-2-visio",
    "seed-2-fast": "seed-2-fast-vision",
}
YES_NO_OPTIONS = ["\u662f", "\u5426"]


def _seedance_model_value(label: str | None) -> str:
    if not label:
        return "seed-2"
    return SEEDANCE_MODEL_VALUE_BY_LABEL.get(label, label)


def _seedance_model_value_for_inputs(label: str | None, has_reference_video: bool) -> str:
    model_value = _seedance_model_value(label)
    if has_reference_video:
        return SEEDANCE_REFERENCE_VIDEO_MODEL_BY_BASE.get(model_value, model_value)
    return model_value


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip() not in {"\u5426", "false", "False", "0", "no", "No"}


def _asset_ids(values: list[str | None]) -> list[str]:
    return [str(value).strip() for value in values if str(value or "").strip()]


def _video_apps() -> list[dict]:
    return load_app_options("video")


def _video_app_choices() -> list[str]:
    return [app_label(app) for app in _video_apps()]


def _find_video_app(label: str) -> dict:
    apps = _video_apps()
    for app in apps:
        if app_label(app) == label:
            return app
    if not apps:
        raise ValueError("\u6ca1\u6709\u53ef\u7528\u7684\u89c6\u9891\u5e94\u7528\uff0c\u8bf7\u5148\u5237\u65b0\u5e94\u7528\u5217\u8868\u3002")
    return apps[0]


class OAIVideoNode(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="OAIVideoNode",
            display_name="OAI \u89c6\u9891",
            category="OAI Bridge/\u89c6\u9891",
            description="\u8c03\u7528 Seedance \u89c6\u9891\u63a5\u53e3\uff0c\u652f\u6301\u56fe\u7247\u3001\u89c6\u9891\u3001\u97f3\u9891\u8f93\u5165\uff0c\u4ee5\u53ca\u53ef\u9009 Seedance \u56fe\u50cf\u8d44\u4ea7 ID\u3002",
            inputs=[
                IO.Combo.Input(APP_FIELD, options=_video_app_choices(), tooltip="\u9009\u62e9 Seedance \u89c6\u9891\u5e94\u7528\u3002"),
                IO.String.Input(PROMPT_FIELD, multiline=True, default="", tooltip="Seedance \u89c6\u9891\u751f\u6210\u63d0\u793a\u8bcd\u3002"),
                IO.Combo.Input(
                    VIDEO_MODEL_FIELD,
                    options=SEEDANCE_MODEL_OPTIONS,
                    default="seedance2.0",
                    tooltip="\u9009\u62e9 Seedance \u89c6\u9891\u6a21\u578b\u3002\u8fde\u63a5\u89c6\u9891\u8f93\u5165\u65f6\u4f1a\u81ea\u52a8\u5207\u6362\u5230\u5bf9\u5e94 vision \u6a21\u578b\u3002",
                ),
                IO.Combo.Input(
                    ASPECT_FIELD,
                    options=["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "adaptive"],
                    default="16:9",
                    tooltip="\u8f93\u51fa\u89c6\u9891\u6bd4\u4f8b\uff0c\u9ed8\u8ba4 16:9\u3002",
                ),
                IO.Int.Input(DURATION_FIELD, default=4, min=4, max=15, step=1, tooltip="\u89c6\u9891\u65f6\u957f\uff0c\u8303\u56f4 4-15 \u79d2\u3002"),
                IO.Combo.Input(
                    RESOLUTION_FIELD,
                    options=["480p", "720p", "1080p"],
                    default="720p",
                    tooltip="\u8f93\u51fa\u6e05\u6670\u5ea6\uff0c\u9ed8\u8ba4 720p\u3002",
                ),
                IO.Combo.Input(
                    GENERATE_AUDIO_FIELD,
                    options=YES_NO_OPTIONS,
                    default="\u662f",
                    tooltip="\u662f\u5426\u751f\u6210\u540c\u6b65\u97f3\u9891\uff0c\u9ed8\u8ba4\u662f\u3002",
                ),
                *[
                    IO.Image.Input(field, optional=True, tooltip=f"\u53ef\u9009\uff0c\u7b2c {index} \u5f20\u56fe\u7247\uff0c\u4f1a\u81ea\u52a8\u4e0a\u4f20\u4e3a\u56fe\u7247 URL\u3002")
                    for index, field in enumerate(IMAGE_FIELDS, start=1)
                ],
                *[
                    IO.Video.Input(field, optional=True, tooltip=f"\u53ef\u9009\uff0c\u7b2c {index} \u4e2a\u89c6\u9891\uff0c\u4f1a\u81ea\u52a8\u4e0a\u4f20\u4e3a\u89c6\u9891 URL\u3002")
                    for index, field in enumerate(VIDEO_FIELDS, start=1)
                ],
                *[
                    IO.Audio.Input(field, optional=True, tooltip=f"\u53ef\u9009\uff0c\u7b2c {index} \u4e2a\u97f3\u9891\uff0c\u4f1a\u81ea\u52a8\u4e0a\u4f20\u4e3a\u97f3\u9891 URL\u3002")
                    for index, field in enumerate(AUDIO_FIELDS, start=1)
                ],
                *[
                    IO.String.Input(field, default="", optional=True, force_input=True, tooltip=f"\u53ef\u9009\uff0c\u7b2c {index} \u4e2a\u56fe\u7247\u8d44\u4ea7 ID\uff0c\u7531 OAI Seedance \u56fe\u50cf\u8d44\u4ea7\u8282\u70b9\u8f93\u51fa\u3002")
                    for index, field in enumerate(IMAGE_ASSET_FIELDS, start=1)
                ],
            ],
            outputs=[IO.Video.Output()],
        )

    @classmethod
    async def execute(cls, **kwargs):
        app = _find_video_app(kwargs.get(APP_FIELD, ""))
        try:
            extra = json.loads(kwargs.get(EXTRA_FIELD) or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("\u9ad8\u7ea7\u53c2\u6570JSON \u683c\u5f0f\u4e0d\u6b63\u786e\u3002") from exc

        image_inputs = [kwargs.get(field) for field in IMAGE_FIELDS]
        video_inputs = [kwargs.get(field) for field in VIDEO_FIELDS]
        audio_inputs = [kwargs.get(field) for field in AUDIO_FIELDS]
        image_asset_ids = _asset_ids([kwargs.get(field) for field in IMAGE_ASSET_FIELDS])
        connected_images = [(index, image) for index, image in enumerate(image_inputs, start=1) if image is not None]
        connected_videos = [(index, video) for index, video in enumerate(video_inputs, start=1) if video is not None]
        connected_audios = [(index, audio) for index, audio in enumerate(audio_inputs, start=1) if audio is not None]
        needs_upload_client = bool(connected_images or connected_videos or connected_audios)
        if needs_upload_client:
            client = OAIClient()
            image_urls = [
                await upload_image_tensor(client, image, f"reference_image_{index}.png")
                for index, image in connected_images
            ]
            uploaded_video_urls = [
                await upload_video_input(client, video, f"reference_video_{index}.mp4")
                for index, video in connected_videos
            ]
            uploaded_audio_urls = [
                await upload_audio_input(client, audio, f"reference_audio_{index}.wav")
                for index, audio in connected_audios
            ]
        else:
            image_urls = []
            uploaded_video_urls = []
            uploaded_audio_urls = []

        if app.get("mode") == "seedance":
            metadata = {
                "ratio": kwargs.get(ASPECT_FIELD, "16:9"),
                "duration": kwargs.get(DURATION_FIELD, 4),
                "resolution": kwargs.get(RESOLUTION_FIELD, "720p"),
                "generate_audio": _as_bool(kwargs.get(GENERATE_AUDIO_FIELD, "\u662f")),
            }
            if image_urls:
                metadata["reference_images"] = image_urls
            if uploaded_video_urls:
                metadata["reference_videos"] = uploaded_video_urls
            if uploaded_audio_urls:
                metadata["reference_audios"] = uploaded_audio_urls
            if image_asset_ids:
                metadata["reference_image_asset_ids"] = image_asset_ids
            metadata.update(extra.pop("metadata", {}))
            model_value = _seedance_model_value_for_inputs(kwargs.get(VIDEO_MODEL_FIELD, "seedance2.0"), bool(metadata.get("reference_videos")))
            if model_value in SEEDANCE_REFERENCE_VIDEO_REQUIRED_MODELS and not metadata.get("reference_videos"):
                raise ValueError("\u5f53\u524d\u89c6\u9891\u6a21\u578b\u9700\u8981\u8fde\u63a5\u89c6\u9891\u8f93\u5165\u3002")
            parameter = {"model": extra.pop("model", model_value), "prompt": kwargs.get(PROMPT_FIELD, ""), "metadata": metadata}
            parameter.update(extra)
        else:
            parameter = extra

        url = await run_app(app, parameter)
        return IO.NodeOutput(await download_video_url(url))

