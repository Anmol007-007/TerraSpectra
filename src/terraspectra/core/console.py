"""Rich console provider for interactive CLI and developer logs."""

from __future__ import annotations

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

console: Console = Console(theme=custom_theme)
error_console: Console = Console(theme=custom_theme, stderr=True)


def get_console() -> Console:
    """Return the global rich console instance."""
    return console


def print_status(message: str, style: str = "info") -> None:
    """Print styled status message using the rich console."""
    console.print(f"[{style}]{message}[/{style}]")
