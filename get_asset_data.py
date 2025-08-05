import requests
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

def get_asset_data(asset):
    asset = asset.strip()
    print(f"[DEBUG] Input: {asset}")

    if is_blacklisted(asset):
        return default_result(asset, "Blacklisted address")

    if is_coin_symbol(asset):
        return fetch_coin_data(asset)
    elif is_token_contract(asset):
        return fetch_token_data(asset)
    elif is_nft(asset):
        return fetch_nft_data(asset)
    elif is_wallet(asset):
        return fetch_wallet_data(asset)
    else:
        return default_result(asset, "Invalid or unsupported input format")

# =================== DETECTION ===================

def is_wallet(s):
    return (
        (s.startswith("0x") and len(s) == 42) or    # ETH, Polygon
        (s.startswith("T") and len(s) == 34) or     # TRON
        (s.startswith("1") or s.startswith("3") or s.startswith("bc1")) or  # BTC
        (s.startswith("r") and len(s) >= 25) or     # XRP
        (len(s) == 44) or                           # Solana
        ("-" in s and len(s) >= 42) or              # HBAR
        (s.endswith(".near")) or                    # NEAR
        (s.startswith("axelar1"))                   # Axelar
    )

def is_token_contract(addr):
    return addr.startswith("0x") and len(addr) == 42

def is_nft(addr):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{addr}")
        return r.status_code == 200
    except:
        return False

def is_coin_symbol(s):
    return s.upper() in ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "MATIC"]

# =================== DEFAULT RESULT ===================

def default_result(input_str, reason):
    return {
        "input": input_str,
        "type": "Unknown",
        "network": "N/A",
        "balance": "0",
        "risk_score": 0,
        "info": f"❌ {reason}"
    }

# =================== FETCHING ===================

def fetch_wallet_data(addr):
    if addr.startswith("0x"):
        return fetch_eth_wallet(addr)
    elif addr.startswith("T"):
        return fetch_tron_wallet(addr)
    elif addr.startswith("1") or addr.startswith("3") or addr.startswith("bc1"):
        return fetch_btc_wallet(addr)
    elif addr.startswith("r"):
        return fetch_xrp_wallet(addr)
    elif len(addr) == 44:
        return fetch_sol_wallet(addr)
    elif "-" in addr:
        return fetch_hbar_wallet(addr)
    elif addr.endswith(".near"):
        return fetch_near_wallet(addr)
    elif addr.startswith("axelar1"):
        return fetch_axelar_wallet(addr)
    else:
        return default_result(addr, "Unknown wallet format")

def fetch_eth_wallet(addr):
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={addr}&tag=latest"
        r = requests.get(url)
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
        "info": "✅ Live from Etherscan"
    }

def fetch_tron_wallet(addr):
    try:
        r = requests.get(f"https://apilist.tronscanapi.com/api/account?address={addr}")
        data = r.json()
        balance = int(data.get("balance", 0)) / 1e6
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "TRON",
        "balance": f"{balance:.4f} TRX",
        "risk_score": score,
        "info": "✅ Live from TronScan"
    }

def fetch_btc_wallet(addr):
    try:
        r = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{addr}/balance")
        data = r.json()
        balance = int(data.get("final_balance", 0)) / 1e8
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Bitcoin",
        "balance": f"{balance:.4f} BTC",
        "risk_score": score,
        "info": "✅ Live from BlockCypher"
    }

def fetch_xrp_wallet(addr):
    try:
        r = requests.get(f"https://api.xrpscan.com/api/v1/account/{addr}")
        data = r.json()
        balance = float(data.get("balance", 0))
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "XRP",
        "balance": f"{balance:.4f} XRP",
        "risk_score": score,
        "info": "✅ Live from XRPSCAN"
    }

def fetch_sol_wallet(addr):
    try:
        r = requests.get(f"https://public-api.solscan.io/account/{addr}")
        data = r.json()
        balance = float(data.get("lamports", 0)) / 1e9
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Solana",
        "balance": f"{balance:.4f} SOL",
        "risk_score": score,
        "info": "✅ Live from Solscan"
    }

def fetch_hbar_wallet(addr):
    try:
        r = requests.get(f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{addr}")
        data = r.json()
        balance = float(data.get("balance", {}).get("balance", 0)) / 1e8
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Hedera",
        "balance": f"{balance:.4f} HBAR",
        "risk_score": score,
        "info": "✅ Live from Hedera Mirror Node"
    }

def fetch_near_wallet(addr):
    try:
        r = requests.get(f"https://rpc.mainnet.near.org", json={
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": "query",
            "params": {
                "request_type": "view_account",
                "finality": "final",
                "account_id": addr
            }
        })
        data = r.json()
        balance = int(data.get("result", {}).get("amount", 0)) / 1e24
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "NEAR",
        "balance": f"{balance:.4f} NEAR",
        "risk_score": score,
        "info": "✅ Live from NEAR RPC"
    }

def fetch_axelar_wallet(addr):
    try:
        r = requests.get(f"https://rest.axelar.dev/cosmos/bank/v1beta1/balances/{addr}")
        data = r.json()
        balance = int(data.get("balances", [{}])[0].get("amount", 0)) / 1e6
    except:
        balance = 0
    score = calculate_risk_score(balance=balance)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Axelar",
        "balance": f"{balance:.4f} AXL",
        "risk_score": score,
        "info": "✅ Live from Axelar"
    }

# ========= Coin, Token, NFT same as before (from your last pasted version) =========
# If you want me to continue with those sections, reply: `sambung token coin nft`
def fetch_token_data(contract):
    try:
        r = requests.get(f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract}")
        data = r.json()
        token = data.get("result", {})
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "Unknown")
        holders = int(token.get("holdersCount", 0))
        score = calculate_risk_score(holders=holders)
        return {
            "input": contract,
            "type": "Token",
            "network": "Ethereum",
            "info": f"{name} ({symbol}) | Holders: {holders}",
            "risk_score": score
        }
    except:
        return default_result(contract, "Token info unavailable")

def fetch_coin_data(symbol):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/coins/{symbol.lower()}")
        data = r.json()
        price = data["market_data"]["current_price"]["usd"]
        volume = data["market_data"]["total_volume"]["usd"]
        mcap = data["market_data"]["market_cap"]["usd"]
        score = calculate_risk_score(volume=volume)
        return {
            "input": symbol.upper(),
            "type": "Coin",
            "network": "Native",
            "info": f"Price: ${price}, Volume: ${volume}, Market Cap: ${mcap}",
            "risk_score": score
        }
    except:
        return default_result(symbol, "Coin data unavailable")

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
        return default_result(contract, "NFT info unavailable")
