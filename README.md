# Houghton Kitchen

Weekly dinner plan, grocery list and recipe box for Levi and Chloe, with a hands-free cook mode.

**Live:** https://levijhoughton.github.io/houghton-kitchen/

It's a static site with no build step, served by GitHub Pages from `main`. Pushing a change deploys it in about a minute.

## What's in the app

- **Week:** tonight's dinner with a start-cooking button and a preview of tomorrow, and the week's dinners, each with its cook time, calories and protein per portion, what a portion is, and any dated reminder (thawing) for that night. Arrows page through past weeks.
- **Groceries:** each week's list by store and aisle, with a check-off per item, which dinners each item is for, a progress bar, and "Copy what's left" for pasting into a pickup order.
- **Recipes:** search by name or ingredient, filter by cuisine, and see when each was last made.
- **Recipe page:** rough macros and calories per portion, what a portion looks like, a servings adjuster that rescales every amount (including amounts inside the steps), and checkable ingredients.
- **Cook mode:** one step at a time in large type, with these features:
  - keeps the screen on where the browser allows it
  - swipe or arrow keys between steps
  - text-size buttons
  - one-tap timers that keep running across reloads and between screens, with a sound, a vibration where supported, and a +1 min button
  - remembers which step you were on
- **Offline:** once the site has loaded, it works with no signal from the last saved copy. It can be added to the home screen.

Checked items, the current cook step, servings and text size are stored on each device. They aren't shared between devices and never reach the repo.

## Layout

```
index.html            the whole app
sw.js                 offline cache (network-first, falls back to the last good copy)
manifest.webmanifest  home-screen app metadata
icons/
tools/check.py        validates data/ before you push
data/
  index.json          lists every recipe id and plan id; nothing unlisted shows up
  recipes/<id>.json   one file per recipe
  plans/<id>.json     one file per week, id = the week's first date (YYYY-MM-DD)
  freezer.json        freezer inventory (planning record; not shown on the site)
  restock.json        running list of pantry items to pick up on the next shop
```

## Weekly update

1. Add new recipes as `data/recipes/<kebab-case-id>.json`.
2. Add the week as `data/plans/<YYYY-MM-DD>.json`, with nights, dated reminders and the grocery list.
3. List both ids in `data/index.json` and set `"updated"` to today.
4. Update `data/freezer.json` if anything went in or came out.
5. Mark last week's cooked nights with `"status": "cooked"`.
6. Run `python3 tools/check.py`. It must report 0 errors.
7. Commit and push to `main`.

## Recipe schema

```json
{
  "name": "Greek Lemon-Oregano Chicken & Potatoes",
  "cuisine": "Greek",
  "subtitle": "With village salad (horiatiki) and tzatziki",
  "servings": 5,
  "servingUnit": "portions",
  "yields": "2 dinners + 3 lunches",
  "time": "~65 min, ~30 hands-on",
  "equipment": "2 sheet pans, air fryer, thermometer",
  "macros": { "basis": "per portion, 1 of 5", "kcal": 800, "protein": 68, "carbs": 64, "fat": 30, "fiber": 10,
              "portion": "About 5½ oz cooked chicken, 1¼ cups roasted potatoes…",
              "note": "Rough estimate from standard nutrition values…" },
  "before": ["Things to do or check first. **bold** = an amount."],
  "notes": "One short paragraph on technique.",
  "ingredients": [ { "group": "Chicken", "items": ["2¼ lb chicken breast", "1 Tbsp olive oil"] } ],
  "steps": [ { "title": "Potatoes in", "body": "Toss **2½ lb potatoes** with **1½ Tbsp olive oil**…", "timerMin": 20 } ],
  "after": ["Packing lunches, leftovers, freezing."],
  "source": { "label": "Where it's adapted from", "url": "https://…" }
}
```

Writing rules:
- **Every step carries its own amounts in `**bold**`**, so the cook never has to scroll back. The servings adjuster rescales only the bold parts of steps, and whole ingredient lines.
- **Keep non-quantities out of bold, or write them so the scaler skips them.** The scaler leaves alone temperatures (°F), times (min, hr), sizes (-inch, -qt), can sizes after `×` (`4 × 15 oz`) and anything in parentheses. Targets that shouldn't scale, like "family gets ~6 cups", go in plain text.
- Steps run in real cooking order. For stir-fries, prep everything first. For sheet-pan and simmer recipes, prep happens during the oven or simmer time.
- `timerMin` adds a one-tap timer to that step.
- `macros` are rough per-portion estimates; say so in `note`.
- `macros.portion` says what one portion is, by eye (cups, ounces of cooked protein, pieces). When dinner plates and lunch containers differ, describe both.
- Required fields: `name`, `ingredients`, `steps`. Everything else is optional.

## Plan schema

```json
{
  "label": "Oct 14–19",
  "startDate": "2026-10-14",
  "nights": [
    { "date": "2026-10-16", "day": "Fri", "recipeId": "greek-lemon-oregano-chicken",
      "title": "Greek lemon-oregano chicken & potatoes", "sizing": "2 + 3 lunches",
      "leftovers": "lunches Sat–Mon", "status": "cooked" },
    { "date": "2026-10-17", "day": "Sat", "recipeId": null, "title": "BYU game: pizza" }
  ],
  "todo": [ { "date": "2026-10-18", "when": "Sun morning", "what": "Move the **turkey** to the fridge." } ],
  "notes": [ "Optional callouts. **bold** allowed." ],
  "grocery": {
    "stores": [ { "name": "Walmart pickup", "groups": [
      { "name": "Produce", "items": [ { "name": "Yellow potatoes", "qty": "3 lb bag", "for": ["Fri"], "note": "optional" } ] }
    ] } ],
    "pantry": [ { "name": "Toasted sesame oil", "qty": "2½ tsp", "note": "Smell it; it goes rancid." } ]
  }
}
```

A `todo` shows on the night with the same `date` and is highlighted that day and the day before. Use it for thawing and freezer moves only; cook time comes from the recipe's `time`.

## Restock schema

```json
{ "updated": "2026-10-19", "items": [ { "name": "Dried oregano", "qty": "1 jar", "store": "Walmart", "note": "optional" } ] }
```

Shown at the top of Groceries for the current and upcoming weeks. When a week's grocery list is built, fold these items into it and empty this list.

## Freezer schema

```json
{ "updated": "2026-10-16",
  "items": [ { "name": "Turkey chili", "amount": "~4 cups (2 portions)", "added": "2026-10-19", "note": "optional" } ] }
```

An item whose `added` date is in the future shows as "Goes in <date>".
