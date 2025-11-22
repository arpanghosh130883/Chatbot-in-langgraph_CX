# main.py
# Simple arithmetic microservice using FastMCP
# to run the code: uv run fastmcp dev mathmcpserver.py


from __future__ import annotations
from fastmcp import FastMCP

# Initialize MCP app with a name
mcp = FastMCP("arith")


def _as_number(x):
    """Accept ints/floats or numeric strings; raise clean errors otherwise."""
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        try:
            return float(x.strip())
        except ValueError:
            raise TypeError(f"Expected a numeric string, got {x!r}")
    raise TypeError("Expected a number (int/float or numeric string)")


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b."""
    return _as_number(a) + _as_number(b)


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b."""
    return _as_number(a) - _as_number(b)


@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Return a * b."""
    return _as_number(a) * _as_number(b)


@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b, raising clean errors for zero division."""
    a_val, b_val = _as_number(a), _as_number(b)
    if b_val == 0:
        raise ZeroDivisionError("Division by zero is not allowed")
    return a_val / b_val


# Entry point
if __name__ == "__main__":
    mcp.run()
