import os
import sys
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL", "").strip()
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY", "").strip()
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS", "").strip())
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS", "").strip())
JOE_ROUTER     = Web3.to_checksum_address(os.getenv("JOE_ROUTER", "0x60ae616a2155ee3d9a68541ba4544862310933d4").strip())
CHAIN_ID       = 43114

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print("❌ RPC not connected:", RPC_URL)
    sys.exit(1)
print("✅ Connected, chainId =", w3.eth.chain_id)

acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ROUTER ABI ─────────────────────────────────────────────────────────────────
ABI = [
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
router = w3.eth.contract(address=JOE_ROUTER, abi=ABI)
code = w3.eth.get_code(JOE_ROUTER)
print("Router code size:", len(code), "bytes")

def buy_heresy():
    amount_in = w3.to_wei(0.25, "ether")                            # 0.25 AVAX
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300       # +5 minutes
    path      = [WAVAX_ADDRESS, HERESY_ADDRESS]

    tx = router.functions.swapExactAVAXForTokens(
        0,            # accept any HERESY → zero slippage tolerance
        path,
        acct.address, # receive HERESY here
        deadline
    ).build_transaction({
        "from":     acct.address,
        "value":    amount_in,
        "gas":      300_000,
        "gasPrice": w3.eth.gas_price,
        "nonce":    w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":  CHAIN_ID
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    print(f"Swapping 0.25 AVAX for HERESY ({HERESY_ADDRESS}) via Joe V2")
    buy_heresy()
