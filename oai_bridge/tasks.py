from __future__ import annotations

import asyncio
import time
from typing import Any

from .client import OAIAPIError, OAIClient
from .config import load_config

IMAGE_TASK_POLL_TIMEOUT = 15 * 60
VIDEO_TASK_POLL_TIMEOUT = 30 * 60


def _extract_task_id(response: dict[str, Any]) -> str:
    data = response.get("data") or {}
    task_id = data.get("taskId") or data.get("task_id")
    if not task_id:
        raise OAIAPIError("\u540e\u7aef\u6ca1\u6709\u8fd4\u56de\u4efb\u52a1 ID\u3002")
    return task_id


def _extract_general_result(response: dict[str, Any]) -> tuple[str, str]:
    data = response.get("data") or {}
    status = data.get("status", "")
    result = data.get("result", "")
    return status, result


def _format_task_failure(data: dict[str, Any]) -> str:
    for key in ("message", "error", "reason", "result"):
        value = data.get(key)
        if value:
            return str(value)
    return ""


async def _poll_general(client: OAIClient, task_id: str) -> str:
    cfg = load_config()
    deadline = time.monotonic() + IMAGE_TASK_POLL_TIMEOUT
    while time.monotonic() < deadline:
        response = await client.query_task(task_id)
        status, result = _extract_general_result(response)
        if status == "success":
            if not result:
                raise OAIAPIError("\u4efb\u52a1\u6210\u529f\uff0c\u4f46\u540e\u7aef\u6ca1\u6709\u8fd4\u56de\u7ed3\u679c URL\u3002")
            return result
        if status == "failed":
            detail = _format_task_failure(response.get("data") or {})
            if detail:
                raise OAIAPIError(f"\u4efb\u52a1\u751f\u6210\u5931\u8d25\uff1a{detail}")
            raise OAIAPIError("\u4efb\u52a1\u751f\u6210\u5931\u8d25\u3002")
        await asyncio.sleep(cfg.poll_interval)
    raise OAIAPIError("\u4efb\u52a1\u8f6e\u8be2\u8d85\u65f6\u3002")


async def _poll_seedance(client: OAIClient, task_id: str) -> str:
    cfg = load_config()
    deadline = time.monotonic() + VIDEO_TASK_POLL_TIMEOUT
    while time.monotonic() < deadline:
        response = await client.seedance_query(task_id)
        data = response.get("data") or {}
        status = data.get("status", "")
        if status == "completed":
            video_url = data.get("video_url")
            if not video_url:
                raise OAIAPIError("Seedance \u4efb\u52a1\u6210\u529f\uff0c\u4f46\u6ca1\u6709\u8fd4\u56de\u89c6\u9891 URL\u3002")
            return video_url
        if status in {"failed", "error"}:
            raise OAIAPIError("Seedance \u4efb\u52a1\u751f\u6210\u5931\u8d25\u3002")
        await asyncio.sleep(cfg.poll_interval)
    raise OAIAPIError("Seedance \u4efb\u52a1\u8f6e\u8be2\u8d85\u65f6\u3002")


def _extract_image_url(response: dict[str, Any], label: str) -> str:
    image_url = (response.get("data") or {}).get("imageUrl")
    if not image_url:
        raise OAIAPIError(f"{label} \u751f\u6210\u6210\u529f\uff0c\u4f46\u6ca1\u6709\u8fd4\u56de\u56fe\u7247 URL\u3002")
    return image_url


def _extract_openai_image_url(response: dict[str, Any], label: str) -> str:
    data = response.get("data") or []
    first = data[0] if data else {}
    image_url = first.get("url") if isinstance(first, dict) else ""
    if not image_url:
        raise OAIAPIError(f"{label} \u751f\u6210\u6210\u529f\uff0c\u4f46\u6ca1\u6709\u8fd4\u56de\u56fe\u7247 URL\u3002")
    return image_url


def _extract_dialogue_content(response: dict[str, Any]) -> str:
    data = response.get("data") or {}
    content = data.get("content") if isinstance(data, dict) else None
    if content is None:
        raise OAIAPIError("LLM \u5bf9\u8bdd\u6210\u529f\uff0c\u4f46\u540e\u7aef\u6ca1\u6709\u8fd4\u56de content\u3002")
    return str(content)


async def run_dialogue(parameter: dict[str, Any]) -> str:
    client = OAIClient(load_config())
    response = await client.dialogue_execute(parameter)
    return _extract_dialogue_content(response)


async def run_app(app: dict[str, Any], parameter: dict[str, Any]) -> str:
    client = OAIClient(load_config())
    mode = app.get("mode", "task_submit")
    app_id = app.get("id")
    if mode == "banana_sync":
        response = await client.banana_generate(parameter)
        return _extract_image_url(response, "Banana")
    if mode == "gpt_image":
        response = await client.gpt_image_generate(parameter)
        return _extract_image_url(response, "GPT \u751f\u56fe")
    if mode == "agnes_image":
        response = await client.image_generations(parameter)
        return _extract_openai_image_url(response, "Agnes Image 2.1 Flash")
    if mode == "seedance":
        response = await client.seedance_create(parameter)
        return await _poll_seedance(client, _extract_task_id(response))
    response = await client.submit_task(app_id, parameter)
    return await _poll_general(client, _extract_task_id(response))