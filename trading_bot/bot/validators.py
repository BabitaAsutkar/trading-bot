import re
from typing import Optional, Dict, Any

def validate_symbol(symbol: str) -> str:
    """
    Validates a trading symbol (e.g., BTCUSDT).
    Must be uppercase alphanumeric, between 3 and 15 characters.
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    
    symbol_upper = symbol.strip().upper()
    # General regex matching USDT-M and COIN-M symbol naming conventions
    if not re.match(r"^[A-Z0-9-]{3,15}$", symbol_upper):
        raise ValueError(
            f"Invalid symbol format: '{symbol}'. "
            "Must be alphanumeric, uppercase (e.g., BTCUSDT, ETHUSDT)."
        )
    return symbol_upper

def validate_side(side: str) -> str:
    """
    Validates trade side. Must be BUY or SELL.
    """
    if not side:
        raise ValueError("Side cannot be empty.")
    
    side_upper = side.strip().upper()
    if side_upper not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side: '{side}'. Must be 'BUY' or 'SELL'.")
    return side_upper

def validate_order_type(order_type: str) -> str:
    """
    Validates order type. Must be MARKET, LIMIT, or STOP_MARKET.
    """
    if not order_type:
        raise ValueError("Order type cannot be empty.")
    
    type_upper = order_type.strip().upper()
    valid_types = ("MARKET", "LIMIT", "STOP_MARKET")
    if type_upper not in valid_types:
        raise ValueError(f"Invalid order type: '{order_type}'. Must be one of {valid_types}.")
    return type_upper

def validate_quantity(quantity: Any) -> float:
    """
    Validates quantity. Must be a positive number.
    """
    try:
        qty_val = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a numeric value, got: '{quantity}'.")
    
    if qty_val <= 0:
        raise ValueError(f"Quantity must be greater than zero, got: {qty_val}.")
    return qty_val

def validate_price(price: Any, required: bool = False) -> Optional[float]:
    """
    Validates price. Must be a positive number if provided or required.
    """
    if price is None or str(price).strip() == "":
        if required:
            raise ValueError("Price is required for LIMIT orders.")
        return None

    try:
        price_val = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price must be a numeric value, got: '{price}'.")
    
    if price_val <= 0:
        raise ValueError(f"Price must be greater than zero, got: {price_val}.")
    return price_val

def validate_stop_price(stop_price: Any, required: bool = False) -> Optional[float]:
    """
    Validates stop price. Must be a positive number if provided or required.
    """
    if stop_price is None or str(stop_price).strip() == "":
        if required:
            raise ValueError("Stop price is required for STOP_MARKET orders.")
        return None

    try:
        stop_price_val = float(stop_price)
    except (TypeError, ValueError):
        raise ValueError(f"Stop price must be a numeric value, got: '{stop_price}'.")
    
    if stop_price_val <= 0:
        raise ValueError(f"Stop price must be greater than zero, got: {stop_price_val}.")
    return stop_price_val

def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: Any,
    price: Optional[Any] = None,
    stop_price: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Orchestrates the validation of all order parameters.
    Returns a dictionary of cleaned/validated values or raises ValueError.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    
    # LIMIT orders require price
    price_required = (validated_type == "LIMIT")
    validated_price = validate_price(price, required=price_required)
    
    # STOP_MARKET orders require stop price
    stop_price_required = (validated_type == "STOP_MARKET")
    validated_stop_price = validate_stop_price(stop_price, required=stop_price_required)
    
    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "type": validated_type,
        "quantity": validated_quantity,
        "price": validated_price,
        "stop_price": validated_stop_price
    }
