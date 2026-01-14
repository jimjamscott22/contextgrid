"""
API client for ContextGrid CLI.
Handles HTTP requests to the API server.
"""

import requests
from typing import Optional, List, Dict, Any

from config import config


class APIError(Exception):
    """Exception raised for API errors."""
    pass


class APIClient:
    """Client for making requests to the ContextGrid API."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for API endpoint (default: from config)
        """
        self.base_url = base_url or config.API_URL
        self.base_url = self.base_url.rstrip('/')
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests library
        
        Returns:
            Response data (JSON)
        
        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise APIError(
                f"Cannot connect to API server at {self.base_url}. "
                "Make sure the API server is running."
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None  # Not found
            try:
                error_detail = e.response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise APIError(f"API error: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    # =========================
    # Project Operations
    # =========================
    
    def create_project(self, **kwargs) -> int:
        """Create a new project and return its ID."""
        data = self._request('POST', '/api/projects', json=kwargs)
        return data['id']
    
    def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single project by ID."""
        return self._request('GET', f'/api/projects/{project_id}')
    
    def list_projects(
        self,
        status: Optional[str] = None,
        tag: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: str = "last_worked_at",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """List projects with optional filtering and pagination."""
        params = {
            'sort_by': sort_by,
            'sort_order': sort_order
        }
        
        if status:
            params['status'] = status
        if tag:
            params['tag'] = tag
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        data = self._request('GET', '/api/projects', params=params)
        return data['projects']
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """Update project fields."""
        # Filter out None values
        updates = {k: v for k, v in kwargs.items() if v is not None}
        
        if not updates:
            return False
        
        self._request('PUT', f'/api/projects/{project_id}', json=updates)
        return True
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project."""
        result = self._request('DELETE', f'/api/projects/{project_id}')
        return result is not None
    
    def update_last_worked(self, project_id: int) -> bool:
        """Update the last_worked_at timestamp for a project."""
        result = self._request('POST', f'/api/projects/{project_id}/touch')
        return result is not None
    
    # =========================
    # Tag Operations
    # =========================
    
    def add_tag_to_project(self, project_id: int, tag_name: str) -> bool:
        """Add a tag to a project."""
        result = self._request(
            'POST',
            f'/api/projects/{project_id}/tags',
            json={'name': tag_name}
        )
        return result is not None
    
    def remove_tag_from_project(self, project_id: int, tag_name: str) -> bool:
        """Remove a tag from a project."""
        result = self._request(
            'DELETE',
            f'/api/projects/{project_id}/tags/{tag_name}'
        )
        return result is not None
    
    def list_project_tags(self, project_id: int) -> List[str]:
        """Get all tags for a specific project."""
        data = self._request('GET', f'/api/projects/{project_id}/tags')
        return [tag['name'] for tag in data]
    
    def list_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags with project counts."""
        data = self._request('GET', '/api/tags')
        return data['tags']
    
    # =========================
    # Note Operations
    # =========================
    
    def create_note(self, project_id: int, content: str, note_type: str = "log") -> int:
        """Create a new note for a project."""
        data = self._request(
            'POST',
            f'/api/projects/{project_id}/notes',
            json={'content': content, 'note_type': note_type}
        )
        return data['id']
    
    def list_notes(self, project_id: int, note_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all notes for a project."""
        data = self._request('GET', f'/api/projects/{project_id}/notes')
        notes = data['notes']
        
        # Filter by note_type if specified
        if note_type:
            notes = [n for n in notes if n['note_type'] == note_type]
        
        return notes
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single note by ID."""
        return self._request('GET', f'/api/notes/{note_id}')
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        result = self._request('DELETE', f'/api/notes/{note_id}')
        return result is not None
    
    def get_recent_notes(self, project_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the N most recent notes for a project."""
        notes = self.list_notes(project_id)
        return notes[:limit]


# Global API client instance
_api_client = None


def get_api_client() -> APIClient:
    """Get or create the global API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
