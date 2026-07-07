from __future__ import annotations

import json
import ssl
import time
import uuid
from typing import Any
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import OAIConfig, load_config

UNKNOWN_ERROR = "\u672a\u77e5\u9519\u8bef"


class OAIAPIError(RuntimeError):
    pass


def _make_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    ignore_unexpected_eof = getattr(ssl, "OP_IGNORE_UNEXPECTED_EOF", 0)
    if ignore_unexpected_eof:
        context.options |= ignore_unexpected_eof
    return context


def _is_retryable_network_error(exc: Exception) -> bool:
    if isinstance(exc, HTTPError):
        return 500 <= getattr(exc, "code", 0) < 600
    if isinstance(exc, (ssl.SSLError, TimeoutError, ConnectionError)):
        return True
    if isinstance(exc, URLError):
        return True
    return isinstance(exc, OSError)

def _format_http_error(exc: HTTPError) -> str:
    status = f"HTTP {exc.code}: {exc.reason}"
    try:
        raw = exc.read().decode("utf-8", errors="replace")
    except Exception:
        raw = ""
    detail = raw[:500]
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            data = None
        if isinstance(data, dict):
            detail = _format_api_error(data)
    return f"{status}，{detail}" if detail else status




def _log_task_payload(payload: dict[str, Any]) -> None:
    print(f"[OAI Bridge] /v1/task/submit payload: {json.dumps(payload, ensure_ascii=False)}")


def _format_api_error(data: dict[str, Any]) -> str:
    message = str(data.get("message") or data.get("error") or UNKNOWN_ERROR)
    err = data.get("err")
    if err not in (None, "", {}):
        return f"{message}锛宔rr={json.dumps(err, ensure_ascii=False)}"
    return message

def _format_request_payload(json_data: dict[str, Any] | None) -> str:
    if not json_data:
        return ""
    return json.dumps(json_data, ensure_ascii=False)[:1000]
