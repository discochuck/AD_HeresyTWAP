import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))

# Pharaoh Legacy V2 Router (Uniswap‑V2 style)
ROUTER_ADDRESS = Web3.to_checksum_address("0xAAA45c8F5ef92a000a121d102F4e89278a711Faa")

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI FOR swapExactAVAXForTokens ─────────────────────────────────────────────
SWAP_AVAX_FOR_TOKENS_ABI = [
  {
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
  }
]
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=SWAP_AVAX_FOR_TOKENS_ABI)

def buy_heresy():
    amount_in = w3.to_wei(0.25, "ether")                            # 0.25 AVAX
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300       # 5 min from now
    path      = [WAVAX_ADDRESS, HERESY_ADDRESS]                     # WAVAX → HERESY

    tx = router.functions.swapExactAVAXForTokens(
        0,                # accept any amountOut
        path,
        acct.address,     # send HERESY here
        deadline
    ).build_transaction({
        "from":     acct.address,
        "value":    amount_in,
        "gas":      300_000,
        "gasPrice": w3.eth.gas_price,
        "nonce":    w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":  43114
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
