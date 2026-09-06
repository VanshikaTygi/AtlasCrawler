import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_to_json, create_ssl_connector
import aiohttp

from llm_extractor import extract_structured_data 
from resolution.entity_resolver import resolve_entity_name

YC_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "yc_companies.json")

def load_json(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

async def process_companies(session, companies):
    processed = []
    for company in companies:
        raw_text = f"{company.get('name')}: {company.get('description')}"
        try:
            structured = await extract_structured_data(session, raw_text)
            structured["resolved_company"] = resolve_entity_name(structured.get("entity_name"))
            processed.append(structured)
            print(f"Processed: {structured.get('entity_name')}")
        except Exception as e:
            print(f"Skipped one company due to error: {e}")
        await asyncio.sleep(2)
    return processed

async def main():
    companies = load_json(YC_DATA_PATH)
    connector = create_ssl_connector()
    async with aiohttp.ClientSession(connector=connector) as session:
        processed = await process_companies(session, companies)
        print(f"Successfully processed {len(processed)} out of {len(companies)} companies")
        save_to_json(processed, YC_DATA_PATH.replace("yc_companies.json", "yc_companies_structured.json"))
        print("Saved to data/yc_companies_structured.json")

if __name__ == "__main__":
    asyncio.run(main())