# Kids Recipes

A project for managing kids' recipes with icon generation for ingredients and tools.

## Claude Code Skills

### `/extract-recipe <recipe text>`

Parses a recipe and outputs a JSON with all ingredients (name + amount) and required kitchen tools.

**Example:**
```
/extract-recipe עוגת שוקולד: 2 כוסות קמח, 1 כוס סוכר, 3 ביצים, 200 גרם חמאה. מערבבים ואופים ב-180 מעלות.
```

**Output:**
```json
{
  "ingredients": [
    {"name": "קמח", "amount": "2 כוסות"},
    {"name": "סוכר", "amount": "1 כוס"}
  ],
  "tools": ["קערת ערבוב", "מערבל", "תבנית אפייה"]
}
```

---

### `/find-icon <ingredient or tool name>`

Looks up an icon in the local DB. If not found, generates one using nanobanana and registers it automatically.

**Example:**
```
/find-icon קמח
/find-icon מערבל עם וו לישה
/find-icon שמן זית
```

**If found:**
```
נמצא אייקון: icons-db/icons/kamach.png
```

**If not found:** generates the icon via nanobanana, saves it to `icons-db/icons/`, and updates the DB.

---

## Icons DB

Icons are stored in `icons-db/`:

```
icons-db/
├── index.json       ← registry of all icons (name, aliases, filename)
└── icons/           ← PNG icon files
```

To manually add an icon, drop the `.png` into `icons-db/icons/` and add an entry to `index.json`:
```json
{"name": "קמח", "aliases": ["קמח לבן", "קמח חיטה"], "file": "flour.png"}
```

---

## Setup: nanobanana (Icon Generation)

The `/find-icon` skill uses [nanobanana](https://github.com/gemini-cli-extensions/nanobanana), a Gemini CLI extension for AI image generation.

### Prerequisites

- Node.js 20+
- A Gemini API key — get one free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Installation

**1. Install Gemini CLI:**
```bash
npm install -g @google/gemini-cli
```

**2. Install the nanobanana extension:**
```bash
gemini extensions install https://github.com/gemini-cli-extensions/nanobanana
```

**3. Set your API key:**
```bash
export NANOBANANA_API_KEY="your-api-key-here"
```

To make it permanent, add the line above to your `~/.zshrc` (or `~/.bashrc`), then run:
```bash
source ~/.zshrc
```

### Optional: switch model

By default nanobanana uses `gemini-3.1-flash-image-preview`. To use the Pro model:
```bash
export NANOBANANA_MODEL="gemini-3-pro-image-preview"
```
