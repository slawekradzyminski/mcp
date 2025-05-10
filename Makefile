.PHONY: fmt fmt-check lint test ci

fmt:
	python -m black mcp_simple_tool tests

fmt-check:
	python -m black --check mcp_simple_tool tests

lint:
	python -m ruff check mcp_simple_tool
	python -m mypy mcp_simple_tool

test:
	python -m pytest -q

# Run all checks (equivalent to CI pipeline)
ci: fmt-check lint test
	@echo "✅ All checks passed!"

# Alias for ci
check: ci 