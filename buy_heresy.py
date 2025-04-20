import os
import json
import requests
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL     = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
HERESY      = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
AMOUNT      = Web3.to_wei(0.25, "ether")
CHAIN_ID    = 43114

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# Odos Multichain Router on Avalanche
ODOS_ROUTER = "0xEd2671f64be0F5f58e6F0FF5bad575c168f16F3d"

def fetch_odos_swap():
    """Query Odos API for the best route AVAX→HERESY."""
    url = "https://api.odos.xyz/v1/route"
    params = {
        "chainId": CHAIN_ID,
        "inToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # native AVAX
        "outToken": HERESY,
        "inAmount": str(AMOUNT),
        "slippage": "100"  # i.e. 1.00%
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError("Odos route lookup failed: " + json.dumps(data))
    return data["swapData"]  # this is the encoded calldata

def buy_heresy():
    swap_data = fetch_odos_swap()
    nonce     = w3.eth.get_transaction_count(acct.address, "pending")
    gas_price = w3.eth.gas_price
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300

    tx = {
        "to":       ODOS_ROUTER,
        "from":     acct.address,
        "value":    AMOUNT,
        "data":     swap_data,
        "gas":      700_000,
        "gasPrice": gas_price,
        "nonce":    nonce,
        "chainId":  CHAIN_ID
    }

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
