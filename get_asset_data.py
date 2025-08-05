import requests
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

ETHERSCAN_API_KEY = "freekey"  # Ganti dengan key sebenar jika perlu

def get_asset_data(input_str):
    input_str = input_str.strip()
    print(f"[DEBUG] Input: {input_str}")

    if is_coin_symbol(input_str):
        return fetch_coin_data(input_str)
    elif is_token_contract(input_str):
        return fetch_token_data(input_str)
    elif is_nft(input_str):
        return fetch_nft_data(input_str)
    elif is_wallet(input_str):
        return fetch_wallet_data(input_str)
    else:
        return {
            "input": input_str,
            "type": "Unknown",
            "network": "N/A",
            "risk_score": 0,
            "info": "❌ Invalid format or unsupported input"
        }

# ==== Detection Helpers ====

def is_token_contract(addr):
    try:
        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={addr}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        data = r.json()
        return data.get("status") == "1" and "name" in data.get("result", {})
    except:
        return False

def is_nft(addr):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{addr}")
        return r.status_code == 200
    except:
        return False

def is_wallet(s):
    return (
        (s.startswith("0x") and len(s) == 42) or   # ETH/BSC wallets
        (s.startswith("T") and len(s) == 34) or    # TRON
        (s.startswith("r") and len(s) >= 25) or    # XRP
        (s.startswith("1") or s.startswith("3") or s.startswith("bc1")) or  # BTC
        (s.startswith("axelar1")) or               # Axelar
        (s.endswith(".near")) or                   # NEAR
        ("-" in s and len(s) >= 42)                # Hedera
    )

def is_coin_symbol(s):
    return s.upper() in ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "MATIC"]

# ==== Real Fetching Logic ====

def fetch_wallet_data(addr):
    try:
        r = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={addr}&tag=latest&apikey={ETHERSCAN_API_KEY}")
        data = r.json()
        balance = int(data.get("result", 0)) / 1e18
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Ethereum",
        "balance": f"{balance:.4f} ETH",
        "risk_score": score,
        "info": "Validated via Etherscan"
    }

def fetch_token_data(contract):
    try:
        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract}&apikey={ETHERSCAN_API_KEY}"
        r = requests.get(url)
        data = r.json()
        name = data.get("result", {}).get("name", "Unknown")
        symbol = data.get("result", {}).get("symbol", "Unknown")
        holders = int(data.get("result", {}).get("holdersCount", "0"))
        score = calculate_risk_score(holders=holders)
        return {
            "input": contract,
            "type": "Token",
            "network": "Ethereum",
            "info": f"{name} ({symbol}), Holders: {holders}",
            "risk_score": score
        }
    except:
        return {
            "input": contract,
            "type": "Token",
            "network": "Ethereum",
            "info": "❌ Failed to fetch token info",
            "risk_score": 0
        }

def fetch_coin_data(symbol):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}")
        data = r.json()
        price = data["market_data"]["current_price"]["usd"]
        volume = data["market_data"]["total_volume"]["usd"]
        mcap = data["market_data"]["market_cap"]["usd"]
        score = calculate_risk_score(volume=volume)
        return {
            "input": symbol,
            "type": "Coin",
            "network": "Native",
            "info": f"Price: ${price}, Volume: ${volume}, Market Cap: ${mcap}",
            "risk_score": score
        }
    except:
        return {
            "input": symbol,
            "type": "Coin",
            "network": "Unknown",
            "info": "❌ Coin data unavailable",
            "risk_score": 0
        }

def fetch_nft_data(contract):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{contract}")
        data = r.json()
        name = data.get("name", "Unknown")
        supply = data.get("total_supply", "N/A")
        verified = "Yes" if data.get("collection", {}).get("safelist_request_status") == "verified" else "No"
        score = 90 if verified == "Yes" else 50
        return {
            "input": contract,
            "type": "NFT",
            "network": "Ethereum",
            "info": f"{name}, Supply: {supply}, Verified: {verified}",
            "risk_score": score
        }
    except:
        return {
            "input": contract,
            "type": "NFT",
            "network": "Ethereum",
            "info": "❌ NFT info not available",
            "risk_score": 0
        }
