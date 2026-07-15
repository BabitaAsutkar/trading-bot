import logging
from typing import Dict, Any, Optional
from bot.client import BinanceFuturesClient
from bot.validators import validate_order_inputs

logger = logging.getLogger("trading_bot.orders")

class OrderManager:
    """
    Orchestration layer that handles input validation, time sync,
    and calls the Binance client to place orders.
    """
    def __init__(self, api_key: str, api_secret: str):
        self.client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    def execute_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Validates parameters, synchronizes time, and places the order via client.
        
        Returns:
            Dict containing order response details.
        """
        # Step 1: Pre-flight Validation
        logger.debug("Validating order parameters...")
        validated = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        logger.info(
            "Validation passed for %s %s order on %s. Qty: %s",
            validated["side"],
            validated["type"],
            validated["symbol"],
            validated["quantity"]
        )

        # Step 2: Ensure client time is in sync before placing the order
        self.client.sync_server_time()

        # Step 3: Place order
        logger.info("Sending order placement request to Binance...")
        response = self.client.place_order(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"],
            time_in_force=time_in_force
        )

        # Step 4: Extract structured outcome details
        # For average price, Binance Futures returns 'avgPrice' in the response.
        # If it's 0.0 (e.g. limit orders that haven't filled), we report it accordingly.
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", "0")
        avg_price = response.get("avgPrice")
        
        # Fallback to price if avgPrice is not available or 0.0 (for unexecuted LIMIT)
        if not avg_price or float(avg_price) == 0.0:
            avg_price = response.get("price", "N/A")

        logger.info("Order placed successfully. ID: %s, Status: %s", order_id, status)
        
        return {
            "orderId": order_id,
            "status": status,
            "executedQty": executed_qty,
            "avgPrice": avg_price,
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "raw_response": response
        }
