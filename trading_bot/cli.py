import os
import sys
import argparse
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add current directory to path to ensure modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.orders import OrderManager
from bot.client import BinanceError, BinanceAPIError, BinanceNetworkError, BinanceAuthError
from bot.validators import validate_order_inputs

# ANSI color codes for premium CLI interface
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

# Initialize logging (defaulting to trading_bot.log)
logger = setup_logging()

def print_banner():
    """Prints a premium welcome banner for the Trading Bot CLI."""
    banner = f"""
{COLOR_CYAN}{COLOR_BOLD}=============================================================
 🚀 BINANCE FUTURES TESTNET TRADING BOT v1.0
============================================================={COLOR_RESET}
    """
    print(banner)

def print_success(message: str):
    print(f"\n{COLOR_GREEN}{COLOR_BOLD}✔ SUCCESS: {message}{COLOR_RESET}")

def print_error(message: str):
    print(f"\n{COLOR_RED}{COLOR_BOLD}✘ ERROR: {message}{COLOR_RESET}", file=sys.stderr)

def print_warning(message: str):
    print(f"\n{COLOR_YELLOW}{COLOR_BOLD}⚠ WARNING: {message}{COLOR_RESET}")

def format_order_summary(params: Dict[str, Any]):
    """Formats a clean visual summary of the order request."""
    print(f"\n{COLOR_BOLD}--- Order Request Summary ---{COLOR_RESET}")
    print(f"  {COLOR_CYAN}Symbol:{COLOR_RESET}     {params['symbol']}")
    print(f"  {COLOR_CYAN}Side:{COLOR_RESET}       {params['side']}")
    print(f"  {COLOR_CYAN}Type:{COLOR_RESET}       {params['type']}")
    print(f"  {COLOR_CYAN}Quantity:{COLOR_RESET}   {params['quantity']}")
    if params.get("price"):
        print(f"  {COLOR_CYAN}Price:{COLOR_RESET}      {params['price']}")
    if params.get("stop_price"):
        print(f"  {COLOR_CYAN}Stop Price:{COLOR_RESET} {params['stop_price']}")
    print("-----------------------------")

def format_order_response(result: Dict[str, Any]):
    """Formats the order response details beautifully."""
    print(f"\n{COLOR_GREEN}{COLOR_BOLD}============================================================={COLOR_RESET}")
    print(f"🎉 {COLOR_GREEN}{COLOR_BOLD}ORDER PLACED SUCCESSFULLY{COLOR_RESET}")
    print(f"{COLOR_GREEN}{COLOR_BOLD}============================================================={COLOR_RESET}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Order ID:{COLOR_RESET}      {result['orderId']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Status:{COLOR_RESET}        {result['status']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Executed Qty:{COLOR_RESET}  {result['executedQty']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Avg Price:{COLOR_RESET}     {result['avgPrice']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Symbol:{COLOR_RESET}        {result['symbol']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Side:{COLOR_RESET}          {result['side']}")
    print(f"  {COLOR_CYAN}{COLOR_BOLD}Type:{COLOR_RESET}          {result['type']}")
    print(f"{COLOR_GREEN}============================================================={COLOR_RESET}")

def load_credentials() -> tuple[Optional[str], Optional[str]]:
    """Loads credentials from .env file or environment, otherwise prompts the user."""
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    return api_key, api_secret

