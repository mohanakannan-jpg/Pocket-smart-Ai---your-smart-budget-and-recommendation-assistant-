from app.products import generate_required_items

def test_interior_items_follow_room_data():
    items=generate_required_items("interior", [{"name":"Living room","items":[{"name":"Sofa"}]}], {"style":"Modern"})
    assert {item["name"] for item in items} >= {"Coffee table", "Lighting", "Curtains"}
    assert "Bed" not in {item["name"] for item in items}

def test_jewelry_type_becomes_checklist_item():
    items=generate_required_items("jewelry", [], {"jewelryType":"Ring"})
    assert any(item["name"] == "Ring" for item in items)
