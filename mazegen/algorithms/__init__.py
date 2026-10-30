"""Registry of the available carving algorithms."""
from __future__ import annotations

from mazegen.algorithms.backtracker import Backtracker
from mazegen.algorithms.base import Algorithm
from mazegen.algorithms.kruskal import Kruskal
from mazegen.errors import ConfigError

ALGORITHMS: dict[str, type[Algorithm]] = {
    Backtracker.name: Backtracker,
    Kruskal.name: Kruskal,
}


def available() -> list[str]:
    """Return the names accepted by the ``ALGORITHM`` config key."""
    return sorted(ALGORITHMS)


def get_algorithm(name: str) -> Algorithm:
    """Return a ready to use instance of the named algorithm.

    Args:
        name: Value of the ``ALGORITHM`` key, case insensitive.

    Returns:
        A new instance of the matching algorithm.

    Raises:
        ConfigError: If no algorithm goes by that name.
    """
    try:
        return ALGORITHMS[name.strip().lower()]()
    except KeyError as error:
        raise ConfigError(
            f"unknown algorithm {name!r}, pick one of "
            f"{', '.join(available())}"
        ) from error


__all__ = ["ALGORITHMS", "Algorithm", "available", "get_algorithm"]
