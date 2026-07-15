import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    validate_order_inputs
)

def test_validate_symbol():
    assert validate_symbol("BTCUSDT") == "BTCUSDT"
    assert validate_symbol("ethusdt") == "ETHUSDT"
    assert validate_symbol(" BTC-USDT ") == "BTC-USDT"
    
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        validate_symbol("")
    with pytest.raises(ValueError, match="Invalid symbol format"):
        validate_symbol("A")
    with pytest.raises(ValueError, match="Invalid symbol format"):
        validate_symbol("BTCUSDT_LONG_NAME_TEST")

def test_validate_side():
    assert validate_side("BUY") == "BUY"
    assert validate_side("sell") == "SELL"
    assert validate_side(" Buy ") == "BUY"
    
    with pytest.raises(ValueError, match="Side cannot be empty"):
        validate_side("")
    with pytest.raises(ValueError, match="Invalid side"):
        validate_side("HOLD")

def test_validate_order_type():
    assert validate_order_type("MARKET") == "MARKET"
    assert validate_order_type("limit") == "LIMIT"
    assert validate_order_type("stop_market") == "STOP_MARKET"
    
    with pytest.raises(ValueError, match="Order type cannot be empty"):
        validate_order_type("")
    with pytest.raises(ValueError, match="Invalid order type"):
        validate_order_type("TRAILING_STOP")

def test_validate_quantity():
    assert validate_quantity(0.001) == 0.001
    assert validate_quantity("0.05") == 0.05
    assert validate_quantity(10) == 10.0
    
    with pytest.raises(ValueError, match="must be a numeric value"):
        validate_quantity("abc")
    with pytest.raises(ValueError, match="must be greater than zero"):
        validate_quantity(-0.5)
    with pytest.raises(ValueError, match="must be greater than zero"):
        validate_quantity(0)

def test_validate_price():
    assert validate_price(None, required=False) is None
    assert validate_price("", required=False) is None
    assert validate_price(100.5, required=False) == 100.5
    assert validate_price("99.9", required=True) == 99.9
    
    with pytest.raises(ValueError, match="Price is required for LIMIT orders"):
        validate_price(None, required=True)
    with pytest.raises(ValueError, match="Price must be a numeric value"):
        validate_price("cheap", required=False)
    with pytest.raises(ValueError, match="Price must be greater than zero"):
        validate_price(-1, required=False)

def test_validate_stop_price():
    assert validate_stop_price(None, required=False) is None
    assert validate_stop_price("", required=False) is None
    assert validate_stop_price(50.0, required=False) == 50.0
    assert validate_stop_price("12.5", required=True) == 12.5
    
    with pytest.raises(ValueError, match="Stop price is required for STOP_MARKET orders"):
        validate_stop_price(None, required=True)
    with pytest.raises(ValueError, match="Stop price must be a numeric value"):
        validate_stop_price("invalid", required=False)
    with pytest.raises(ValueError, match="Stop price must be greater than zero"):
        validate_stop_price(0, required=False)

def test_validate_order_inputs_success():
    res = validate_order_inputs("BTCUSDT", "BUY", "LIMIT", 0.01, price=95000)
    assert res["symbol"] == "BTCUSDT"
    assert res["side"] == "BUY"
    assert res["type"] == "LIMIT"
    assert res["quantity"] == 0.01
    assert res["price"] == 95000.0
    assert res["stop_price"] is None

def test_validate_order_inputs_failure():
    # Price missing for LIMIT
    with pytest.raises(ValueError, match="Price is required for LIMIT orders"):
        validate_order_inputs("BTCUSDT", "BUY", "LIMIT", 0.01, price=None)
        
    # Stop price missing for STOP_MARKET
    with pytest.raises(ValueError, match="Stop price is required for STOP_MARKET orders"):
        validate_order_inputs("BTCUSDT", "BUY", "STOP_MARKET", 0.01, stop_price=None)