class OAIClient:
    def __init__(self, config: OAIConfig | None = None):
        self.config = config or load_config()

    def _url(self, path: str) -> str:
        return urljoin(self.config.base_url.rstrip("/") + "/", path.lstrip("/"))

    def _headers(self, request_id: str | None = None) -> dict[str, str]:
        if not self.config.token:
            raise OAIAPIError("请先在 OAI Bridge 面板中配置 API Token。")
        headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
        }
        if request_id:
            headers["X-OAI-Bridge-Request-Id"] = request_id
        return headers
    def _urlopen_with_retries(self, request: Request, timeout: int, *, attempts: int = 3):
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                return self._urlopen_once(request, timeout)
            except Exception as exc:
                last_error = exc
                if attempt >= attempts - 1 or not _is_retryable_network_error(exc):
                    raise
                time.sleep(0.5 * (attempt + 1))
        raise last_error or OAIAPIError("请求后端失败。")
    def _urlopen_once(self, request: Request, timeout: int):
        kwargs: dict[str, Any] = {"timeout": timeout}
        if request.full_url.lower().startswith("https://"):
            kwargs["context"] = _make_ssl_context()
        try:
            return urlopen(request, **kwargs)
        except TypeError:
            kwargs.pop("context", None)
            return urlopen(request, **kwargs)

    async def request_json(
        self,
        method: str,
        path: str,
        json_data: dict[str, Any] | None = None,
        *,
        retry: bool = True,
        request_id: str | None = None,
        include_request_id_in_body: bool = False,
    ) -> dict[str, Any]:
        payload_data = dict(json_data or {})
        if include_request_id_in_body and request_id:
            payload_data.setdefault("client_request_id", request_id)
        body = json.dumps(payload_data, ensure_ascii=False).encode("utf-8") if method != "GET" else None
        request = Request(self._url(path), data=body, headers=self._headers(request_id), method=method)
        try:
            with self._urlopen_with_retries(request, timeout=120, attempts=3 if retry else 1) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            payload = _format_request_payload(payload_data)
            detail = _format_http_error(exc)
            if request_id:
                detail = f"{detail}；请求ID={request_id}"
            if payload:
                detail = f"{detail}；payload={payload}"
            raise OAIAPIError(f"请求后端失败：{detail}") from exc
        except Exception as exc:
            raise OAIAPIError(f"请求后端失败：{exc}") from exc
        try:
            data = json.loads(raw)
        except Exception as exc:
            raise OAIAPIError(f"后端返回了非 JSON 响应：{raw[:200]}") from exc
        if data.get("code") not in (None, 200):
            detail = _format_api_error(data)
            if request_id:
                detail = f"{detail}；请求ID={request_id}"
            raise OAIAPIError(f"请求失败：{detail}")
        return data
    async def get_model_list(self) -> dict[str, Any]:
        return await self.request_json("GET", "/v1/model/list")

    async def submit_task(self, app_id: str, parameter: dict[str, Any]) -> dict[str, Any]:
        payload = {"appId": app_id, "parameter": parameter}
        _log_task_payload(payload)
        return await self.request_json("POST", "/v1/task/submit", payload)

    async def query_task(self, task_id: str) -> dict[str, Any]:
        return await self.request_json("GET", f"/v1/task/query/{task_id}")

    def _new_request_id(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex}"

    async def banana_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = self._new_request_id("banana")
        return await self.request_json("POST", "/v1/banbana/generate", payload, retry=False, request_id=request_id, include_request_id_in_body=True)

    async def gpt_image_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = self._new_request_id("gpt-image")
        return await self.request_json("POST", "/v1/gpt/image/generate", payload, retry=False, request_id=request_id, include_request_id_in_body=True)

    async def image_generations(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = self._new_request_id("image-generations")
        return await self.request_json("POST", "/v1/images/generations", payload, retry=False, request_id=request_id, include_request_id_in_body=True)

    async def dialogue_execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/dialogue/execute", payload)

    async def workflow_app_cost(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/workflow/app/cost", payload, retry=False)

    async def gpt_image_cost(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/gpt/image/cost", payload, retry=False)

    async def model_cost(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/model/cost", payload, retry=False)

    async def seedance_cost(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/seedance/cost", payload, retry=False)

    async def seedance_create(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = self._new_request_id("seedance")
        return await self.request_json("POST", "/v1/seedance/create", payload, retry=False, request_id=request_id, include_request_id_in_body=True)

    async def seedance_upload_asset(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/seedance/upload-asset", payload)

    async def seedance_query(self, task_id: str) -> dict[str, Any]:
        return await self.request_json("POST", "/v1/seedance/query", {"task_id": task_id})

    async def upload_file(self, filename: str, content: bytes, content_type: str) -> str:
        boundary = f"----OAIBridge{uuid.uuid4().hex}"
        body = b"".join(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                content,
                b"\r\n",
                f"--{boundary}--\r\n".encode("utf-8"),
            ]
        )
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        if self.config.token:
            headers["Authorization"] = f"Bearer {self.config.token}"
        request = Request(self.config.upload_url, data=body, headers=headers, method="POST")
        try:
            with self._urlopen_with_retries(request, timeout=300, attempts=3) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise OAIAPIError(f"\u4e0a\u4f20\u6587\u4ef6\u5931\u8d25\uff1a{_format_http_error(exc)}") from exc
        except Exception as exc:
            raise OAIAPIError(f"\u4e0a\u4f20\u6587\u4ef6\u5931\u8d25\uff1a{exc}") from exc
        try:
            data = json.loads(raw)
        except Exception as exc:
            raise OAIAPIError(f"\u4e0a\u4f20\u63a5\u53e3\u8fd4\u56de\u4e86\u975e JSON \u54cd\u5e94\uff1a{raw[:200]}") from exc
        if data.get("code") not in (None, 200):
            message = data.get("message") or UNKNOWN_ERROR
            raise OAIAPIError(f"\u4e0a\u4f20\u5931\u8d25\uff1a{message}")
        url = data.get("data")
        if not url:
            raise OAIAPIError("\u4e0a\u4f20\u6210\u529f\uff0c\u4f46\u6ca1\u6709\u8fd4\u56de\u6587\u4ef6 URL\u3002")
        return url
