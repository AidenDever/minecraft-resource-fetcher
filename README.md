# Minecraft Resource Calculator

Paste a list of Minecraft items you want to build and get back the exact raw materials you need to gather. Handles recipes recursively, ask for oak stairs and it'll trace all the way back to oak logs.

**Live site: [aidendever.github.io/minecraft-resource-fetcher](https://aidendever.github.io/minecraft-resource-fetcher/)**

Targets **MC Java Edition 1.21.1** (more versions can be added via the dropdown).

---

## Features

- Resolves crafting recipes recursively to base materials
- Understands common quantity formats:
  - `64 oak planks`
  - `2 stacks of stone bricks`
  - `oak stairs x4`
  - `glass pane (32)`
- Fuzzy item name matching — typos and approximate names are handled
- Supports bulk lists (numbered, bulleted, plain)
- Web UI runs entirely client-side, no server needed
- Python CLI for terminal use

---

## Web UI

Open the live site, paste your item list into the text box, and click **Calculate**.

Data is fetched from [PrismarineJS/minecraft-data](https://github.com/PrismarineJS/minecraft-data) on first use and cached in memory for the session.

---

## CLI

**Requirements:** Python 3.10+

```bash
pip install -r requirements.txt
```

**From stdin:**
```bash
echo "64 oak planks
2 stacks of stone bricks" | python main.py
```

**From a file:**
```bash
python main.py my_list.txt
```

**Example output:**
```
64 oak planks      -> Oak Planks
128 stone bricks   -> Stone Bricks

Materials needed:
  16  Oak Log
 128  Stone
```

---

## Adding more versions

In `index.html`, add an entry to the `EDITIONS` object and a matching `<option>` in the dropdown:

```js
const EDITIONS = {
  java_1_21_1: 'https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.21.1',
  java_1_20_4: 'https://raw.githubusercontent.com/PrismarineJS/minecraft-data/master/data/pc/1.20.4',
};
```

```html
<optgroup label="Java Edition">
  <option value="java_1_21_1">Java 1.21.1</option>
  <option value="java_1_20_4">Java 1.20.4</option>
</optgroup>
```

---

## Tech

- **Web:** vanilla JS, [Fuse.js](https://fusejs.io/) for fuzzy matching, PrismarineJS data via CDN
- **CLI:** Python, [rapidfuzz](https://github.com/rapidfuzz/RapidFuzz), [requests](https://docs.python-requests.org/)
- **Data:** [PrismarineJS/minecraft-data](https://github.com/PrismarineJS/minecraft-data)
