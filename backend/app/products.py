from typing import Any

# Deliberately local illustrative catalog: it is not live commerce data.
CATALOG: list[dict[str, Any]] = [
 {"id":"sample-sofa","name":"Compact fabric sofa","category":"interior","description":"Illustrative two-seat option for smaller living rooms.","price":2899900,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-bed","name":"Storage queen bed","category":"interior","description":"Illustrative engineered-wood bed with storage.","price":2199900,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-light","name":"Warm LED pendant","category":"interior","description":"Illustrative warm ambient lighting.","price":349900,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-catering","name":"Vegetarian buffet service","category":"event","description":"Illustrative per-guest catering entry.","price":65000,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-decor","name":"Minimal floral decor","category":"event","description":"Illustrative decor package.","price":1850000,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-earrings","name":"Gold-tone drop earrings","category":"jewelry","description":"Illustrative festive accessory.","price":249900,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
 {"id":"sample-necklace","name":"Pearl accent necklace","category":"jewelry","description":"Illustrative classic necklace option.","price":579900,"currency":"INR","merchant":"Sample catalog","availability":"Illustrative only","source":"illustrative"},
]

def find_products(query: str = "", category: str = "") -> list[dict[str, Any]]:
    tokens = query.lower().split()
    return [p for p in CATALOG if (not category or p["category"] == category) and all(t in (p["name"]+p["description"]).lower() for t in tokens)]

def rank_products(category: str, budget: int) -> list[dict[str, Any]]:
    items = [p for p in find_products(category=category) if p["price"] <= budget]
    return sorted(items, key=lambda p: p["price"])

def generate_required_items(planner_type: str, categories: list[dict[str, Any]], preferences: dict[str, Any]) -> list[dict[str, str]]:
    """Create an editable, price-free checklist from the user's supplied context.

    This is intentionally rule based: it does not pretend that a generated item is
    a live product or assign an invented price to it.
    """
    context = " ".join(str(value).lower() for category in categories for value in [category.get("name", ""), *[item.get("name", "") for item in category.get("items", [])]])
    context += " " + " ".join(str(value).lower() for value in preferences.values())
    if planner_type == "interior":
        recipes = [
            ("living", "Living room", ["Sofa", "Coffee table", "Lighting", "Curtains"]),
            ("bed", "Bedroom", ["Bed", "Mattress", "Wardrobe", "Bedside lighting"]),
            ("kitchen", "Kitchen", ["Cooktop", "Essential cookware", "Storage organizers", "Task lighting"]),
        ]
    elif planner_type == "event":
        recipes = [("", "Event essentials", ["Venue", "Catering", "Decorations", "Photography", "Invitations", "Transportation", "Contingency"])]
        if "wedding" in context: recipes[0] = ("", "Wedding essentials", ["Venue", "Catering", "Decorations", "Photography", "Invitations", "Guest transport", "Contingency"])
        elif "corporate" in context: recipes[0] = ("", "Corporate event essentials", ["Venue", "Catering", "AV equipment", "Signage", "Photography", "Guest transport", "Contingency"])
    else:
        requested_type = str(preferences.get("jewelryType", "")).strip()
        pieces = [requested_type] if requested_type else ["Earrings", "Necklace", "Bracelet or bangle"]
        recipes = [("", "Jewelry shortlist", pieces + ["Jewelry storage or care cloth"])]
    existing = {str(item.get("name", "")).strip().lower() for category in categories for item in category.get("items", [])}
    suggestions: list[dict[str, str]] = []
    for trigger, category, items in recipes:
        if trigger and trigger not in context: continue
        for item in items:
            if item.lower() not in existing:
                suggestions.append({"category": category, "name": item, "reason": "Suggested from your planner details; add a price only when you have one."})
    return suggestions[:12]
