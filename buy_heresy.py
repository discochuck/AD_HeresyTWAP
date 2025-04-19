from web3 import Web3

RPC_URL      = "YOUR_AVAX_RPC_URL"
FACTORY_V3   = Web3.to_checksum_address("0xAAA16c016BF556fcD620328f0759252E29b1AB57")
WAVAX        = Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
PHAR         = Web3.to_checksum_address("0xAAAB9D12A30504559B0C5A9A5977fEE4A6081c6b")
HERESY       = Web3.to_checksum_address("0x432d38F83a50EC77C409D086e97448794cf76dCF")
FACTORY_ABI  = [{
    "inputs":[
      {"internalType":"address","name":"tokenA","type":"address"},
      {"internalType":"address","name":"tokenB","type":"address"},
      {"internalType":"uint24","name":"fee","type":"uint24"}
    ],
    "name":"getPool",
    "outputs":[{"internalType":"address","name":"pool","type":"address"}],
    "stateMutability":"view","type":"function"
}]

w3      = Web3(Web3.HTTPProvider(RPC_URL))
factory = w3.eth.contract(address=FACTORY_V3, abi=FACTORY_ABI)

p1 = factory.functions.getPool(WAVAX, PHAR, 3000).call()
p2 = factory.functions.getPool(PHAR, HERESY, 3000).call()
print("WAVAX → PHAR pool:", p1)
print("PHAR → HERESY pool:", p2)
