import os
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(
    os.getenv("HERESY_ADDRESS", "0x432d38F83a50EC77C409D086e97448794cf76dCF")
)
ROUTER_ADDRESS = Web3.to_checksum_address(
    os.getenv("PHARAOH_ROUTER", "0x062c62cA66E50Cfe277A95564Fe5bB504db1Fab8")
)
WAVAX_ADDRESS  = Web3.to_checksum_address(
    os.getenv("WAVAX_ADDRESS", "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)

# ── SETUP ─────────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
# AVAX chain uses a PoA middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABIs ──────────────────────────────────────────────────────────────────────
WAVAX_ABI = [
    { "inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function" },
    { "inputs": [{"internalType":"uint256","name":"wad","type":"uint256"}], 
      "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function" },
    { "inputs":[{"internalType":"address","name":"guy","type":"address"},
                {"internalType":"uint256","name":"wad","type":"uint256"}],
      "name": "approve", "outputs":[{"internalType":"bool","name":"","type":"bool"}],
      "stateMutability":"nonpayable", "type":"function" }
]

ROUTER_ABI = [
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
      ],"internalType":"struct ISwapRouter.ExactInputSingleParams",
        "name":"params","type":"tuple"
      }
    ],
    "name":"exactInputSingle",
    "outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],
    "stateMutability":"nonpayable","type":"function"
  }
]

wavax  = w3.eth.contract(address=WAVAX_ADDRESS,  abi=WAVAX_ABI)
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def buy_heresy():
    # 1) wrap native AVAX → WAVAX
    amount = w3.to_wei(0.25, "ether")
    tx1 = wavax.functions.deposit().build_transaction({
        "from": acct.address,
        "value": amount,
        "gas": 100_000,
        "nonce": w3.eth.get_transaction_count(acct.address)
    })
    signed1 = acct.sign_transaction(tx1)
    w3.eth.send_raw_transaction(signed1.raw_transaction)
    print("Wrapped 0.25 AVAX → WAVAX")
    # wait for wrap to confirm
    w3.eth.wait_for_transaction_receipt(signed1.hash)

    # 2) approve the router to spend your WAVAX
    tx2 = wavax.functions.approve(ROUTER_ADDRESS, amount).build_transaction({
        "from": acct.address,
        "gas": 100_000,
        "nonce": w3.eth.get_transaction_count(acct.address)
    })
    signed2 = acct.sign_transaction(tx2)
    w3.eth.send_raw_transaction(signed2.raw_transaction)
    print("Approved router for 0.25 WAVAX")
    w3.eth.wait_for_transaction_receipt(signed2.hash)

    # 3) swap WAVAX → HERESY via exactInputSingle (1% fee pool) :contentReference[oaicite:1]{index=1}
    deadline = w3.eth.get_block("latest")["timestamp"] + 300
    params   = {
      "tokenIn":     WAVAX_ADDRESS,
      "tokenOut":    HERESY_ADDRESS,
      "fee":         10000,
      "recipient":   acct.address,
      "deadline":    deadline,
      "amountIn":    amount,
     
