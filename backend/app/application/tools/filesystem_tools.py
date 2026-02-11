"""
File System Tools

Provides safe file system operations within the workspace directory.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any


class FileSystemTools:
    """
    File system utilities for workspace management.

    All operations are constrained to the backend/projects/ directory
    to prevent unauthorized file access.
    """

    def __init__(self, base_path: str = "backend/projects"):
        """
        Initialize file system tools.

        Args:
            base_path: Base directory for all workspace operations
        """
        self.base_path = Path(base_path).resolve()

    def _validate_path(self, path: str) -> Path:
        """
        Validate that a path is within the allowed base directory.

        Args:
            path: Path to validate

        Returns:
            Resolved absolute Path

        Raises:
            ValueError: If path attempts to escape base directory
        """
        resolved = (self.base_path / path).resolve()

        # Check if the resolved path is within base_path
        try:
            resolved.relative_to(self.base_path)
        except ValueError:
            raise ValueError(
                f"Path security violation: {path} is outside allowed workspace"
            )

        return resolved

    def create_workspace(self, workflow_id: str) -> str:
        """
        Create a new workspace directory for a workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            Absolute path to the workspace root
        """
        workspace_path = self.base_path / workflow_id

        # Create directory structure
        (workspace_path / "input").mkdir(parents=True, exist_ok=True)
        (workspace_path / "workspace").mkdir(parents=True, exist_ok=True)
        (workspace_path / "artifacts" / "copy").mkdir(parents=True, exist_ok=True)
        (workspace_path / "artifacts" / "images").mkdir(parents=True, exist_ok=True)
        (workspace_path / "artifacts" / "video").mkdir(parents=True, exist_ok=True)
        (workspace_path / "logs").mkdir(parents=True, exist_ok=True)

        return str(workspace_path)

    def ensure_dir(self, path: str) -> None:
        """
        Ensure a directory exists, creating if necessary.

        Args:
            path: Directory path (relative to workspace)

        Raises:
            ValueError: If path is outside workspace
        """
        resolved = self._validate_path(path)
        resolved.mkdir(parents=True, exist_ok=True)

    def read_file(self, path: str) -> str:
        """
        Read a text file.

        Args:
            path: File path (relative to workspace)

        Returns:
            File contents as string

        Raises:
            ValueError: If path is outside workspace
            FileNotFoundError: If file doesn't exist
        """
        resolved = self._validate_path(path)

        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return resolved.read_text(encoding="utf-8")

    def write_file(self, path: str, content: str) -> None:
        """
        Write content to a text file.

        Args:
            path: File path (relative to workspace)
            content: Text content to write

        Raises:
            ValueError: If path is outside workspace
        """
        resolved = self._validate_path(path)
        self.ensure_dir(str(resolved.parent))
        resolved.write_text(content, encoding="utf-8")

    def write_json(self, path: str, payload: Dict[str, Any]) -> None:
        """
        Write data as JSON file.

        Args:
            path: File path (relative to workspace)
            payload: Data to serialize as JSON

        Raises:
            ValueError: If path is outside workspace
        """
        resolved = self._validate_path(path)
        self.ensure_dir(str(resolved.parent))

        with resolved.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def read_json(self, path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON file.

        Args:
            path: File path (relative to workspace)

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If path is outside workspace or invalid JSON
        """
        resolved = self._validate_path(path)

        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")

        return json.loads(resolved.read_text(encoding="utf-8"))

    def list_dir(self, path: str, recursive: bool = False) -> List[str]:
        """
        List files in a directory.

        Args:
            path: Directory path (relative to workspace)
            recursive: If True, list files recursively

        Returns:
            List of file paths (relative to workspace)

        Raises:
            ValueError: If path is outside workspace
        """
        resolved = self._validate_path(path)

        if not resolved.exists() or not resolved.is_dir():
            return []

        if recursive:
            files = []
            for item in resolved.rglob("*"):
                if item.is_file():
                    # Return path relative to workspace
                    rel_path = item.relative_to(self.base_path)
                    files.append(str(rel_path))
            return files
        else:
            return [
                str(item.relative_to(self.base_path))
                for item in resolved.iterdir()
                if item.is_file()
            ]

    def exists(self, path: str) -> bool:
        """
        Check if a path exists.

        Args:
            path: File or directory path (relative to workspace)

        Returns:
            True if path exists, False otherwise
        """
        try:
            resolved = self._validate_path(path)
            return resolved.exists()
        except ValueError:
            return False

    def get_workspace_path(self, workflow_id: str, *parts: str) -> str:
        """
        Get absolute path for a workflow workspace.

        Args:
            workflow_id: Workflow identifier
            *parts: Additional path components

        Returns:
            Absolute path string
        """
        path = self.base_path / workflow_id
        for part in parts:
            path = path / part
        return str(path)
