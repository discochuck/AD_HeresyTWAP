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
WAVAX_ADDRESS  = Web3.to_checksum_address(
    os.getenv("WAVAX_ADDRESS",  "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)

# Immutable Uniswap V3 SwapRouter on Avalanche
SWAP_ROUTER    = Web3.to_checksum_address("0xAAAE99091Fbb28D400029052821653C1C752483B")

# ── SETUP ─────────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI SNIPPETS ────────────────────────────────────────────────────────────────
WAVAX_ABI = [
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs":[{"internalType":"address","name":"guy","type":"address"},{"internalType":"uint256","name":"wad","type":"uint256"}],
     "name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}
]
V3_ROUTER_ABI = [
  {
    "inputs":[
      {"components":[
        {"internalType":"address","name":"tokenIn","type":"address"},
        {"internalType":"address","name":"tokenOut","type":"address"},
        {"internalType":"uint24","name":"fee","type":"uint24"},
        {"internalType":"address","name":"recipient","type":"address"},
        {"internalType":"uint256","name":"deadline","type":"uint256"},
        {"internalType":"uint256","name":"amountIn","type":"uint256"},
        {"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},
        {"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}
      ],"internalType":"struct ISwapRouter.ExactInputSingleParams","name":"params","type":"tuple"}
    ],
    "name":"exactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
    "stateMutability":"payable","type":"function"
  }
]

wavax  = w3.eth.contract(address=WAVAX_ADDRESS, abi=WAVAX_ABI)
router = w3.eth.contract(address=SWAP_ROUTER,  abi=V3_ROUTER_ABI)

def buy_heresy():
    amount    = w3.to_wei(0.25, "ether")
    gas_price = w3.eth.gas_price
    base_nonce= w3.eth.get_transaction_count(acct.address, "pending")
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300

    # 1) Wrap AVAX → WAVAX
    tx1 = wavax.functions.deposit().build_transaction({
        "from":     acct.address,
        "value":    amount,
        "gas":      150_000,
        "gasPrice": gas_price,
        "nonce":    base_nonce,
        "chainId":  43114
    })
    sig1 = acct.sign_transaction(tx1)
    w3.eth.send_raw_transaction(sig1.raw_transaction)
    w3.eth.wait_for_transaction_receipt(sig1.hash)

    # 2) Approve SwapRouter
    tx2 = wavax.functions.approve(SWAP_ROUTER, amount).build_transaction({
        "from":     acct.address,
        "gas":      100_000,
        "gasPrice": gas_price,
        "nonce":    base_nonce + 1,
        "chainId":  43114
    })
    sig2 = acct.sign_transaction(tx2)
    w3.eth.send_raw_transaction(sig2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(sig2.hash)

    # 3) Swap WAVAX → HERESY via exactInputSingle (0.3% fee)
    params = {
      "tokenIn":         WAVAX_ADDRESS,
      "tokenOut":        HERESY_ADDRESS,
      "fee":             3000,
      "recipient":       acct.address,
      "deadline":        deadline,
      "amountIn":        amount,
      "amountOutMinimum":0,
      "sqrtPriceLimitX96": 0
    }
    tx3 = router.functions.exactInputSingle(params).build_transaction({
        "from":     acct.address,
        "value":    0,
        "gas":      500_000,
        "gasPrice": gas_price,
        "nonce":    base_nonce + 2,
        "chainId":  43114
    })
    sig3 = acct.sign_transaction(tx3)
    tx_hash = w3.eth.send_raw_transaction(sig3.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
