from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from .client import OAIClient
from .config import DATA_DIR, load_config
from .registry import filter_apps, merge_apps

CACHE_PATH = DATA_DIR / "metadata.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_metadata_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        apps = merge_apps()
        return {"updated_at": "", "apps": apps, "models": [], "source": "builtin"}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        apps = merge_apps()
        return {"updated_at": "", "apps": apps, "models": [], "source": "builtin"}


def write_metadata_cache(data: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


async def refresh_metadata() -> dict[str, Any]:
    client = OAIClient(load_config())
    response = await client.get_model_list()
    models = response.get("data", {}).get("models", [])
    apps = merge_apps(models)
    data = {"updated_at": _now_iso(), "apps": apps, "models": models, "source": "backend"}
    write_metadata_cache(data)
    return data


def load_app_options(category: str) -> list[dict[str, Any]]:
    return filter_apps(read_metadata_cache().get("apps", merge_apps()), category)
