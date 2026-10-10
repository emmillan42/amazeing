# A-Maze-ing - common development tasks.
#
# The program itself only uses the standard library, so `run` and
# `debug` work on a fresh clone with the system interpreter.  The
# virtual environment holds the development tools only (linters,
# packaging, tests).

PYTHON ?= python3
CONFIG ?= config.txt

VENV   := .venv
BIN    := $(VENV)/bin
# Marker file: its timestamp records when the tools were installed,
# so make reinstalls them only if requirements-dev.txt is newer.
STAMP  := $(VENV)/.installed

.DEFAULT_GOAL := run

.PHONY: install run debug clean fclean lint lint-strict test

install: $(STAMP)

$(STAMP): requirements-dev.txt
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -r requirements-dev.txt
	touch $(STAMP)

run:
	$(PYTHON) a_maze_ing.py $(CONFIG)

debug:
	$(PYTHON) -m pdb a_maze_ing.py $(CONFIG)

# Caches and build leftovers only.  The wheel at the repository root
# is a deliverable, so it is never matched here.
clean:
	find . -path ./$(VENV) -prune -o -type d -name __pycache__ \
		-prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.egg-info

fclean: clean
	rm -rf $(VENV)

lint: $(STAMP)
	$(BIN)/flake8 .
	$(BIN)/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict: $(STAMP)
	$(BIN)/flake8 .
	$(BIN)/mypy . --strict

# `python -m pytest`, not `pytest`: only the former puts the repository
# root on sys.path, which the tests need to import mazegen.
test: $(STAMP)
	$(BIN)/python -m pytest
