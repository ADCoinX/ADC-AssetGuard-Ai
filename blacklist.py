# blacklist.py

# Senarai contoh address/token/NFT/coin yang disenarai hitam
BLACKLISTED_ITEMS = [
    "0x000000000000000000000000000000000000dead",  # Burn address
    "BTC", "ETH", "TRX",  # Contoh coin scam tiruan
    "0x1111111111111111111111111111111111111111",  # Dummy token
    "nftscam.eth",  # Nama domain scam
    "scamcoin"  # Coin label scam
]

def is_blacklisted(input_str):
    return input_str.strip().lower() in [item.lower() for item in BLACKLISTED_ITEMS]
