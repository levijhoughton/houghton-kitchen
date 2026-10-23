#!/usr/bin/env python3
"""Validate the site's data before pushing.

Usage:  python3 tools/check.py
Exits non-zero (and prints what's wrong) if anything would break or silently disappear on the site.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
errors, warnings = [], []

def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        errors.append(f"missing file: {os.path.relpath(path, ROOT)}")
    except json.JSONDecodeError as e:
        errors.append(f"bad JSON in {os.path.relpath(path, ROOT)}: {e}")
    return None

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")

ix = load(os.path.join(D, "index.json")) or {}
recipes = {}
for rid in ix.get("recipes", []):
    if not ID.match(rid):
        errors.append(f"recipe id '{rid}' should be lowercase-kebab-case")
    r = load(os.path.join(D, "recipes", rid + ".json"))
    if r is None:
        continue
    recipes[rid] = r
    where = f"recipes/{rid}"
    for k in ("name", "ingredients", "steps"):
        if not r.get(k):
            errors.append(f"{where}: missing '{k}'")
    for i, s in enumerate(r.get("steps", [])):
        if not s.get("title") or not s.get("body"):
            errors.append(f"{where}: step {i+1} needs title and body")
        if "timerMin" in s and not isinstance(s["timerMin"], (int, float)):
            errors.append(f"{where}: step {i+1} timerMin must be a number")
        if s.get("body", "").count("**") % 2:
            errors.append(f"{where}: step {i+1} has an unclosed ** bold marker")
    for g in r.get("ingredients", []):
        if not isinstance(g.get("items"), list) or not g["items"]:
            errors.append(f"{where}: ingredient group '{g.get('group')}' has no items")
    if "servings" in r and not (isinstance(r["servings"], int) and r["servings"] > 0):
        errors.append(f"{where}: servings must be a positive whole number")
    if "servings" not in r:
        warnings.append(f"{where}: no 'servings', so the servings adjuster is hidden")
    m = r.get("macros")
    if m is None:
        warnings.append(f"{where}: no 'macros'")
    else:
        if not isinstance(m.get("portion"), str) or not m["portion"].strip():
            warnings.append(f"{where}: no 'macros.portion', so the page doesn't say what a portion is")
        for k in ("protein", "kcal", "carbs", "fat", "fiber"):
            if k in m and not isinstance(m[k], (int, float)):
                errors.append(f"{where}: macros.{k} must be a number")

listed = set(ix.get("recipes", []))
on_disk = {f[:-5] for f in os.listdir(os.path.join(D, "recipes")) if f.endswith(".json")}
for rid in sorted(on_disk - listed):
    warnings.append(f"recipes/{rid}.json exists but isn't listed in data/index.json, so it won't show up")

for pid in ix.get("plans", []):
    p = load(os.path.join(D, "plans", pid + ".json"))
    if p is None:
        continue
    where = f"plans/{pid}"
    if not DATE.match(p.get("startDate", "")):
        errors.append(f"{where}: startDate must be YYYY-MM-DD")
    for n in p.get("nights", []):
        if not DATE.match(n.get("date", "")):
            errors.append(f"{where}: night '{n.get('title')}' has a bad date")
        rid = n.get("recipeId")
        if rid and rid not in recipes:
            errors.append(f"{where}: night {n.get('date')} points at recipe '{rid}', which isn't listed")
    for t in p.get("todo", []):
        if "date" in t and not DATE.match(t["date"]):
            errors.append(f"{where}: todo '{t.get('what','')[:30]}' has a bad date")
    for s in (p.get("grocery") or {}).get("stores", []):
        for g in s.get("groups", []):
            for it in g.get("items", []):
                if not it.get("name"):
                    errors.append(f"{where}: grocery item without a name in {s.get('name')}/{g.get('name')}")
                if not it.get("qty"):
                    warnings.append(f"{where}: grocery '{it.get('name')}' has no qty")

plans_on_disk = {f[:-5] for f in os.listdir(os.path.join(D, "plans")) if f.endswith(".json")}
for pid in sorted(plans_on_disk - set(ix.get("plans", []))):
    warnings.append(f"plans/{pid}.json exists but isn't listed in data/index.json")

if ix.get("freezer"):
    fz = load(os.path.join(D, "freezer.json"))
    if fz is not None and not isinstance(fz.get("items"), list):
        errors.append("freezer.json: 'items' must be a list")

for w in warnings:
    print("warning:", w)
for e in errors:
    print("ERROR:", e)
print(f"{len(recipes)} recipes, {len(ix.get('plans', []))} plans checked: {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
