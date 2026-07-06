from __future__ import annotations

from typing import Any

BUILTIN_APPS: list[dict[str, Any]] = [
    {"id": "banana", "label": "Banana 生图", "category": "image", "mode": "banana_sync", "output": "image"},
    {"id": "qwenedit", "label": "Qwen 编辑图像", "category": "image", "mode": "task_submit", "output": "image"},    {"id": "seedance", "label": "Seedance 视频", "category": "video", "mode": "seedance", "output": "video"},
]


def app_label(app: dict[str, Any]) -> str:
    return f"{app.get('label', app.get('id', '未知应用'))} ({app.get('id', '')})"


def merge_apps(dynamic_apps: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    apps_by_id = {app["id"]: dict(app) for app in BUILTIN_APPS}
    for app in dynamic_apps or []:
        app_id = app.get("id") or app.get("name")
        if not app_id:
            continue
        merged = apps_by_id.get(app_id, {"id": app_id})
        merged.update(app)
        merged.setdefault("label", app.get("alias") or app_id)
        merged.setdefault("category", "image")
        merged.setdefault("mode", "task_submit")
        merged.setdefault("output", "image")
        apps_by_id[app_id] = merged
    return list(apps_by_id.values())


def filter_apps(apps: list[dict[str, Any]], category: str) -> list[dict[str, Any]]:
    return [app for app in apps if app.get("category") == category]
