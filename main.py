#!/usr/bin/env python3
"""
Minecraft Resource Fetcher — CLI entry point.

Usage:
    python main.py [file]
    echo "64 oak planks" | python main.py
"""

import sys

from src.data import get_items, get_recipes
from src.items import get_items_by_id
from src.parser import parse_resource_list
from src.recipes import build_recipe_index, calculate_materials


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    resource_list = parse_resource_list(text)
    if not resource_list:
        print("No items found in input.")
        return

    # Load data (fetches from network on first run, then uses cache)
    get_items()
    get_recipes()
    items_by_id = get_items_by_id()
    recipes_raw = get_recipes()
    index = build_recipe_index(recipes_raw, items_by_id)

    materials, resolved, unresolved = calculate_materials(resource_list, index, items_by_id)

    # --- Matched items ---
    print("\nResolved items:")
    for query, display_name, confidence in resolved:
        if confidence < 100:
            print(f"  '{query}' -> {display_name}  ({confidence:.0f}% match)")
        else:
            print(f"  '{query}' -> {display_name}")

    if unresolved:
        print("\nWarning — could not resolve:")
        for query in unresolved:
            print(f"  '{query}'")

    # --- Materials list ---
    print("\nMaterials needed:")
    if materials:
        qty_width = len(str(max(materials.values())))
        for name, qty in materials.items():
            print(f"  {qty:>{qty_width}}x  {name}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()
