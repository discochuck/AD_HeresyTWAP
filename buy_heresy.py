import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL         = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY     = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS  = Web3.to_checksum_address(
    os.getenv("HERESY_ADDRESS", "0x432d38F83a50EC77C409D086e97448794cf76dCF")
)
PHARAOH_ROUTER  = Web3.to_checksum_address(
    os.getenv("PHARAOH_ROUTER", "0xAAA45c8F5ef92a000a121d102F4e89278a711Faa")
)
WAVAX_ADDRESS   = Web3.to_checksum_address(
    os.getenv("WAVAX_ADDRESS",  "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)

# ── PROVIDER & ACCOUNT ────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI for native‐AVAX V2 swapExactAVAXForTokens ────────────────────────────
SWAP_NATIVE_ABI = [
  {
    "inputs": [
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
router = w3.eth.contract(address=PHARAOH_ROUTER, abi=SWAP_NATIVE_ABI)

def buy_heresy():
    # 0.25 AVAX in Wei
    amount   = w3.to_wei(0.25, "ether")
    # deadline = now + 5 minutes
    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    tx = router.functions.swapExactAVAXForTokens(
        0,                              # accept any amount of HERESY
        [WAVAX_ADDRESS, HERESY_ADDRESS],# path: WAVAX → HERESY
        acct.address,                   # send tokens here
        deadline
    ).build_transaction({
        "from":  acct.address,
        "value": amount,                # send 0.25 AVAX
        "gas":   500_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
