import requests
from ai_risk import calculate_risk_score
from iso_export import generate_iso_xml
from utils import log_asset_scan, get_usage_stats
from blacklist import is_blacklisted

def get_asset_data(input_str):
    input_str = input_str.strip()
    print(f"[DEBUG] Input: {input_str}")

    if is_blacklisted(input_str):
        return {
            "input": input_str,
            "type": "Blocked",
            "network": "N/A",
            "risk_score": 100,
            "info": "⚠️ Blacklisted address",
            "iso": generate_iso_xml(input_str, "blacklisted", 100),
            "usage": get_usage_stats()
        }

    if is_coin_symbol(input_str):
        result = fetch_coin_data(input_str)
    elif is_token_contract(input_str):
        result = fetch_token_data(input_str)
    elif is_nft_contract(input_str):
        result = fetch_nft_data(input_str)
    else:
        return {
            "input": input_str,
            "type": "Unknown",
            "network": "N/A",
            "risk_score": 0,
            "info": "❌ Invalid format or unsupported input",
            "iso": generate_iso_xml(input_str, "unknown", 0),
            "usage": get_usage_stats()
        }

    log_asset_scan(input_str, result["type"], result["network"])
    result["iso"] = generate_iso_xml(input_str, result["type"], result["risk_score"])
    result["usage"] = get_usage_stats()
    return result

# =====================
# Detection Functions
# =====================

def is_coin_symbol(s):
    return s.upper() in [
        "BTC", "ETH", "BNB", "XRP", "SOL", "ADA",
        "DOGE", "MATIC", "TRX", "NEAR", "HBAR", "AXL", "AVAX", "DOT"
    ]

def is_token_contract(addr):
    try:
        url = f"https://api.ethplorer.io/getTokenInfo/{addr}?apiKey=freekey"
        r = requests.get(url, timeout=8)
        return r.status_code == 200 and "name" in r.json()
    except:
        return False

def is_nft_contract(addr):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{addr}", timeout=8)
        return r.status_code == 200
    except:
        return False

# =====================
# Fetching Functions
# =====================

def fetch_coin_data(symbol):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}", timeout=10)
        data = r.json()
        price = data["market_data"]["current_price"]["usd"]
        volume = data["market_data"]["total_volume"]["usd"]
        mcap = data["market_data"]["market_cap"]["usd"]
        score = calculate_risk_score(volume=volume, mcap=mcap)
        return {
            "input": symbol.upper(),
            "type": "Coin",
            "network": "Native",
            "info": f"Price: ${price:,}, Volume: ${volume:,}, Market Cap: ${mcap:,}",
            "risk_score": score
        }
    except:
        return {
            "input": symbol.upper(),
            "type": "Coin",
            "network": "Unknown",
            "info": "❌ Coin data unavailable",
            "risk_score": 0
        }

def fetch_token_data(addr):
    try:
        r = requests.get(f"https://api.ethplorer.io/getTokenInfo/{addr}?apiKey=freekey", timeout=10)
        data = r.json()
        name = data.get("name", "Unknown")
        symbol = data.get("symbol", "N/A")
        holders = data.get("holdersCount", 0)
        score = calculate_risk_score(holders=holders)
        return {
            "input": addr,
            "type": "Token",
            "network": "Ethereum",
            "info": f"{name} ({symbol}), Holders: {holders:,}",
            "risk_score": score
        }
    except:
        return {
            "input": addr,
            "type": "Token",
            "network": "Ethereum",
            "info": "❌ Token info not available",
            "risk_score": 0
        }

def fetch_nft_data(addr):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{addr}", timeout=10)
        data = r.json()
        name = data.get("name", "Unknown")
        supply = data.get("total_supply", "N/A")
        verified = "Yes" if data.get("collection", {}).get("safelist_request_status") == "verified" else "No"
        score = 90 if verified == "Yes" else 50
        return {
            "input": addr,
            "type": "NFT",
            "network": "Ethereum",
            "info": f"{name}, Supply: {supply}, Verified: {verified}",
            "risk_score": score
        }
    except:
        return {
            "input": addr,
            "type": "NFT",
            "network": "Ethereum",
            "info": "❌ NFT info not available",
            "risk_score": 0
        }
