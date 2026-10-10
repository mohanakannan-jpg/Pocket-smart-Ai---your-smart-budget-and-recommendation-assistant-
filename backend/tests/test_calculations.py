import pytest
from app.calculations import calculate_plan, money
def test_totals_and_over_budget():
    result=calculate_plan(10000,[{"name":"Venue","items":[{"name":"Hall","price":70,"quantity":2,"priceSource":"verified"}]}])
    assert result["estimatedTotal"] == 14000
    assert result["verifiedTotal"] == 14000
    assert result["overBudget"] == 4000
def test_unknown_prices_are_not_zero():
    result=calculate_plan(10000,[{"name":"Items","items":[{"name":"Unknown","quantity":1}]}])
    assert result["estimatedTotal"] == 0 and result["unpricedItems"] == ["Unknown"]
def test_negative_rejected():
    with pytest.raises(ValueError): money(-1)
