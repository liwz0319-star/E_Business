"""
Tool Registry

Central registry for managing and injecting tools.
"""

from typing import Dict, Any, Optional
from .filesystem_tools import FileSystemTools
from .text_tools import TextTools
from .vision_tools import VisionTools
from .image_tools import ImageTools
from .video_tools import VideoTools
from .storage_tools import StorageTools


class ToolRegistry:
    """
    Central registry for all application tools.

    Provides dependency injection and lazy initialization of tools.
    """

    def __init__(self):
        """Initialize empty tool registry."""
        self._tools: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}

    def register_factory(self, name: str, factory: callable) -> None:
        """
        Register a tool factory for lazy initialization.

        Args:
            name: Tool name
            factory: Factory function that creates the tool
        """
        self._factories[name] = factory

    def register(self, name: str, tool: Any) -> None:
        """
        Register a tool instance directly.

        Args:
            name: Tool name
            tool: Tool instance
        """
        self._tools[name] = tool

    def get(self, name: str) -> Optional[Any]:
        """
        Get a tool by name, initializing if necessary.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        # Check if already initialized
        if name in self._tools:
            return self._tools[name]

        # Check if factory exists
        if name in self._factories:
            self._tools[name] = self._factories[name]()
            return self._tools[name]

        return None

    @property
    def filesystem(self) -> FileSystemTools:
        """Get filesystem tools."""
        tool = self.get("filesystem")
        if tool is None:
            raise RuntimeError("FileSystemTools not registered")
        return tool

    @property
    def text(self) -> TextTools:
        """Get text tools."""
        tool = self.get("text")
        if tool is None:
            raise RuntimeError("TextTools not registered")
        return tool

    @property
    def vision(self) -> VisionTools:
        """Get vision tools."""
        tool = self.get("vision")
        if tool is None:
            raise RuntimeError("VisionTools not registered")
        return tool

    @property
    def image(self) -> ImageTools:
        """Get image tools."""
        tool = self.get("image")
        if tool is None:
            raise RuntimeError("ImageTools not registered")
        return tool

    @property
    def video(self) -> VideoTools:
        """Get video tools."""
        tool = self.get("video")
        if tool is None:
            raise RuntimeError("VideoTools not registered")
        return tool

    @property
    def storage(self) -> StorageTools:
        """Get storage tools."""
        tool = self.get("storage")
        if tool is None:
            raise RuntimeError("StorageTools not registered")
        return tool

    @classmethod
    def create_default(cls, llm_client=None, video_asset_repository=None) -> "ToolRegistry":
        """
        Create a tool registry with default configuration.

        Args:
            llm_client: LLM client for text/vision operations
            video_asset_repository: Repository for video assets

        Returns:
            Configured ToolRegistry instance
        """
        registry = cls()

        # Register factories
        registry.register_factory("filesystem", lambda: FileSystemTools())
        registry.register_factory("text", lambda: TextTools(llm_client))
        registry.register_factory("vision", lambda: VisionTools(llm_client))
        registry.register_factory("image", lambda: ImageTools(
            provider_factory=None,  # TODO: inject
            asset_repository=video_asset_repository,
        ))
        registry.register_factory("video", lambda: VideoTools(
            video_provider=None,  # TODO: inject
            slideshow_provider=None,  # TODO: inject
            asset_repository=video_asset_repository,
        ))

        # Storage will be registered with repository
        # registry.register("storage", StorageTools(repository))

        return registry


# Global registry instance
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry.

    Returns:
        Global ToolRegistry instance

    Raises:
        RuntimeError: If registry not initialized
    """
    global _global_registry
    if _global_registry is None:
        raise RuntimeError("ToolRegistry not initialized. Call init_tool_registry() first.")
    return _global_registry


def init_tool_registry(registry: ToolRegistry) -> None:
    """
    Initialize the global tool registry.

    Args:
        registry: ToolRegistry instance to use as global
    """
    global _global_registry
    _global_registry = registry
