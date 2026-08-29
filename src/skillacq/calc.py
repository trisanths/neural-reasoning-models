"""A calculator reachable through the retrieval channel.

The model already knows one way to ask the outside world for something: emit
the retrieve token, write a query, read the result. Rather than teach it a
second protocol, this makes arithmetic answerable through the same channel.
A query that parses as an arithmetic expression comes back evaluated; anything
else falls through to the document retriever untouched.

This is the tools-as-accelerators idea in its smallest honest form. The weights
never have to approximate arithmetic; they only have to learn to ask.
"""

from __future__ import annotations

import ast
import operator
import re

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# A query is treated as arithmetic only when it is made of digits, spaces and
# the operators below. Anything with letters goes to the document retriever.
_ARITH = re.compile(r"^[\s0-9()+\-*/%^]+$")
_MAX_ABS = 10 ** 12


def looks_arithmetic(query: str) -> bool:
    q = query.strip()
    if not q or not _ARITH.match(q):
        return False
    return any(ch.isdigit() for ch in q) and any(ch in "+-*/%^" for ch in q)


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return node.value
        raise ValueError("only integers")
    if isinstance(node, ast.BinOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError("unsupported operator")
        left, right = _eval(node.left), _eval(node.right)
        if type(node.op) in (ast.FloorDiv, ast.Mod) and right == 0:
            raise ValueError("division by zero")
        if type(node.op) is ast.Pow and (abs(left) > 1000 or right > 8):
            raise ValueError("exponent too large")
        value = op(left, right)
        if abs(value) > _MAX_ABS:
            raise ValueError("result too large")
        return value
    if isinstance(node, ast.UnaryOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError("unsupported operator")
        return op(_eval(node.operand))
    raise ValueError("unsupported expression")


def evaluate(query: str) -> str | None:
    """Return the value of an arithmetic query, or None if it is not one."""
    if not looks_arithmetic(query):
        return None
    expr = query.strip().replace("^", "**").replace("/", "//")
    try:
        tree = ast.parse(expr, mode="eval")
        return str(_eval(tree))
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, RecursionError):
        return None
