"""
Async database/query layer for ContextGrid projects.
Wraps the async API client so the web UI can remain fully async.
"""

from typing import Optional, List, Dict, Any

from async_api_client import get_async_api_client, APIError, aclose_async_api_client

_client = get_async_api_client()


def _handle_api_error(e: APIError):
    raise Exception(str(e))


async def create_project(
    name: str,
    status: str = "idea",
    description: Optional[str] = None,
    project_type: Optional[str] = None,
    primary_language: Optional[str] = None,
    stack: Optional[str] = None,
    repo_url: Optional[str] = None,
    local_path: Optional[str] = None,
    scope_size: Optional[str] = None,
    learning_goal: Optional[str] = None,
    progress: int = 0,
) -> int:
    try:
        return await _client.create_project(
            name=name,
            description=description,
            status=status,
            project_type=project_type,
            primary_language=primary_language,
            stack=stack,
            repo_url=repo_url,
            local_path=local_path,
            scope_size=scope_size,
            learning_goal=learning_goal,
            progress=progress,
        )
    except APIError as e:
        _handle_api_error(e)


async def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    try:
        return await _client.get_project(project_id)
    except APIError as e:
        _handle_api_error(e)


async def list_projects(
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc",
) -> List[Dict[str, Any]]:
    try:
        return await _client.list_projects(
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except APIError as e:
        _handle_api_error(e)


async def update_project(project_id: int, **kwargs) -> bool:
    try:
        return await _client.update_project(project_id, **kwargs)
    except APIError as e:
        _handle_api_error(e)


async def delete_project(project_id: int) -> bool:
    try:
        return await _client.delete_project(project_id)
    except APIError as e:
        _handle_api_error(e)


async def update_last_worked(project_id: int) -> bool:
    try:
        return await _client.update_last_worked(project_id)
    except APIError as e:
        _handle_api_error(e)


async def create_note(project_id: int, content: str, note_type: str = "log") -> int:
    valid_types = ["log", "idea", "blocker", "reflection"]
    if note_type not in valid_types:
        raise ValueError(
            f"Invalid note_type: {note_type}. Must be one of: {', '.join(valid_types)}"
        )
    try:
        return await _client.create_note(project_id, content, note_type)
    except APIError as e:
        _handle_api_error(e)


async def list_notes(project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        return await _client.list_notes(project_id, note_type)
    except APIError as e:
        _handle_api_error(e)


async def get_note(note_id: int) -> Optional[Dict[str, Any]]:
    try:
        return await _client.get_note(note_id)
    except APIError as e:
        _handle_api_error(e)


async def delete_note(note_id: int) -> bool:
    try:
        return await _client.delete_note(note_id)
    except APIError as e:
        _handle_api_error(e)


async def get_recent_notes(project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    try:
        notes = await _client.get_recent_notes(project_id, limit)
        return notes
    except APIError as e:
        _handle_api_error(e)


async def add_tag_to_project(project_id: int, tag_name: str) -> bool:
    try:
        return await _client.add_tag_to_project(project_id, tag_name)
    except APIError as e:
        _handle_api_error(e)


async def remove_tag_from_project(project_id: int, tag_name: str) -> bool:
    try:
        return await _client.remove_tag_from_project(project_id, tag_name)
    except APIError as e:
        _handle_api_error(e)


async def list_project_tags(project_id: int) -> List[str]:
    try:
        return await _client.list_project_tags(project_id)
    except APIError as e:
        _handle_api_error(e)


async def list_all_tags() -> List[Dict[str, Any]]:
    try:
        return await _client.list_all_tags()
    except APIError as e:
        _handle_api_error(e)


async def list_projects_by_tag(
    tag_name: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc",
) -> List[Dict[str, Any]]:
    try:
        return await _client.list_projects(
            status=status,
            tag=tag_name,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except APIError as e:
        _handle_api_error(e)


async def search_projects(
    query: str,
    status: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    sort_by: str = "last_worked_at",
    sort_order: str = "desc",
) -> List[Dict[str, Any]]:
    # TODO: Implement server-side search; currently fallback to list_projects
    try:
        return await _client.list_projects(
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except APIError as e:
        _handle_api_error(e)


async def get_projects_count(
    status: Optional[str] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    try:
        projects = await _client.list_projects(status=status, tag=tag)
        # search is ignored until API supports it explicitly
        return len(projects)
    except APIError as e:
        _handle_api_error(e)


async def aclose_client() -> None:
    await aclose_async_api_client()


# =========================
# Activity / Heatmap Operations
# =========================

async def get_activity_heatmap(days: int = 365) -> Dict[str, Any]:
    try:
        return await _client.get_activity_heatmap(days=days)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Relationship Operations
# =========================

async def create_relationship(
    project_id: int, target_project_id: int, relationship_type: str
) -> int:
    valid_types = ["related_to", "depends_on", "part_of"]
    if relationship_type not in valid_types:
        raise ValueError(
            f"Invalid relationship_type: {relationship_type}. Must be one of: {', '.join(valid_types)}"
        )
    try:
        return await _client.create_relationship(project_id, target_project_id, relationship_type)
    except APIError as e:
        _handle_api_error(e)


async def list_project_relationships(project_id: int) -> List[Dict[str, Any]]:
    try:
        return await _client.list_project_relationships(project_id)
    except APIError as e:
        _handle_api_error(e)


async def delete_relationship(relationship_id: int) -> bool:
    try:
        return await _client.delete_relationship(relationship_id)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Graph Operations
# =========================

async def get_full_graph(include_inferred: bool = True) -> Dict[str, Any]:
    try:
        return await _client.get_full_graph(include_inferred)
    except APIError as e:
        _handle_api_error(e)


async def get_project_graph(project_id: int, include_inferred: bool = True) -> Dict[str, Any]:
    try:
        return await _client.get_project_graph(project_id, include_inferred)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Project Link Operations
# =========================

async def list_project_links(project_id: int) -> List[Dict[str, Any]]:
    try:
        return await _client.list_project_links(project_id)
    except APIError as e:
        _handle_api_error(e)


async def create_project_link(
    project_id: int, title: str, url: str, link_type: str = "other"
) -> Dict[str, Any]:
    try:
        return await _client.create_project_link(project_id, title, url, link_type)
    except APIError as e:
        _handle_api_error(e)


async def delete_link(link_id: int) -> bool:
    try:
        return await _client.delete_link(link_id)
    except APIError as e:
        _handle_api_error(e)


# =========================
# Project Template Operations
# =========================

async def list_templates() -> List[Dict[str, Any]]:
    try:
        return await _client.list_templates()
    except APIError as e:
        _handle_api_error(e)


async def get_template(template_id: int) -> Optional[Dict[str, Any]]:
    try:
        return await _client.get_template(template_id)
    except APIError as e:
        _handle_api_error(e)


async def create_template(**kwargs) -> Dict[str, Any]:
    try:
        return await _client.create_template(**kwargs)
    except APIError as e:
        _handle_api_error(e)


async def update_template(template_id: int, **kwargs) -> Dict[str, Any]:
    try:
        return await _client.update_template(template_id, **kwargs)
    except APIError as e:
        _handle_api_error(e)


async def delete_template(template_id: int) -> bool:
    try:
        return await _client.delete_template(template_id)
    except APIError as e:
        _handle_api_error(e)

