"""Item lookup with fuzzy name matching."""

from __future__ import annotations

from rapidfuzz import process, fuzz

from .data import get_items

_items_by_id: dict[int, dict] | None = None
_items_by_name: dict[str, dict] | None = None
_all_names: list[str] | None = None


def _load():
    global _items_by_id, _items_by_name, _all_names
    if _items_by_id is not None:
        return
    raw = get_items()
    _items_by_id = {}
    _items_by_name = {}
    for item in raw:
        _items_by_id[item["id"]] = item
        _items_by_name[item["name"]] = item
    _all_names = list(_items_by_name.keys())


def get_items_by_id() -> dict[int, dict]:
    _load()
    return _items_by_id


# Exact aliases: normalized query → canonical item name
_ALIASES: dict[str, str] = {
    "beds": "white_bed",
    "bed": "white_bed",
    "bookshelves": "bookshelf",
}

# Suffix substitutions applied before exact/fuzzy lookup (e.g. wood-type fence gates)
_SUFFIX_SUBS: list[tuple[str, str]] = [
    ("_fence_doors", "_fence_gate"),
    ("_fence_door", "_fence_gate"),
]


def resolve_item_name(query: str) -> tuple[dict | None, float]:
    """Return (item_dict, confidence_pct) or (None, 0) if no match found."""
    _load()
    normalized = query.strip().lower().replace(" ", "_")

    # Apply exact alias map first
    normalized = _ALIASES.get(normalized, normalized)

    # Apply suffix substitutions (e.g. spruce_fence_doors -> spruce_fence_gate)
    for old_suffix, new_suffix in _SUFFIX_SUBS:
        if normalized.endswith(old_suffix):
            normalized = normalized[: -len(old_suffix)] + new_suffix
            break

    if normalized in _items_by_name:
        return _items_by_name[normalized], 100.0

    result = process.extractOne(normalized, _all_names, scorer=fuzz.WRatio)
    if result is None:
        return None, 0.0

    match_name, score, _ = result
    if score < 60:
        return None, score

    return _items_by_name[match_name], score
