# src/google_logger.py

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

def log_scan(wallet, asset_type, score, status):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_json = json.loads(os.environ.get("GOOGLE_CREDENTIALS_JSON"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)

        sheet = client.open("AssetGuard_Logs").sheet1  # Nama Google Sheet
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = [now, wallet, asset_type, str(score), status]
        sheet.append_row(row)

    except Exception as e:
        print(f"❌ Google Sheet log error: {e}")
