import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))
PHAR_ADDRESS   = Web3.to_checksum_address("0xAAAB9D12A30504559B0C5A9A5977fEE4A6081c6b")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))

# Uniswap V3 SwapRouter on Avalanche that supports multi‑hop
SWAP_ROUTER    = "0xAAAE99091Fbb28D400029052821653C1C752483B"

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI SNIPPETS ────────────────────────────────────────────────────────────────
WAVAX_ABI = [
    {"inputs":[],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],
     "name":"approve","outputs":[{"type":"bool"}],"stateMutability":"nonpayable","type":"function"}
]
V3_ROUTER_ABI = [
  {
    "inputs":[
      {"components":[
        {"internalType":"bytes","name":"path","type":"bytes"},
        {"internalType":"address","name":"recipient","type":"address"},
        {"internalType":"uint256","name":"deadline","type":"uint256"},
        {"internalType":"uint256","name":"amountIn","type":"uint256"},
        {"internalType":"uint256","name":"amountOutMinimum","type":"uint256"}
      ],"internalType":"struct ISwapRouter.ExactInputParams","name":"params","type":"tuple"}
    ],
    "name":"exactInput","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
    "stateMutability":"payable","type":"function"
  }
]

wavax  = w3.eth.contract(address=WAVAX_ADDRESS, abi=WAVAX_ABI)
router = w3.eth.contract(address=SWAP_ROUTER,   abi=V3_ROUTER_ABI)

def buy_heresy():
    amount    = w3.to_wei(0.25, "ether")
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300
    gas_price = w3.eth.gas_price
    nonce     = w3.eth.get_transaction_count(acct.address, "pending")

    # 1) Wrap AVAX → WAVAX
    tx1 = wavax.functions.deposit().build_transaction({
      "from":acct.address, "value":amount,
      "gas":150_000, "gasPrice":gas_price,
      "nonce":nonce, "chainId":43114
    })
    sig1 = acct.sign_transaction(tx1)
    w3.eth.send_raw_transaction(sig1.raw_transaction)
    w3.eth.wait_for_transaction_receipt(sig1.hash)

    # 2) Approve router to pull your WAVAX
    tx2 = wavax.functions.approve(SWAP_ROUTER, amount).build_transaction({
      "from":acct.address, "gas":100_000,
      "gasPrice":gas_price, "nonce":nonce+1, "chainId":43114
    })
    sig2 = acct.sign_transaction(tx2)
    w3.eth.send_raw_transaction(sig2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(sig2.hash)

    # 3) Build the multi‑hop path: WAVAX→PHAR→HERESY
    #   WAVAX (20 bytes) | fee3000 (0x0bb8) | PHAR (20 bytes) | fee3000 | HERESY
    path = (
      WAVAX_ADDRESS[2:] +
      "0bb8" +
      PHAR_ADDRESS[2:] +
      "0bb8" +
      HERESY_ADDRESS[2:]
    )
    path_bytes = bytes.fromhex(path)

    # 4) exactInput multi‑hop
    params = {
      "path":            path_bytes,
      "recipient":       acct.address,
      "deadline":        deadline,
      "amountIn":        amount,
      "amountOutMinimum":0
    }
    tx3 = router.functions.exactInput(params).build_transaction({
      "from":acct.address, "value":amount,
      "gas":500_000, "gasPrice":gas_price,
      "nonce":nonce+2, "chainId":43114
    })
    sig3 = acct.sign_transaction(tx3)
    tx_hash = w3.eth.send_raw_transaction(sig3.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
