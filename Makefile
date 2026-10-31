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

# Date written on every file of the wheel (2026-09-23, start of the
# project).  With a fixed date, the same sources always give the same
# bytes, so git shows the wheel as modified only when the code changed.
EPOCH  := 1790121600
# Scratch folder, outside the repository, for package-test.
TRY    ?= /tmp/mazegen-package-test

.DEFAULT_GOAL := run

.PHONY: install run debug clean fclean lint lint-strict test \
	package package-test

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

# Build the wheel straight into the repository root.  build/ goes
# first: setuptools reuses it, and a module deleted since the last
# build would end up in the new wheel.  The old wheel goes too, so a
# version bump never leaves two of them.
package: $(STAMP)
	rm -rf build *.egg-info mazegen-*.whl
	SOURCE_DATE_EPOCH=$(EPOCH) $(BIN)/python -m build --wheel --outdir .
	rm -rf build *.egg-info

# What the evaluation sheet asks: install the wheel in another
# virtualenv and run a_maze_ing.py with it.  It has to happen outside
# the repository, where no local mazegen/ folder can hide the
# installed one (ADR-008); app/ is copied because it is not part of
# the reusable package.
package-test: package
	rm -rf $(TRY)
	mkdir -p $(TRY)
	$(PYTHON) -m venv $(TRY)/venv
	$(TRY)/venv/bin/python -m pip install --quiet mazegen-*.whl
	cp -r a_maze_ing.py app $(CONFIG) $(TRY)/
	cd $(TRY) && venv/bin/python -c \
		"import mazegen, sys; print(mazegen.__file__); \
		sys.exit('site-packages' not in mazegen.__file__)"
	cd $(TRY) && venv/bin/python a_maze_ing.py $(notdir $(CONFIG)) \
		< /dev/null > /dev/null
	@echo "package-test OK: mazegen installed outside the repository"
