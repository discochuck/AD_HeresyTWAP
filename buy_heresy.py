import os
from web3 import Web3
from dotenv import load_dotenv
from oneinch_py import OneInchSwap, TransactionHelper

load_dotenv()

RPC_URL     = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY = os.getenv("BOT_PRIVATE_KEY")
HERESY      = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
AVAX        = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"  # 1inch sentinel

# ← Chain ID for Avalanche
CHAIN_ID    = 43114

# Initialize Web3 & 1inch SDK
w3    = Web3(Web3.HTTPProvider(RPC_URL))
swap  = OneInchSwap(chain_id=CHAIN_ID)             # no API key needed for public endpoints
helper= TransactionHelper(provider_url=RPC_URL)

def buy_heresy():
    amount = w3.to_wei(0.25, "ether")

    # build the swap via 1inch
    tx_params = swap.build_swap(
        from_token_address = AVAX,
        to_token_address   = HERESY,
        amount             = amount,
        from_address       = w3.eth.account.from_key(PRIVATE_KEY).address,
        slippage            = 1   # 1%
    )

    # sign & send it in one step
    signed_tx = helper.sign_transaction(tx_params, PRIVATE_KEY)
    tx_hash   = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
