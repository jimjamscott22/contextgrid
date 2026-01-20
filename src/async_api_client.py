"""
Async API client for ContextGrid.
Uses httpx.AsyncClient for non-blocking HTTP calls from the web UI.
"""

import os
from typing import Optional, List, Dict, Any

import httpx

# API endpoint configuration
API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000")


class APIError(Exception):
    """Exception raised for API errors."""
    pass


class AsyncAPIClient:
    """Async client for making requests to the ContextGrid API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or API_ENDPOINT).rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        url = endpoint
        try:
            response = await self._client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise APIError(
                f"Cannot connect to API server at {self.base_url}. "
                "Make sure the API server is running."
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            raise APIError(f"API error: {error_detail}")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")

    async def create_project(self, **kwargs) -> int:
        data = await self._request("POST", "/api/projects", json=kwargs)
        return data["id"]

    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        return await self._request("GET", f"/api/projects/{project_id}")

    async def list_projects(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        params = {"sort_by": sort_by, "sort_order": sort_order}
        if status:
            params["status"] = status
        if tag:
            params["tag"] = tag
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset

        data = await self._request("GET", "/api/projects", params=params)
        return data["projects"]

    async def update_project(self, project_id: int, **kwargs) -> bool:
        updates = {k: v for k, v in kwargs.items() if v is not None}
        if not updates:
            return False
        await self._request("PUT", f"/api/projects/{project_id}", json=updates)
        return True

    async def delete_project(self, project_id: int) -> bool:
        result = await self._request("DELETE", f"/api/projects/{project_id}")
        return result is not None

    async def update_last_worked(self, project_id: int) -> bool:
        result = await self._request("POST", f"/api/projects/{project_id}/touch")
        return result is not None

    async def add_tag_to_project(self, project_id: int, tag_name: str) -> bool:
        result = await self._request(
            "POST",
            f"/api/projects/{project_id}/tags",
            json={"name": tag_name},
        )
        return result is not None

    async def remove_tag_from_project(self, project_id: int, tag_name: str) -> bool:
        result = await self._request(
            "DELETE",
            f"/api/projects/{project_id}/tags/{tag_name}",
        )
        return result is not None

    async def list_project_tags(self, project_id: int) -> List[str]:
        data = await self._request("GET", f"/api/projects/{project_id}/tags")
        return [tag["name"] for tag in data]

    async def list_all_tags(self) -> List[Dict[str, Any]]:
        data = await self._request("GET", "/api/tags")
        return data["tags"]

    async def create_note(self, project_id: int, content: str, note_type: str = "log") -> int:
        data = await self._request(
            "POST",
            f"/api/projects/{project_id}/notes",
            json={"content": content, "note_type": note_type},
        )
        return data["id"]

    async def list_notes(self, project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
        data = await self._request("GET", f"/api/projects/{project_id}/notes")
        notes = data["notes"]
        if note_type:
            notes = [n for n in notes if n["note_type"] == note_type]
        return notes

    async def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        return await self._request("GET", f"/api/notes/{note_id}")

    async def delete_note(self, note_id: int) -> bool:
        result = await self._request("DELETE", f"/api/notes/{note_id}")
        return result is not None

    async def get_recent_notes(self, project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        notes = await self.list_notes(project_id)
        return notes[:limit]

    async def aclose(self) -> None:
        await self._client.aclose()


_async_client: Optional[AsyncAPIClient] = None


def get_async_api_client() -> AsyncAPIClient:
    global _async_client
    if _async_client is None:
        _async_client = AsyncAPIClient()
    return _async_client


async def aclose_async_api_client() -> None:
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None
