import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

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

w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# V3 router ABI fragment for exactInputSingle
ROUTER_ABI = [
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

router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def buy_heresy():
    amount_in = w3.to_wei(0.25, "ether")
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300

    params = {
      "tokenIn": WAVAX_ADDRESS,
      "tokenOut": HERESY_ADDRESS,
      "fee": 10000,
      "recipient": acct.address,
      "deadline": deadline,
      "amountIn": amount_in,
      "amountOutMinimum": 0,
      "sqrtPriceLimitX96": 0
    }

    tx = router.functions.exactInputSingle(params).build_transaction({
        "from": acct.address,
        "value": amount_in,
        "gas": 500_000,
        "nonce": w3.eth.get_transaction_count(acct.address)
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
