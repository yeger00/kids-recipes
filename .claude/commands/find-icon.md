Look up or generate an icon for a recipe ingredient or kitchen tool.

Item name: $ARGUMENTS

---

## Step 1 — Read the icon DB

Read `icons-db/index.json`. It has an `items` array where each entry looks like:
```json
{"name": "קמח", "aliases": ["קמח לבן"], "file": "flour.png"}
```

## Step 2 — Search for the item

Check if `$ARGUMENTS` matches any entry's `name` or any value in its `aliases` array (case-insensitive, ignore whitespace differences).

---

## Step 3a — If FOUND

Report:
```
נמצא אייקון: icons-db/icons/<filename>
```
Done. Stop here.

---

## Step 3b — If NOT FOUND — generate with nanobanana

### 3b.1 — Build the prompt

Compose a nanobanana icon prompt using this fixed style phrase + a variable subject you write:

**Fixed style (always use verbatim):**
```
flat icon, cute kawaii illustration for kids, white background, thick black outline, soft pastel colors, simple bold shapes, no shading, no gradients, no text, no labels
```

**Variable subject:** Write a short, clear English visual description of `$ARGUMENTS` — what it looks like, its shape, color, key features. Be specific. Examples:
- קמח → "a small open paper bag of white flour with a few puffs of flour dust"
- מערבל עם וו לישה → "a stand mixer with a dough hook attachment, light pastel body"
- שמן זית → "a small bottle of golden olive oil with a green olive and leaf"
- שמרים → "a small packet or cube of fresh yeast, beige-tan color"

### 3b.2 — Create a safe filename slug

Create an ASCII slug from `$ARGUMENTS` (e.g., קמח → `kamach`, מערבל → `mearbel`, שמן_זית → `shemen-zayit`). Use simple English transliteration, lowercase, hyphens for spaces.

The target filename is `<slug>.png`.

### 3b.3 — Generate the icon with nanobanana

Run this bash command (fill in the full prompt from 3b.1 and the slug from 3b.2):

```bash
uv run scripts/generate_image.py \
  --prompt "<FULL_PROMPT_HERE>" \
  --output "icons-db/icons/<slug>.png" \
  --aspect square \
  --model 2 \
  --size 512
```

The script writes the image directly to `icons-db/icons/<slug>.png`.

### 3b.6 — Update index.json

Read `icons-db/index.json` again, append a new entry to the `items` array:
```json
{"name": "$ARGUMENTS", "aliases": [], "file": "<slug>.png"}
```
Write the updated JSON back to `icons-db/index.json`.

### 3b.7 — Report

```
נוצר אייקון חדש: icons-db/icons/<slug>.png
נוסף ל-DB בשם: $ARGUMENTS
```
