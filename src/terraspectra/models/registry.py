"""Simple model registry for looking up model classes by name."""

from __future__ import annotations

from typing import Any


class ModelRegistry:
    """Registry mapping model names to their constructor callables.

    Example:
        >>> registry = ModelRegistry()
        >>> registry.register("my_model", MyModel)
        >>> model = registry.build("my_model", num_classes=3)
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._registry: dict[str, type[Any]] = {}

    def register(self, name: str, cls: type[Any]) -> None:
        """Register a model class under *name*.

        Args:
            name: Unique identifier string.
            cls: Model class (must be callable with keyword args).

        Raises:
            ValueError: If *name* is already registered.
        """
        if name in self._registry:
            raise ValueError(f"Model '{name}' is already registered.")
        self._registry[name] = cls

    def build(self, name: str, **kwargs: Any) -> Any:
        """Instantiate and return a registered model.

        Args:
            name: Registered model name.
            **kwargs: Forwarded to the model constructor.

        Returns:
            New model instance.

        Raises:
            KeyError: If *name* is not found in the registry.
        """
        if name not in self._registry:
            raise KeyError(f"Model '{name}' not found. Available: {list(self._registry)}")
        return self._registry[name](**kwargs)

    def list_models(self) -> list[str]:
        """Return sorted list of registered model names."""
        return sorted(self._registry)
