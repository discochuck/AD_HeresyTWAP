import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(
    os.getenv("HERESY_ADDRESS", "0x432d38F83a50EC77C409D086e97448794cf76dCF")
)
ROUTER_ADDRESS = Web3.to_checksum_address(
    os.getenv("PHARAOH_ROUTER", "0xAAA45c8F5ef92a000a121d102F4e89278a711Faa")
)
WAVAX_ADDRESS  = Web3.to_checksum_address(
    os.getenv("WAVAX_ADDRESS",  "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)

# ── SETUP ─────────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABIs ──────────────────────────────────────────────────────────────────────
WAVAX_ABI = [
    {"inputs": [], "name": "deposit",     "outputs": [], "stateMutability": "payable",   "type": "function"},
    {"inputs": [{"internalType":"uint256","name":"wad","type":"uint256"}],
     "name": "withdraw",    "outputs": [], "stateMutability": "nonpayable", "type":"function"},
    {"inputs":[{"internalType":"address","name":"guy","type":"address"},
               {"internalType":"uint256","name":"wad","type":"uint256"}],
     "name": "approve",     "outputs":[{"internalType":"bool","name":"","type":"bool"}],
     "stateMutability":"nonpayable","type":"function"}
]

V2_ROUTER_ABI = [
    {
      "name":"swapExactTokensForTokens",
      "type":"function",
      "stateMutability":"nonpayable",
      "inputs":[
        {"name":"amountIn","type":"uint256"},
        {"name":"amountOutMin","type":"uint256"},
        {"name":"path","type":"address[]"},
        {"name":"to","type":"address"},
        {"name":"deadline","type":"uint256"}
      ],
      "outputs":[{"name":"amounts","type":"uint256[]"}]
    }
]

wavax  = w3.eth.contract(address=WAVAX_ADDRESS,  abi=WAVAX_ABI)
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=V2_ROUTER_ABI)

def buy_heresy():
    amount   = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    # 1) Wrap AVAX → WAVAX
    tx1 = wavax.functions.deposit().build_transaction({
        "from":  acct.address,
        "value": amount,
        "gas":   100_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed1 = acct.sign_transaction(tx1)
    w3.eth.send_raw_transaction(signed1.raw_transaction)
    w3.eth.wait_for_transaction_receipt(signed1.hash)
    print("✅ Wrapped 0.25 AVAX → WAVAX")

    # 2) Approve router to spend WAVAX
    tx2 = wavax.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
        "from":  acct.address,
        "gas":   100_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed2 = acct.sign_transaction(tx2)
    w3.eth.send_raw_transaction(signed2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(signed2.hash)
    print("✅ Approved router for 0.25 WAVAX")

    # 3) Swap WAVAX → HERESY via V2
    tx3 = router.functions.swapExactTokensForTokens(
        amount,
        0,
        [WAVAX_ADDRESS, HERESY_ADDRESS],
        acct.address,
        deadline
    ).build_transaction({
        "from":  acct.address,
        "gas":   300_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed3  = acct.sign_transaction(tx3)
    tx_hash3 = w3.eth.send_raw_transaction(signed3.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash3.hex())

if __name__ == "__main__":
    buy_heresy()
