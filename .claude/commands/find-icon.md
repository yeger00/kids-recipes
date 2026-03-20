You are looking up an icon for a recipe ingredient or kitchen tool.

Item name: $ARGUMENTS

Follow these steps:

## Step 1 — Read the icon DB
Read the file at `icons-db/index.json`. It contains an `items` array where each entry looks like:
```json
{"name": "קמח", "aliases": ["קמח לבן", "קמח חיטה"], "file": "flour.png"}
```

## Step 2 — Search for the item
Check if `$ARGUMENTS` matches any entry's `name` or any value in its `aliases` array (case-insensitive, ignore niqqud/whitespace differences).

## Step 3a — If found
Respond with:
```
נמצא אייקון: icons-db/icons/<filename>
```

## Step 3b — If NOT found
Respond with the following nanobanan image generation prompt (output it exactly, filling in the <description> part):

---
**Nanobanan prompt:**

Style: flat icon, cute kawaii illustration for kids, white background, thick black outline, soft pastel colors, simple bold shapes, no shading, no gradients, no text

Subject: <write a clear visual description in English of what "$ARGUMENTS" looks like — be specific about shape, color, and defining features. For tools describe the object itself. For ingredients describe the raw ingredient.>

---

After the prompt, also add:
> האייקון לא נמצא ב-DB. ניתן להוסיף אותו לאחר היצירה על ידי עדכון `icons-db/index.json` עם השם, כינויים, ושם הקובץ.
