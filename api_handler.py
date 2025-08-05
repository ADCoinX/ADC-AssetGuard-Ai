import requests
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
from utils import log_usage  # Simpan bilangan penggunaan pengguna

# === MAIN ENTRY ===
def get_asset_data(input_str):
    input_str = input_str.strip()
    print(f"[DEBUG] Input: {input_str}")

    if is_token_contract(input_str):
        return fetch_token_data(input_str)
    elif is_nft_contract(input_str):
        return fetch_nft_data(input_str)
    elif is_coin_symbol(input_str):
        return fetch_coin_data(input_str)
    else:
        return {
            "input": input_str,
            "type": "Unknown",
            "network": "N/A",
            "risk_score": 0,
            "info": "❌ Unsupported asset type"
        }

# === DETECTION HELPERS ===

def is_token_contract(addr):
    return addr.startswith("0x") and len(addr) == 42

def is_nft_contract(addr):
    return addr.startswith("0x") and len(addr) == 42

def is_coin_symbol(s):
    return s.upper() in ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "MATIC", "USDT", "LINK", "AVAX", "NEAR", "DOT"]

# === FETCH TOKEN DATA (Ethereum & backup) ===

def fetch_token_data(contract):
    try:
        # Primary (Etherscan)
        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract}&apikey=freekey"
        r = requests.get(url)
        data = r.json()
        if data.get("status") != "1":
            raise Exception("Etherscan rejected")

        name = data["result"].get("name", "Unknown")
        symbol = data["result"].get("symbol", "N/A")
        holders = int(data["result"].get("holdersCount", "0"))
        score = calculate_risk_score(holders=holders)
        log_usage("token")
        return {
            "input": contract,
            "type": "Token",
            "network": "Ethereum",
            "info": f"{name} ({symbol}) – Holders: {holders}",
            "risk_score": score
        }
    except:
        # Backup API if available
        return {
            "input": contract,
            "type": "Token",
            "network": "Ethereum",
            "info": "❌ Token API rejected",
            "risk_score": 0
        }

# === FETCH NFT DATA ===

def fetch_nft_data(contract):
    try:
        url = f"https://api.opensea.io/api/v1/asset_contract/{contract}"
        r = requests.get(url)
        data = r.json()
        name = data.get("name", "Unknown")
        supply = data.get("total_supply", "N/A")
        verified = "Yes" if data.get("collection", {}).get("safelist_request_status") == "verified" else "No"
        score = 90 if verified == "Yes" else 40
        log_usage("nft")
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
            "info": "❌ NFT API rejected",
            "risk_score": 0
        }

# === FETCH COIN DATA ===

def fetch_coin_data(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}"
        r = requests.get(url)
        data = r.json()
        price = data["market_data"]["current_price"]["usd"]
        volume = data["market_data"]["total_volume"]["usd"]
        mcap = data["market_data"]["market_cap"]["usd"]
        score = calculate_risk_score(volume=volume)
        log_usage("coin")
        return {
            "input": symbol,
            "type": "Coin",
            "network": "Native",
            "info": f"Price: ${price:.2f}, Volume: ${volume:.0f}, MCap: ${mcap:.0f}",
            "risk_score": score
        }
    except:
        return {
            "input": symbol,
            "type": "Coin",
            "network": "Unknown",
            "info": "❌ Coin API rejected",
            "risk_score": 0
        }
