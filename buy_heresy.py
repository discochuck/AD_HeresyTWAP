import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(
    os.getenv("HERESY_ADDRESS", "0x432d38F83a50EC77C409D086e97448794cf76dCF")
)
SWAP_ROUTER    = Web3.to_checksum_address(
    os.getenv("PHARAOH_ROUTER", "0x062c62cA66E50Cfe277A95564Fe5bB504db1Fab8")
)
WAVAX_ADDRESS  = Web3.to_checksum_address(
    os.getenv("WAVAX_ADDRESS",  "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)

w3    = Web3(Web3.HTTPProvider(RPC_URL))
acct  = w3.eth.account.from_key(PRIVATE_KEY)

# ── Minimal ABIs ───────────────────────────────────────────────────────────────
WAVAX_ABI = [
    {"inputs":[],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"address","name":"guy","type":"address"},
               {"internalType":"uint256","name":"wad","type":"uint256"}],
     "name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],
     "stateMutability":"nonpayable","type":"function"}
]

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
    "stateMutability":"nonpayable",
    "type":"function"
  }
]

wavax  = w3.eth.contract(address=WAVAX_ADDRESS,   abi=WAVAX_ABI)
router = w3.eth.contract(address=SWAP_ROUTER,     abi=V3_ROUTER_ABI)

def buy_heresy():
    amount   = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300

    # 1) wrap AVAX → WAVAX
    tx1 = wavax.functions.deposit().build_transaction({
        "from": acct.address,
        "value": amount,
        "gas": 100_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed1 = acct.sign_transaction(tx1)
    w3.eth.send_raw_transaction(signed1.raw_transaction)
    w3.eth.wait_for_transaction_receipt(signed1.hash)
    print("✅ Wrapped")

    # 2) approve SwapRouter to spend WAVAX
    tx2 = wavax.functions.approve(SWAP_ROUTER, amount).build_transaction({
        "from": acct.address,
        "gas": 100_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed2 = acct.sign_transaction(tx2)
    w3.eth.send_raw_transaction(signed2.raw_transaction)
    w3.eth.wait_for_transaction_receipt(signed2.hash)
    print("✅ Approved")

    # 3) swap WAVAX → HERESY via V3 (0.3% fee tier)
    params = {
      "tokenIn":         WAVAX_ADDRESS,
      "tokenOut":        HERESY_ADDRESS,
      "fee":             3000,  # 0.3% pool
      "recipient":       acct.address,
      "deadline":        deadline,
      "amountIn":        amount,
      "amountOutMinimum": 0,
      "sqrtPriceLimitX96": 0
    }
    tx3 = router.functions.exactInputSingle(params).build_transaction({
        "from": acct.address,
        "value": 0,
        "gas": 500_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed3  = acct.sign_transaction(tx3)
    tx_hash3 = w3.eth.send_raw_transaction(signed3.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash3.hex())

if __name__ == "__main__":
    buy_heresy()
