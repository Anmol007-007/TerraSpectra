"""Rich console provider for interactive CLI and developer logs with fallback."""

from __future__ import annotations

import re
from typing import Any

try:
    from rich.console import Console
    from rich.theme import Theme

    custom_theme = Theme(
        {
            "info": "dim cyan",
            "warning": "magenta",
            "danger": "bold red",
            "success": "bold green",
            "spectral": "bold yellow",
        }
    )

    console: Any = Console(theme=custom_theme)
    error_console: Any = Console(theme=custom_theme, stderr=True)
except ImportError:

    class _FallbackConsole:
        def print(self, *args: Any, **kwargs: Any) -> None:
            clean_args = []
            for a in args:
                if isinstance(a, str):
                    clean_args.append(re.sub(r"\[/?[a-zA-Z0-9_ =#]+\]", "", a))
                else:
                    clean_args.append(a)
            print(*clean_args)

    console = _FallbackConsole()
    error_console = _FallbackConsole()


def get_console() -> Any:
    """Return the global console instance."""
    return console


def print_status(message: str, style: str = "info") -> None:
    """Print styled status message using the console."""
    console.print(f"[{style}]{message}[/{style}]")
