import json
import os
import sys
import gspread
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "service_account.json")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

TAB_TO_FILE = {
    "Papers": "papers.json",
    "News": "news.json",
    "Jobs": "jobs.json",
    "Startups": "startups.json",
    "Products": "startups.json",
    "Entity Mapping Log": "entity_mapping_log.json",
}

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def dict_list_to_rows(data):
    if not data:
        return [["No data available"]]
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    headers = sorted(all_keys)
    rows = [headers]
    for item in data:
        row = []
        for key in headers:
            value = item.get(key, "")
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            row.append(str(value) if value is not None else "")
        rows.append(row)
    return rows

def push_all_tabs():
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
    spreadsheet = gc.open_by_key(SHEET_ID)

    for tab_name, filename in TAB_TO_FILE.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Skipping {tab_name}: {filename} not found")
            continue
        data = load_json(filepath)
        rows = dict_list_to_rows(data)

        worksheet = spreadsheet.worksheet(tab_name)
        worksheet.clear()
        worksheet.update(rows)
        print(f"Pushed {len(rows) - 1} rows to '{tab_name}' tab")

if __name__ == "__main__":
    push_all_tabs()