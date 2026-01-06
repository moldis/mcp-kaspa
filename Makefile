.PHONY: help build clean test run dev-deps

help:
	@echo "Available targets:"
	@echo "  build      - Install dependencies using uv"
	@echo "  clean      - Remove build artifacts and cache files"
	@echo "  test       - Run tests"
	@echo "  run        - Run the MCP server"
	@echo "  dev-deps   - Install development dependencies"

build:
	uv sync

dev-deps:
	uv sync --extra dev

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type f -name 'coverage.out' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name 'build' -exec rm -rf {} +
	find . -type d -name 'dist' -exec rm -rf {} +
	rm -rf .uv

test:
	uv run python tests/test_kaspa_client.py

run:
	uvx --from . kaspa-mcp-server
