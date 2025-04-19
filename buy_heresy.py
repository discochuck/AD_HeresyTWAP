import os
from web3 import Web3
from dotenv import load_dotenv

# ── ENV & WEB3 SETUP ──────────────────────────────────────────────────────────
load_dotenv()
w3   = Web3(Web3.HTTPProvider(os.getenv("AVAX_RPC_URL")))
acct = w3.eth.account.from_key(os.getenv("BOT_PRIVATE_KEY"))

HERESY     = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
ROUTER     = Web3.to_checksum_address(os.getenv("PHARAOH_ROUTER"))
WAVAX      = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))

# ── ABI FOR swapExactAVAXForTokens ────────────────────────────────────────────
SWAP_NATIVE_ABI = [{
    "inputs":[
      {"name":"amountOutMin","type":"uint256"},
      {"name":"path","type":"address[]"},
      {"name":"to","type":"address"},
      {"name":"deadline","type":"uint256"}
    ],
    "name":"swapExactAVAXForTokens",
    "outputs":[{"name":"amounts","type":"uint256[]"}],
    "stateMutability":"payable",
    "type":"function"
}]
router = w3.eth.contract(address=ROUTER, abi=SWAP_NATIVE_ABI)

def buy_heresy():
    amount   = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    tx = router.functions.swapExactAVAXForTokens(
        0,                # accept any amountOut
        [WAVAX, HERESY],  # path: native AVAX → HERESY
        acct.address,     # recipient
        deadline
    ).build_transaction({
        "from": acct.address,
        "value": amount,
        "gas":   350_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
