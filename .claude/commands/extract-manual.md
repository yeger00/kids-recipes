Given the following manual/instruction text, extract all materials/supplies needed with their quantities and all required tools.

Output ONLY valid JSON in this exact format (no extra text, no markdown code blocks):
{
  "materials": [
    {"name": "<material name in Hebrew>", "amount": "<quantity or spec in Hebrew>"},
    ...
  ],
  "tools": ["<tool 1 in Hebrew>", "<tool 2 in Hebrew>", ...]
}

Rules:
- Translate everything to Hebrew
- For tools, infer ALL tools needed — even if not explicitly mentioned
- If a material has no specific amount, use "לפי הצורך"
- Do not include any explanation or text outside the JSON

Manual text:
$ARGUMENTS
