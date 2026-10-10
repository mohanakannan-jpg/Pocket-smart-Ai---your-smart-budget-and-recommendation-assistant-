from app.main import RecommendationIn, recommendations
from app.products import generate_required_items, rank_products

def test_interior_items_follow_room_data():
    items=generate_required_items("interior", [{"name":"Living room","items":[{"name":"Sofa"}]}], {"style":"Modern"})
    assert {item["name"] for item in items} >= {"Coffee table", "Lighting", "Curtains"}
    assert "Bed" not in {item["name"] for item in items}

def test_jewelry_type_becomes_checklist_item():
    items=generate_required_items("jewelry", [], {"jewelryType":"Ring"})
    assert any(item["name"] == "Ring" for item in items)

def test_product_recommendations_stay_within_available_budget():
    result = recommendations(RecommendationIn(
        plannerType="jewelry",
        budget=900000,
        categories=[{"name":"Jewelry","items":[{"name":"Ring","quantity":1,"price":5000}]}],
    ))
    assert result["calculation"]["remaining"] == 400000
    assert [product["name"] for product in result["products"]] == ["Gold-tone drop earrings"]
    assert all(product["price"] <= result["calculation"]["remaining"] for product in result["products"])

def test_no_products_recommended_when_no_budget_remains():
    result = recommendations(RecommendationIn(
        plannerType="jewelry",
        budget=250000,
        categories=[{"name":"Jewelry","items":[{"name":"Earrings","quantity":1,"price":2500}]}],
    ))
    assert result["products"] == []

def test_rank_products_excludes_items_over_budget():
    products = rank_products("interior", 400000)
    assert products
    assert all(product["price"] <= 400000 for product in products)
    assert products == sorted(products, key=lambda product: product["price"])
