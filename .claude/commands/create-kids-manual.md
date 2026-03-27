Create a kids-friendly manual/instruction page from a URL or raw instruction text.

Input: $ARGUMENTS

---

## Step 1 — Get the manual text

**Mode A — URL** (if input starts with `http://` or `https://`):
Use WebFetch to fetch the URL. Extract: title, materials/supplies with quantities, tools, and all steps. Strip navigation, ads, and boilerplate.

**Mode B — Raw text** (if input does not start with `http`):
Use the input directly. Extract the title from the first line or heading. If no clear title, use "מדריך".

In both modes:
- Translate all content to Hebrew
- Save as `<MANUAL_TEXT>`, `<MANUAL_TITLE>`, and `<SOURCE_URL>` (empty for Mode B)

---

## Step 2 — Extract materials and tools

Call the `extract-manual` skill with `<MANUAL_TEXT>` as the argument.

Returns JSON:
```json
{
  "materials": [{"name": "...", "amount": "..."}, ...],
  "tools": ["...", ...]
}
```

Save as `<EXTRACTED>`.

---

## Step 3 — Find or generate icons

For EACH material in `<EXTRACTED>.materials`, call the `find-icon` skill with the material's `name`. Record the icon path.

For EACH tool in `<EXTRACTED>.tools`, call the `find-icon` skill with the tool name. Record the icon path.

Build:
- `<MATERIAL_ICONS>`: list of `{name, amount, icon_path}`
- `<TOOL_ICONS>`: list of `{name, icon_path}`

---

## Step 3b — Generate step illustrations

For EACH step, generate an illustration of a kawaii child performing that action.

First, determine the manual slug (same as Step 4 below — compute it now so it's available for file paths).

Build a short English visual description of what the child is doing in each step (be specific about the action and props).

Make sure the `icons-db/steps/` directory exists:
```bash
mkdir -p icons-db/steps
```

Write a JSONL file to `/tmp/steps-batch.jsonl` where each line is one step job:
```json
{"prompt": "cute kawaii boy with short brown hair and rosy cheeks DOING_ACTION, flat illustration for kids, white background, thick black outline, soft pastel colors, simple bold shapes, no shading, no gradients, no text, no labels. The boy should look like the boy in the reference image.", "output": "icons-db/steps/SLUG-step-N.png", "aspect": "square", "model": "2", "size": "512", "references": ["icons-db/icons/reference.png"]}
```

Write one line per step (N = 1-based step index, SLUG = manual slug, DOING_ACTION = your visual description).

Then run the batch:
```bash
source .env && uv run scripts/generate_image.py --batch-input /tmp/steps-batch.jsonl
```

Build: `<STEP_IMAGES>`: list of `{step_index (1-based), image_path}`

---

## Step 4 — Create a slug for the output filename

Create an ASCII slug from `<MANUAL_TITLE>` — lowercase, hyphens for spaces, no special characters.
Output path: `manuals/<slug>.html`

Ensure `manuals/` directory exists.

---

## Step 5 — Generate the HTML file

Read `templates/manual.html`. Replace placeholders:

- `{{MANUAL_TITLE}}` — appears twice (in `<title>` and `<h1>`)
- `{{SOURCE_LINK}}`:
  - If `<SOURCE_URL>` set: `<p class="source-link">מקור: <a href="SOURCE_URL" target="_blank">SOURCE_URL</a></p>`
  - If empty: replace with empty string
- `{{MATERIAL_CARDS}}` — material card snippets
- `{{TOOL_CARDS}}` — tool card snippets
- `{{STEP_ITEMS}}` — step item snippets

**Material card snippet:**
```html
<div class="material-card" onclick="this.classList.toggle('checked')">
  <div class="checkmark">✔</div>
  <img src="../icons-db/icons/ICON_FILE" alt="NAME">
  <div class="card-amount">AMOUNT</div>
  <div class="card-name">NAME</div>
</div>
```

**Tool card snippet:**
```html
<div class="tool-card" onclick="this.classList.toggle('checked')">
  <div class="checkmark">✔</div>
  <img src="../icons-db/icons/ICON_FILE" alt="NAME">
  <div class="card-name">NAME</div>
</div>
```

**Step item snippet:**
```html
<li onclick="this.classList.toggle('checked')">
  <span class="step-number"></span>
  <span class="step-check">✔</span>
  <div class="step-body">
    <span class="step-text">STEP TEXT</span>
    <div class="step-materials">
      <span class="step-material-tag">
        <img src="../icons-db/icons/ICON_FILE" alt="NAME">NAME
      </span>
    </div>
  </div>
  <img class="step-image" src="../icons-db/steps/SLUG-step-N.png" alt="שלב N">
</li>
```

For each step, infer which materials/tools from `<MATERIAL_ICONS>` and `<TOOL_ICONS>` are used. Include only relevant ones. If none, omit the `.step-materials` div.

Write result to `manuals/<slug>.html`.

---

## Step 6 — Add card to index.html

Add a card to the manuals section in `index.html`:
```html
<a class="recipe-card" href="manuals/<slug>.html">
  <div class="recipe-icon">EMOJI</div>
  <div class="recipe-title">MANUAL_TITLE</div>
</a>
```

Choose an appropriate emoji for the topic.

---

## Step 7 — Report

```
נוצר דף מדריך: manuals/<slug>.html
חומרים: <N>
כלים: <N>
שלבים: <N>
```
