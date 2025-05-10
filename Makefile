fmt:
	black mcp_simple_tool tests

lint:
	ruff check mcp_simple_tool
	mypy mcp_simple_tool

test:
	pytest -q 