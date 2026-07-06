from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PLUGIN_ROOT / "oai_bridge_data"
CONFIG_PATH = DATA_DIR / "config.json"
HARDCODED_BASE_URL = "https://oaigc.cn/api"
HARDCODED_UPLOAD_URL = "https://oaigc.cn/api/file/tool/upload"


@dataclass
class OAIConfig:
    base_url: str = HARDCODED_BASE_URL
    upload_url: str = HARDCODED_UPLOAD_URL
    token: str = ""
    poll_interval: float = 3.0
    poll_timeout: float = 900.0

    def __post_init__(self) -> None:
        self.base_url = HARDCODED_BASE_URL
        self.upload_url = HARDCODED_UPLOAD_URL

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "has_token": bool(self.token),
            "token_masked": mask_token(self.token),
            "poll_interval": self.poll_interval,
            "poll_timeout": self.poll_timeout,
        }


def mask_token(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}****{token[-4:]}"


def load_config() -> OAIConfig:
    if not CONFIG_PATH.exists():
        return OAIConfig()
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8-sig"))
    except Exception:
        return OAIConfig()
    cfg = OAIConfig()
    for key in asdict(cfg):
        if key in {"base_url", "upload_url"}:
            continue
        if key in data:
            setattr(cfg, key, data[key])
    cfg.base_url = HARDCODED_BASE_URL
    cfg.upload_url = HARDCODED_UPLOAD_URL
    return cfg


def save_config(update: dict[str, Any]) -> OAIConfig:
    cfg = load_config()
    for key in asdict(cfg):
        if key in {"base_url", "upload_url"}:
            continue
        if key in update:
            setattr(cfg, key, update[key])
    cfg.base_url = HARDCODED_BASE_URL
    cfg.upload_url = HARDCODED_UPLOAD_URL
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
    return cfg

