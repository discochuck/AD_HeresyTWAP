import os
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL      = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY  = os.getenv("BOT_PRIVATE_KEY")
HERESY       = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
ZEROX_KEY    = os.getenv("ZEROX_API_KEY")
CHAIN_ID     = 43114
AMOUNT       = Web3.to_wei(0.25, "ether")  # 0.25 AVAX

if not ZEROX_KEY:
    raise RuntimeError("Set ZEROX_API_KEY in your Heroku config to your 0x API key.")

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def fetch_0x_quote():
    url = "https://api.0x.org/swap/v1/quote"
    params = {
        "sellToken":          "AVAX",       # native AVAX
        "buyToken":           HERESY,
        "sellAmount":         str(AMOUNT),
        "slippagePercentage": 0.01          # 1% slippage tolerance
    }
    headers = {
        "0x-api-key": ZEROX_KEY,
        "Accept":     "application/json"
    }
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.json()

def buy_heresy():
    quote = fetch_0x_quote()
    # Build the tx exactly as 0x returned it
    tx = {
        "to":        quote["to"],
        "from":      acct.address,
        "data":      quote["data"],
        "value":     int(quote.get("value", 0)),
        "gas":       int(quote["gas"]),
        "gasPrice":  int(quote["gasPrice"]),
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   CHAIN_ID
    }

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
