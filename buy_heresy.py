import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RPC_URL        = os.getenv("AVAX_RPC_URL")
PRIVATE_KEY    = os.getenv("BOT_PRIVATE_KEY")
HERESY         = Web3.to_checksum_address(os.getenv("HERESY_ADDRESS"))
WAVAX          = Web3.to_checksum_address(os.getenv("WAVAX_ADDRESS"))
ROUTER_ADDRESS = Web3.to_checksum_address(os.getenv("PHARAOH_ROUTER"))

# ── WEB3 SETUP ─────────────────────────────────────────────────────────────────
w3   = Web3(Web3.HTTPProvider(RPC_URL))
acct = w3.eth.account.from_key(PRIVATE_KEY)

# ── ABI FOR native‐AVAX UniswapV2‑style swap ────────────────────────────────────
SWAP_NATIVE_ABI = [{
    "inputs":[
      {"name":"amountOutMin","type":"uint256"},
      {"name":"path","type":"address[]"},
      {"name":"to","type":"address"},
      {"name":"deadline","type":"uint256"}
    ],
    "name":"swapExactAVAXForTokens",
    "outputs":[{"name":"amounts","type":"uint256[]"}],
    "stateMutability":"payable",
    "type":"function"
}]
router = w3.eth.contract(address=ROUTER_ADDRESS, abi=SWAP_NATIVE_ABI)

def buy_heresy():
    amount   = w3.to_wei(0.25, "ether")
    deadline = w3.eth.get_block("latest")["timestamp"] + 300
    path     = [WAVAX, HERESY]

    # --- DEBUG INFO -------------------------------------------------------------
    print("Using router address:", ROUTER_ADDRESS)
    code = w3.eth.get_code(ROUTER_ADDRESS)
    print("Router code size:", len(code), "bytes")
    print("Your AVAX balance:", w3.from_wei(w3.eth.get_balance(acct.address), "ether"))
    print("Swap path:", path, "→ amountIn:", amount, "Wei")

    # 1) static‐call to catch on‑chain reverts early
    try:
        router.functions.swapExactAVAXForTokens(
            0, path, acct.address, deadline
        ).call({
            "from": acct.address,
            "value": amount
        })
        print("✅ Static call succeeded (no revert in view)")
    except Exception as e:
        print("❌ Static call revert:", e)

    # 2) build & send the real tx
    tx = router.functions.swapExactAVAXForTokens(
        0, path, acct.address, deadline
    ).build_transaction({
        "from":  acct.address,
        "value": amount,
        "gas":   350_000,
        "nonce": w3.eth.get_transaction_count(acct.address, "pending")
    })
    signed  = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    print("🔄 Swap TX → https://snowtrace.io/tx/" + tx_hash.hex())

if __name__=="__main__":
    buy_heresy()
