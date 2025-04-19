import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))

# ← Pharaoh V3 SwapRouter (immutable & verified) :contentReference[oaicite:1]{index=1}
SWAP_ROUTER    = "0xAAAE99091Fbb28D400029052821653C1C752483B"

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI FOR exactInputSingle (Uniswap V3‑style) ───────────────────────────────
V3_ROUTER_ABI = [
  {
    "inputs":[
      {
        "components":[
          {"internalType":"address","name":"tokenIn","type":"address"},
          {"internalType":"address","name":"tokenOut","type":"address"},
          {"internalType":"uint24","name":"fee","type":"uint24"},
          {"internalType":"address","name":"recipient","type":"address"},
          {"internalType":"uint256","name":"deadline","type":"uint256"},
          {"internalType":"uint256","name":"amountIn","type":"uint256"},
          {"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},
          {"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}
        ],
        "internalType":"struct ISwapRouter.ExactInputSingleParams",
        "name":"params","type":"tuple"
      }
    ],
    "name":"exactInputSingle",
    "outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
    "stateMutability":"payable",
    "type":"function"
  }
]
router = w3.eth.contract(address=SWAP_ROUTER, abi=V3_ROUTER_ABI)

def buy_heresy():
    amountIn = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    params = {
      "tokenIn":         WAVAX_ADDRESS,
      "tokenOut":        HERESY_ADDRESS,
      "fee":             3000,            # 0.3% pool
      "recipient":       acct.address,
      "deadline":        deadline,
      "amountIn":        amountIn,
      "amountOutMinimum":0,               # accept any output
      "sqrtPriceLimitX96": 0
    }

    tx = router.functions.exactInputSingle(params).build_transaction({
        "from":      acct.address,
        "value":     amountIn,            # send 0.25 AVAX to wrap
        "gas":       500_000,
        "gasPrice":  w3.eth.gas_price,
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   43114
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
