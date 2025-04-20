import os
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
# 1inch uses this sentinel for native AVAX
NATIVE_AVAX    = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def fetch_1inch_swap(amount_wei, slippage=1):
    """Call 1inch’s swap endpoint to get the on‑chain TX payload."""
    url    = "https://api.1inch.io/v5.0/43114/swap"
    params = {
      "fromTokenAddress": NATIVE_AVAX,
      "toTokenAddress":   HERESY_ADDRESS,
      "amount":           str(amount_wei),
      "fromAddress":      acct.address,
      "slippage":         str(slippage),    # 1 = 1%
      "disableEstimate":  "true"            # skip extra RPC calls
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "tx" not in data:
        raise RuntimeError(f"1inch API error: {data}")
    return data["tx"]    # { to, data, value, gasPrice, gas, ... }

def buy_heresy():
    amount_wei = w3.to_wei(0.25, "ether")
    swap_tx    = fetch_1inch_swap(amount_wei, slippage=1)

    # Build a transaction dict directly from 1inch’s response
    tx = {
        "to":        swap_tx["to"],
        "from":      swap_tx["from"],
        "data":      swap_tx["data"],
        "value":     int(swap_tx.get("value", 0)),
        "gas":       int(swap_tx["gas"]),
        "gasPrice":  int(swap_tx["gasPrice"]),
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   43114
    }

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
