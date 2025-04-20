import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
# Paste your working manual TX hash here (or set MANUAL_TX_HASH in Heroku config)
MANUAL_TX_HASH = os.getenv("MANUAL_TX_HASH", "0x7acec5325e7254660abbaa3850e46f05c3f6a06136cd9592f4b3d1ad0b1286a1")

if not MANUAL_TX_HASH.startswith("0x"):
    raise RuntimeError("Set MANUAL_TX_HASH to your proven Odos swap TX hash")

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

def buy_heresy():
    # fetch your manual-swap transaction
    orig = w3.eth.get_transaction(MANUAL_TX_HASH)

    # replay exactly the same call
    tx = {
        "to":        orig["to"],
        "from":      acct.address,
        "data":      orig["input"],
        "value":     orig["value"],
        "gas":       700_000,
        "gasPrice":  w3.eth.gas_price,
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   43114
    }

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
