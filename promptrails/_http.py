from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from .config import Config
from .exceptions import RateLimitError, ServerError, raise_for_status


class HTTPClient:
    """Synchronous HTTP wrapper around httpx."""

    def __init__(self, config: Config):
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            headers=config.headers,
            timeout=config.timeout,
        )

    def close(self):
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        for attempt in range(self._config.max_retries + 1):
            try:
                response = self._client.request(method, path, json=json, params=params)
                body = response.json() if response.content else {}
                if response.status_code >= 500:
                    raise ServerError(
                        message=body.get("error", "Server error"),
                        status_code=response.status_code,
                    )
                raise_for_status(response.status_code, body)
                return body
            except (httpx.ConnectError, httpx.TimeoutException, ServerError):
                if attempt < self._config.max_retries:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise
            except RateLimitError:
                raise

    def get(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("POST", path, **kwargs)

    def patch(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("PATCH", path, **kwargs)

    def put(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> Dict[str, Any]:
        return self.request("DELETE", path, **kwargs)
