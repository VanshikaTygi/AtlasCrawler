import asyncio
from playwright.async_api import async_playwright
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import save_to_json, create_ssl_connector

YC_URL = "https://www.ycombinator.com/companies"

async def fetch_yc_companies(max_companies=200):
    companies = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(YC_URL, timeout=60000)
        await page.wait_for_selector("a[href^='/companies/']", timeout=30000)

        previous_count = 0
        while len(companies) < max_companies:
            cards = await page.query_selector_all("a[href^='/companies/']")
            companies = []

            # print(f"Found {len(cards)} company card elements")
            # if cards:
            #     print("Sample card HTML:", await cards[0].inner_html())
                
            for card in cards:
                name_el = await card.query_selector("span[class*='_coName_']")
                name = await name_el.inner_text() if name_el else None
                description = await card.inner_text() if name_el else None
                if name:
                    companies.append({"name": name, "description": description})

            if len(companies) == previous_count:
                break
            previous_count = len(companies)

            await page.mouse.wheel(0, 3000)
            await asyncio.sleep(1.5)

        await browser.close()
    return companies

async def main():
    companies = await fetch_yc_companies()
    print(f"Total fetched: {len(companies)} companies")
    save_to_json(companies, "data/yc_companies.json")
    print("Saved to data/yc_companies.json")

if __name__ == "__main__":
    asyncio.run(main())