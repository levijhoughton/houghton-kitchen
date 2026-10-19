# Houghton Kitchen: notes for Claude

This repo is the published side of the **Houghton Food** meal-planning project. Planning happens in the project; this site is where the result lands. README.md has the full data schema.

## Weekly hand-off checklist

1. Write any new recipes to `data/recipes/<id>.json` following the README schema, including `servings`, `servingUnit` and rough `macros`.
2. Write the week to `data/plans/<first-date>.json` with nights, dated `todo` reminders (thawing!) and the store-split `grocery` list.
3. Add the ids to `data/index.json` and set `updated` to today.
4. Update `data/freezer.json` for anything that went in or came out. Fold `data/restock.json` items into the new grocery list, then empty its `items`.
5. Set `"status": "cooked"` on last week's nights that were cooked.
6. Run `python3 tools/check.py` and fix every error.
7. Commit as `Levi Houghton <levijhoughton@users.noreply.github.com>` (repo is public; don't commit a personal email) and push to `main`.

## Rules

- Amounts in step bodies go in `**bold**`; that's what the servings scaler rescales and what the cook-mode highlighter shows.
- Don't put non-quantities in bold unless the scaler already skips them (°F, min, -inch, parentheses, `× 15 oz`).
- Recipes are written in real cooking order. Stir-fries: prep everything first. Sheet-pan and simmer recipes: prep during the oven or simmer time.
- The repo is public. No personal contact details, addresses or other people's names in data files.
- **The site shows the plan, not the reasons.** Nights without a dinner are just "No dinner planned". A night cooked at a larger size gets that size as its default (`servings` on the recipe, `sizing` on the night) with no explanation of who it's for or why. The same goes for grocery groups, reminders, recipe notes and the freezer.
- Changing `index.html`, `sw.js` or the icons: bump `CACHE` in `sw.js` so installed copies pick up the new shell.
- Test UI changes in a headless browser at 390px and 1280px, light and dark, before pushing.
