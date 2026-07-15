 Binance Futures Testnet Trading Bot

A robust, decoupled, and feature-rich Python trading bot designed to interact with the **Binance Futures Testnet (USDT-M)**. Built from scratch with modular client, logic, validation, and logging layers.

---

## 🌟 Key Features

1. **Decoupled Architecture**: Separate API/Client layer, Order orchestrator layer, and Command-Line Interface (CLI).
2. **Multiple Order Types**:
   - `MARKET` Order (BUY/SELL)
   - `LIMIT` Order (BUY/SELL, requires price)
   - `STOP_MARKET` Order (BUY/SELL, requires stop price - *Bonus Feature*)
3. **Advanced CLI UX (Bonus)**: 
   - Supports parameter inputs via traditional CLI arguments.
   - Triggers an **Interactive Setup & Order Wizard** if run without arguments or with `--interactive`.
   - Colorful CLI menus, loaders, validation checks, and confirmation banners.
   - Interactive prompt for credentials if they are missing from files.
4. **Pre-flight Validation**: Strict input validation before triggering network requests to avoid rate limits or unnecessary API errors.
5. **Robust Exception Handling**: Maps network problems, authentication failures, and custom API messages to descriptive user-facing errors.
6. **Smart Time Synchronization**: Dynamic sync with Binance server clock (`GET /fapi/v1/time`) during execution to eliminate standard `recvWindow` timing errors.
7. **Detailed Rotating Logs**: Automatically writes request details, timing offset info, and error tracebacks to `trading_bot.log` while redacting sensitive API secrets/signatures.

---

## 📂 Project Structure

```text
trading_bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py          # HTTP requests, signatures, custom errors
│   ├── logging_config.py  # File & Console Logger configuration
│   ├── orders.py          # Orchestrates validations and client calls
│   └── validators.py      # Input validation logic
│
├── ui/
│   ├── index.html         # Dashboard HTML structure
│   ├── style.css          # Space-dark premium design tokens & styling
│   └── app.js             # Form toggles, simulated endpoints, logs
│
├── tests/
│   ├── __init__.py
│   ├── test_validators.py # Unit tests for validators
│   └── test_client.py     # Unit tests for signature & API logic
│
├── .env.example           # Example API keys dotenv file
├── cli.py                 # CLI entry point (argparse & interactive mode)
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

---

## 🚀 Setup & Installation

### Prerequisite: Python 3.8+

1. **Clone or copy the directory**:
   Navigate to the project directory:
   ```bash
   cd trading_bot
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup API Credentials**:
   - Register or login to [Binance Futures Testnet](https://testnet.binancefuture.com).
   - Generate your Testnet API Key and API Secret.
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your API keys:
     ```env
     BINANCE_API_KEY=your_actual_api_key
     BINANCE_API_SECRET=your_actual_api_secret
     ```

---

## 🛠️ Usage Examples

### 1. Interactive Wizard Mode (Recommended)
Run the script without arguments or with `--interactive` / `-i`. The bot will check your `.env` credentials (prompting you if missing) and start the step-by-step order builder wizard:
```bash
python cli.py
```
*or*
```bash
python cli.py -i
```

### 2. CLI Argument Mode
For automated scripts or headless executions, specify arguments directly:

#### A. Place a MARKET BUY Order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

#### B. Place a LIMIT SELL Order:
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 4500
```

#### C. Place a STOP_MARKET SELL Order (Bonus Order Type):
```bash
python cli.py --symbol SOLUSDT --side SELL --type STOP_MARKET --quantity 1.5 --stop-price 120.5
```

### 3. Interactive Web Dashboard UI (Bonus)
A premium space-dark single page application dashboard is available for placing orders and reading live simulated API server logs interactively:
- Open [`ui/index.html`](file:///c:/Users/Shree/Desktop/Antigravity/trading_bot/ui/index.html) directly in any web browser to view, interact, and test order flow visualizations visually!

---

## 🧪 Running Unit Tests

The test suite validates input parsing, validator logic, signature calculations, and mock client actions. Run tests using `pytest`:

```bash
# Run all tests
pytest

# Run tests with output verbosity
pytest -v
```

---

## 📝 Design Assumptions & Constraints

1. **Testnet-only endpoint**: The codebase targets `https://testnet.binancefuture.com`. Production credentials from `binance.com` will not function.
2. **Leverage and Margins**: Orders are placed based on your current account margin settings (Cross/Isolated) and leverage configuration. Make sure you have sufficient collateral (testnet USDT) before running orders.
3. **Quantity and Step-Size restrictions**: Different symbols have specific minimum quantities (e.g., minimum quantity for BTCUSDT is typically 0.001). Placing an order below this quantity will fail with an API error from Binance.

