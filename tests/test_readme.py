"""The README items the evaluation sheet grades with a zero (B8).

A missing item fails the whole project, so each one is a test: the
exact first line, every mandatory section, and the documentation of
the package, which the subject wants in the main README too.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT: Path = Path(__file__).resolve().parent.parent
README: Path = ROOT / "README.md"
MODULE_DOC: Path = ROOT / "mazegen" / "README.md"

FIRST_LINE: str = (
    "*This project has been created as part of the 42 curriculum "
    "by emmmilla, lugarcia.*"
)

# The three names the subject imposes, then ours for the items it only
# describes, in the order of chapter VII.
SECTIONS: list[str] = [
    "## Description",
    "## Instructions",
    "## Resources",
    "### How AI was used",
    "## Configuration file",
    "## Maze generation algorithm",
    "### Why this algorithm",
    "### Advanced features",
    "## Reusable module",
    "### Roles",
    "### Planning and how it evolved",
    "### What worked well and what could be improved",
    "### Tools",
]


def readme_lines() -> list[str]:
    """Return the lines of the README."""
    return README.read_text(encoding="utf-8").splitlines()


def test_first_line_is_exact() -> None:
    assert readme_lines()[0] == FIRST_LINE


@pytest.mark.parametrize("heading", SECTIONS)
def test_section_is_present(heading: str) -> None:
    assert heading in readme_lines()


def test_sections_follow_the_subject_order() -> None:
    lines = readme_lines()
    positions = [lines.index(heading) for heading in SECTIONS]
    assert positions == sorted(positions)


def test_module_documentation_is_included() -> None:
    # The package documentation goes in one heading level deeper and
    # without its title: a later edit of one copy only must fail here.
    lines = MODULE_DOC.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "# mazegen"
    body = "\n".join(
        "#" + line if line.startswith("## ") else line
        for line in lines[1:]
    ).strip("\n")
    assert body in README.read_text(encoding="utf-8")
