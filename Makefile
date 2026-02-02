.PHONY: install install-dev install-tool test run clean format format-check

install:
	uv sync

install-tool:
	uv tool install -e .

install-dev:
	uv sync --extra dev

test:
	uv run pytest

run:
	uv run python main.py $(PUZZLE)

clean:
	rm -rf __pycache__ .pytest_cache *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

format:
	uv run black .

format-check:
	uv run black --check .
