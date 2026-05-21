from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..types import AgentVFSFile, AgentVFSGrepMatch
from .base import AsyncBaseResource, BaseResource


def _build_list_params(
    path: Optional[str], recursive: Optional[bool], offset: Optional[int], limit: Optional[int]
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if path is not None:
        params["path"] = path
    if recursive:
        params["recursive"] = "true"
    if offset is not None:
        params["offset"] = offset
    if limit is not None:
        params["limit"] = limit
    return params


class AgentVFSResource(BaseResource):
    """Per-agent Virtual Filesystem: list, read, write, mkdir, move, copy, delete, grep, glob.

    Files persist across executions and double as long-term memory for the agent.
    """

    def list(
        self,
        agent_id: str,
        *,
        path: str = "/",
        recursive: bool = False,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSFile]:
        params = _build_list_params(path, recursive, offset, limit)
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs", params=params)
        items = self._unwrap(body).get("items", []) or []
        return [AgentVFSFile.from_dict(item) for item in items]

    def read(
        self,
        agent_id: str,
        path: str,
        *,
        line_offset: Optional[int] = None,
        line_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"path": path}
        if line_offset is not None:
            params["line_offset"] = line_offset
        if line_limit is not None:
            params["line_limit"] = line_limit
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs/file", params=params)
        return self._unwrap(body)

    def write(
        self,
        agent_id: str,
        path: str,
        content: str,
        *,
        mode: str = "overwrite",
        mime_type: Optional[str] = None,
    ) -> AgentVFSFile:
        payload: Dict[str, Any] = {"path": path, "content": content, "mode": mode}
        if mime_type:
            payload["mime_type"] = mime_type
        body = self._http.put(f"/api/v1/agents/{agent_id}/vfs/file", json=payload)
        return AgentVFSFile.from_dict(self._unwrap(body))

    def stat(self, agent_id: str, path: str) -> AgentVFSFile:
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs/stat", params={"path": path})
        return AgentVFSFile.from_dict(self._unwrap(body))

    def mkdir(self, agent_id: str, path: str) -> AgentVFSFile:
        body = self._http.post(f"/api/v1/agents/{agent_id}/vfs/mkdir", json={"path": path})
        return AgentVFSFile.from_dict(self._unwrap(body))

    def move(self, agent_id: str, src: str, dst: str) -> None:
        self._http.post(f"/api/v1/agents/{agent_id}/vfs/move", json={"from": src, "to": dst})

    def copy(self, agent_id: str, src: str, dst: str) -> None:
        self._http.post(f"/api/v1/agents/{agent_id}/vfs/copy", json={"from": src, "to": dst})

    def delete(self, agent_id: str, path: str, *, recursive: bool = False) -> int:
        params: Dict[str, Any] = {"path": path}
        if recursive:
            params["recursive"] = "true"
        body = self._http.delete(f"/api/v1/agents/{agent_id}/vfs", params=params)
        if body is None:
            return 0
        return int(self._unwrap(body).get("deleted", 0))

    def grep(
        self,
        agent_id: str,
        query: str,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSGrepMatch]:
        params: Dict[str, Any] = {"q": query}
        if path:
            params["path"] = path
        if limit is not None:
            params["limit"] = limit
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs/grep", params=params)
        matches = self._unwrap(body).get("matches", []) or []
        return [AgentVFSGrepMatch.from_dict(m) for m in matches]

    def glob(
        self,
        agent_id: str,
        pattern: str,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSFile]:
        params: Dict[str, Any] = {"pattern": pattern}
        if path:
            params["path"] = path
        if limit is not None:
            params["limit"] = limit
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs/glob", params=params)
        items = self._unwrap(body).get("items", []) or []
        return [AgentVFSFile.from_dict(item) for item in items]

    def usage(self, agent_id: str) -> int:
        body = self._http.get(f"/api/v1/agents/{agent_id}/vfs/usage")
        return int(self._unwrap(body).get("bytes_used", 0))


class AsyncAgentVFSResource(AsyncBaseResource):
    """Async variant of AgentVFSResource."""

    async def list(
        self,
        agent_id: str,
        *,
        path: str = "/",
        recursive: bool = False,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSFile]:
        params = _build_list_params(path, recursive, offset, limit)
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs", params=params)
        items = self._unwrap(body).get("items", []) or []
        return [AgentVFSFile.from_dict(item) for item in items]

    async def read(
        self,
        agent_id: str,
        path: str,
        *,
        line_offset: Optional[int] = None,
        line_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"path": path}
        if line_offset is not None:
            params["line_offset"] = line_offset
        if line_limit is not None:
            params["line_limit"] = line_limit
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs/file", params=params)
        return self._unwrap(body)

    async def write(
        self,
        agent_id: str,
        path: str,
        content: str,
        *,
        mode: str = "overwrite",
        mime_type: Optional[str] = None,
    ) -> AgentVFSFile:
        payload: Dict[str, Any] = {"path": path, "content": content, "mode": mode}
        if mime_type:
            payload["mime_type"] = mime_type
        body = await self._http.put(f"/api/v1/agents/{agent_id}/vfs/file", json=payload)
        return AgentVFSFile.from_dict(self._unwrap(body))

    async def stat(self, agent_id: str, path: str) -> AgentVFSFile:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs/stat", params={"path": path})
        return AgentVFSFile.from_dict(self._unwrap(body))

    async def mkdir(self, agent_id: str, path: str) -> AgentVFSFile:
        body = await self._http.post(f"/api/v1/agents/{agent_id}/vfs/mkdir", json={"path": path})
        return AgentVFSFile.from_dict(self._unwrap(body))

    async def move(self, agent_id: str, src: str, dst: str) -> None:
        await self._http.post(f"/api/v1/agents/{agent_id}/vfs/move", json={"from": src, "to": dst})

    async def copy(self, agent_id: str, src: str, dst: str) -> None:
        await self._http.post(f"/api/v1/agents/{agent_id}/vfs/copy", json={"from": src, "to": dst})

    async def delete(self, agent_id: str, path: str, *, recursive: bool = False) -> int:
        params: Dict[str, Any] = {"path": path}
        if recursive:
            params["recursive"] = "true"
        body = await self._http.delete(f"/api/v1/agents/{agent_id}/vfs", params=params)
        if body is None:
            return 0
        return int(self._unwrap(body).get("deleted", 0))

    async def grep(
        self,
        agent_id: str,
        query: str,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSGrepMatch]:
        params: Dict[str, Any] = {"q": query}
        if path:
            params["path"] = path
        if limit is not None:
            params["limit"] = limit
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs/grep", params=params)
        matches = self._unwrap(body).get("matches", []) or []
        return [AgentVFSGrepMatch.from_dict(m) for m in matches]

    async def glob(
        self,
        agent_id: str,
        pattern: str,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AgentVFSFile]:
        params: Dict[str, Any] = {"pattern": pattern}
        if path:
            params["path"] = path
        if limit is not None:
            params["limit"] = limit
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs/glob", params=params)
        items = self._unwrap(body).get("items", []) or []
        return [AgentVFSFile.from_dict(item) for item in items]

    async def usage(self, agent_id: str) -> int:
        body = await self._http.get(f"/api/v1/agents/{agent_id}/vfs/usage")
        return int(self._unwrap(body).get("bytes_used", 0))
