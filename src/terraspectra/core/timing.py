"""Performance profiling helpers: Timer context manager and timing decorator."""

from __future__ import annotations

import functools
import logging
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])
logger = logging.getLogger(__name__)


class Timer:
    """Context manager measuring execution wall-clock time in seconds.

    Example:
        >>> with Timer("PCA reduction") as t:
        ...     do_pca()
        >>> print(f"Elapsed: {t.elapsed:.3f}s")
    """

    def __init__(self, name: str = "Operation", verbose: bool = False) -> None:
        """Initialise timer.

        Args:
            name: Description of the timed block.
            verbose: If True, log elapsed time on exit.
        """
        self.name = name
        self.verbose = verbose
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> Timer:
        """Start timer."""
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Stop timer and record elapsed seconds."""
        self.end_time = time.perf_counter()
        self.elapsed = self.end_time - self.start_time
        if self.verbose:
            logger.info("%s took %.4f seconds", self.name, self.elapsed)


def timeit(func: F) -> F:
    """Decorator logging execution time of a callable."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            logger.debug("%s executed in %.4f seconds", func.__name__, elapsed)

    return wrapper  # type: ignore[return-value]
