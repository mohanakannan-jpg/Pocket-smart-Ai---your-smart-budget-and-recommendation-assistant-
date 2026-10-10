from decimal import Decimal, ROUND_HALF_UP
from typing import Any

def money(value: Any) -> int:
    """Convert a user amount in major currency units to integer paise/cents."""
    try:
        amount = Decimal(str(value))
    except Exception as exc:
        raise ValueError("Amount must be numeric") from exc
    if amount < 0:
        raise ValueError("Amounts cannot be negative")
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def calculate_plan(budget: int, categories: list[dict[str, Any]]) -> dict[str, Any]:
    if budget < 0:
        raise ValueError("Budget cannot be negative")
    estimated = verified = 0
    unpriced: list[str] = []
    category_summaries = []
    for category in categories:
        subtotal = category_verified = 0
        unknown = 0
        for item in category.get("items", []):
            quantity = int(item.get("quantity", 1))
            if quantity < 1 or quantity > 10000:
                raise ValueError("Quantity must be between 1 and 10,000")
            price = item.get("price")
            if price is None or price == "":
                unknown += 1
                unpriced.append(str(item.get("name", "Unnamed item")))
                continue
            item_cost = money(price) * quantity
            subtotal += item_cost
            if item.get("priceSource") == "verified": category_verified += item_cost
        estimated += subtotal
        verified += category_verified
        category_summaries.append({"name": category.get("name", "Uncategorized"), "total": subtotal, "unpricedItems": unknown})
    remaining = budget - estimated
    return {
        "budget": budget, "estimatedTotal": estimated, "verifiedTotal": verified,
        "illustrativeTotal": estimated - verified, "remaining": remaining,
        "overBudget": max(0, -remaining),
        "utilization": round((estimated / budget * 100), 1) if budget else (0 if not estimated else 100),
        "categories": category_summaries, "unpricedItems": unpriced,
    }
