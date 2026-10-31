"""The documentation shipped in the wheel must work (B6).

Every ``python`` block of ``mazegen/README.md`` is run, in order and in
a shared namespace, against the package of the repository.  A renamed
method or a wrong import breaks this test instead of a later project.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

DOC: Path = Path(__file__).resolve().parent.parent / "mazegen" / "README.md"
BLOCK = re.compile(r"^```python\n(.*?)^```$", re.MULTILINE | re.DOTALL)


def python_blocks() -> list[str]:
    """Return the source of every ``python`` block of the document."""
    return BLOCK.findall(DOC.read_text(encoding="utf-8"))


def test_the_document_has_examples() -> None:
    # Without this, a broken regular expression would make the next
    # test pass on zero blocks.
    assert len(python_blocks()) >= 4


def test_every_example_runs(capsys: pytest.CaptureFixture[str]) -> None:
    namespace: dict[str, object] = {}
    for number, source in enumerate(python_blocks(), start=1):
        exec(compile(source, f"{DOC.name}, block {number}", "exec"),
             namespace)
    out = capsys.readouterr().out
    assert "falls on the" in out
