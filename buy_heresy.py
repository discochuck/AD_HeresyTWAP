import os
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
CHAIN_ID       = 43114
AMOUNT         = Web3.to_wei(0.25, "ether")  # 0.25 AVAX

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def fetch_0x_quote():
    url = "https://api.0x.org/swap/v1/quote"
    params = {
        "sellToken":    "AVAX",            # native Avalanche
        "buyToken":     HERESY_ADDRESS,    # your token
        "sellAmount":   str(AMOUNT),
        "slippagePercentage": 0.01         # 1% max slippage
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

def buy_heresy():
    quote = fetch_0x_quote()
    # quote contains: to, data, value, gas, gasPrice
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

if __name__ == "__main__":
    buy_heresy()
