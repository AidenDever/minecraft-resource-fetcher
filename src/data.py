"""Fetch and cache Minecraft 1.21.1 data files from PrismarineJS/minecraft-data."""

import json
import os
from pathlib import Path

import requests

_BASE_URL = "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.1"
_CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


def _fetch_or_load(filename: str, url: str, force_refresh: bool = False) -> object:
    cache_path = _CACHE_DIR / filename
    if not force_refresh and cache_path.exists():
        with cache_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Fetching {url} ...")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(data, f)

    return data


def get_items(force_refresh: bool = False) -> list[dict]:
    return _fetch_or_load("items.json", f"{_BASE_URL}/items.json", force_refresh)


def get_recipes(force_refresh: bool = False) -> dict:
    return _fetch_or_load("recipes.json", f"{_BASE_URL}/recipes.json", force_refresh)
