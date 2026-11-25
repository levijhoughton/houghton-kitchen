#!/usr/bin/env python3
"""Build data/catalog.json: one small entry per recipe, used by the recipe list, search, contents page and week view.

Full recipes are only fetched when one is opened, so the app doesn't download every recipe on every load.
check.py runs this automatically, so you normally don't need to run it yourself.

Usage:  python3 tools/build_catalog.py
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

# Fixed display order for the contents page and filters. check.py rejects anything else.
CATEGORIES = ["Mains", "Soups", "Salads", "Sides", "Appetizers",
              "Breakfast & quick breads", "Yeast breads", "Cookies", "Desserts", "Extras"]
PROTEINS = ["Beef", "Chicken & turkey", "Pork", "Seafood", "Meatless"]
COLLECTIONS = ["weekly", "family"]

FR = {"½": .5, "¼": .25, "¾": .75, "⅓": 1 / 3, "⅔": 2 / 3, "⅛": .125}
NUM = r"(\d+(?:\.\d+)?)?([½¼¾⅓⅔⅛])?"


def _num(whole, frac):
    if not whole and not frac:
        return None
    return (float(whole) if whole else 0) + (FR[frac] if frac else 0)


def minutes(text):
    """First duration in a piece of text, in minutes: '~1 hr 25 min' -> 85, '3½–4½ hr' -> 210, '~65 min' -> 65."""
    if not text:
        return None
    total, hit = 0.0, False
    m = re.search(NUM + r"\s*(?:[–-]\s*" + NUM + r")?\s*(hrs?|hours?)\b", text)
    if m:
        v = _num(m.group(1), m.group(2))
        if v is not None:
            total += v * 60
            hit = True
        rest = text[m.end():]
        m2 = re.match(r"\s*" + NUM + r"\s*min", rest)
        if m2 and _num(m2.group(1), m2.group(2)) is not None:
            total += _num(m2.group(1), m2.group(2))
        return round(total)
    m = re.search(NUM + r"\s*(?:[–-]\s*" + NUM + r")?\s*min", text)
    if m:
        v = _num(m.group(1), m.group(2))
        if v is not None:
            return round(v)
    return None


def time_fields(t):
    if not t:
        return None, None
    parts = [p.strip() for p in t.split(",")]
    total = minutes(parts[0])
    hands = None
    for p in parts:
        if "hands-on" in p:
            hands = minutes(p)
            if hands is None:  # '~30 hands-on': a bare number in the same unit as the total
                m = re.search(NUM + r"\s*hands-on", p)
                if m and _num(m.group(1), m.group(2)) is not None:
                    hands = round(_num(m.group(1), m.group(2)))
    return total, hands


def strip_md(s):
    return re.sub(r"\*\*", "", str(s or ""))


def entry(rid, r, order):
    total, hands = time_fields(r.get("time"))
    ing = []
    for g in r.get("ingredients", []):
        ing.extend(strip_md(i) for i in g.get("items", []))
    e = {
        "id": rid,
        "name": r.get("name"),
        "subtitle": r.get("subtitle"),
        "category": r.get("category"),
        "protein": r.get("protein"),
        "cuisine": r.get("cuisine"),
        "collection": r.get("collection", "weekly"),
        "tags": r.get("tags") or None,
        "time": r.get("time"),
        "mins": total,
        "hands": hands,
        "servings": r.get("servings"),
        "servingUnit": r.get("servingUnit"),
        "yields": r.get("yields"),
        "ing": " · ".join(ing),
        "notes": strip_md(r.get("notes"))[:400] or None,
        "n": order,
    }
    m = r.get("macros")
    if m:
        e["macros"] = {k: m[k] for k in ("kcal", "protein") if k in m}
    return {k: v for k, v in e.items() if v not in (None, "", [])}


def build(write=True):
    with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
        ix = json.load(f)
    out = []
    for i, rid in enumerate(ix.get("recipes", [])):
        p = os.path.join(D, "recipes", rid + ".json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            try:
                r = json.load(f)
            except json.JSONDecodeError:
                continue
        out.append(entry(rid, r, i))
    cat = {"categories": CATEGORIES, "proteins": PROTEINS, "recipes": out}
    if write:
        with open(os.path.join(D, "catalog.json"), "w", encoding="utf-8") as f:
            json.dump(cat, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    return cat


if __name__ == "__main__":
    c = build()
    print(f"catalog.json: {len(c['recipes'])} recipes")
