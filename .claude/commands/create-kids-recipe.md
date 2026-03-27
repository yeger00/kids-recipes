Create a kids-friendly recipe page from a URL or from raw recipe text.

Input: $ARGUMENTS

---

## Step 1 — Get the recipe text

Look at `$ARGUMENTS` and decide which mode to use:

**Mode A — URL** (if `$ARGUMENTS` starts with `http://` or `https://`):
Use the WebFetch tool to fetch the URL. Extract only the meaningful text content: recipe title, ingredients, amounts, and cooking steps. Strip navigation, ads, comments, and boilerplate. Keep the text in its original language.

**Mode B — Raw text** (if `$ARGUMENTS` does not start with `http`):
Use `$ARGUMENTS` directly as the recipe text. Extract the recipe title from the first line or heading. If no clear title is found, use "מתכון" as the title.

In both modes, save the result as `<RECIPE_TEXT>` and the recipe title as `<RECIPE_TITLE>`.

For Mode A, also save the URL as `<SOURCE_URL>`. For Mode B, set `<SOURCE_URL>` to empty.

---

## Step 2 — Extract ingredients and tools

Call the `extract-recipe` skill with `<RECIPE_TEXT>` as the argument.

This returns JSON like:
```json
{
  "ingredients": [
    {"name": "קמח", "amount": "2 כוסות"},
    ...
  ],
  "tools": ["קערה", "מטרפה", ...]
}
```

Save this as `<EXTRACTED>`.

---

## Step 3 — Find or generate icons

For EACH ingredient in `<EXTRACTED>.ingredients`, call the `find-icon` skill with the ingredient's `name` as the argument. Record the returned icon path.

For EACH tool in `<EXTRACTED>.tools`, call the `find-icon` skill with the tool name as the argument. Record the returned icon path.

Build two lists:
- `<INGREDIENT_ICONS>`: list of `{name, amount, icon_path}`
- `<TOOL_ICONS>`: list of `{name, icon_path}`

---

## Step 3b — Generate step illustrations

For EACH step in the recipe, generate an illustration of a cute kawaii child performing that action.

Build a short English visual description of what the child is doing in that step (be specific about the action and props — e.g. "pouring milk into a bowl", "flipping a pancake with a spatula on a pan").

Then run (replace N with 1-based step number, SLUG with the recipe slug from step 4, and fill in the prompt):

```bash
source .env && uv run scripts/generate_image.py \
  --prompt "cute kawaii boy with short brown hair and rosy cheeks DOING_ACTION, flat illustration for kids, white background, thick black outline, soft pastel colors, simple bold shapes, no shading, no gradients, no text, no labels. The boy should look like the boy in the reference image." \
  --reference "icons-db/icons/reference.png" \
  --output "icons-db/steps/SLUG-step-N.png" \
  --aspect square \
  --model 2 \
  --size 512
```

Run all step image generations in parallel (append `&` to each command, then `wait` at the end).

Make sure the `icons-db/steps/` directory exists (create with `mkdir -p icons-db/steps` if needed).

Build: `<STEP_IMAGES>`: list of `{step_index (1-based), image_path}`

---

## Step 4 — Create a slug for the output filename

Create an ASCII slug from `<RECIPE_TITLE>` — lowercase, hyphens for spaces, no special characters.
Output path: `recipes/<slug>.html`

Make sure the `recipes/` directory exists (create it if needed).

---

## Step 5 — Generate the HTML file

Read the template file at `templates/recipe.html`. It contains three placeholders:
- `{{RECIPE_TITLE}}` — appears twice (in `<title>` and `<h1>`)
- `{{INGREDIENT_CARDS}}` — where ingredient cards go
- `{{TOOL_CARDS}}` — where tool cards go
- `{{STEP_ITEMS}}` — where step items go

Replace each placeholder with the generated HTML snippets below, then write the result to `recipes/<slug>.html`.

**`{{SOURCE_LINK}}`**:
- If `<SOURCE_URL>` is set: `<p class="source-link">מקור: <a href="SOURCE_URL" target="_blank">SOURCE_URL</a></p>`
- If empty: remove the placeholder entirely (replace with empty string)

**Ingredient card snippet** (repeat for each ingredient):
```html
<div class="ingredient-card" onclick="this.classList.toggle('checked')">
  <div class="checkmark">✔</div>
  <img src="../icons-db/icons/ICON_FILE" alt="NAME">
  <div class="card-amount">AMOUNT</div>
  <div class="card-name">NAME</div>
</div>
```
If no icon is available, replace `<img ...>` with:
```html
<div class="icon-placeholder">?</div>
```

**Tool card snippet** (repeat for each tool):
```html
<div class="tool-card" onclick="this.classList.toggle('checked')">
  <div class="checkmark">✔</div>
  <img src="../icons-db/icons/ICON_FILE" alt="NAME">
  <div class="card-name">NAME</div>
</div>
```

**Step item snippet** (repeat for each step):
```html
<li onclick="this.classList.toggle('checked')">
  <span class="step-number"></span>
  <span class="step-check">✔</span>
  <div class="step-body">
    <span class="step-text">STEP TEXT</span>
    <div class="step-ingredients">
      <!-- repeat for each ingredient used in this step: -->
      <span class="step-ingredient-tag">
        <img src="../icons-db/icons/ICON_FILE" alt="NAME">NAME
      </span>
    </div>
  </div>
  <img class="step-image" src="../icons-db/steps/SLUG-step-N.png" alt="שלב N">
</li>
```

For each step, infer which ingredients from `<INGREDIENT_ICONS>` are used in that step. Include only the relevant ones. If a step uses no specific ingredient (e.g. "heat the pan"), omit the `.step-ingredients` div entirely.

Use the step image path from `<STEP_IMAGES>` for the matching step index. Replace SLUG and N accordingly.

All icon `src` paths must be relative: `../icons-db/icons/<filename>`.

---

## Step 6 — Report

```
נוצר דף מתכון: recipes/<slug>.html
מצרכים: <N>
כלים: <N>
```
