"""Parse loose text lists of Minecraft items into (item_text, quantity) pairs."""

from __future__ import annotations

import re

# Matches leading list markers: "- ", "* ", "• ", "1. ", "1) ", etc.
_PREFIX_RE = re.compile(r"^\s*(?:[-*•]|\d+[.):])\s*")

# Quantity patterns — tried in order:
#   "64 oak planks"          leading number
#   "oak planks x64"         trailing xN
#   "oak planks: 64"         colon-separated
#   "oak planks (64)"        parenthesised
_LEADING_QTY  = re.compile(r"^(\d+)\s+(.+)$", re.IGNORECASE)
_TRAILING_X   = re.compile(r"^(.+?)\s*[xX](\d+)$")
_COLON_QTY    = re.compile(r"^(.+?):\s*(\d+)$")
_PAREN_QTY    = re.compile(r"^(.+?)\s*\((\d+)\)$")

# "2 stacks" / "1 stack" — matched after stripping list prefix
_STACK_RE     = re.compile(r"(\d+)\s+stacks?", re.IGNORECASE)


def _parse_line(line: str) -> tuple[str, int] | None:
    line = _PREFIX_RE.sub("", line).strip()
    if not line:
        return None

    # Handle "X stacks" notation anywhere in the line
    stack_match = _STACK_RE.search(line)
    if stack_match:
        qty = int(stack_match.group(1)) * 64
        item_text = _STACK_RE.sub("", line).strip().strip("of").strip()
        return item_text, qty

    for pattern in (_LEADING_QTY, _TRAILING_X, _COLON_QTY, _PAREN_QTY):
        m = pattern.match(line)
        if m:
            if pattern is _LEADING_QTY:
                qty_str, item_text = m.group(1), m.group(2)
            else:
                item_text, qty_str = m.group(1), m.group(2)
            return item_text.strip(), int(qty_str)

    return line, 1


def parse_resource_list(text: str) -> list[tuple[str, int]]:
    """Parse multi-line text into a list of (item_text, quantity) pairs."""
    results = []
    for raw_line in text.splitlines():
        parsed = _parse_line(raw_line)
        if parsed is not None:
            results.append(parsed)
    return results
