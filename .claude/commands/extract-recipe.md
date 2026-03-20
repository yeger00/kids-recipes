Given the following recipe, extract all ingredients with their amounts and all required kitchen tools.

Output ONLY valid JSON in this exact format (no extra text, no markdown code blocks):
{
  "ingredients": [
    {"name": "<ingredient name in Hebrew>", "amount": "<amount and unit in Hebrew>"},
    ...
  ],
  "tools": ["<tool 1 in Hebrew>", "<tool 2 in Hebrew>", ...]
}

Rules:
- Keep ingredient names and amounts in the same language as the recipe
- For tools, infer ALL tools needed (bowls, spoons, pans, measuring cups, etc.) — even if not explicitly mentioned
- If an ingredient has no specific amount (e.g. "to taste"), use "לפי הטעם"
- Do not include any explanation or text outside the JSON

Recipe:
$ARGUMENTS
