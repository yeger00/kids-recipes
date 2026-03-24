Create a kids-friendly recipe page from a URL.

URL: $ARGUMENTS

---

## Step 1 — Fetch the recipe

Use the WebFetch tool to fetch `$ARGUMENTS`. Extract only the meaningful text content: recipe title, ingredients, amounts, and cooking steps. Strip navigation, ads, comments, and boilerplate. Keep the text in its original language.

Save the cleaned recipe text as `<RECIPE_TEXT>` and the recipe title as `<RECIPE_TITLE>`.

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

Write a self-contained HTML file to `recipes/<slug>.html` using the template below.

**Rules:**
- Icon `src` paths should be relative: `../icons-db/icons/<filename>`
- For any ingredient or tool where icon generation failed or returned no file, use a placeholder div with a question mark instead of an `<img>`
- Include ALL ingredients and ALL tools
- The steps section should contain the full cooking steps from `<RECIPE_TEXT>`, formatted as a numbered list

**HTML template:**

```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><!-- RECIPE_TITLE --></title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background: #fffdf7;
      color: #333;
      padding: 24px;
      max-width: 800px;
      margin: 0 auto;
    }

    h1 {
      font-size: 2rem;
      text-align: center;
      color: #e07b39;
      margin-bottom: 32px;
    }

    h2 {
      font-size: 1.3rem;
      color: #5a9e6f;
      margin-bottom: 16px;
      border-bottom: 2px dashed #c8e6c9;
      padding-bottom: 6px;
    }

    section { margin-bottom: 36px; }

    /* Ingredients */
    .ingredients-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 16px;
    }

    .ingredient-card {
      background: #fff;
      border: 2px solid #ffe0b2;
      border-radius: 16px;
      padding: 14px 10px;
      text-align: center;
      cursor: pointer;
      transition: background 0.2s, transform 0.1s;
      user-select: none;
    }

    .ingredient-card.checked {
      background: #e8f5e9;
      border-color: #81c784;
    }

    .ingredient-card.checked .card-name,
    .ingredient-card.checked .card-amount {
      text-decoration: line-through;
      opacity: 0.6;
    }

    .ingredient-card img, .ingredient-card .icon-placeholder {
      width: 72px;
      height: 72px;
      object-fit: contain;
      margin-bottom: 8px;
    }

    .icon-placeholder {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: #f5f5f5;
      border-radius: 50%;
      font-size: 1.8rem;
      color: #aaa;
    }

    .checkmark {
      font-size: 1.5rem;
      height: 28px;
      margin-bottom: 4px;
      color: #81c784;
      visibility: hidden;
    }

    .ingredient-card.checked .checkmark { visibility: visible; }

    .card-amount {
      font-size: 0.85rem;
      color: #888;
      margin-bottom: 4px;
    }

    .card-name {
      font-size: 0.95rem;
      font-weight: bold;
      color: #555;
    }

    /* Tools */
    .tools-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
    }

    .tool-card {
      background: #fff;
      border: 2px solid #b3e0ff;
      border-radius: 14px;
      padding: 12px 10px;
      text-align: center;
      width: 110px;
    }

    .tool-card img, .tool-card .icon-placeholder {
      width: 56px;
      height: 56px;
      object-fit: contain;
      margin-bottom: 6px;
    }

    .tool-card .card-name {
      font-size: 0.85rem;
      color: #555;
    }

    /* Steps */
    .steps-list {
      list-style: none;
      counter-reset: steps;
    }

    .steps-list li {
      counter-increment: steps;
      display: flex;
      align-items: flex-start;
      gap: 14px;
      margin-bottom: 16px;
      background: #fff;
      border: 2px solid #f3e5f5;
      border-radius: 14px;
      padding: 14px 16px;
      cursor: pointer;
      transition: background 0.2s;
    }

    .steps-list li.checked { background: #f1f8e9; }

    .step-number {
      font-size: 1.4rem;
      font-weight: bold;
      color: #ce93d8;
      min-width: 32px;
      line-height: 1.4;
    }

    .step-number::before { content: counter(steps); }

    .step-check {
      font-size: 1.2rem;
      color: #81c784;
      min-width: 24px;
      visibility: hidden;
    }

    .steps-list li.checked .step-check { visibility: visible; }

    .step-text { line-height: 1.6; font-size: 1rem; }
  </style>
</head>
<body>

  <h1><!-- RECIPE_TITLE --></h1>

  <section>
    <h2>🧂 מצרכים</h2>
    <div class="ingredients-grid">
      <!-- INGREDIENT CARDS — repeat for each ingredient:
      <div class="ingredient-card" onclick="this.classList.toggle('checked')">
        <div class="checkmark">✔</div>
        <img src="../icons-db/icons/ICON_FILE" alt="NAME">
        <div class="card-amount">AMOUNT</div>
        <div class="card-name">NAME</div>
      </div>
      -->
    </div>
  </section>

  <section>
    <h2>🍳 כלים</h2>
    <div class="tools-grid">
      <!-- TOOL CARDS — repeat for each tool:
      <div class="tool-card">
        <img src="../icons-db/icons/ICON_FILE" alt="NAME">
        <div class="card-name">NAME</div>
      </div>
      -->
    </div>
  </section>

  <section>
    <h2>👩‍🍳 אופן הכנה</h2>
    <ol class="steps-list">
      <!-- STEP ITEMS — repeat for each step:
      <li onclick="this.classList.toggle('checked')">
        <span class="step-number"></span>
        <span class="step-check">✔</span>
        <span class="step-text">STEP TEXT</span>
      </li>
      -->
    </ol>
  </section>

</body>
</html>
```

Fill in all the template comments with real content. Do not leave any comment placeholders in the final output.

---

## Step 6 — Report

```
נוצר דף מתכון: recipes/<slug>.html
מצרכים: <N>
כלים: <N>
```
