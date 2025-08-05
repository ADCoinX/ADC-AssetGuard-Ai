import os

COUNT_FILE = os.path.join("static", "user_count.txt")

def log_asset_scan(asset, asset_type, network):
    try:
        if not os.path.exists(COUNT_FILE):
            with open(COUNT_FILE, 'w') as f:
                f.write("1")
        else:
            with open(COUNT_FILE, 'r') as f:
                count = int(f.read().strip())
            count += 1
            with open(COUNT_FILE, 'w') as f:
                f.write(str(count))
    except Exception as e:
        print(f"[ERROR] Failed to log scan: {e}")

def get_usage_stats():
    try:
        with open(COUNT_FILE, 'r') as f:
            count = int(f.read().strip())
        return f"{count} assets validated"
    except:
        return "Usage data unavailable"
