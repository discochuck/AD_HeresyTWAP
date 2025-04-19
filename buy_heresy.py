import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
WAVAX_ADDRESS  = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))

# ← This is the *only* router that implements swapExactAVAXForTokens on Avalanche
SWAP_ROUTER    = "0x062c62cA66E50Cfe277A95564Fe5bB504db1Fab8"

w3    = Web3(Web3.HTTPProvider(RPC_URL))
acct  = w3.eth.account.from_key(PRIVATE_KEY)

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
router = w3.eth.contract(address=SWAP_ROUTER, abi=SWAP_NATIVE_ABI)

def buy_heresy():
    amount   = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300
    tx = router.functions.swapExactAVAXForTokens(
        0,                      # accept any HERESY
        [WAVAX_ADDRESS, HERESY_ADDRESS],
        acct.address,
        deadline
    ).build_transaction({
        "from":      acct.address,
        "value":     amount,
        "gas":       350_000,
        "gasPrice":  w3.eth.gas_price,
        "nonce":     w3.eth.get_transaction_count(acct.address, "pending"),
        "chainId":   43114
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
