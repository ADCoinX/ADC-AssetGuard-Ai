import csv
import os
from datetime import datetime

LOG_FILE = "asset_log.csv"

def log_asset_scan(asset, asset_type, network):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, asset, asset_type, network]
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "input", "type", "network"])
        writer.writerow(row)

def get_usage_stats():
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        total = sum(1 for _ in reader)
    return total
