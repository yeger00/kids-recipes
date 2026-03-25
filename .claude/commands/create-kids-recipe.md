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
<div class="tool-card">
  <img src="../icons-db/icons/ICON_FILE" alt="NAME">
  <div class="card-name">NAME</div>
</div>
```

**Step item snippet** (repeat for each step):
```html
<li onclick="this.classList.toggle('checked')">
  <span class="step-number"></span>
  <span class="step-check">✔</span>
  <span class="step-text">STEP TEXT</span>
</li>
```

All icon `src` paths must be relative: `../icons-db/icons/<filename>`.

---

## Step 6 — Report

```
נוצר דף מתכון: recipes/<slug>.html
מצרכים: <N>
כלים: <N>
```
