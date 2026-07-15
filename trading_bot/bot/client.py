import hmac
import hashlib
import time
import urllib.parse
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger("trading_bot.client")

class BinanceError(Exception):
    """Base exception for all Binance Client errors."""
    pass

class BinanceNetworkError(BinanceError):
    """Raised when there is a network-level issue (connection, timeout, DNS)."""
    pass

class BinanceAPIError(BinanceError):
    """Raised when Binance returns a non-success response with an error code and message."""
    def __init__(self, status_code: int, code: int, message: str, response_body: str):
        super().__init__(f"Binance API Error: HTTP {status_code} | Code {code}: {message}")
        self.status_code = status_code
        self.code = code
        self.message = message
        self.response_body = response_body

class BinanceAuthError(BinanceError):
    """Raised when API credentials are missing, invalid, or signature fails."""
    pass

class BinanceFuturesClient:
    """
    Lightweight, robust Python client for the Binance Futures Testnet (USDT-M).
    Handles authentication, query signing, time synchronization, and HTTP requests.
    """
    BASE_URL = "https://testnet.binancefuture.com"

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
        # Configure headers
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "AntigravityBinanceTradingBot/1.0"
        })
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})
            
        self.time_offset_ms = 0
        logger.debug("Binance Futures Client initialized.")

    def sync_server_time(self) -> int:
        """
        Fetches the current Binance server time and calculates local clock offset.
        This mitigates 'Timestamp for this request is outside of the recvWindow' errors.
        """
        logger.debug("Syncing server time with Binance Futures...")
        try:
            url = f"{self.BASE_URL}/fapi/v1/time"
            start_local_ms = int(time.time() * 1000)
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                raise BinanceNetworkError(f"Failed to fetch server time: HTTP {response.status_code}")
                
            server_time_ms = response.json()["serverTime"]
            end_local_ms = int(time.time() * 1000)
            
            # Account for roundtrip latency (approximate)
            latency = (end_local_ms - start_local_ms) // 2
            local_time_ms = end_local_ms - latency
            
            self.time_offset_ms = server_time_ms - local_time_ms
            logger.info("Time synchronized. Offset: %d ms, Network Latency: %d ms", self.time_offset_ms, latency)
            return self.time_offset_ms
        except requests.RequestException as e:
            logger.error("Failed to sync server time due to network error: %s", str(e))
            raise BinanceNetworkError(f"Network error syncing server time: {e}")

    def ping(self) -> bool:
        """
        Pings the Binance Futures Testnet to verify connectivity.
        """
        try:
            url = f"{self.BASE_URL}/fapi/v1/ping"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error("Ping failed: %s", str(e))
            return False

    def _sign_payload(self, params: Dict[str, Any]) -> str:
        """
        Generates HMAC-SHA256 signature of the query string using the API Secret.
        """
        if not self.api_secret:
            raise BinanceAuthError("API Secret is required for signing requests but was not provided.")
            
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature

    def _request(self, method: str, endpoint: str, signed: bool = False, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Constructs and sends requests to the Binance Futures Testnet, handling signing and errors.
        """
        url = f"{self.BASE_URL}{endpoint}"
        req_params = params.copy() if params else {}

        if signed:
            if not self.api_key or not self.api_secret:
                raise BinanceAuthError("API Key and Secret must be provided for signed requests.")
            
            # Include synced timestamp
            current_local_ms = int(time.time() * 1000)
            req_params["timestamp"] = current_local_ms + self.time_offset_ms
            req_params["recvWindow"] = 6000  # standard recvWindow
            
            # Sign parameters
            signature = self._sign_payload(req_params)
            req_params["signature"] = signature

        # Log the request (redacting API Key for security if it was in params, though it's typically in the header)
        log_params = req_params.copy()
        if "signature" in log_params:
            log_params["signature"] = "[REDACTED]"
            
        logger.info("HTTP Request: %s %s | Params: %s", method, endpoint, log_params)

        try:
            if method.upper() == "POST":
                response = self.session.post(url, data=req_params, timeout=15)
            elif method.upper() == "GET":
                response = self.session.get(url, params=req_params, timeout=15)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=req_params, timeout=15)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_body = response.text
            
            # Log response summary
            logger.info("HTTP Response: Status %d | Body: %s", response.status_code, response_body[:200])

            if response.status_code == 200:
                return response.json()
            else:
                # Attempt to parse standard Binance error code/msg JSON
                try:
                    err_json = response.json()
                    err_code = err_json.get("code", 0)
                    err_msg = err_json.get("msg", "Unknown error")
                except ValueError:
                    err_code = -1
                    err_msg = "Could not parse JSON response"
                
                raise BinanceAPIError(
                    status_code=response.status_code,
                    code=err_code,
                    message=err_msg,
                    response_body=response_body
                )
        except requests.Timeout as e:
            logger.error("Request timed out: %s %s", method, endpoint)
            raise BinanceNetworkError(f"Request timeout contacting Binance: {e}")
        except requests.RequestException as e:
            logger.error("Request failed: %s %s | Error: %s", method, endpoint, str(e))
            raise BinanceNetworkError(f"Network error contacting Binance: {e}")

    def place_order(
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
        Sends an order placement request to Binance Futures.
        """
        endpoint = "/fapi/v1/order"
        
        # Base parameters
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(quantity),
        }

        # Handle specific order type requirements
        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = str(price)
            params["timeInForce"] = time_in_force
        elif order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("Stop price is required for STOP_MARKET orders.")
            params["stopPrice"] = str(stop_price)

        return self._request(method="POST", endpoint=endpoint, signed=True, params=params)
