import pytest
from unittest.mock import MagicMock, patch
from bot.client import BinanceFuturesClient, BinanceAPIError, BinanceNetworkError, BinanceAuthError

@pytest.fixture
def mock_client():
    # Initialize client with mock keys
    return BinanceFuturesClient(api_key="mock_key", api_secret="mock_secret")

def test_signature_generation(mock_client):
    params = {"symbol": "BTCUSDT", "side": "BUY", "timestamp": 1578302302302}
    signature = mock_client._sign_payload(params)
    
    # Expected signature hash using SHA256 of:
    # "symbol=BTCUSDT&side=BUY&timestamp=1578302302302" with key "mock_secret"
    # Let's verify it matches the format of hex digest (64 chars)
    assert len(signature) == 64
    assert all(c in "0123456789abcdef" for c in signature)

@patch("requests.Session.get")
def test_sync_server_time(mock_get, mock_client):
    # Setup mock response for /fapi/v1/time
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"serverTime": 1700000000000}
    mock_get.return_value = mock_response
    
    offset = mock_client.sync_server_time()
    
    assert mock_client.time_offset_ms != 0
    assert isinstance(offset, int)

@patch("requests.Session.get")
def test_ping_success(mock_get, mock_client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    assert mock_client.ping() is True

import requests

@patch("requests.Session.get")
def test_ping_failure(mock_get, mock_client):
    mock_get.side_effect = requests.RequestException("Connection error")
    assert mock_client.ping() is False

@patch("requests.Session.post")
def test_place_market_order_success(mock_post, mock_client):
    # Mock order success response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "orderId": 12345678,
        "symbol": "BTCUSDT",
        "status": "FILLED",
        "clientOrderId": "my_order_123",
        "price": "0.0",
        "avgPrice": "90000.5",
        "origQty": "0.001",
        "executedQty": "0.001",
        "side": "BUY",
        "type": "MARKET"
    }
    mock_post.return_value = mock_response
    
    # Place order
    result = mock_client.place_order(
        symbol="BTCUSDT",
        side="BUY",
        order_type="MARKET",
        quantity=0.001
    )
    
    assert result["orderId"] == 12345678
    assert result["status"] == "FILLED"
    assert result["executedQty"] == "0.001"
    assert result["avgPrice"] == "90000.5"

@patch("requests.Session.post")
def test_place_order_api_error(mock_post, mock_client):
    # Mock order failed response from Binance (e.g. insufficient balance)
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {
        "code": -2019,
        "msg": "Margin is insufficient."
    }
    mock_response.text = '{"code": -2019, "msg": "Margin is insufficient."}'
    mock_post.return_value = mock_response
    
    with pytest.raises(BinanceAPIError) as exc_info:
        mock_client.place_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.001
        )
        
    assert exc_info.value.code == -2019
    assert "Margin is insufficient" in exc_info.value.message
