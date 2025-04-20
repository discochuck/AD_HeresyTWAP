import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL     = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
# This is your wrapper that swaps for you when it receives AVAX
WRAPPER     = Web3.to_checksum_address("0x22C81c051a134c81Ce370D82Fa26975aE9D100B4")

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def buy_heresy():
    amount    = w3.to_wei(0.25, "ether")
    nonce     = w3.eth.get_transaction_count(acct.address, "pending")
    gas_price = w3.eth.gas_price

    # Plain AVAX transfer to your wrapper's fallback
    tx = {
        "to":       WRAPPER,
        "from":     acct.address,
        "value":    amount,
        "gas":      500_000,
        "gasPrice": gas_price,
        "nonce":    nonce,
        "chainId":  43114
    }

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
