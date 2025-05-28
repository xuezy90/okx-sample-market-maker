import os

# api key credential
API_KEY = "a134645d-747e-4d52-a5d0-36d3f1dbac21"
API_KEY_SECRET = "72761FBA1C9BFF78014F38DD32C50D89"
API_PASSPHRASE = "Xzy905097@1"
IS_PAPER_TRADING = True

# market-making instrument
TRADING_INSTRUMENT_ID = "BTC-USDT"
TRADING_MODE = "spot"  # "cash" / "isolated" / "cross"

# default latency tolerance level
ORDER_BOOK_DELAYED_SEC = 600  # Warning if OrderBook not updated for these seconds, potential issues from wss connection
ACCOUNT_DELAYED_SEC = 600  # Warning if Account not updated for these seconds, potential issues from wss connection

# risk-free ccy
RISK_FREE_CCY_LIST = ["USDT", "USDC", "DAI"]

# params yaml path
PARAMS_PATH = os.path.abspath(os.path.dirname(__file__) + "/params.yaml")
