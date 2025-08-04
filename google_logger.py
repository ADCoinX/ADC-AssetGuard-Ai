import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

def log_scan(user_input, asset_type):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sheet = client.open("ADC_AssetGuard_Logs").sheet1
        sheet.append_row([user_input, asset_type])
    except Exception as e:
        print("Logging failed:", e)
