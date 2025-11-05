
# Directory Paths
UNIT_TEST_DIR=./test
SRC_DIR=./taew

# Makefile for Taew Core
all: sync static coverage

sync:
	@echo "Synchronizing dependencies..."
	@uv sync
	
coverage: erase-coverage test-unit combine-coverage report-coverage

test-unit:
	@echo "Running all tests in $(UNIT_TEST_DIR)..."
	@coverage run -m unittest discover -s $(UNIT_TEST_DIR) -t $(UNIT_TEST_DIR) -p "test_*.py"

erase-coverage:
	@rm -f .coverage*

combine-coverage:
	@coverage combine

report-coverage:
	@coverage report

static: ruff-check ruff-format mypy pyright

ruff-check:
	@echo "Running ruff linter ..."
	@uvx ruff check --exclude ./typings

ruff-format:
	@echo "Running ruff formatter ..."
	@uvx ruff format

# TBC: if mypy is run with uvx, it does not see installed stubs
mypy:
	@echo "Running MyPy..."
	@mypy ./
	@echo "MyPy check passed"

pyright:
	@echo "Running pyright..."
	@pyright ./
	@echo "Pyright check passed"


.PHONY: all sync coverage erase-coverage test-unit combine-coverage report-coverage static ruff-check ruff-format mypy pyright