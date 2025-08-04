import requests
from ai_risk import calculate_risk_score
from blacklist import is_blacklisted

def get_asset_data(asset):
    asset = asset.strip()
    if is_eth_wallet(asset):
        return fetch_eth_data(asset)
    elif is_tron_wallet(asset):
        return fetch_tron_data(asset)
    elif is_btc_wallet(asset):
        return fetch_btc_data(asset)
    elif is_xrp_wallet(asset):
        return fetch_xrp_data(asset)
    elif is_sol_wallet(asset):
        return fetch_sol_data(asset)
    elif is_hbar_wallet(asset):
        return fetch_hbar_data(asset)
    elif is_polygon_wallet(asset):
        return fetch_polygon_data(asset)
    elif is_near_wallet(asset):
        return fetch_near_data(asset)
    elif is_axelar_wallet(asset):
        return fetch_axelar_data(asset)
    else:
        return {
            "input": asset,
            "type": "Unknown",
            "network": "N/A",
            "risk_score": 0,
            "info": "❌ Invalid or unsupported wallet format"
        }

# === Detection Helpers ===
def is_eth_wallet(addr): return addr.startswith("0x") and len(addr) == 42
def is_tron_wallet(addr): return addr.startswith("T") and len(addr) == 34
def is_btc_wallet(addr): return addr.startswith("1") or addr.startswith("3") or addr.startswith("bc1")
def is_xrp_wallet(addr): return addr.startswith("r") and len(addr) >= 25
def is_sol_wallet(addr): return len(addr) == 44
def is_hbar_wallet(addr): return "-" in addr and len(addr) >= 42
def is_polygon_wallet(addr): return addr.startswith("0x") and len(addr) == 42
def is_near_wallet(addr): return addr.endswith(".near")
def is_axelar_wallet(addr): return addr.startswith("axelar1")

# === API Fetch Functions ===

def fetch_eth_data(addr):
    try:
        r = requests.get(f"https://api.etherscan.io/api?module=account&action=balance&address={addr}&tag=latest&apikey=YOUR_API_KEY")
        data = r.json()
        bal = int(data.get("result", 0)) / 1e18
    except:
        r = requests.get(f"https://api.blockchair.com/ethereum/dashboards/address/{addr}")
        data = r.json()
        bal = data["data"][addr]["address"].get("balance_usd", 0)
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Ethereum",
        "balance": f"{bal:.4f} ETH",
        "risk_score": score
    }

def fetch_tron_data(addr):
    try:
        r = requests.get(f"https://api.trongrid.io/v1/accounts/{addr}")
        data = r.json()
        bal = int(data["data"][0].get("balance", 0)) / 1e6
    except:
        r = requests.get(f"https://apilist.tronscanapi.com/api/account?address={addr}")
        data = r.json()
        bal = int(data.get("balance", 0)) / 1e6
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "TRON",
        "balance": f"{bal:.2f} TRX",
        "risk_score": score
    }

def fetch_btc_data(addr):
    try:
        r = requests.get(f"https://api.blockcypher.com/v1/btc/main/addrs/{addr}/balance")
        data = r.json()
        bal = int(data.get("final_balance", 0)) / 1e8
    except:
        r = requests.get(f"https://blockstream.info/api/address/{addr}")
        data = r.json()
        bal = data.get("chain_stats", {}).get("funded_txo_sum", 0) / 1e8
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Bitcoin",
        "balance": f"{bal:.6f} BTC",
        "risk_score": score
    }

def fetch_xrp_data(addr):
    try:
        r = requests.get(f"https://api.xrpscan.com/api/v1/account/{addr}/balance")
        data = r.json()
        bal = float(data.get("balance", 0))
    except:
        r = requests.get(f"https://data.ripple.com/v2/accounts/{addr}/balances")
        data = r.json()
        bal = float(data.get("balances", [{}])[0].get("value", 0))
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "XRP",
        "balance": f"{bal:.2f} XRP",
        "risk_score": score
    }

def fetch_sol_data(addr):
    try:
        r = requests.get(f"https://api.helius.xyz/v0/address/{addr}/balances?api-key=YOUR_HELIUS_KEY")
        data = r.json()
        bal = float(data.get("nativeBalance", {}).get("sol", 0))
    except:
        r = requests.get(f"https://public-api.solscan.io/account/{addr}")
        data = r.json()
        bal = data.get("lamports", 0) / 1e9
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Solana",
        "balance": f"{bal:.2f} SOL",
        "risk_score": score
    }

def fetch_hbar_data(addr):
    try:
        r = requests.get(f"https://mainnet-public.mirrornode.hedera.com/api/v1/accounts/{addr}")
        data = r.json()
        bal = int(data.get("balance", {}).get("balance", 0)) / 1e8
    except:
        r = requests.get(f"https://testnet.mirrornode.hedera.com/api/v1/accounts/{addr}")
        data = r.json()
        bal = int(data.get("balance", {}).get("balance", 0)) / 1e8
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Hedera",
        "balance": f"{bal:.2f} HBAR",
        "risk_score": score
    }

def fetch_polygon_data(addr):
    try:
        r = requests.get(f"https://api.polygonscan.com/api?module=account&action=balance&address={addr}&apikey=YOUR_POLYGON_KEY")
        data = r.json()
        bal = int(data.get("result", 0)) / 1e18
    except:
        r = requests.get(f"https://api.covalenthq.com/v1/137/address/{addr}/balances_v2/")
        data = r.json()
        bal = float(data["data"]["items"][0].get("balance", 0)) / 1e18
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Polygon",
        "balance": f"{bal:.4f} MATIC",
        "risk_score": score
    }

def fetch_near_data(addr):
    try:
        r = requests.post("https://rpc.mainnet.near.org", json={
            "jsonrpc": "2.0",
            "method": "query",
            "params": {"request_type": "view_account", "finality": "final", "account_id": addr},
            "id": "dontcare"
        })
        data = r.json()
        bal = int(data["result"]["amount"]) / 1e24
    except:
        bal = 0
    score = calculate_risk_score(balance=bal)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "NEAR",
        "balance": f"{bal:.2f} NEAR",
        "risk_score": score
    }

def fetch_axelar_data(addr):
    try:
        r = requests.get(f"https://axelar-lcd.quickapi.com/cosmos/bank/v1beta1/balances/{addr}")
        data = r.json()
        amount = int(data["balances"][0]["amount"]) / 1e6
    except:
        amount = 0
    score = calculate_risk_score(balance=amount)
    return {
        "input": addr,
        "type": "Wallet",
        "network": "Axelar",
        "balance": f"{amount:.2f} AXL",
        "risk_score": score
    }
