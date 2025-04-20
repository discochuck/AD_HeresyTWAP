import os
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
ZEROX_KEY      = os.getenv("ZEROX_API_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))
CHAIN_ID       = 43114
AMOUNT         = Web3.to_wei(0.25, "ether")  # 0.25 AVAX

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def fetch_0x_quote():
    url     = "https://api.0x.org/swap/v2/quote"
    params  = {
        "sellToken":          "AVAX",
        "buyToken":           HERESY_ADDRESS,
        "sellAmount":         str(AMOUNT),
        "slippagePercentage": 0.01,
        "takerAddress":       acct.address
    }
    headers = {
        "0x-api-key": ZEROX_KEY,
        "Accept":     "application/json"
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def buy_heresy():
    q    = fetch_0x_quote()
    tx   = {
        "to":        q["to"],
        "from":      acct.address,
        "data":      q["data"],
        "value":     int(q.get("value", 0)),
        "gas":       int(q["gas"]),
        "gasPrice":  int(q["gasPrice"]),
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   CHAIN_ID
    }
    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
