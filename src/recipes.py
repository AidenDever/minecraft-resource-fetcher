"""Recursive recipe resolution to base (raw) materials."""

from __future__ import annotations

from collections import Counter
from math import ceil

from .data import get_recipes
from .items import get_items_by_id, resolve_item_name


def build_recipe_index(
    recipes_raw: dict,
    items_by_id: dict[int, dict],
) -> dict[int, list[dict]]:
    """
    Normalize shaped and shapeless crafting recipes into a common structure.

    Each entry: {result_id, result_count, ingredients: list[int]}
    Only crafting recipes (inShape / ingredients) are included.
    """
    index: dict[int, list[dict]] = {}

    for result_id_str, recipe_list in recipes_raw.items():
        result_id = int(result_id_str)
        if result_id not in items_by_id:
            continue

        for recipe in recipe_list:
            ingredients: list[int] = []

            if "inShape" in recipe:
                # Shaped recipe — 2-D grid; None slots are empty
                for row in recipe["inShape"]:
                    for cell in row:
                        if cell is not None:
                            ingredients.append(int(cell))

            elif "ingredients" in recipe:
                # Shapeless recipe
                for ing in recipe["ingredients"]:
                    ingredients.append(int(ing))

            else:
                # Not a crafting recipe (e.g. smelting) — skip
                continue

            result_count = recipe.get("result", {}).get("count", 1)

            normalized = {
                "result_id": result_id,
                "result_count": result_count,
                "ingredients": ingredients,
            }
            index.setdefault(result_id, []).append(normalized)

    return index


def resolve_to_materials(
    item_id: int,
    quantity: int,
    index: dict[int, list[dict]],
    items_by_id: dict[int, dict],
    visited: set[int] | None = None,
) -> dict[str, int]:
    """
    Recursively expand item_id/quantity into base materials.

    Returns {display_name: total_quantity}.
    """
    if visited is None:
        visited = set()

    display_name = items_by_id.get(item_id, {}).get("displayName", str(item_id))

    if item_id not in index or item_id in visited:
        return {display_name: quantity}

    # Use the first available crafting recipe
    recipe = index[item_id][0]
    result_count = recipe["result_count"] or 1
    batches = ceil(quantity / result_count)

    visited = visited | {item_id}  # immutable copy per branch

    # Aggregate duplicate ingredients before recursing to avoid overcounting
    # (e.g. 6 oak_plank slots should recurse as one call with qty 6*batches)
    ingredient_counts = Counter(recipe["ingredients"])
    totals: dict[str, int] = {}
    for ing_id, count in ingredient_counts.items():
        sub = resolve_to_materials(ing_id, batches * count, index, items_by_id, visited)
        for name, qty in sub.items():
            totals[name] = totals.get(name, 0) + qty

    return totals


def calculate_materials(
    resource_list: list[tuple[str, int]],
    index: dict[int, list[dict]],
    items_by_id: dict[int, dict],
) -> tuple[dict[str, int], list[tuple[str, str, float]], list[str]]:
    """
    Resolve a parsed resource list to base materials.

    Returns:
        materials   — {display_name: total_quantity} sorted alphabetically
        resolved    — [(original_query, display_name, confidence_pct)]
        unresolved  — [original_query]
    """
    totals: dict[str, int] = {}
    resolved: list[tuple[str, str, float]] = []
    unresolved: list[str] = []

    for query, qty in resource_list:
        item, confidence = resolve_item_name(query)
        if item is None:
            unresolved.append(query)
            continue

        resolved.append((query, item["displayName"], confidence))
        sub = resolve_to_materials(item["id"], qty, index, items_by_id)
        for name, amount in sub.items():
            totals[name] = totals.get(name, 0) + amount

    sorted_totals = dict(sorted(totals.items()))
    return sorted_totals, resolved, unresolved