def run_interactive_wizard() -> Dict[str, Any]:
    """Runs a premium interactive CLI wizard to capture validated order details."""
    print_banner()
    print(f"{COLOR_BOLD}Interactive Order Configuration Wizard{COLOR_RESET}")
    print("Please follow the prompts to configure your order.\n")

    # 1. Symbol Input
    while True:
        try:
            symbol_raw = input(f"Enter Symbol {COLOR_CYAN}[e.g. BTCUSDT, default: BTCUSDT]{COLOR_RESET}: ").strip()
            symbol = symbol_raw.upper() if symbol_raw else "BTCUSDT"
            # Validate immediately
            from bot.validators import validate_symbol
            validate_symbol(symbol)
            break
        except ValueError as e:
            print_error(str(e))

    # 2. Side Input
    while True:
        side = input(f"Enter Side {COLOR_CYAN}[BUY / SELL, default: BUY]{COLOR_RESET}: ").strip().upper()
        if not side:
            side = "BUY"
        if side in ("BUY", "SELL"):
            break
        print_error("Invalid side. Must be 'BUY' or 'SELL'.")

    # 3. Order Type Input
    while True:
        type_choice = input(f"Enter Order Type {COLOR_CYAN}[MARKET / LIMIT / STOP_MARKET, default: MARKET]{COLOR_RESET}: ").strip().upper()
        if not type_choice:
            type_choice = "MARKET"
        if type_choice in ("MARKET", "LIMIT", "STOP_MARKET"):
            break
        print_error("Invalid type. Must be 'MARKET', 'LIMIT', or 'STOP_MARKET'.")

    # 4. Quantity Input
    while True:
        try:
            qty_raw = input(f"Enter Quantity {COLOR_CYAN}[e.g. 0.001]{COLOR_RESET}: ").strip()
            from bot.validators import validate_quantity
            quantity = validate_quantity(qty_raw)
            break
        except ValueError as e:
            print_error(str(e))

    # 5. Price Input (LIMIT only)
    price = None
    if type_choice == "LIMIT":
        while True:
            try:
                price_raw = input(f"Enter Price {COLOR_CYAN}[e.g. 95000]{COLOR_RESET}: ").strip()
                from bot.validators import validate_price
                price = validate_price(price_raw, required=True)
                break
            except ValueError as e:
                print_error(str(e))

    # 6. Stop Price Input (STOP_MARKET only)
    stop_price = None
    if type_choice == "STOP_MARKET":
        while True:
            try:
                stop_price_raw = input(f"Enter Stop Price {COLOR_CYAN}[e.g. 90000]{COLOR_RESET}: ").strip()
                from bot.validators import validate_stop_price
                stop_price = validate_stop_price(stop_price_raw, required=True)
                break
            except ValueError as e:
                print_error(str(e))

    # Review & Confirmation
    order_params = {
        "symbol": symbol,
        "side": side,
        "type": type_choice,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price
    }
    
    format_order_summary(order_params)
    
    confirm = input(f"\nDo you want to execute this order? {COLOR_YELLOW}[y/N]{COLOR_RESET}: ").strip().lower()
    if confirm not in ("y", "yes"):
        print_warning("Order execution cancelled by user.")
        sys.exit(0)
        
    return order_params

def main():
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet (USDT-M) Trading Bot CLI tool.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g. BTCUSDT, ETHUSDT)")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="Order side (BUY or SELL)")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT", "STOP_MARKET"], help="Order type")
    parser.add_argument("--quantity", type=float, help="Order quantity")
    parser.add_argument("--price", type=float, help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", type=float, help="Stop price (required for STOP_MARKET orders)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Force interactive wizard mode")

    args = parser.parse_args()

    # Load and check API Credentials
    api_key, api_secret = load_credentials()

    # If key/secret are missing, prompt user for them interactively
    if not api_key or not api_secret:
        print_banner()
        print_warning("Binance API credentials not found in .env file.")
        print("Please enter them now (they will be used for this session only and NOT saved to disk):")
        if not api_key:
            api_key = input("Enter Binance Testnet API Key: ").strip()
        if not api_secret:
            api_secret = input("Enter Binance Testnet API Secret: ").strip()
        
        if not api_key or not api_secret:
            print_error("Credentials cannot be empty. Exiting.")
            sys.exit(1)

    # Determine if we should run in interactive mode:
    # Trigger interactive if explicitly requested OR if no command line arguments are provided
    is_interactive = args.interactive or (
        args.symbol is None and
        args.side is None and
        args.type is None and
        args.quantity is None
    )

    if is_interactive:
        order_params = run_interactive_wizard()
    else:
        # Validate arguments using helper validator layer
        try:
            order_params = validate_order_inputs(
                symbol=args.symbol,
                side=args.side,
                order_type=args.type,
                quantity=args.quantity,
                price=args.price,
                stop_price=args.stop_price
            )
            format_order_summary(order_params)
        except ValueError as e:
            print_error(f"Input validation failed: {e}")
            sys.exit(1)

    # Execute the order using OrderManager
    try:
        manager = OrderManager(api_key=api_key, api_secret=api_secret)
        
        # Test connection first
        print(f"\n🔄 Connecting to Binance Futures Testnet...")
        if not manager.client.ping():
            print_error("Failed to ping Binance Futures Testnet. Please check your internet connection.")
            sys.exit(1)
        
        print(f"🟢 Connected. Placing order...")
        result = manager.execute_order(
            symbol=order_params["symbol"],
            side=order_params["side"],
            order_type=order_params["type"],
            quantity=order_params["quantity"],
            price=order_params["price"],
            stop_price=order_params["stop_price"]
        )
        
        # Print output details
        format_order_response(result)
        print_success("Order placement workflow completed.")
        
    except BinanceAPIError as e:
        print_error(f"Binance API returned error {e.code}: {e.message}")
        logger.error("Binance API error: %s", str(e))
        sys.exit(1)
    except BinanceNetworkError as e:
        print_error(f"Network error: {e}")
        logger.error("Network error: %s", str(e))
        sys.exit(1)
    except BinanceAuthError as e:
        print_error(f"Authentication error: {e}")
        logger.error("Authentication error: %s", str(e))
        sys.exit(1)
    except BinanceError as e:
        print_error(f"Binance exception: {e}")
        logger.error("Binance exception: %s", str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        logger.exception("Unexpected exception occurred during CLI run")
        sys.exit(1)

if __name__ == "__main__":
    main()
