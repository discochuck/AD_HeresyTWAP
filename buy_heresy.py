import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()  # locally loads .env; Heroku uses config vars

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY_ADDRESS = Web3.toChecksumAddress(
    os.getenv("HERESY_ADDRESS", "0x432d38F83a50EC77C409D086e97448794cf76dCF")
)
ROUTER_ADDRESS = Web3.toChecksumAddress(
    os.getenv("PHARAOH_ROUTER", "0x062c62cA66E50Cfe277A95564Fe5bB504db1Fab8")
)
WAVAX_ADDRESS  = Web3.toChecksumAddress(
    os.getenv("WAVAX_ADDRESS", "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
)
# ── SETUP ─────────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# Minimal ABI for UniswapV2‑style swapExactAVAXForTokens
ROUTER_ABI = [
    {
      "inputs": [
        {"internalType":"uint256","name":"amountOutMin","type":"uint256"},
        {"internalType":"address[]","name":"path","type":"address[]"},
        {"internalType":"address","name":"to","type":"address"},
        {"internalType":"uint256","name":"deadline","type":"uint256"}
      ],
      "name": "swapExactAVAXForTokens",
      "outputs": [{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],
      "stateMutability":"payable",
      "type":"function"
    }
]

router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)

def buy_heresy():
    amount_in = w3.toWei(0.25, "ether")
    path      = [WAVAX_ADDRESS, HERESY_ADDRESS]
    deadline  = w3.eth.get_block("latest")["timestamp"] + 300

    tx = router.functions.swapExactAVAXForTokens(
        0,        # accept any amount of HERESY
        path,
        acct.address,
        deadline
    ).build_transaction({
        "from": acct.address,
        "value": amount_in,
        "gas": 300_000,
        "nonce": w3.eth.get_transaction_count(acct.address)
    })

    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__ == "__main__":
    buy_heresy()
