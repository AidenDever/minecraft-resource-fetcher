# CLAUDE.md — AI Assistant Guide for minecraft-resource-fetcher

## Project Overview

A Minecraft crafting resource calculator with two interfaces:
- **Python CLI** — reads item lists from stdin or a file, outputs raw materials needed
- **Web UI** (`index.html`) — single-file, client-side, no server required

Data is sourced from [PrismarineJS/minecraft-data](https://github.com/PrismarineJS/minecraft-data) and cached locally on first run.

Live site: <https://aidendever.github.io/minecraft-resource-fetcher/>

---

## Repository Structure

```
minecraft-resource-fetcher/
├── main.py              # CLI entry point
├── index.html           # Self-contained web UI (HTML + CSS + JS)
├── requirements.txt     # Python dependencies
├── test_input.txt       # Sample input for manual testing
├── README.md
└── src/
    ├── __init__.py      # Empty package marker
    ├── data.py          # Fetch + cache Minecraft JSON data
    ├── items.py         # Item name resolution with fuzzy matching
    ├── parser.py        # Parse freeform item-list text
    └── recipes.py       # Recursive recipe resolution + material totals
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| HTTP client | `requests` |
| Fuzzy matching (CLI) | `rapidfuzz` |
| Fuzzy matching (web) | Fuse.js (CDN) |
| Minecraft data | PrismarineJS/minecraft-data JSON API |
| Web frontend | Vanilla JS (ES6), no build step |

---

## Running the CLI

```bash
# Install dependencies (once)
pip install -r requirements.txt

# Read from file
python main.py test_input.txt

# Read from stdin
cat test_input.txt | python main.py
```

### Accepted Input Formats

The parser (`src/parser.py`) handles all of these on each line:

```
64 oak planks
oak planks x64
oak planks: 64
oak planks (64)
2 stacks of stone bricks   # expands to 128
- 10 torches               # list markers stripped
* 4 furnaces
```

---

## Module Responsibilities

### `src/parser.py`
- `parse_resource_list(text)` → `list[(item_str, qty)]`
- `_parse_line(line)` handles a single line
- "stacks" expand to multiples of 64
- List markers (`-`, `*`, `•`, `1.`, `1)`) are stripped before parsing

### `src/data.py`
- Base URL: `https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.1`
- Cache dir: `data/cache/` (auto-created, git-ignored)
- `get_items()` → list of item dicts (`{id, name, displayName, ...}`)
- `get_recipes()` → raw recipe dict keyed by result item ID
- `_fetch_or_load(filename)` downloads on first call, reads cache thereafter

### `src/items.py`
- `resolve_item_name(query, items)` → `(item_dict | None, confidence_pct)`
- Resolution order: alias table → suffix substitution → exact match → RapidFuzz (threshold 60)
- Module-level caches (`_items_by_id`, `_items_by_name`, `_all_names`) — populated lazily
- Aliases hardcoded in `_ALIASES` dict (e.g. `"beds"` → `"white_bed"`)

### `src/recipes.py`
- `build_recipe_index(recipes, items)` → `{result_id: [{result_id, result_count, ingredients}]}`
- Skips smelting/non-crafting recipes
- `resolve_to_materials(item_id, qty, recipe_index, items, visited)` — recursive DFS with cycle detection
- `calculate_materials(text)` — top-level orchestrator; returns `(totals_dict, matched_items, unresolved_items)`

### `main.py`
- Reads input (file arg or stdin)
- Calls `calculate_materials()`, prints matched items and raw material totals
- Reports unresolved item names to stderr

---

## Web UI (`index.html`)

- Entirely self-contained — no build tool, no bundler
- Fetches `items.json` and `recipes.json` lazily from PrismarineJS CDN on first calculation
- Edition switching (Java / Bedrock) clears in-memory data cache
- Uses Fuse.js for client-side fuzzy matching (loaded from CDN)
- DOM manipulation only — no framework

---

## Code Conventions

### Python Style
- **snake_case** for functions and variables
- **`_` prefix** for private/internal functions (`_parse_line`, `_fetch_or_load`)
- **SCREAMING_SNAKE_CASE** for module-level constants (`_BASE_URL`, `_CACHE_DIR`)
- Purely functional — no classes used anywhere
- Lazy-loaded module-level caches instead of passing state around
- `collections.Counter` for deduplication of ingredient lists

### Error Handling
- Exceptions are allowed to propagate from `requests` and JSON parsing
- Unresolved items are collected and reported rather than crashing
- Cycle detection in recipe traversal uses immutable `visited` sets passed per-branch

### No Formal Tooling
- No linter configured (no `.pylintrc`, no `pyproject.toml`)
- No formatter configured
- No test framework (no pytest/unittest)
- Keep this in mind: do not add linting configs unless asked

---

## Adding a New Minecraft Version

1. Update `_BASE_URL` in `src/data.py` to point to the desired version path, e.g.:
   ```python
   _BASE_URL = "https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.20.4"
   ```
2. Delete `data/cache/` to force a fresh download.
3. In `index.html`, update the `BASE_URL` constant in the `<script>` section similarly.

---

## Testing

No automated test suite exists. Manual testing:

```bash
python main.py test_input.txt
```

`test_input.txt` contains 38 realistic lines covering various input formats and item types. Check that:
- All items resolve (or unresolved ones are reported clearly)
- Raw material totals look correct
- "stacks" notation expands properly

---

## Git Workflow

- Main branch: `master`
- Feature branches follow the pattern: `claude/<description>-<ID>`
- No CI/CD — pushes go directly to origin

---

## What to Avoid

- **Do not add a build system** (no webpack, poetry, etc.) unless explicitly requested.
- **Do not introduce classes** — the codebase is intentionally functional.
- **Do not change the cache directory** (`data/cache/`) — it is git-ignored by design.
- **Do not add test files next to source files** — keep the root clean.
- **Do not modify `index.html` dependencies** (Fuse.js CDN URL) without verifying the new version works client-side.
