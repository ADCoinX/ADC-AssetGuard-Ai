import requests
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

def get_asset_data(input_str):
    input_str = input_str.strip()
    
    if is_blacklisted(input_str):
        return {
            "input": input_str,
            "type": "Blacklisted",
            "network": "N/A",
            "risk_score": 100,
            "info": "❌ Blacklisted address"
        }

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
    return addr.startswith("0x") and len(addr) == 42

def is_nft(addr):
    try:
        r = requests.get(f"https://api.opensea.io/api/v1/asset_contract/{addr}")
        return r.status_code == 200
    except:
        return False

def is_wallet(s):
    return (
        (s.startswith("0x") and len(s) == 42) or
        (s.startswith("T") and len(s) == 34) or
        (s.startswith("r") and len(s) >= 25) or
        (s.startswith("1") or s.startswith("3") or s.startswith("bc1")) or
        (s.startswith("axelar1")) or
        (s.endswith(".near")) or
        ("-" in s and len(s) >= 42)
    )

def is_coin_symbol(s):
    return s.upper() in ["BTC", "ETH", "BNB", "XRP", "SOL", "ADA", "DOGE", "MATIC"]

# ==== Fetch Logic ====

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

def fetch_token_data(contract):
    try:
        url = f"https://api.etherscan.io/api?module=token&action=tokeninfo&contractaddress={contract}&apikey=freekey"
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

# ==== Wallet Dispatcher ====

def fetch_wallet_data(addr):
    if addr.startswith("0x"):
        return fetch_eth_wallet(addr)
    elif addr.startswith("T"):
        return fetch_tron_wallet(addr)
    elif addr.startswith("r"):
        return fetch_xrp_wallet(addr)
    elif addr.startswith("1") or addr.startswith("3") or addr.startswith("bc1"):
        return fetch_btc_wallet(addr)
    elif addr.startswith("axelar1"):
        return fetch_axelar_wallet(addr)
    elif addr.endswith(".near"):
        return fetch_near_wallet(addr)
    elif "-" in addr and len(addr) >= 42:
        return fetch_hbar_wallet(addr)
    else:
        return {
            "input": addr,
            "type": "Wallet",
            "network": "Unknown",
            "risk_score": 0,
            "info": "❌ Unknown wallet format"
        }

# ==== Per Chain Wallet Handlers ====

def fetch_eth_wallet(addr):
    try:
        r = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={addr}&tag=latest&apikey=freekey")
        data = r.json()
        balance = int(data.get("result", 0)) / 1e18
    except:
        return error_result(addr, "Ethereum")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "Ethereum", f"{balance:.4f} ETH", score)

def fetch_tron_wallet(addr):
    try:
        r = requests.get(f"https://api.trongrid.io/v1/accounts/{addr}")
        data = r.json()
        balance = int(data.get("data", [{}])[0].get("balance", 0)) / 1_000_000
    except:
        return error_result(addr, "TRON")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "TRON", f"{balance:.2f} TRX", score)

def fetch_btc_wallet(addr):
    try:
        r = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{addr}/balance")
        data = r.json()
        balance = data.get("final_balance", 0) / 1e8
    except:
        return error_result(addr, "Bitcoin")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "Bitcoin", f"{balance:.4f} BTC", score)

def fetch_xrp_wallet(addr):
    try:
        r = requests.get(f"https://api.xrpscan.com/api/v1/account/{addr}")
        data = r.json()
        balance = float(data.get("account_data", {}).get("Balance", 0)) / 1_000_000
    except:
        return error_result(addr, "XRP")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "XRP", f"{balance:.2f} XRP", score)

def fetch_sol_wallet(addr):
    try:
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        r = requests.post("https://api.mainnet-beta.solana.com", json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [addr]
        }, headers=headers)
        data = r.json()
        balance = int(data.get("result", {}).get("value", 0)) / 1e9
    except:
        return error_result(addr, "Solana")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "Solana", f"{balance:.4f} SOL", score)

def fetch_hbar_wallet(addr):
    try:
        r = requests.get(f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{addr}")
        data = r.json()
        balance = int(data.get("balance", {}).get("balance", 0)) / 1e8
    except:
        return error_result(addr, "Hedera")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "Hedera", f"{balance:.4f} HBAR", score)

def fetch_axelar_wallet(addr):
    try:
        r = requests.get(f"https://lcd-axelar.imperator.co/axelar/evm/v1beta1/account_balance/{addr}")
        data = r.json()
        balance = int(data.get("balance", {}).get("amount", 0)) / 1e6
    except:
        return error_result(addr, "Axelar")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "Axelar", f"{balance:.4f} AXL", score)

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
        return error_result(addr, "NEAR")
    score = calculate_risk_score(balance=balance)
    return success_result(addr, "Wallet", "NEAR", f"{balance:.4f} NEAR", score)

# ==== Output Helpers ====

def success_result(addr, type_, network, balance_str, score):
    return {
        "input": addr,
        "type": type_,
        "network": network,
        "balance": balance_str,
        "risk_score": score,
        "info": f"✅ Live from {network}"
    }

def error_result(addr, network):
    return {
        "input": addr,
        "type": "Wallet",
        "network": network,
        "risk_score": 0,
        "info": "❌ API rejected"
    }
